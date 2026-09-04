# ============================================================
# SENTENCIA DE VOZ DE ULTRATUMBA
# Versión SIN API de OpenAI
# Compatible con Streamlit y preparada para Streamlit Cloud.
#
# ARCHIVOS QUE DEBES TENER:
#   app.py              <- este código
#   hell.mp3            <- música/ambiente de fondo
#
# requirements.txt:
#   streamlit
#   edge-tts
#   reportlab
#
# packages.txt:
#   ffmpeg
#
# IMPORTANTE:
# - No utiliza API de OpenAI.
# - La voz se genera con Microsoft Edge TTS.
# - La misma voz generada se utiliza para reproducir y descargar.
# - "Escuchar" y "Descargar acta" NO reinician los campos.
# - El botón "Limpiar campos" es el único que limpia el formulario.
# ============================================================

import asyncio
import html
import os
import random
import re
import subprocess
import tempfile
import uuid
import json
from datetime import date, datetime
from pathlib import Path

import streamlit as st
from edge_tts import Communicate
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Sentencia de Voz de Ultratumba",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
HELL_FILE = BASE_DIR / "hell.mp3"
TEMP_DIR = Path(tempfile.gettempdir()) / "sentencia_ultratumba"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# VOZ
# ============================================================
#
# Puedes cambiar aquí la voz y velocidad.
#
# Voces masculinas recomendadas:
#   es-MX-JorgeNeural
#   es-ES-AlvaroNeural
#   es-ES-JorgeNeural
#
# Para una voz más grave:
#   PITCH_SEMITONES = -2.5
#
# Para una voz todavía más grave:
#   PITCH_SEMITONES = -3.5
#
# SPEED:
#   0.90 = lenta
#   1.00 = normal
#   0.85 = más lenta y siniestra
#
VOICE = "es-MX-JorgeNeural"
VOICE_RATE = "-10%"
VOICE_VOLUME = "+0%"

# Grave, pero sin convertirla en una voz monstruosa artificial.
PITCH_SEMITONES = -2.5

# Reverberación MUY ligera.
# No usamos eco fuerte ni efecto de sonidero.
REVERB_DELAY_MS = 55
REVERB_DECAY = 0.18

# ============================================================
# APOYO AL PROYECTO / CONTADOR DE VISITAS
# ============================================================
# IMPORTANTE:
# Sustituye esta URL por TU enlace real de PayPal.
# Ejemplo: https://www.paypal.me/TuUsuario
PAYPAL_URL = "https://www.paypal.me/TU_USUARIO"

# Contador local de visitas.
# En Streamlit Cloud el archivo puede reiniciarse cuando el servicio
# se reinicia o vuelve a desplegarse. Para un contador permanente
# entre reinicios se requiere un servicio/base de datos externa.
VISITS_FILE = BASE_DIR / "visitas.json"


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Share Tech Mono', monospace;
}

.stApp {
    background:
        radial-gradient(circle at 50% 15%, rgba(70, 25, 90, .22), transparent 35%),
        radial-gradient(circle at 50% 70%, rgba(0, 255, 145, .07), transparent 38%),
        #030305;
    color: #ddd;
}

h1, h2, h3 {
    font-family: 'Cinzel', serif !important;
    letter-spacing: 3px;
}

.ritual-title {
    text-align:center;
    font-family:'Cinzel', serif;
    font-size:42px;
    letter-spacing:5px;
    color:#b06cff;
    text-shadow:0 0 15px rgba(160,70,255,.65);
    margin-top:10px;
}

.subtitle {
    text-align:center;
    color:#777;
    letter-spacing:3px;
    margin-bottom:35px;
}

.palida {
    position:relative;
    max-width:720px;
    margin:25px auto 45px auto;
    padding:34px 32px;
    border:2px solid #37ff9b;
    border-radius:30px;
    background:
        linear-gradient(180deg, rgba(15,15,18,.96), rgba(5,5,7,.98));
    box-shadow:
        0 0 10px rgba(55,255,155,.45),
        inset 0 0 40px rgba(0,0,0,.9);
}

.palida::before {
    content:"";
    position:absolute;
    inset:-9px;
    border:1px solid rgba(55,255,155,.22);
    border-radius:35px;
    pointer-events:none;
}

