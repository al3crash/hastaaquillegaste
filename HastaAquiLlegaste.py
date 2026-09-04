import streamlit as st
import io
import os
import json
import base64
import html
import random
import hashlib
import tempfile
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# OpenAI
from openai import OpenAI

# Audio
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.utils import which


# ============================================================
# HASTA AQUÍ LLEGASTE — EL ORÁCULO NEGRO V5
# ============================================================
#
# Windows / VS Code:
#
#   pip install streamlit openai reportlab pydub
#
# Además necesitas FFmpeg para que pydub pueda leer/exportar MP3.
# Puedes comprobarlo desde una terminal con:
#
#   ffmpeg -version
#
# En Streamlit Cloud también habrá que declarar las dependencias.
#
# API KEY:
#   NO la pongas aquí.
#
# Windows PowerShell:
#   $env:OPENAI_API_KEY="TU_API_KEY"
#
# Windows CMD:
#   set OPENAI_API_KEY=TU_API_KEY
#
# Streamlit Cloud:
#   OPENAI_API_KEY = "TU_API_KEY"
#   dentro de Secrets.
#
# Coloca:
#   hell.mp3
# junto a este archivo.
#
# IMPORTANTE:
# Esta aplicación es una experiencia narrativa/entretenimiento.
# Las fechas y circunstancias generadas no son predicciones reales.
# ============================================================


st.set_page_config(
    page_title="HASTA AQUÍ LLEGASTE — El Oráculo Negro",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CLIENTE OPENAI
# ============================================================

# ============================================================
# 🔑 API KEY DE OPENAI
# ============================================================
# PEGA AQUÍ TU NUEVA API KEY.
#
# IMPORTANTE:
# - NO uses la API key que publicaste anteriormente.
# - Genera una nueva en la plataforma de OpenAI.
# - No compartas este archivo ni lo subas a GitHub mientras
#   la llave esté escrita directamente aquí.
#
OPENAI_API_KEY = "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"


def obtener_cliente_openai():
    api_key = OPENAI_API_KEY.strip()

    if not api_key:
        return None

    return OpenAI(api_key=api_key)


client = obtener_cliente_openai()


# ============================================================
# ESTADO DE SESIÓN
# ============================================================

defaults = {
    "ritual_iniciado": False,
    "resultado": None,
    "audio_bytes": None,
    "folio": None,
    "hell_autoplay_intento": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
<style>

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 50% 35%, #12051c 0%, #050207 45%, #010102 100%);
    min-height: 100vh;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.block-container {
    max-width: 780px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

h1 {
    color: #00ff66 !important;
    text-align: center;
    font-family: Georgia, serif;
    font-weight: bold;
    letter-spacing: 4px;
    text-shadow:
        0 0 8px #00ff66,
        0 0 20px #1b4d3e,
        0 0 40px #3d0066;
}

h2, h3 {
    color: #9d4edd !important;
    text-align: center;
    font-family: "Courier New", monospace;
    letter-spacing: 2px;
}

p, label {
    color: #b5b5c3 !important;
    font-family: "Courier New", monospace;
    font-size: 13px;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox input {
    background-color: #090810 !important;
    color: #00ff66 !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: #00ff66 !important;
    box-shadow: 0 0 12px rgba(0,255,102,.2);
}

.stButton > button,
.stFormSubmitButton > button {
    background-color: #1a0033;
    color: #00ff66 !important;
    font-weight: bold;
    font-family: Georgia, serif;
    border: 2px solid #00ff66;
    padding: 14px;
    font-size: 16px;
    letter-spacing: 2px;
    transition: all 0.3s ease;
    width: 100%;
    min-height: 52px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #00ff66;
    color: #020204 !important;
    box-shadow: 0 0 30px #00ff66;
}

.contenedor-centrado {
    display: flex;
    justify-content: center;
    width: 100%;
    padding: 35px 0;
}

.lapida-canvas {
    background: linear-gradient(180deg, #29282d 0%, #111014 100%);
    border: 5px double #00ff66;
    border-radius: 180px 180px 25px 25px;
    padding: 55px 28px 40px 28px;
    color: #c1c1cb !important;
    text-align: center;
    font-family: Georgia, serif;
    box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    width: min(450px, 88vw);
    margin: 20px auto;
    border-bottom: 20px solid #080709;
    box-sizing: border-box;
}

.lapida-rip {
    font-size: clamp(30px, 8vw, 40px);
    font-weight: bold;
    color: #020204;
    letter-spacing: 6px;
    margin-bottom: 8px;
}

.lapida-nombre {
    font-size: clamp(18px, 5vw, 25px);
    font-weight: bold;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 2px;
    overflow-wrap: anywhere;
}

.lapida-fechas {
    font-size: 13px;
    color: #00ff66;
    font-style: italic;
    margin-bottom: 22px;
    border-bottom: 1px double #3d0066;
    padding-bottom: 12px;
}

.lapida-causa {
    font-size: 13px;
    color: #e2e2e9;
    line-height: 1.6;
    text-align: justify;
    margin-bottom: 25px;
    background: rgba(5,2,10,0.6);
    padding: 14px;
    border-top: 1px solid #3d0066;
    border-bottom: 1px solid #3d0066;
}

.lapida-dedicatoria {
    font-size: 12px;
    color: #777785;
    font-style: italic;
    line-height: 1.5;
}

.oraculo-box {
    text-align: center;
    background: #110b1a;
    padding: 18px;
    border: 1px solid #9d4edd;
    border-radius: 8px;
    width: min(560px, 94vw);
    margin: 0 auto 20px auto;
    box-sizing: border-box;
}

.oraculo-status {
    color: #00ff66 !important;
    font-family: monospace;
    font-size: 12px;
    margin-bottom: 12px;
}

.terror-narrativa {
    background:
        linear-gradient(rgba(10,3,15,.92), rgba(5,2,8,.96));
    border-left: 2px solid #7b2cbf;
    border-right: 2px solid #7b2cbf;
    padding: 22px;
    border-radius: 8px;
    color: #cfcbd8;
    font-family: Georgia, serif;
    font-size: 16px;
    line-height: 1.75;
    box-shadow: 0 0 30px rgba(123,44,191,.12);
}

.nota {
    color: #666678 !important;
    font-size: 10px !important;
    text-align: center;
}

@media (max-width: 600px) {

    .block-container {
        padding-left: .7rem;
        padding-right: .7rem;
    }

    h1 {
        font-size: 1.7rem !important;
        letter-spacing: 2px;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        font-size: 14px;
    }

    .lapida-canvas {
        padding-left: 18px;
        padding-right: 18px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# AUDIO AMBIENTAL
# ============================================================

def reproducir_ambiente():
    if not os.path.exists("hell.mp3"):
        return

    try:
        with open("hell.mp3", "rb") as f:
            data = f.read()

        b64 = base64.b64encode(data).decode()

        st.markdown(
            f"""
            <audio id="hell-background"
                   src="data:audio/mpeg;base64,{b64}"
                   loop
                   preload="auto"
                   style="display:none">
            </audio>

            <script>
            (() => {{
                const audio = document.getElementById("hell-background");

                if (!audio) return;

                audio.volume = 0.55;

                const iniciar = () => {{
                    audio.volume = 0.55;

                    const p = audio.play();

                    if (p) {{
                        p.catch(() => {{}});
                    }}
                }};

                document.addEventListener("click", iniciar, {{once:true}});
                document.addEventListener("touchstart", iniciar, {{once:true}});

                iniciar();
            }})();
            </script>
            """,
            unsafe_allow_html=True,
        )

    except Exception:
        pass


# ============================================================
# UTILIDADES
# ============================================================

def escapar(texto):
    return html.escape(str(texto))


def limpiar_nombre_archivo(nombre):
    caracteres = '<>:"/\\|?*'
    limpio = "".join("_" if c in caracteres else c for c in nombre)
    return limpio.strip() or "Expediente"


def edad_desde_fecha(fecha):
    hoy = datetime.now().date()

    edad = hoy.year - fecha.year

    if (hoy.month, hoy.day) < (fecha.month, fecha.day):
        edad -= 1

    return max(0, edad)


def dibujar_codigo_barras(canvas, x, y, semilla):
    canvas.saveState()

    random.seed(semilla)

    ancho_total = 0
    grosores = [1, 2, 3, 1.5]
    espaciados = [1, 2, 1.5]

    for _ in range(40):
        ancho_barra = random.choice(grosores)
        espacio = random.choice(espaciados)

        canvas.setFillColor(colors.black)

        canvas.rect(
            x + ancho_total,
            y,
            ancho_barra,
            40,
            fill=1,
            stroke=0,
        )

        ancho_total += ancho_barra + espacio

    canvas.restoreState()


# ============================================================
# OPENAI: GENERACIÓN DE SENTENCIA
# ============================================================

def generar_sentencia_ia(datos):

    if client is None:
        raise RuntimeError(
            "No se encontró OPENAI_API_KEY. "
            "Configúrala como variable de entorno o en Streamlit Secrets."
        )

    prompt_sistema = """
Eres EL ORÁCULO NEGRO, un narrador especializado en terror psicológico.

Tu función es transformar el expediente de una persona en una experiencia
narrativa oscura, cinematográfica e inquietante.

REGLAS IMPORTANTES:

1. Esto es una experiencia de entretenimiento y ficción narrativa.
2. NO afirmes tener poderes sobrenaturales reales.
3. NO presentes la fecha como una predicción real.
4. La fecha puede ser ficticia y debe tratarse como parte del juego.
5. Usa los datos proporcionados para construir una historia coherente.
6. La causa y las circunstancias deben depender de múltiples respuestas,
   no solamente de un único campo.
7. Utiliza especialmente los dos miedos seleccionados.
8. El sexo debe respetarse para esposa/esposo.
9. Evita gore explícito y descripciones gráficas.
10. El terror debe ser psicológico: anticipación, aislamiento, sonidos,
    lugares, decisiones, coincidencias inquietantes y sensación de destino.
11. No repitas exactamente frases del cuestionario.
12. No uses siempre accidentes de vehículo. Varía las circunstancias.
13. La historia debe sentirse escrita específicamente para esa persona.
14. La muerte debe ser ficticia, pero internamente coherente.
15. No hagas afirmaciones médicas reales ni calcules expectativa de vida real.

DEVUELVE ÚNICAMENTE JSON VÁLIDO con esta estructura:

{
  "titulo": "...",
  "fecha_muerte": "DD/MM/YYYY",
  "lugar": "...",
  "causa": "...",
  "circunstancias": "...",
  "narracion": "...",
  "epitafio": "...",
  "ambiente": "...",
  "nivel_terror": 1
}

nivel_terror debe estar entre 1 y 10.

La narración debe tener entre 180 y 350 palabras.
"""


    datos_json = json.dumps(
        datos,
        ensure_ascii=False,
        indent=2,
    )

    respuesta = client.responses.create(
        model="gpt-5.6-luna",
        instructions=prompt_sistema,
        input=(
            "Analiza este expediente y genera la sentencia personalizada.\n\n"
            + datos_json
        ),
    )

    texto = respuesta.output_text.strip()

    # Limpiar posibles fences si el modelo los incluye.
    if texto.startswith("```"):
        texto = texto.replace("```json", "", 1)
        texto = texto.replace("```", "")
        texto = texto.strip()

    resultado = json.loads(texto)

    campos = [
        "titulo",
        "fecha_muerte",
        "lugar",
        "causa",
        "circunstancias",
        "narracion",
        "epitafio",
        "ambiente",
        "nivel_terror",
    ]

    for campo in campos:
        if campo not in resultado:
            raise ValueError(
                f"La respuesta de la IA no contiene el campo: {campo}"
            )

    return resultado


# ============================================================
# OPENAI: VOZ
# ============================================================

def generar_audio_openai(texto):

    if client is None:
        raise RuntimeError(
            "No se encontró OPENAI_API_KEY."
        )

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3",
    )

    tmp.close()

    try:

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="onyx",
            input=texto,
            instructions=(
                "Habla como un hombre adulto de voz profunda y grave. "
                "Mantén un ritmo lento, solemne y controlado. "
                "La interpretación debe parecer la de una entidad oscura "
                "que habla con calma desde un espacio enorme y vacío. "
                "No grites. No susurres. No hagas voces caricaturescas. "
                "La voz debe permanecer natural, clara y amenazante."
            ),
            response_format="mp3",
        ) as response:

            response.stream_to_file(tmp.name)

        audio = AudioSegment.from_file(
            tmp.name,
            format="mp3",
        )

        # ====================================================
        # CONTROL DE VELOCIDAD
        # ====================================================
        #
        # 1.00 = velocidad original
        # 0.95 = ligeramente lenta
        # 0.90 = lenta
        #
        velocidad = 0.92

        nuevo_rate = int(audio.frame_rate * velocidad)

        audio = audio._spawn(
            audio.raw_data,
            overrides={
                "frame_rate": nuevo_rate
            },
        ).set_frame_rate(audio.frame_rate)

        # ====================================================
        # PROFUNDIDAD / GRAVEDAD
        # ====================================================
        #
        # 1.00 = tono original
        # 0.96 = ligeramente más grave
        # 0.92 = grave
        #
        factor_grave = 0.93

        nuevo_rate = int(audio.frame_rate * factor_grave)

        audio = audio._spawn(
            audio.raw_data,
            overrides={
                "frame_rate": nuevo_rate
            },
        ).set_frame_rate(audio.frame_rate)

        # ====================================================
        # REVERBERACIÓN SUAVE
        # ====================================================

        reverb = AudioSegment.silent(
            duration=len(audio) + 140
        )

        for delay_ms, gain_db in [
            (32, -21),
            (68, -27),
            (105, -33),
        ]:

            copia = audio + gain_db

            reverb = reverb.overlay(
                copia,
                position=delay_ms,
            )

        audio = audio.overlay(
            reverb[:len(audio) + 140]
        )

        audio = normalize(
            audio,
            headroom=2.0,
        )

        salida = io.BytesIO()

        audio.export(
            salida,
            format="mp3",
            bitrate="128k",
        )

        return salida.getvalue()

    finally:

        try:
            os.remove(tmp.name)
        except Exception:
            pass


# ============================================================
# GENERACIÓN DEL PDF
# ============================================================

def generar_pdf(datos, resultado, folio):

    buffer = io.BytesIO()

    nombre = datos["nombre"].upper()
    sexo = datos["sexo"]

    if sexo == "Masculino":
        dedicatoria = (
            "En memoria de tu esposa, tus amigos y seres queridos."
        )
    else:
        dedicatoria = (
            "En memoria de tu esposo, tus amigos y seres queridos."
        )

    def marco(canvas, doc):

        canvas.saveState()

        canvas.setStrokeColor(
            colors.HexColor("#7b2cbf")
        )

        canvas.setLineWidth(2)

        canvas.rect(
            20,
            20,
            572,
            752,
        )

        canvas.setLineWidth(.5)

        canvas.rect(
            24,
            24,
            564,
            744,
        )

        canvas.setFillColor(
            colors.HexColor("#111111")
        )

        canvas.rect(
            530,
            710,
            8,
            40,
            fill=1,
            stroke=0,
        )

        canvas.rect(
            516,
            732,
            36,
            8,
            fill=1,
            stroke=0,
        )

        dibujar_codigo_barras(
            canvas,
            40,
            45,
            sum(ord(c) for c in folio),
        )

        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=100,
    )

    styles = getSampleStyleSheet()

    gob = ParagraphStyle(
        "Gob",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#111111"),
    )

    sub = ParagraphStyle(
        "Sub",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#444444"),
    )

    sec = ParagraphStyle(
        "Sec",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.white,
        backColor=colors.HexColor("#4a154b"),
        borderPadding=4,
    )

    campo = ParagraphStyle(
        "Campo",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#222222"),
    )

    valor = ParagraphStyle(
        "Valor",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#444444"),
    )

    causa = ParagraphStyle(
        "Causa",
        fontName="Helvetica-BoldOblique",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#8b0000"),
    )

    story = []

    story.append(
        Paragraph(
            "ESTADOS UNIDOS DEL MÁS ALLÁ",
            gob,
        )
    )

    story.append(
        Paragraph(
            "REGISTRO CIVIL RESTRINGIDO • "
            "ACTA DE DEFUNCIÓN FICTICIA",
            sub,
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>FOLIO:</b> {escapar(folio)}",
            valor,
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "I. DATOS DE LA PERSONA",
            sec,
        )
    )

    story.append(Spacer(1, 6))

    persona = [
        [
            Paragraph("NOMBRE:", campo),
            Paragraph(escapar(nombre), valor),
        ],
        [
            Paragraph("SEXO:", campo),
            Paragraph(escapar(sexo), valor),
        ],
        [
            Paragraph("NACIMIENTO:", campo),
            Paragraph(
                datos["fecha_nacimiento"],
                valor,
            ),
        ],
        [
            Paragraph("ESTADO CIVIL:", campo),
            Paragraph(
                escapar(datos["estado_civil"]),
                valor,
            ),
        ],
        [
            Paragraph("OCUPACIÓN:", campo),
            Paragraph(
                escapar(datos["ocupacion"]),
                valor,
            ),
        ],
    ]

    t = Table(
        persona,
        colWidths=[150, 370],
    )

    t.setStyle(
        TableStyle(
            [
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    .25,
                    colors.HexColor("#E0E0E0"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    .5,
                    colors.HexColor("#AAAAAA"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(t)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "II. DATOS DEL FALLECIMIENTO",
            sec,
        )
    )

    story.append(Spacer(1, 6))

    fallecimiento = [
        [
            Paragraph("FECHA:", campo),
            Paragraph(
                escapar(resultado["fecha_muerte"]),
                valor,
            ),
        ],
        [
            Paragraph("LUGAR:", campo),
            Paragraph(
                escapar(resultado["lugar"]),
                valor,
            ),
        ],
        [
            Paragraph("CAUSA:", campo),
            Paragraph(
                escapar(resultado["causa"]),
                causa,
            ),
        ],
        [
            Paragraph("CIRCUNSTANCIAS:", campo),
            Paragraph(
                escapar(resultado["circunstancias"]),
                valor,
            ),
        ],
    ]

    tf = Table(
        fallecimiento,
        colWidths=[150, 370],
    )

    tf.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    .25,
                    colors.HexColor("#E0E0E0"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    .5,
                    colors.HexColor("#AAAAAA"),
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(tf)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "III. NARRATIVA DEL ORÁCULO",
            sec,
        )
    )

    story.append(Spacer(1, 7))

    story.append(
        Paragraph(
            escapar(resultado["narracion"]),
            valor,
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "IV. EPITAFIO",
            sec,
        )
    )

    story.append(Spacer(1, 7))

    story.append(
        Paragraph(
            f'<i>"{escapar(dedicatoria)} '
            f'{escapar(resultado["epitafio"])}"</i>',
            valor,
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "V. CADENA DIGITAL DEL INFRAMUNDO",
            sec,
        )
    )

    story.append(Spacer(1, 7))

    cadena = (
        f"||{folio}||"
        f"{nombre}||"
        f"{resultado['fecha_muerte']}||"
        f"{hashlib.sha256(nombre.encode()).hexdigest()[:16]}||"
        "#PARCAS_AUTENTICACION_DIGITAL||"
    )

    story.append(
        Paragraph(
            f"<font size=7 color='#666666'>"
            f"{escapar(cadena)}"
            f"</font>",
            sub,
        )
    )

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "_____________________________<br/>"
            "Átropos<br/>"
            "Oficial Registrador del Hilo",
            sub,
        )
    )

    doc.build(
        story,
        onFirstPage=marco,
        onLaterPages=marco,
    )

    return buffer.getvalue()


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    "<h1>⛧ HASTA AQUÍ LLEGASTE ⛧</h1>",
    unsafe_allow_html=True,
)


# ============================================================
# INICIO DEL RITUAL
# ============================================================

if not st.session_state.ritual_iniciado:

    st.markdown(
        "<p style='text-align:center;color:#8a2be2;"
        "font-size:16px;font-weight:bold;'>"
        "EL ALTAR ESTÁ APAGADO"
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center;color:#666;'>"
        "Las respuestas abrirán el expediente del Oráculo."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="contenedor-centrado">',
        unsafe_allow_html=True,
    )

    if st.button(
        "👁️ INICIAR EL RITUAL OMINOSO",
        key="iniciar_ritual",
    ):

        st.session_state.ritual_iniciado = True
        st.session_state.resultado = None
        st.session_state.audio_bytes = None

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.stop()


# Intentar iniciar el ambiente una vez que el usuario ya interactuó.
reproducir_ambiente()


# ============================================================
# CABECERA DEL EXPEDIENTE
# ============================================================

st.markdown(
    "<p style='text-align:center;color:#4e4e6a !important;"
    "font-style:italic;'>"
    "Las respuestas serán interpretadas por el Oráculo."
    "</p>",
    unsafe_allow_html=True,
)

st.write("---")


# ============================================================
# FORMULARIO
# ============================================================

with st.form("expediente_oraculo"):

    st.markdown("### 👁️ I. Identidad")

    nombre = st.text_input(
        "Nombre completo:",
        max_chars=120,
    )

    sexo = st.radio(
        "Sexo:",
        [
            "Masculino",
            "Femenino",
        ],
        horizontal=True,
    )

    fecha_nacimiento = st.date_input(
        "Fecha de nacimiento:",
        min_value=datetime(1910, 1, 1).date(),
        max_value=datetime.today().date(),
        value=datetime(1990, 1, 1).date(),
    )

    estado_civil = st.selectbox(
        "Estado civil:",
        [
            "Soltero/a",
            "Casado/a",
            "Divorciado/a",
            "Viudo/a",
            "En una relación",
        ],
    )

    st.write("---")

    st.markdown("### 🏢 II. Vida cotidiana")

    ocupacion = st.selectbox(
        "¿A qué te dedicas?",
        [
            "Construcción / Trabajo operativo",
            "Conductor / Repartidor",
            "Oficina / Desarrollo / Trabajo digital",
            "Comercio / Servicios",
            "Estudiante",
            "Trabajo médico / Emergencias",
            "Trabajo nocturno / Seguridad",
            "Otro",
        ],
    )

    transporte = st.selectbox(
        "¿Cuál es tu transporte principal?",
        [
            "Automóvil",
            "Motocicleta",
            "Bicicleta",
            "Metro / Tren",
            "Autobús",
            "Avión",
            "A pie",
            "Otro",
        ],
    )

    piso = st.slider(
        "¿En qué nivel/piso pasas más tiempo?",
        1,
        60,
        1,
    )

    entorno = st.select_slider(
        "¿Cómo describirías tu entorno habitual?",
        options=[
            "Muy tranquilo",
            "Normal",
            "Impredecible",
            "Hostil",
        ],
    )

    horario = st.select_slider(
        "¿En qué horario te desplazas más?",
        options=[
            "Mañana",
            "Tarde",
            "Noche",
            "Madrugada",
        ],
    )

    st.write("---")

    st.markdown("### 🌑 III. Miedos")

    miedo_principal = st.selectbox(
        "¿Qué te provoca más miedo?",
        [
            "El mar y las aguas profundas",
            "Un volcán",
            "Un terremoto",
            "Las alturas",
            "La oscuridad",
            "Estar completamente solo",
            "Lugares abandonados",
            "Espacios cerrados",
            "Incendios",
            "Tormentas eléctricas",
            "Accidentes automovilísticos",
            "Accidentes aéreos",
            "Animales agresivos",
            "Perder el control",
            "No poder pedir ayuda",
            "Ser perseguido",
            "Desconocidos",
            "Nada en particular",
        ],
    )

    miedo_secundario = st.selectbox(
        "¿Y qué otra cosa te inquieta?",
        [
            "El silencio absoluto",
            "El mar",
            "Las alturas",
            "Los terremotos",
            "La oscuridad",
            "La noche",
            "Los hospitales",
            "Los bosques",
            "Los túneles",
            "Los elevadores",
            "Las multitudes",
            "Viajar solo",
            "Perderme",
            "Quedar atrapado",
            "No saber qué está pasando",
            "Que nadie me escuche",
            "Los ruidos desconocidos",
            "Los lugares desconocidos",
        ],
    )

    miedo_nivel = st.slider(
        "¿Qué tan intenso es ese miedo?",
        1,
        10,
        6,
    )

    st.write("---")

    st.markdown("### 🕯️ IV. Hábitos y exposición")

    tabaco = st.select_slider(
        "Tabaco / vapeo:",
        options=[
            "Nunca",
            "Ocasional",
            "Frecuente",
            "Diario",
        ],
    )

    alcohol = st.select_slider(
        "Alcohol:",
        options=[
            "Nulo",
            "Ocasional",
            "Moderado",
            "Frecuente",
        ],
    )

    deportes = st.select_slider(
        "Actividades de riesgo:",
        options=[
            "Nunca",
            "Raras veces",
            "A veces",
            "Frecuentemente",
        ],
    )

    fatiga = st.select_slider(
        "Nivel de cansancio:",
        options=[
            "Bajo",
            "Moderado",
            "Alto",
            "Extremo",
        ],
    )

    dormir = st.select_slider(
        "¿Cómo duermes normalmente?",
        options=[
            "Muy bien",
            "Normal",
            "Mal",
            "Muy mal",
        ],
    )

    st.write("---")

    st.markdown("### 🕳️ V. El último detalle")

    lugar_preferido = st.selectbox(
        "¿Dónde te sentirías más vulnerable?",
        [
            "Una carretera vacía",
            "Un edificio abandonado",
            "Un bosque de noche",
            "Una playa desierta",
            "Una ciudad desconocida",
            "Un hospital vacío",
            "Un túnel",
            "Un elevador detenido",
            "Un edificio muy alto",
            "Una embarcación",
            "Una estación de tren",
            "Una casa desconocida",
        ],
    )

    aislamiento = st.select_slider(
        "¿Qué tan cómodo estás estando completamente solo?",
        options=[
            "Muy cómodo",
            "Normal",
            "Incómodo",
            "Me aterra",
        ],
    )

    objeto_extraño = st.selectbox(
        "Si encontraras un objeto antiguo, ¿qué harías?",
        [
            "Lo ignoraría",
            "Lo observaría",
            "Lo tocaría",
            "Me lo llevaría",
            "Intentaría descubrir su historia",
        ],
    )

    enviar = st.form_submit_button(
        "👁️ REVELAR SENTENCIA DEL ORÁCULO",
        use_container_width=True,
    )


# ============================================================
# BOTÓN LIMPIAR
# ============================================================

if st.button(
    "🧹 LIMPIAR EXPEDIENTE",
    key="limpiar_expediente",
):

    st.session_state.resultado = None
    st.session_state.audio_bytes = None
    st.session_state.folio = None

    st.rerun()


# ============================================================
# PROCESAMIENTO
# ============================================================

if enviar:

    if not nombre.strip():

        st.error(
            "El Oráculo necesita un nombre para abrir el expediente."
        )

    elif client is None:

        st.error(
            "No se encontró OPENAI_API_KEY. "
            "Configura la variable de entorno antes de continuar."
        )

    else:

        edad = edad_desde_fecha(
            fecha_nacimiento
        )

        datos = {
            "nombre": nombre.strip(),
            "sexo": sexo,
            "edad_actual": edad,
            "fecha_nacimiento": fecha_nacimiento.strftime("%d/%m/%Y"),
            "estado_civil": estado_civil,
            "ocupacion": ocupacion,
            "transporte": transporte,
            "piso": piso,
            "entorno": entorno,
            "horario": horario,
            "miedo_principal": miedo_principal,
            "miedo_secundario": miedo_secundario,
            "intensidad_miedo": miedo_nivel,
            "tabaco": tabaco,
            "alcohol": alcohol,
            "actividades_riesgo": deportes,
            "fatiga": fatiga,
            "sueno": dormir,
            "lugar_vulnerable": lugar_preferido,
            "aislamiento": aislamiento,
            "objeto_extraño": objeto_extraño,
        }

        with st.spinner(
            "El Oráculo está leyendo el expediente..."
        ):

            try:

                resultado = generar_sentencia_ia(
                    datos
                )

                # Validación básica de fecha.
                try:
                    datetime.strptime(
                        resultado["fecha_muerte"],
                        "%d/%m/%Y",
                    )
                except Exception:
                    resultado["fecha_muerte"] = (
                        datetime.now() +
                        timedelta(
                            days=random.randint(
                                3650,
                                14600,
                            )
                        )
                    ).strftime("%d/%m/%Y")

                st.session_state.resultado = {
                    "datos": datos,
                    "resultado": resultado,
                }

                st.session_state.audio_bytes = None

                st.session_state.folio = (
                    f"DEF-"
                    f"{random.randint(100000,999999)}-"
                    f"{datetime.now().year}"
                )

            except Exception as e:

                st.error(
                    "No fue posible consultar al Oráculo. "
                    f"Detalle técnico: {e}"
                )


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

if st.session_state.resultado:

    datos = st.session_state.resultado["datos"]
    resultado = st.session_state.resultado["resultado"]
    folio = st.session_state.folio

    nombre_upper = datos["nombre"].upper()

    if datos["sexo"] == "Masculino":
        dedicatoria = (
            "En memoria de tu esposa, tus amigos y seres queridos."
        )
    else:
        dedicatoria = (
            "En memoria de tu esposo, tus amigos y seres queridos."
        )

    st.write("---")

    st.markdown(
        f"""
        <div class="lapida-canvas">

            <div class="lapida-rip">
                R. I. P.
            </div>

            <div class="lapida-nombre">
                {escapar(nombre_upper)}
            </div>

            <div class="lapida-fechas">
                {escapar(datos["fecha_nacimiento"])}
                &nbsp;—&nbsp;
                {escapar(resultado["fecha_muerte"])}
            </div>

            <div class="lapida-causa">

                <b>CAUSA DE MI MUERTE:</b><br>

                {escapar(resultado["causa"])}

                <br><br>

                <b>LUGAR:</b><br>

                {escapar(resultado["lugar"])}

            </div>

            <div class="lapida-dedicatoria">

                "{escapar(dedicatoria)}"

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="terror-narrativa">
            <b>{escapar(resultado["titulo"])}</b>
            <br><br>
            {escapar(resultado["narracion"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        "### 🎙️ SENTENCIA DE ULTRATUMBA"
    )

    # ========================================================
    # GENERAR AUDIO UNA SOLA VEZ
    # ========================================================

    if st.session_state.audio_bytes is None:

        if st.button(
            "🎙️ GENERAR Y ESCUCHAR SENTENCIA",
            key="generar_voz",
        ):

            with st.spinner(
                "El Oráculo está tomando forma..."
            ):

                try:

                    texto_voz = (
                        f"Hasta aquí llegaste, "
                        f"{nombre_upper}. "
                        f"{resultado['narracion']}"
                    )

                    st.session_state.audio_bytes = (
                        generar_audio_openai(
                            texto_voz
                        )
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"No se pudo generar la voz: {e}"
                    )

    if st.session_state.audio_bytes:

        audio_bytes = st.session_state.audio_bytes

        # El audio NO tiene loop.
        st.audio(
            audio_bytes,
            format="audio/mp3",
        )

        st.download_button(
            label="⬇️ DESCARGAR SENTENCIA DE ULTRATUMBA",
            data=audio_bytes,
            file_name=(
                f"Sentencia_Ultratumba_"
                f"{limpiar_nombre_archivo(nombre_upper)}.mp3"
            ),
            mime="audio/mpeg",
            key="descargar_audio",
            use_container_width=True,
        )

    st.write("---")

    # ========================================================
    # PDF
    # ========================================================

    try:

        pdf_bytes = generar_pdf(
            datos,
            resultado,
            folio,
        )

        st.download_button(
            label="📄 DESCARGAR ACTA DE DEFUNCIÓN",
            data=pdf_bytes,
            file_name=(
                f"Acta_Defuncion_Ficticia_"
                f"{limpiar_nombre_archivo(nombre_upper)}.pdf"
            ),
            mime="application/pdf",
            key="descargar_pdf",
            use_container_width=True,
        )

    except Exception as e:

        st.error(
            f"No se pudo generar el acta: {e}"
        )

    st.write("---")

    st.markdown(
        f"""
        <p class="nota">
            FOLIO DEL EXPEDIENTE: {escapar(folio)}
        </p>
        """,
        unsafe_allow_html=True,
    )