.lapida-nombre {
    text-align:center;
    font-family:'Cinzel', serif;
    font-size:35px;
    color:#eee;
    letter-spacing:4px;
    margin-bottom:15px;
}

.lapida-fechas {
    text-align:center;
    color:#8b8b8b;
    margin-bottom:28px;
}

.lapida-causa {
    background:rgba(255,255,255,.035);
    border-radius:10px;
    padding:18px;
    line-height:1.7;
    color:#d1d1d1;
}

.lapida-dedicatoria {
    margin-top:20px;
    padding-top:18px;
    border-top:1px solid rgba(255,255,255,.12);
    text-align:center;
    color:#aaa;
    line-height:1.8;
}

.expediente {
    border:1px solid rgba(175,80,255,.6);
    border-radius:12px;
    padding:18px;
    color:#bbb;
    background:rgba(90,20,120,.06);
    line-height:1.7;
}

.sentencia-box {
    border:1px solid rgba(180,80,255,.65);
    border-radius:14px;
    padding:25px;
    background:rgba(30,10,40,.32);
    box-shadow:0 0 25px rgba(130,50,255,.08);
    line-height:1.9;
    color:#ddd;
}

.final-text {
    text-align:center;
    margin:50px 0;
    color:#26ff96;
    font-family:'Cinzel', serif;
    font-size:23px;
    text-shadow:0 0 10px rgba(38,255,150,.35);
}

.reveal-wait {
    border:1px solid #b45cff;
    border-radius:14px;
    padding:20px;
    margin:18px 0;
    background:
        radial-gradient(circle at 50% 50%, rgba(160,60,255,.16), transparent 65%),
        rgba(10,6,16,.96);
    box-shadow:0 0 25px rgba(160,60,255,.16), inset 0 0 25px rgba(0,0,0,.8);
    text-align:center;
}

.reveal-wait-title {
    color:#c879ff;
    font-family:'Cinzel', serif;
    font-size:20px;
    letter-spacing:3px;
    margin-bottom:8px;
}

.reveal-wait-text {
    color:#aaa;
    font-size:12px;
    line-height:1.7;
}

.footer-hud {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:10px;
    margin:28px 0 12px 0;
    padding:12px;
    border-top:1px solid rgba(55,255,155,.35);
    border-bottom:1px solid rgba(180,92,255,.35);
    background:rgba(5,5,8,.8);
}

.footer-item {
    text-align:center;
    color:#777;
    font-size:10px;
    letter-spacing:1px;
}

.footer-item span {
    display:block;
    margin-bottom:5px;
}

.footer-item strong {
    display:block;
    color:#37ff9b;
    font-size:14px;
    letter-spacing:2px;
}

.support-title {
    text-align:center;
    color:#a965ff;
    font-family:'Cinzel', serif;
    letter-spacing:2px;
    font-size:13px;
    margin:12px 0;
}

.footer-signature {
    text-align:center;
    color:#555;
    font-size:10px;
    letter-spacing:2px;
    margin:18px 0 8px 0;
}

div.stButton > button {
    width:100%;
    border:2px solid #27ff9a;
    background:linear-gradient(90deg, #161021, #241438, #161021);
    color:#ddd;
    letter-spacing:2px;
    font-family:'Share Tech Mono', monospace;
    min-height:52px;
}

div.stButton > button:hover {
    border-color:#b45cff;
    color:#fff;
    box-shadow:0 0 18px rgba(180,92,255,.35);
}

[data-testid="stForm"] {
    background:rgba(255,255,255,.015);
    border:1px solid rgba(255,255,255,.08);
    border-radius:15px;
    padding:20px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES
# ============================================================

def limpiar_nombre(nombre: str) -> str:
    nombre = nombre.strip()
    nombre = re.sub(r'[\\/:*?"<>|]+', "", nombre)
    nombre = re.sub(r"\s+", " ", nombre)
    return nombre[:80] or "Sin_nombre"


def sexo_texto(sexo: str) -> tuple[str, str]:
    if sexo == "Masculino":
        return "tu esposo", "él"
    return "tu esposa", "ella"


def calcular_indice(datos: dict) -> int:
    score = 20

    edad = int(datos["edad"])
    if edad < 18:
        score += 12
    elif edad < 30:
        score += 7
    elif edad > 60:
        score += 10

    miedo = datos["miedo"]
    if miedo in ["La oscuridad", "La muerte", "Estar solo/a", "Lo desconocido"]:
        score += 15
    elif miedo in ["El mar", "Un volcán", "Terremotos", "Alturas"]:
        score += 9

    escenario = datos["escenario"]
    score += {
        "Accidente vehicular": 12,
        "Ahogamiento": 15,
        "Incendio": 13,
        "Caída": 10,
        "Desaparición": 18,
        "Causa desconocida": 20,
    }.get(escenario, 5)

    if datos["ultimo_estado"] == "Muy asustado/a":
        score += 15
    elif datos["ultimo_estado"] == "Inquieto/a":
        score += 8

    return max(1, min(99, score + random.randint(-5, 7)))


def generar_expediente(datos: dict) -> dict:
    indice = calcular_indice(datos)

    escenario = datos["escenario"]
    lugar = datos["entorno"]
    miedo = datos["miedo"]
    objeto = datos["objeto"]
    ultimo_estado = datos["ultimo_estado"]
    detalle = datos["detalle"]
    hora = datos["hora"]

    frases = {
        "Accidente vehicular": [
            "el vehículo perdió estabilidad antes del impacto",
            "se registraron signos compatibles con una colisión de alta energía",
            "la trayectoria terminó de forma abrupta",
        ],
        "Ahogamiento": [
            "el registro indica una inmersión prolongada",
            "se encontraron indicios compatibles con permanencia bajo el agua",
            "la última ubicación conocida se encontraba próxima a una zona acuática",
        ],
        "Incendio": [
            "el entorno presentó evidencia de exposición intensa al fuego",
            "el lugar registró daños compatibles con un incendio",
            "la concentración de humo habría reducido considerablemente la visibilidad",
        ],
        "Caída": [
            "la posición final es compatible con una caída desde altura",
            "el punto de impacto coincide con una trayectoria descendente",
            "el entorno presenta características compatibles con una caída accidental",
        ],
        "Desaparición": [
            "no existe una secuencia completa de los últimos acontecimientos",
            "la información disponible presenta un intervalo sin explicación",
            "la última ubicación confirmada no permite establecer una salida clara",
        ],
        "Causa desconocida": [
            "la causa no puede establecerse con absoluta precisión",
            "el expediente presenta información insuficiente para determinar una causa única",
            "algunos elementos del registro permanecen sin explicación",
        ],
    }

    frase = random.choice(frases.get(escenario, frases["Causa desconocida"]))

    if miedo == "El mar":
        detalle_miedo = "La referencia al mar aparece asociada con una respuesta de temor especialmente marcada."
    elif miedo == "Un volcán":
        detalle_miedo = "La actividad volcánica aparece registrada como uno de los temores principales."
    elif miedo == "Terremotos":
        detalle_miedo = "El expediente registra una preocupación recurrente relacionada con movimientos sísmicos."
    elif miedo == "La oscuridad":
        detalle_miedo = "La oscuridad aparece asociada a una reacción emocional elevada."
    elif miedo == "La muerte":
        detalle_miedo = "El concepto de muerte aparece como uno de los temores declarados."
    elif miedo == "Lo desconocido":
        detalle_miedo = "El temor a lo desconocido aparece de forma consistente en las respuestas."
    else:
        detalle_miedo = f"El temor declarado fue: {miedo.lower()}."

    causa = (
        f"{frase}. El incidente fue registrado en {lugar.lower()}. "
        f"La hora indicada fue aproximadamente {hora}. "
        f"{detalle_miedo} "
        f"Antes del desenlace, el estado descrito fue: {ultimo_estado.lower()}. "
        f"Cuando se le preguntó qué haría si encontrara un objeto antiguo, respondió: "
        f"“{objeto}”. "
        f"Detalle adicional proporcionado: {detalle if detalle else 'sin información adicional'}."
    )

    return {
        "indice": indice,
        "causa": causa,
        "frase": frase,
    }


def generar_sentencia(datos: dict, expediente: dict) -> str:
    nombre = datos["nombre"]
    edad = datos["edad"]
    sexo = datos["sexo"]
    miedo = datos["miedo"]
    escenario = datos["escenario"]
    entorno = datos["entorno"]
    estado = datos["ultimo_estado"]
    objeto = datos["objeto"]
    hora = datos["hora"]

    esposo_esposa, pronombre = sexo_texto(sexo)

    aperturas = [
        f"{nombre}... escucha con atención.",
        f"{nombre}... el expediente ya tiene tu nombre.",
        f"{nombre}... hay algo que aparece una y otra vez en tus respuestas.",
        f"{nombre}... algunas respuestas dejan una huella más profunda de lo que parecen.",
    ]

    conexiones = [
        f"Elegiste {miedo.lower()} como uno de tus mayores temores.",
        f"Tu respuesta sobre {miedo.lower()} no pasó desapercibida.",
        f"Entre todas tus respuestas, el temor a {miedo.lower()} quedó registrado.",
    ]

    finales = [
        "El expediente termina aquí.",
        "No hay más preguntas en este registro.",
        "Lo que queda ahora pertenece al silencio.",
        "A partir de este momento, el expediente queda cerrado.",
    ]

    sentencia = (
        f"{random.choice(aperturas)} "
        f"Tu edad registrada es {edad} años. "
        f"El escenario que elegiste fue {escenario.lower()}, en {entorno.lower()}, "
        f"aproximadamente a las {hora}. "
        f"{random.choice(conexiones)} "
        f"Tu último estado registrado fue {estado.lower()}. "
        f"También dijiste que, al encontrar un objeto antiguo, {objeto.lower()}. "
        f"El expediente encontró una relación entre tus respuestas y el desenlace registrado. "
        f"Hay detalles que no pueden explicarse solamente con las respuestas proporcionadas. "
        f"Y existe uno especialmente extraño: {expediente['frase'].lower()}. "
        f"En memoria de {esposo_esposa}, tus amigos y tus seres queridos. "
        f"{random.choice(finales)}"
    )

    return sentencia


async def _crear_voz_edge(texto: str, salida: Path):
    communicate = Communicate(
        texto,
        VOICE,
        rate=VOICE_RATE,
        volume=VOICE_VOLUME,
    )
    await communicate.save(str(salida))


def crear_voz_base(texto: str, salida: Path) -> bool:
    try:
        asyncio.run(_crear_voz_edge(texto, salida))
        return salida.exists() and salida.stat().st_size > 1000
    except Exception:
        return False


def aplicar_voz_grave_reverb(entrada: Path, salida: Path) -> bool:
    """
    Usa ffmpeg directamente.
    Esto evita la dependencia de pydub/pyaudioop que causaba
    el ModuleNotFoundError visto anteriormente.

    El procesamiento:
      1. baja ligeramente el tono
      2. mantiene la duración aproximadamente estable
      3. añade una reverberación corta y discreta
      4. no crea loop
    """
    # Factor aproximado para -2.5 semitonos.
    factor = 2 ** (PITCH_SEMITONES / 12)

    # Aecho:
    # in_gain, out_gain, delays, decays
    filtro = (
        f"asetrate=44100*{factor:.6f},"
        f"aresample=44100,"
        f"atempo={1/factor:.6f},"
        f"aecho=0.95:0.85:{REVERB_DELAY_MS}:{REVERB_DECAY}"
    )

    comando = [
        "ffmpeg",
        "-y",
        "-i",
        str(entrada),
        "-vn",
        "-af",
        filtro,
        "-codec:a",
        "libmp3lame",
        "-b:a",
        "128k",
        str(salida),
    ]

    try:
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )
        return resultado.returncode == 0 and salida.exists() and salida.stat().st_size > 1000
    except Exception:
        return False


def generar_audio_sentencia(texto: str) -> Path | None:
    identificador = uuid.uuid4().hex

    base = TEMP_DIR / f"voz_base_{identificador}.mp3"
    final = TEMP_DIR / f"sentencia_{identificador}.mp3"

    if not crear_voz_base(texto, base):
        return None

    # Si ffmpeg existe, procesamos la voz.
    procesada = aplicar_voz_grave_reverb(base, final)

    if procesada:
        try:
            base.unlink(missing_ok=True)
        except Exception:
            pass
        return final

    # Fallback: si ffmpeg no está disponible, entregamos la voz base.
    # Así la página sigue teniendo audio y no se queda en blanco.
    return base


def registrar_visita() -> int:
    """
    Contador sencillo y persistente mientras el archivo de la app
    permanezca en el mismo almacenamiento.
    Se incrementa una sola vez por sesión del navegador.
    """
    if st.session_state.get("visita_contada", False):
        return int(st.session_state.get("visitas", 0))

    visitas = 0

    try:
        if VISITS_FILE.exists():
            data = json.loads(VISITS_FILE.read_text(encoding="utf-8"))
            visitas = int(data.get("visitas", 0))
    except Exception:
        visitas = 0

    visitas += 1

    try:
        VISITS_FILE.write_text(
            json.dumps({"visitas": visitas}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        # Si el entorno no permite escribir, seguimos mostrando
        # al menos el contador de esta sesión.
        pass

    st.session_state.visita_contada = True
    st.session_state.visitas = visitas
    return visitas


def mostrar_hud_inferior():
    """HUD inferior con contador, apoyo y firma del creador."""
    visitas = registrar_visita()

    st.markdown(
        f"""
        <div class="footer-hud">
            <div class="footer-item">
                👁️ <span>EXPEDIENTES VISITANTES</span>
                <strong>{visitas:,}</strong>
            </div>
            <div class="footer-item">
                ☠️ <span>REGISTRO</span>
                <strong>ULTRATUMBA</strong>
            </div>
            <div class="footer-item">
                <span>CREATED BY</span>
                <strong>ALEX A.</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="support-title">🕯️ AYUDA A MANTENER ABIERTA ESTA PUERTA</div>',
        unsafe_allow_html=True,
    )

    st.link_button(
        "💜 APOYAR PROYECTO",
        PAYPAL_URL,
        use_container_width=True,
    )


def iniciar_ambiente():
    """
    El navegador bloquea el autoplay de audio en muchas circunstancias.
    Por eso el ambiente se inicia mediante el botón "INICIAR EL RITUAL".
    Se utiliza HTML/JS con reproducción después de una interacción
    directa del usuario.
    """
    if not HELL_FILE.exists():
        return

    try:
        import base64

        audio_bytes = HELL_FILE.read_bytes()
        encoded = base64.b64encode(audio_bytes).decode("utf-8")

        st.components.v1.html(
            f"""
            <audio id="hellAmbient" autoplay loop>
                <source src="data:audio/mpeg;base64,{encoded}" type="audio/mpeg">
            </audio>

            <script>
            const audio = document.getElementById("hellAmbient");
            audio.volume = 0.22;
            audio.play().catch(() => {{}});
            </script>
            """,
            height=1,
        )
    except Exception:
        pass


def crear_acta_pdf(datos: dict, expediente: dict) -> bytes:
    nombre = limpiar_nombre(datos["nombre"])

    archivo = TEMP_DIR / f"acta_{uuid.uuid4().hex}.pdf"

    # Intentar una fuente Unicode de Windows.
    fuente_normal = "Helvetica"
    fuente_negrita = "Helvetica-Bold"

    posibles_fuentes = [
        ("C:/Windows/Fonts/arial.ttf", "Arial"),
        ("C:/Windows/Fonts/arialbd.ttf", "Arial-Bold"),
    ]

    try:
        normal_path = Path(posibles_fuentes[0][0])
        bold_path = Path(posibles_fuentes[1][0])

        if normal_path.exists() and bold_path.exists():
            pdfmetrics.registerFont(TTFont("ArialCustom", str(normal_path)))
            pdfmetrics.registerFont(TTFont("ArialCustomBold", str(bold_path)))
            fuente_normal = "ArialCustom"
            fuente_negrita = "ArialCustomBold"
    except Exception:
        pass

    doc = SimpleDocTemplate(
        str(archivo),
        pagesize=LETTER,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
    )

    estilos = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Title"],
        fontName=fuente_negrita,
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    normal = ParagraphStyle(
        "NormalCustom",
        parent=estilos["BodyText"],
        fontName=fuente_normal,
        fontSize=9.5,
        leading=14,
        spaceAfter=8,
    )

    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Heading2"],
        fontName=fuente_negrita,
        fontSize=11,
        leading=15,
        spaceBefore=10,
        spaceAfter=7,
    )

    story = []

    story.append(Paragraph("ACTA DE DEFUNCIÓN", titulo))
    story.append(
        Paragraph(
            "REGISTRO DEL EXPEDIENTE DE ULTRATUMBA",
            ParagraphStyle(
                "Mini",
                parent=normal,
                alignment=TA_CENTER,
                fontName=fuente_negrita,
            ),
        )
    )
    story.append(Spacer(1, 15))

    expediente_id = f"DEF-{random.randint(10000,99999)}-{date.today().year}"

    tabla = [
        ["EXPEDIENTE", expediente_id],
        ["NOMBRE", html.escape(nombre)],
        ["SEXO", html.escape(datos["sexo"])],
        ["EDAD", f"{datos['edad']} años"],
        ["ESCENARIO", html.escape(datos["escenario"])],
        ["ENTORNO", html.escape(datos["entorno"])],
        ["HORA REGISTRADA", html.escape(datos["hora"])],
        ["ÍNDICE NARRATIVO", f"{expediente['indice']} / 100"],
        ["FECHA DEL REGISTRO", date.today().strftime("%d/%m/%Y")],
    ]

    t = Table(tabla, colWidths=[5 * cm, 11 * cm])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), fuente_normal),
                ("FONTNAME", (0, 0), (0, -1), fuente_negrita),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("CAUSA DE MUERTE", subtitulo))
    story.append(Paragraph(html.escape(expediente["causa"]), normal))

    story.append(Paragraph("DATOS COMPLEMENTARIOS", subtitulo))
    story.append(
        Paragraph(
            f"Temor declarado: {html.escape(datos['miedo'])}. "
            f"Estado previo: {html.escape(datos['ultimo_estado'])}. "
            f"Respuesta ante objeto antiguo: {html.escape(datos['objeto'])}.",
            normal,
        )
    )

    story.append(Paragraph("DETALLE ADICIONAL", subtitulo))
    story.append(
        Paragraph(
            html.escape(datos["detalle"] or "No se proporcionó información adicional."),
            normal,
        )
    )

    story.append(Spacer(1, 18))

    esposo_esposa, _ = sexo_texto(datos["sexo"])

    story.append(
        Paragraph(
            f"En memoria de {esposo_esposa}, tus amigos y seres queridos.",
            ParagraphStyle(
                "Dedicatoria",
                parent=normal,
                alignment=TA_CENTER,
                fontName=fuente_normal,
                fontSize=10,
                leading=15,
            ),
        )
    )

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "DOCUMENTO GENERADO POR EL REGISTRO NARRATIVO.",
            ParagraphStyle(
                "Final",
                parent=normal,
                alignment=TA_CENTER,
                fontName=fuente_normal,
                fontSize=7,
            ),
        )
    )

    doc.build(story)

    return archivo.read_bytes()


def renderizar_ambiente_y_control():
    """
    Se mantiene separado para evitar que reproducir la voz
    reinicie los datos del formulario.
    """
    if st.session_state.get("ritual_iniciado", False):
        iniciar_ambiente()


# ============================================================
# ESTADO DE LA APLICACIÓN
# ============================================================

defaults = {
    "ritual_iniciado": False,
    "expediente": None,
    "sentencia": None,
    "audio_bytes": None,
    "audio_filename": None,
    "acta_bytes": None,
    "acta_filename": None,
    "visita_contada": False,
    "visitas": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CABECERA
# ============================================================

st.markdown(
    '<div class="ritual-title">☠ SENTENCIA DE VOZ DE ULTRATUMBA</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">EL EXPEDIENTE ESPERA TUS RESPUESTAS</div>',
    unsafe_allow_html=True,
)


# ============================================================
# BOTÓN INICIAR RITUAL
# ============================================================

if not st.session_state.ritual_iniciado:
    if st.button("🕯️  INICIAR EL RITUAL OMINOSO", use_container_width=True):
        st.session_state.ritual_iniciado = True
        st.rerun()
else:
    renderizar_ambiente_y_control()


# ============================================================
# FORMULARIO
# ============================================================

st.markdown("## Registro del expediente")

with st.form("expediente_form", clear_on_submit=False):

    nombre = st.text_input(
        "Nombre completo",
        placeholder="Escribe el nombre del expediente",
    )

    c1, c2 = st.columns(2)

    with c1:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
        )

    with c2:
        edad = st.number_input(
            "Edad",
            min_value=1,
            max_value=120,
            value=26,
            step=1,
        )

    escenario = st.selectbox(
        "Escenario del fallecimiento",
        [
            "Accidente vehicular",
            "Ahogamiento",
            "Incendio",
            "Caída",
            "Desaparición",
            "Causa desconocida",
        ],
    )

    entorno = st.selectbox(
        "¿Dónde ocurrió?",
        [
            "Una carretera de circulación rápida",
            "Una casa abandonada",
            "Un bosque",
            "Una zona cercana al mar",
            "Una zona montañosa",
            "Un edificio antiguo",
            "Un lugar desconocido",
            "Un camino aislado",
        ],
    )

    hora = st.time_input(
        "Hora aproximada del incidente",
        value=datetime.strptime("03:17", "%H:%M").time(),
    )

    st.markdown("### Preguntas complementarias")

    miedo = st.selectbox(
        "¿A qué le tienes más miedo?",
        [
            "La oscuridad",
            "El mar",
            "Un volcán",
            "Terremotos",
            "Alturas",
            "La muerte",
            "Estar solo/a",
            "Lo desconocido",
            "Animales",
            "Espacios cerrados",
            "Otro",
        ],
    )

    if miedo == "Otro":
        miedo_otro = st.text_input("Especifica tu miedo")
        miedo_final = miedo_otro.strip() or "Un miedo no especificado"
    else:
        miedo_final = miedo

    ultimo_estado = st.selectbox(
        "¿Cómo crees que estarías justo antes de morir?",
        [
            "Tranquilo/a",
            "Inquieto/a",
            "Muy asustado/a",
            "Confundido/a",
            "Enojado/a",
            "Intentando escapar",
            "No lo sé",
        ],
    )

    objeto = st.selectbox(
        "Si encontraras un objeto antiguo, ¿qué harías?",
        [
            "Lo ignoraría",
            "Lo recogería",
            "Lo investigaría",
            "Se lo mostraría a alguien",
            "Me lo llevaría a casa",
        ],
    )

    lugar_muerte = st.selectbox(
        "¿Dónde preferirías NO morir?",
        [
            "En el mar",
            "En un bosque",
            "En una carretera",
            "En un hospital",
            "En una casa abandonada",
            "En un edificio alto",
            "En un lugar desconocido",
        ],
    )

    sonido = st.selectbox(
        "Si escuchas una voz llamándote desde otra habitación, ¿qué harías?",
        [
            "Iría a investigar",
            "Preguntaría quién es",
            "No iría",
            "Saldría del lugar",
            "Esperaría en silencio",
        ],
    )

    detalle = st.text_area(
        "¿Hay algo más que quieras dejar registrado?",
        placeholder="Escribe cualquier detalle...",
        height=110,
    )

    generar = st.form_submit_button(
        "☠️  CERRAR EL EXPEDIENTE Y REVELAR LA SENTENCIA",
        use_container_width=True,
    )


# ============================================================
# PROCESAMIENTO
# ============================================================

if generar:

    if not nombre.strip():
        st.error("Es necesario introducir un nombre para crear el expediente.")
        st.stop()

    datos = {
        "nombre": nombre.strip(),
        "sexo": sexo,
        "edad": int(edad),
        "escenario": escenario,
        "entorno": entorno,
        "hora": hora.strftime("%H:%M"),
        "miedo": miedo_final,
        "ultimo_estado": ultimo_estado,
        "objeto": objeto,
        "lugar_muerte": lugar_muerte,
        "sonido": sonido,
        "detalle": detalle.strip(),
    }

    # --------------------------------------------------------
    # REVELACIÓN CON ESTADO VISIBLE
    # --------------------------------------------------------
    # El usuario ve inmediatamente que el botón sí funcionó.
    # El proceso permanece visible mientras se genera el audio
    # y el acta.
    with st.status("☠️ REVELANDO EL EXPEDIENTE...", expanded=True) as estado:

        st.write("🕯️ Abriendo el registro de ultratumba...")
        expediente = generar_expediente(datos)

        st.write("📜 Inscribiendo los datos en la lápida...")
        sentencia = generar_sentencia(datos, expediente)

        st.write("🎙️ La voz de ultratumba está tomando forma...")
        audio_path = generar_audio_sentencia(sentencia)

        st.write("⚖️ Sellando el acta de defunción...")
        acta_bytes = crear_acta_pdf(datos, expediente)

        st.write("🩸 Preparando la revelación final...")

        # Guardar TODO en session_state.
        # Así los botones posteriores NO vuelven a ejecutar el formulario.
        st.session_state.expediente = expediente
        st.session_state.sentencia = sentencia
        st.session_state.acta_bytes = acta_bytes

        nombre_archivo = limpiar_nombre(datos["nombre"])

        st.session_state.acta_filename = f"Acta_de_defuncion_{nombre_archivo}.pdf"

        if audio_path:
            st.session_state.audio_bytes = audio_path.read_bytes()
            st.session_state.audio_filename = f"Sentencia_{nombre_archivo}.mp3"
        else:
            st.session_state.audio_bytes = None
            st.session_state.audio_filename = None

        estado.update(
            label="☠️ EXPEDIENTE REVELADO",
            state="complete",
            expanded=False,
        )

    st.rerun()


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

if st.session_state.expediente:

    expediente = st.session_state.expediente

    # Recuperamos el nombre desde la sentencia/formulario de forma segura.
    # Se conserva en session_state mediante una extracción simple.
    # Si quieres persistirlo entre sesiones, habría que usar almacenamiento externo.

    st.markdown("---")

    st.markdown(
        f"""
        <div class="expediente">
        <b>EXPEDIENTE:</b> DEF-{expediente['indice']:02d}{random.randint(100,999)}-{date.today().year}<br>
        <b>ÍNDICE NARRATIVO:</b> {expediente['indice']} / 100<br>
        <b>FECHA DEL REGISTRO:</b> {date.today().strftime("%d/%m/%Y")}<br>
        <b>ESTADO:</b> REGISTRO CERRADO
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🕯️ Registro de Voz de Ultratumba")

    st.markdown(
        f"""
        <div class="sentencia-box">
        {html.escape(st.session_state.sentencia)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    st.markdown("### 🎙️ Voz del expediente")

    if st.session_state.audio_bytes:

        # IMPORTANTE:
        # Este es EXACTAMENTE el mismo archivo que se descarga.
        st.audio(
            st.session_state.audio_bytes,
            format="audio/mp3",
        )

        st.download_button(
            "⬇️ DESCARGAR AUDIO DE LA VOZ",
            data=st.session_state.audio_bytes,
            file_name=st.session_state.audio_filename,
            mime="audio/mpeg",
            use_container_width=True,
        )

    else:
        st.write("La generación de voz no está disponible en este entorno.")

    # --------------------------------------------------------
    # ACTA
    # --------------------------------------------------------

    st.markdown("### 📜 Acta de defunción")

    if st.session_state.acta_bytes:
        st.download_button(
            "⚖️ DESCARGAR ACTA DE DEFUNCIÓN",
            data=st.session_state.acta_bytes,
            file_name=st.session_state.acta_filename,
            mime="application/pdf",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="final-text">
        👁<br>
        EL EXPEDIENTE HA SIDO CERRADO.<br><br>
        Algunas puertas se abren una sola vez.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# BOTÓN LIMPIAR
# ============================================================

st.markdown("---")

if st.button("🧹 LIMPIAR CAMPOS Y COMENZAR OTRO EXPEDIENTE", use_container_width=True):

    # Este botón SÍ reinicia los datos.
    st.session_state.expediente = None
    st.session_state.sentencia = None
    st.session_state.audio_bytes = None
    st.session_state.audio_filename = None
    st.session_state.acta_bytes = None
    st.session_state.acta_filename = None
    st.rerun()


# ============================================================
# PIE DE PÁGINA
# ============================================================

mostrar_hud_inferior()

st.markdown(
    '<div class="footer-signature">CREATED BY ALEX A. // EVIL_PHOTO / ULTRATUMBA</div>',
    unsafe_allow_html=True,
)
