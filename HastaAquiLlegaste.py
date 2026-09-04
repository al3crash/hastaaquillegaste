import streamlit as st
import random
import io
import base64
import html
import json
import hashlib
import wave
import math
import os
import tempfile
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="HASTA AQUÍ LLEGASTE — El Oráculo Negro",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ESTADO PERSISTENTE
# ============================================================
if "ritual_iniciado" not in st.session_state:
    st.session_state.ritual_iniciado = False
if "resultado_generado" not in st.session_state:
    st.session_state.resultado_generado = False
if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "audio_generado" not in st.session_state:
    st.session_state.audio_generado = None
if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = None
if "folio" not in st.session_state:
    st.session_state.folio = None


def limpiar_todo():
    widget_keys = [
        "campo_nombre", "campo_sexo", "campo_fecha", "campo_estado", "campo_dependientes",
        "campo_ocupacion", "campo_piso", "campo_transporte", "campo_tiempo",
        "campo_horario", "campo_entorno", "campo_sismos", "campo_clima",
        "campo_actividad", "campo_extremos", "campo_sueno", "campo_fatiga",
        "campo_tabaco", "campo_alcohol", "campo_sustancias", "campo_vivienda",
        "campo_escaleras", "campo_agua", "campo_maquinaria", "campo_cansado",
        "campo_objetos", "campo_visibilidad", "campo_atencion", "campo_lugar",
        "campo_creencias", "campo_terror", "campo_reliquias", "campo_temor", "campo_segundo_temor"
    ]
    for key in widget_keys:
        st.session_state.pop(key, None)
    st.session_state.ritual_iniciado = False
    st.session_state.resultado_generado = False
    st.session_state.resultado = None
    st.session_state.audio_generado = None
    st.session_state.pdf_generado = None
    st.session_state.folio = None


# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 50% 42%, #17051f 0%, #07020a 44%, #010102 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stToolbar"] { visibility: hidden; }
.block-container { max-width: 780px; padding-top: 1.5rem; padding-bottom: 4rem; }

h1 {
    color: #00ff66 !important;
    text-align: center;
    font-family: Georgia, serif;
    font-weight: bold;
    letter-spacing: 4px;
    text-shadow: 0 0 8px #00ff66, 0 0 22px #1b4d3e, 0 0 45px #3d0066;
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
.stTextInput input, .stNumberInput input, .stSelectbox input {
    background-color: #090810 !important;
    color: #00ff66 !important;
}
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    background-color: #1a0033;
    color: #00ff66 !important;
    font-weight: bold;
    font-family: Georgia, serif;
    border: 2px solid #00ff66;
    padding: 14px;
    font-size: 15px;
    letter-spacing: 2px;
    transition: all .3s ease;
    width: 100%;
    min-height: 52px;
}
.stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
    background-color: #00ff66;
    color: #020204 !important;
    box-shadow: 0 0 30px #00ff66;
}

.contenedor-centrado { display:flex; justify-content:center; width:100%; padding:35px 0; }

.lapida-canvas {
    background: radial-gradient(circle at 50% 20%, #35343a 0%, #18171c 45%, #0c0b0f 100%);
    border: 5px double #00ff66;
    border-radius: 180px 180px 25px 25px;
    padding: 55px 28px 40px 28px;
    color: #c1c1cb;
    text-align:center;
    font-family:Georgia,serif;
    box-shadow:0 20px 50px rgba(0,0,0,.95),0 0 35px rgba(0,255,102,.10);
    width:min(470px,90vw);
    margin:20px auto;
    border-bottom:20px solid #080709;
    box-sizing:border-box;
    animation:aparecerLapida 1.4s ease;
}
@keyframes aparecerLapida {
    from { opacity:0; transform:translateY(25px) scale(.96); filter:brightness(0); }
    to { opacity:1; transform:translateY(0) scale(1); filter:brightness(1); }
}
.lapida-rip { font-size:clamp(30px,8vw,40px); font-weight:bold; color:#020204; letter-spacing:6px; margin-bottom:8px; text-shadow:0 1px 0 #666; }
.lapida-nombre { font-size:clamp(18px,5vw,25px); font-weight:bold; color:#fff; text-transform:uppercase; letter-spacing:2px; overflow-wrap:anywhere; }
.lapida-fechas { font-size:13px; color:#00ff66; font-style:italic; margin-bottom:22px; border-bottom:1px double #3d0066; padding-bottom:12px; }
.lapida-causa { font-size:13px; color:#e2e2e9; line-height:1.6; text-align:justify; margin-bottom:25px; background:rgba(5,2,10,.72); padding:14px; border-top:1px solid #3d0066; border-bottom:1px solid #3d0066; }
.lapida-dedicatoria { font-size:12px; color:#777785; font-style:italic; line-height:1.4; }

.oraculo-box { text-align:center; background:radial-gradient(circle at 50% 0%,#21102e 0%,#110b1a 65%); padding:18px; border:1px solid #9d4edd; border-radius:8px; width:min(560px,94vw); margin:0 auto 20px; box-sizing:border-box; box-shadow:0 0 25px rgba(123,44,191,.15); }
.oraculo-status { color:#00ff66 !important; font-family:monospace; font-size:12px; margin-bottom:12px; }
.nota-voz { color:#777785 !important; font-family:monospace; font-size:10px; margin-top:10px; }
.resultado-profundo { background:rgba(4,2,7,.82); border:1px solid #3d0066; border-radius:8px; padding:18px; margin:18px auto; color:#c9c9d4; font-family:"Courier New",monospace; font-size:12px; line-height:1.7; box-shadow:inset 0 0 25px rgba(61,0,102,.12); }
.lectura-final { color:#00ff66 !important; text-align:center; font-family:Georgia,serif; font-size:17px; letter-spacing:1px; line-height:1.7; padding:18px; }

@media (max-width:600px) {
    .block-container { padding-left:.7rem; padding-right:.7rem; padding-top:1.2rem; }
    h1 { font-size:1.7rem !important; letter-spacing:2px; }
    .stButton > button,.stFormSubmitButton > button,.stDownloadButton > button { font-size:13px; }
    .lapida-canvas { padding-left:18px; padding-right:18px; }
}
</style>
""", unsafe_allow_html=True)


def elegir(lista, rng):
    return lista[rng.randrange(len(lista))]


def generar_semilla(*valores):
    texto = "|".join(str(v) for v in valores)
    return int(hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16], 16)


def calcular_edad_en_fecha(fecha_nacimiento, fecha_muerte):
    """Calcula la edad exacta que tenía la persona en la fecha de fallecimiento."""
    nacimiento = fecha_nacimiento
    muerte = fecha_muerte.date()

    edad = muerte.year - nacimiento.year

    if (muerte.month, muerte.day) < (nacimiento.month, nacimiento.day):
        edad -= 1

    return max(0, edad)


def dibujar_codigo_barras(canvas, x, y, semilla):
    canvas.saveState()
    rng = random.Random(semilla)
    ancho_total = 0
    for _ in range(42):
        ancho = rng.choice([1, 1.5, 2, 3])
        espacio = rng.choice([1, 1.5, 2])
        canvas.setFillColor(colors.black)
        canvas.rect(x + ancho_total, y, ancho, 40, fill=1, stroke=0)
        ancho_total += ancho + espacio
    canvas.restoreState()


# ============================================================
# VOZ MASCULINA GRAVE PARA STREAMLIT CLOUD
# edge-tts + FFmpeg: no depende de voces instaladas en Windows/Linux
# ============================================================
def generar_voz_ultratumba(texto, semilla):
    """Genera una voz masculina en español compatible con Streamlit Cloud.

    Usa Microsoft Edge TTS para obtener una voz masculina estable y FFmpeg
    para bajarla de tono y añadir reverberación suave.
    """
    try:
        import asyncio
        import subprocess
        import shutil
        import edge_tts
    except Exception:
        return None

    if shutil.which("ffmpeg") is None:
        return None

    tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_mp3.close()
    tmp_wav.close()

    mp3_path = tmp_mp3.name
    wav_path = tmp_wav.name

    async def sintetizar():
        # Voz masculina mexicana. Se genera en el servidor, no en el equipo
        # del usuario, por lo que funciona igual en Streamlit Cloud.
        comunicador = edge_tts.Communicate(
            texto,
            "es-MX-JorgeNeural",
            rate="-18%",
            volume="-4%",
            pitch="-8Hz"
        )
        await comunicador.save(mp3_path)

    try:
        asyncio.run(sintetizar())

        # Bajamos el tono manteniendo aproximadamente la misma duración y
        # añadimos únicamente una reverberación corta y discreta.
        filtro = (
            "asetrate=44100*0.82,"
            "aresample=44100,"
            "atempo=1.219512,"
            "lowpass=f=520,"
            "aecho=0.80:0.72:50|100|160|240:0.18|0.13|0.09|0.06,"
            "loudnorm=I=-16:TP=-1.5:LRA=7"
        )

        comando = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", mp3_path,
            "-af", filtro,
            "-ac", "1",
            "-ar", "44100",
            "-c:a", "pcm_s16le",
            wav_path
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        if resultado.returncode != 0:
            return None

        with open(wav_path, "rb") as f:
            return f.read()

    except Exception:
        return None
    finally:
        for ruta in (mp3_path, wav_path):
            try:
                os.remove(ruta)
            except Exception:
                pass


# ============================================================
# AUDIO AMBIENTAL PERSISTENTE EN EL DOCUMENTO PADRE
# ============================================================
def instalar_ambiente():
    try:
        with open("hell.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return

    st.components.v1.html(f"""
    <script>
    (() => {{
        const SRC = "data:audio/mpeg;base64,{b64}";
        const PARENT = window.parent.document;
        let audio = PARENT.getElementById("oraculo-ambiente-persistente");

        if (!audio) {{
            audio = PARENT.createElement("audio");
            audio.id = "oraculo-ambiente-persistente";
            audio.src = SRC;
            audio.loop = true;
            audio.preload = "auto";
            audio.volume = 0.42;
            audio.style.display = "none";
            PARENT.body.appendChild(audio);
        }} else if (!audio.src.startsWith("data:audio")) {{
            audio.src = SRC;
        }}

        window.__oraculoAudio = audio;

        function iniciar() {{
            audio.loop = true;
            audio.volume = 0.42;
            const p = audio.play();
            if (p && p.catch) p.catch(() => {{}});
        }}

        if (!window.__oraculoClickHook) {{
            window.__oraculoClickHook = true;
            PARENT.addEventListener("click", (ev) => {{
                const el = ev.target && ev.target.closest
                    ? ev.target.closest("button") : null;
                if (!el) return;
                const txt = (el.innerText || "").toUpperCase();
                if (txt.includes("INICIAR EL RITUAL")) iniciar();
            }}, true);
        }}

        const flag = PARENT.documentElement.dataset.oraculoIniciado === "1";
        if (flag) iniciar();
    }})();
    </script>
    """, height=0)


# ============================================================
# ENCABEZADO + AMBIENTE
# ============================================================
st.markdown("<h1>⛧ HASTA AQUÍ LLEGASTE ⛧</h1>", unsafe_allow_html=True)
instalar_ambiente()


# ============================================================
# PANTALLA INICIAL
# ============================================================
if not st.session_state.ritual_iniciado:
    st.markdown("<p style='text-align:center;color:#8a2be2;font-size:16px;font-weight:bold;'>EL ALTAR ESTÁ APAGADO</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#666;'>El Oráculo aguarda. Cuando cruces el umbral, no cierres los ojos.</p>", unsafe_allow_html=True)
    st.markdown('<div class="contenedor-centrado">', unsafe_allow_html=True)
    if st.button("👁️ INICIAR EL RITUAL OMINOSO", use_container_width=False):
        st.session_state.ritual_iniciado = True
        st.session_state.resultado_generado = False
        st.session_state.resultado = None
        st.components.v1.html("""<script>try { window.parent.document.documentElement.dataset.oraculoIniciado='1'; const a=window.parent.document.getElementById('oraculo-ambiente-persistente'); if(a){a.loop=true;a.volume=.42;const p=a.play();if(p&&p.catch)p.catch(()=>{});} } catch(e) {}</script>""", height=0)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

st.components.v1.html("""<script>try { window.parent.document.documentElement.dataset.oraculoIniciado='1'; const a=window.parent.document.getElementById('oraculo-ambiente-persistente'); if(a){a.loop=true; if(a.paused){const p=a.play();if(p&&p.catch)p.catch(()=>{});}} } catch(e) {}</script>""", height=0)

st.markdown("<p style='text-align:center;color:#4e4e6a !important;font-style:italic;'>El velo se ha roto. Algo ha escuchado tu nombre.</p>", unsafe_allow_html=True)
st.write("---")


# ============================================================
# CUESTIONARIO
# ============================================================
with st.form("ritual_mortal_completo"):
    st.markdown("### 👁️ Bloque I: Datos de Amarra Corporal")
    nombre = st.text_input("Tu nombre completo y apellidos verdaderos:", max_chars=120, key="campo_nombre")
    sexo = st.radio("Sexo:", ["Masculino", "Femenino"], horizontal=True, key="campo_sexo")
    fecha_nacimiento = st.date_input("Fecha de nacimiento:", min_value=datetime(1910,1,1), max_value=datetime.today(), value=datetime(2000,1,1), key="campo_fecha")
    estado_civil = st.radio("Estado civil:", ["Soltero/a","Casado/a","Divorciado/a","Viudo/a / Separado/a"], key="campo_estado")
    personas_dependientes = st.selectbox("¿Cuántas personas dependen directamente de ti?", ["Ninguna","1","2","3","4 o más"], key="campo_dependientes")

    st.write("---")
    st.markdown("### 🏢 Bloque II: Exposición Física y Tránsito")
    ocupacion = st.selectbox("¿A qué dedicas tu energía durante el día?", ["Construcción / Trabajo Operativo / Alturas","Conductor / Repartidor / Tránsito continuo","Oficina / Desarrollo / Trabajo Digital","Comercio / Servicios / Multitudes","Estudiante / Trabajo principalmente en casa","Trabajo nocturno / Turnos variables"], key="campo_ocupacion")
    piso = st.slider("¿En qué nivel o piso permaneces más tiempo?", 1, 60, 1, key="campo_piso")
    transporte_principal = st.selectbox("¿En qué te desplazas regularmente?", ["Automóvil","Motocicleta / Bicicleta","Metro / Tren","Metrobús / Autobús","Camión urbano / Microbús / Combi","Cablebús / Teleférico","Avión","Principalmente a pie"], key="campo_transporte")
    tiempo_desplazamiento = st.selectbox("¿Cuánto tiempo pasas desplazándote al día?", ["Menos de 30 minutos","30 minutos a 1 hora","1 a 2 horas","2 a 4 horas","Más de 4 horas"], key="campo_tiempo")
    horario_mayor_riesgo = st.selectbox("¿En qué horario realizas la mayor parte de tus trayectos?", ["Mañana","Mediodía","Tarde","Noche","Madrugada"], key="campo_horario")
    entorno_urbano = st.radio("¿Qué tan hostil es el entorno habitual de tus trayectos?", ["Bajo","Moderado","Alto","Crítico"], key="campo_entorno")
    sismos_zona = st.radio("¿La zona donde vives o trabajas presenta actividad sísmica?", ["No","Sí, ocasional","Sí, frecuente"], key="campo_sismos")
    clima_exposicion = st.selectbox("¿A qué condiciones ambientales estás más expuesto?", ["Clima estable","Lluvia frecuente","Calor intenso","Frío intenso","Tormentas eléctricas","Cambios extremos"], key="campo_clima")

    st.write("---")
    st.markdown("### 🕯️ Bloque III: Hábitos y Umbral del Riesgo")
    actividad_fisica = st.selectbox("¿Cuál describe mejor tu actividad física?", ["Frecuente","Moderada","Poca","Casi ninguna"], key="campo_actividad")
    deportes_extremos = st.radio("¿Realizas actividades de alta adrenalina o riesgo físico?", ["Nunca","Pocas veces","Frecuentemente","Constantemente"], key="campo_extremos")
    sueño = st.selectbox("¿Cuántas horas duermes normalmente?", ["Menos de 4","4 a 5","5 a 6","6 a 7","7 a 8","Más de 8"], key="campo_sueno")
    fatiga = st.select_slider("Nivel habitual de fatiga:", options=["Mínimo","Estrés común","Alto","Agotamiento extremo"], key="campo_fatiga")
    tabaco = st.radio("¿Consumes tabaco o vapores?", ["No","Ocasionalmente","Diariamente"], key="campo_tabaco")
    alcohol = st.radio("Consumo de alcohol:", ["Nulo","Moderado","Frecuente"], key="campo_alcohol")
    sustancias = st.radio("¿Consumes alguna sustancia ilegal?", ["No","Ocasional","Regular"], key="campo_sustancias")

    st.write("---")
    st.markdown("### 🔮 Bloque IV: El Entorno")
    vivienda = st.selectbox("¿Dónde pasas la mayor parte de tus noches?", ["Casa independiente","Departamento","Casa compartida","Lugar aislado","Hotel / alojamiento temporal","Otro"], key="campo_vivienda")
    escaleras = st.radio("¿Tu rutina incluye escaleras, azoteas o desniveles?", ["Casi nunca","A veces","Frecuentemente"], key="campo_escaleras")
    agua = st.radio("¿Pasas tiempo cerca de cuerpos de agua?", ["No","A veces","Frecuentemente"], key="campo_agua")
    maquinaria = st.radio("¿Trabajas cerca de maquinaria, herramientas o instalaciones eléctricas?", ["No","A veces","Frecuentemente"], key="campo_maquinaria")
    conducir_cansado = st.radio("¿Has conducido estando muy cansado/a?", ["Nunca","Alguna vez","Frecuentemente"], key="campo_cansado")
    objetos_riesgo = st.radio("¿Tienes en casa objetos o instalaciones potencialmente peligrosos?", ["No","Algunos","Varios"], key="campo_objetos")
    visibilidad = st.selectbox("¿Cómo suele ser la visibilidad en tus trayectos?", ["Buena","Variable","Mala","Muy mala"], key="campo_visibilidad")
    atencion = st.select_slider("¿Qué tan atento sueles estar cuando estás bajo presión?", options=["Muy atento","Atento","Distraído","Agotado"], key="campo_atencion")
    lugar_frecuente = st.selectbox("¿Cuál de estos lugares forma parte de tu rutina?", ["Carretera","Edificio alto","Obra","Taller","Oficina","Centro comercial","Estación de transporte","Casa"], key="campo_lugar")

    st.write("---")
    st.markdown("### 📿 Bloque V: Inclinaciones Ocultas")
    creencias = st.selectbox("¿Qué lugar ocupa lo sobrenatural en tu vida?", ["Ninguno","Curiosidad","Creo en energías / fenómenos","Creo firmemente en lo sobrenatural"], key="campo_creencias")
    aficion_terror = st.radio("¿Consumes historias de ultratumba, casas embrujadas o terror psicológico?", ["Me aterra","Consumo ocasional","Me fascina"], key="campo_terror")
    reliquias = st.radio("¿Posees algún objeto antiguo, heredado o extraño?", ["No","Sí, uno","Sí, varios"], key="campo_reliquias")
    lugar_temido = st.selectbox(
        "¿Qué escenario te produce mayor incomodidad?",
        [
            "Ninguno en particular", "El mar / agua profunda", "Un volcán",
            "Un terremoto", "Una carretera vacía", "Una caída desde altura",
            "Un incendio", "Una tormenta eléctrica", "Un edificio abandonado",
            "Un ascensor / espacio cerrado", "Un bosque de noche", "La oscuridad total",
            "Estar completamente solo", "Una multitud", "Un accidente aéreo",
            "Un accidente automovilístico", "Animales agresivos", "No poder pedir ayuda"
        ],
        key="campo_temor"
    )
    segundo_temor = st.selectbox(
        "¿Y cuál de estos peligros te inquieta en segundo lugar?",
        [
            "Ninguno", "Agua profunda", "Fuego", "Alturas", "Terremotos",
            "Volcanes", "Tormentas", "Accidentes", "Espacios cerrados",
            "Soledad", "Oscuridad", "Perder el control", "Quedar atrapado"
        ],
        key="campo_segundo_temor"
    )

    enviar = st.form_submit_button("REVELAR SENTENCIA DEL ORÁCULO NEGRO 👁️", use_container_width=True)


st.button("🕯️ LIMPIAR CAMPOS Y CERRAR EL EXPEDIENTE", on_click=limpiar_todo, use_container_width=True)


# ============================================================
# GENERAR RESULTADO Y GUARDARLO EN SESSION_STATE
# ============================================================
if enviar:
    if not nombre.strip():
        st.error("El Oráculo necesita un nombre para abrir el expediente.")
    else:
        nombre_str = nombre.strip().upper()
        semilla = generar_semilla(
            nombre_str, sexo, fecha_nacimiento, estado_civil, personas_dependientes,
            ocupacion, piso, transporte_principal, tiempo_desplazamiento,
            horario_mayor_riesgo, entorno_urbano, sismos_zona, clima_exposicion,
            actividad_fisica, deportes_extremos, sueño, fatiga, tabaco, alcohol,
            sustancias, vivienda, escaleras, agua, maquinaria, conducir_cansado,
            objetos_riesgo, visibilidad, atencion, lugar_frecuente, creencias,
            aficion_terror, reliquias, lugar_temido, segundo_temor
        )
        rng = random.Random(semilla)

        riesgo = 8
        riesgo += {"Bajo":0,"Moderado":5,"Alto":10,"Crítico":18}[entorno_urbano]
        riesgo += {"Menos de 30 minutos":0,"30 minutos a 1 hora":2,"1 a 2 horas":5,"2 a 4 horas":8,"Más de 4 horas":12}[tiempo_desplazamiento]
        riesgo += {"Mañana":0,"Mediodía":1,"Tarde":3,"Noche":8,"Madrugada":10}[horario_mayor_riesgo]
        riesgo += {"Buena":0,"Variable":3,"Mala":7,"Muy mala":11}[visibilidad]
        riesgo += {"Muy atento":0,"Atento":2,"Distraído":6,"Agotado":10}[atencion]
        if "Motocicleta" in transporte_principal: riesgo += 15
        elif "Automóvil" in transporte_principal: riesgo += 7
        if "Sí, frecuente" in sismos_zona: riesgo += 7
        elif "Sí, ocasional" in sismos_zona: riesgo += 3
        if "Tormentas" in clima_exposicion: riesgo += 5
        if "Constantemente" in deportes_extremos: riesgo += 15
        elif "Frecuentemente" in deportes_extremos: riesgo += 8
        riesgo += {"Menos de 4":10,"4 a 5":6,"5 a 6":3,"6 a 7":1,"7 a 8":0,"Más de 8":0}[sueño]
        riesgo += {"Mínimo":0,"Estrés común":2,"Alto":5,"Agotamiento extremo":9}[fatiga]
        if tabaco == "Diariamente": riesgo += 5
        if alcohol == "Frecuente": riesgo += 4
        if sustancias == "Regular": riesgo += 8
        elif sustancias == "Ocasional": riesgo += 3
        if conducir_cansado == "Frecuentemente": riesgo += 10
        elif conducir_cansado == "Alguna vez": riesgo += 3
        if maquinaria == "Frecuentemente": riesgo += 8
        if escaleras == "Frecuentemente": riesgo += 5
        if agua == "Frecuentemente": riesgo += 4
        riesgo = min(98, max(5, riesgo + rng.randint(-4, 7)))

        nivel = "UMBRAL CRÍTICO" if riesgo >= 75 else "SOMBRA ELEVADA" if riesgo >= 55 else "VIGILIA" if riesgo >= 35 else "BAJO EL VELO"

        edad_actual = max(1, (datetime.now().date() - fecha_nacimiento).days // 365)
        horizonte = rng.randint(8, 46)
        if riesgo >= 75: horizonte = rng.randint(4,24)
        elif riesgo >= 55: horizonte = rng.randint(8,30)
        elif riesgo < 35: horizonte = rng.randint(18,46)

        fecha_muerte = datetime.now() + timedelta(
            days=int(horizonte*365.25) + rng.randint(-180,180)
        )

        # Edad exacta al momento de la muerte.
        edad_muerte = calcular_edad_en_fecha(fecha_nacimiento, fecha_muerte)

        escenarios = []
        if "Motocicleta" in transporte_principal:
            escenarios.append(("COLISIÓN EN TRAYECTO", "La superficie está húmeda y el tráfico avanza en oleadas. Un vehículo cambia de trayectoria demasiado tarde. El margen de reacción desaparece casi por completo."))
        if "Automóvil" in transporte_principal:
            escenarios.append(("ACCIDENTE VEHICULAR", "El trayecto comienza como cualquier otro. Una maniobra inesperada, una distancia demasiado corta y un instante de indecisión convierten una ruta conocida en una escena que nadie esperaba."))
        if "Noche" in horario_mayor_riesgo or "Madrugada" in horario_mayor_riesgo:
            escenarios.append(("EL TRAYECTO SIN TESTIGOS", "La ciudad está casi vacía. La iluminación deja zonas enteras fuera de la vista y un ruido que al principio parece lejano termina formando parte de la última secuencia del expediente."))
        if "Frecuentemente" in maquinaria:
            escenarios.append(("FALLA OPERATIVA", "La rutina había convertido el procedimiento en algo automático. Una pequeña anomalía pasa inadvertida y, cuando alguien comprende que el mecanismo no está respondiendo como debería, ya no queda suficiente margen."))
        if "Frecuentemente" in escaleras:
            escenarios.append(("CAÍDA EN ESTRUCTURA", "Un desnivel conocido deja de serlo durante un segundo. La superficie, la postura y el punto de apoyo se combinan de una manera que transforma una acción cotidiana en una emergencia."))
        if "Frecuentemente" in agua:
            escenarios.append(("EL AGUA", "La superficie parece estable hasta que una corriente cambia la posición del cuerpo. La distancia hacia un punto seguro resulta mayor de lo que parecía desde la orilla."))
        if "Sí, frecuente" in sismos_zona:
            escenarios.append(("EL MOVIMIENTO", "Primero aparece una vibración tenue. Después, los objetos comienzan a responder y el espacio conocido pierde durante unos instantes sus referencias habituales."))
        if "Tormentas" in clima_exposicion:
            escenarios.append(("TORMENTA ELÉCTRICA", "La visibilidad cae rápidamente. La lluvia golpea con tanta fuerza que oculta sonidos pequeños y el entorno se vuelve difícil de leer."))
        if "Constantemente" in deportes_extremos:
            escenarios.append(("EL LÍMITE", "La experiencia había hecho que muchos riesgos parecieran controlables. Esta vez una falla mínima aparece justo cuando ya no existe suficiente espacio para corregirla."))
        if conducir_cansado == "Frecuentemente":
            escenarios.append(("MICROSUEÑO", "Los ojos se cierran durante un instante que el cerebro no registra como sueño. Cuando la atención regresa, el escenario frente a ti ya ha cambiado."))
        if "Crítico" == entorno_urbano and horario_mayor_riesgo in ["Noche","Madrugada"]:
            escenarios.append(("REGRESO SIN TESTIGOS", "El trayecto habitual termina en un tramo aislado. La combinación de poca visibilidad, tránsito irregular y un entorno hostil deja muy poco margen para reaccionar."))
        if atencion in ["Distraído","Agotado"] and sueño in ["Menos de 4","4 a 5"]:
            escenarios.append(("EL SEGUNDO PERDIDO", "El cuerpo llevaba horas pidiendo descanso. El error no aparece como una gran decisión equivocada, sino como una fracción de segundo en la que la atención abandona el entorno."))
        if lugar_frecuente == "Edificio alto" or piso >= 20:
            escenarios.append(("ALTURA", "El expediente señala una rutina desarrollada a varios niveles del suelo. Un punto de apoyo inestable convierte un movimiento ordinario en una situación irreversible."))

        miedo_escenarios = {
            "El mar / agua profunda": ("LA PROFUNDIDAD", "La superficie del agua parecía tranquila. Un cambio repentino en la corriente separó el cuerpo de la zona segura y la distancia hacia la orilla resultó engañosamente grande."),
            "Un volcán": ("TIERRA EN LLAMAS", "La alerta había llegado, pero el entorno seguía pareciendo inmóvil. Una nube de ceniza redujo la visibilidad y convirtió una ruta conocida en un laberinto oscuro."),
            "Un terremoto": ("EL SUELO CEDE", "La primera vibración fue casi imperceptible. Después, el edificio comenzó a responder con violencia y varios objetos perdieron sus puntos de apoyo al mismo tiempo."),
            "Una carretera vacía": ("LA CARRETERA", "El tramo parecía interminable y apenas había otros vehículos. Un instante de mala visibilidad y una maniobra inesperada cambiaron el trayecto para siempre."),
            "Una caída desde altura": ("EL BORDE", "Un punto de apoyo que parecía firme dejó de estarlo. El cuerpo perdió el equilibrio antes de que hubiera tiempo suficiente para recuperar la posición."),
            "Un incendio": ("EL HUMO", "El fuego no fue lo primero que se volvió peligroso. Fue el humo, que redujo la visibilidad y desorientó la salida que segundos antes parecía evidente."),
            "Una tormenta eléctrica": ("LA TORMENTA", "El cielo se cerró rápidamente. La lluvia, el viento y los destellos hicieron difícil distinguir qué sonidos pertenecían al entorno y cuáles anunciaban un peligro más cercano."),
            "Un edificio abandonado": ("EL EDIFICIO VACÍO", "El lugar estaba inmóvil hasta que una estructura cedió en algún punto del interior. El sonido parecía lejano, pero la ruta de salida dejó de ser segura."),
            "Un ascensor / espacio cerrado": ("SIN SALIDA", "El espacio se detuvo entre niveles. La iluminación falló y, durante los siguientes minutos, la sensación de encierro hizo que cada segundo pareciera mucho más largo."),
            "Un bosque de noche": ("EL BOSQUE", "La oscuridad borró las referencias habituales. Un ruido detrás de los árboles provocó un cambio de dirección y esa decisión terminó alejando del camino seguro."),
            "La oscuridad total": ("A CIEGAS", "Durante unos instantes no hubo ninguna referencia visual. El cuerpo avanzó confiando en la memoria del lugar, pero un obstáculo apareció donde no debía estar."),
            "Estar completamente solo": ("SIN TESTIGOS", "El incidente ocurrió lejos de otras personas. Cuando finalmente alguien advirtió que algo había sucedido, el tiempo transcurrido ya había sido decisivo."),
            "Una multitud": ("LA MULTITUD", "Un movimiento colectivo comenzó sin que fuera evidente su origen. En pocos segundos, el espacio personal desapareció y una salida aparentemente cercana quedó bloqueada."),
            "Un accidente aéreo": ("EL VUELO", "Todo transcurría con normalidad hasta que una señal de emergencia interrumpió el silencio de la cabina. La tripulación actuó de inmediato, pero la secuencia se desarrolló demasiado rápido."),
            "Un accidente automovilístico": ("EL IMPACTO", "Dos trayectorias se cruzaron en el momento equivocado. El primer sonido fue breve y seco, seguido por una sucesión de movimientos imposibles de detener."),
            "Animales agresivos": ("EL ENCUENTRO", "El animal apareció a una distancia demasiado corta para permitir una retirada tranquila. El intento de escapar provocó una reacción inesperada del entorno."),
            "No poder pedir ayuda": ("SIN SEÑAL", "La situación se volvió crítica mientras el dispositivo de comunicación permanecía sin señal. El lugar estaba suficientemente lejos para que la ayuda tardara demasiado en llegar.")
        }
        if lugar_temido in miedo_escenarios:
            escenarios.append(miedo_escenarios[lugar_temido])

        if not escenarios:
            escenarios = [
                ("EL ACCIDENTE IMPREVISTO", "El escenario parece completamente normal. Precisamente por eso nadie identifica el peligro hasta que la cadena de pequeños acontecimientos ya no puede detenerse."),
                ("UNA NOCHE EXTRAÑA", "No existe una señal evidente. Solo una sucesión de detalles pequeños que, vistos después, parecen haber estado apuntando hacia el mismo momento."),
                ("EL DESCUIDO", "Una acción cotidiana se realiza de forma automática. Un error mínimo desencadena una secuencia que nadie había previsto.")
            ]

        titulo_escenario, descripcion_escenario = elegir(escenarios, rng)

        lugares = []
        if "Automóvil" in transporte_principal: lugares.append("una avenida de tránsito rápido")
        if "Motocicleta" in transporte_principal: lugares.append("una vía urbana con pavimento irregular")
        if horario_mayor_riesgo in ["Noche","Madrugada"]: lugares.append("una calle con iluminación intermitente")
        if piso >= 10: lugares.append(f"un edificio situado en el nivel {piso}")
        if vivienda == "Departamento": lugares.append("un edificio residencial")
        if vivienda == "Lugar aislado": lugares.append("una propiedad alejada del tránsito habitual")
        if lugar_frecuente == "Carretera": lugares.append("un tramo de carretera de circulación rápida")
        if lugar_frecuente == "Obra": lugares.append("una zona de trabajo en construcción")
        if lugar_frecuente == "Taller": lugares.append("un taller con maquinaria en funcionamiento")
        if lugar_frecuente == "Estación de transporte": lugares.append("una estación de transporte durante una hora de alta circulación")
        if not lugares: lugares.append("un entorno cotidiano que conocías perfectamente")
        lugar_final = elegir(lugares, rng)

        detalle_psicologico = elegir([
            "Lo inquietante es que durante los días anteriores habías notado pequeños detalles fuera de lugar.",
            "Existe un instante previo en el que todo parece demasiado silencioso.",
            "El último recuerdo claro corresponde a un detalle completamente insignificante.",
            "Quienes reconstruyen la escena descubren que una decisión aparentemente pequeña cambió toda la secuencia.",
            "La parte más perturbadora es que el lugar era completamente familiar.",
            "Horas antes, el expediente registra una rutina exactamente igual a muchas otras. Nadie esperaba que esa fuera la última.",
        ], rng)

        detalles_miedo = {
            "Agua profunda": "El expediente también registra una incomodidad marcada ante la cercanía del agua.",
            "Fuego": "El calor y el olor a humo aparecen entre los detalles que más alteran la reconstrucción.",
            "Alturas": "La altura forma parte de los factores que el expediente considera especialmente sensibles.",
            "Terremotos": "La actividad del suelo aparece como un factor psicológico relevante en la reconstrucción.",
            "Volcanes": "La presencia de actividad volcánica aparece como una de las imágenes más inquietantes del expediente.",
            "Tormentas": "Los cambios bruscos del clima forman parte de los elementos que elevan la tensión de la escena.",
            "Accidentes": "La posibilidad de una cadena repentina de acontecimientos aparece repetidamente en el expediente.",
            "Espacios cerrados": "El encierro aparece como uno de los elementos que más altera la percepción del tiempo.",
            "Soledad": "La ausencia de testigos hace que la reconstrucción resulte especialmente perturbadora.",
            "Oscuridad": "La falta de referencias visuales aparece como un elemento decisivo en la escena.",
            "Perder el control": "La sensación de que los acontecimientos avanzan sin posibilidad de intervenir domina la reconstrucción.",
            "Quedar atrapado": "La imposibilidad de abandonar el lugar aparece como uno de los detalles más inquietantes.",
            "Ninguno": ""
        }
        detalle_miedo = detalles_miedo.get(segundo_temor, "")
        if detalle_miedo:
            detalle_psicologico += " " + detalle_miedo

        pareja_memoria = "esposa" if sexo == "Masculino" else "esposo"
        dedicatoria = (
            f"En memoria de tu {pareja_memoria}, tus amigos y seres queridos, "
            "que conservan tu recuerdo y las pequeñas cosas que dejaste atrás."
        )

        causa_final = f"{descripcion_escenario} El incidente ocurrió en {lugar_final}. {detalle_psicologico}"
        nacimiento_str = fecha_nacimiento.strftime("%d/%m/%Y")
        muerte_str = fecha_muerte.strftime("%d/%m/%Y")
        folio_num = f"DEF-{rng.randint(100000,999999)}-2026"

        texto_a_leer = (
            f"Hasta aquí llegaste, {nombre_str}. El Oráculo ha cerrado tu expediente. "
            f"El escenario registrado es {titulo_escenario}. "
            f"{causa_final} "
            f"Muriste a los {edad_muerte} años. "
            f"{dedicatoria}"
        )

        resultado = dict(
            nombre=nombre_str,
            sexo=sexo,
            nacimiento=nacimiento_str,
            muerte=muerte_str,
            edad_muerte=edad_muerte,
            estado=estado_civil.upper(),
            ocupacion=ocupacion.upper(),
            piso=piso,
            nivel=nivel,
            riesgo=riesgo,
            escenario=titulo_escenario,
            descripcion=descripcion_escenario,
            lugar=lugar_final,
            causa=causa_final,
            detalle=detalle_psicologico,
            dedicatoria=dedicatoria,
            texto=texto_a_leer,
            folio=folio_num,
            edad=edad_actual,
            miedo=lugar_temido,
            segundo_miedo=segundo_temor,
            fecha_registro=datetime.now().strftime("%d/%m/%Y")
        )

        st.session_state.resultado = resultado
        st.session_state.folio = folio_num
        st.session_state.resultado_generado = True
        st.session_state.audio_generado = generar_voz_ultratumba(texto_a_leer, semilla)


# ============================================================
# MOSTRAR RESULTADO DESDE SESSION_STATE
# ============================================================
if st.session_state.resultado_generado and st.session_state.resultado:
    r = st.session_state.resultado

    # ========================================================
    # SCROLL AUTOMÁTICO HACIA LA LÁPIDA
    # ========================================================
    st.markdown(
        '<div id="lapida-anchor" style="height:1px; scroll-margin-top:30px;"></div>',
        unsafe_allow_html=True
    )

    st.components.v1.html("""
    <script>
    (() => {
        function irALapida() {
            try {
                const parentDoc = window.parent.document;
                const objetivo = parentDoc.getElementById("lapida-anchor");

                if (objetivo) {
                    objetivo.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                    return true;
                }
            } catch(e) {}

            return false;
        }

        setTimeout(irALapida, 150);
        setTimeout(irALapida, 500);
        setTimeout(irALapida, 1000);
    })();
    </script>
    """, height=0, scrolling=False)

    # ========================================================
    # LÁPIDA
    # ========================================================
    st.components.v1.html(f"""
    <style>
      html,body{{margin:0;padding:0;background:transparent;}}
      .lapida-canvas{{background:radial-gradient(circle at 50% 20%,#35343a 0%,#18171c 45%,#0c0b0f 100%);border:5px double #00ff66;border-radius:180px 180px 25px 25px;padding:55px 28px 40px;color:#c1c1cb;text-align:center;font-family:Georgia,serif;box-shadow:0 20px 50px rgba(0,0,0,.95),0 0 35px rgba(0,255,102,.10);width:min(470px,90vw);margin:10px auto;border-bottom:20px solid #080709;box-sizing:border-box;animation:entrada 1.2s ease;}}
      @keyframes entrada{{from{{opacity:0;transform:translateY(20px) scale(.96);filter:brightness(0)}}to{{opacity:1;transform:none;filter:brightness(1)}}}}
      .rip{{font-size:clamp(30px,8vw,40px);font-weight:bold;color:#020204;letter-spacing:6px;margin-bottom:8px;text-shadow:0 1px 0 #666;}}
      .nombre{{font-size:clamp(18px,5vw,25px);font-weight:bold;color:white;text-transform:uppercase;letter-spacing:2px;overflow-wrap:anywhere;}}
      .fechas{{font-size:13px;color:#00ff66;font-style:italic;margin-bottom:22px;border-bottom:1px double #3d0066;padding-bottom:12px;line-height:1.7;}}
      .edad-muerte{{color:#9d4edd;font-style:normal;font-weight:bold;font-size:14px;letter-spacing:1px;}}
      .causa{{font-size:13px;color:#e2e2e9;line-height:1.6;text-align:justify;margin-bottom:25px;background:rgba(5,2,10,.72);padding:14px;border-top:1px solid #3d0066;border-bottom:1px solid #3d0066;}}
      .dedicatoria{{font-size:12px;color:#777785;font-style:italic;line-height:1.4;}}
    </style>
    <div class="lapida-canvas">
      <div class="rip">R. I. P.</div>
      <div class="nombre">{html.escape(r['nombre'])}</div>
      <div class="fechas">
        {r['nacimiento']} &nbsp;—&nbsp; {r['muerte']}<br>
        <span class="edad-muerte">MURIÓ A LOS {r['edad_muerte']} AÑOS</span>
      </div>
      <div class="causa"><b>CAUSA DE MI MUERTE:</b><br>{html.escape(r['causa'])}</div>
      <div class="dedicatoria">"{html.escape(r['dedicatoria'])}"</div>
    </div>
    """, height=525, scrolling=False)

    st.markdown(f"""
    <div class="resultado-profundo">
      <b>EXPEDIENTE:</b> {html.escape(r['folio'])}<br>
      <b>ESTADO DEL VELO:</b> {html.escape(r['nivel'])}<br>
      <b>ÍNDICE NARRATIVO:</b> {r['riesgo']} / 100<br>
      <b>ESCENARIO:</b> {html.escape(r['escenario'])}<br>
      <b>ENTORNO:</b> {html.escape(r['lugar'])}<br>
      <b>EDAD ACTUAL:</b> {r['edad']} años<br>
      <b>EDAD AL FALLECER:</b> {r['edad_muerte']} años<br>
      <b>FECHA DEL REGISTRO:</b> {r['fecha_registro']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎙️ Sentencia de Voz de Ultratumba")

    if st.session_state.audio_generado:
        audio_b64 = base64.b64encode(st.session_state.audio_generado).decode("ascii")
        st.components.v1.html(f"""
        <div style="text-align:center;background:#110b1a;padding:18px;border:1px solid #9d4edd;border-radius:8px;font-family:monospace;color:#00ff66;">
          <div style="margin-bottom:12px;">🔊 ORÁCULO DE ULTRATUMBA ACTIVO</div>
          <audio id="sentencia-oraculo" controls preload="metadata" style="width:94%;height:48px;">
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
          </audio>
          <div style="color:#777785;font-size:10px;margin-top:10px;">Voz masculina grave con reverberación suave.</div>
        </div>
        <script>
        (() => {{
          const player=document.getElementById('sentencia-oraculo');
          const parent=window.parent.document;
          const musica=parent.getElementById('oraculo-ambiente-persistente');
          if(!player) return;
          player.addEventListener('play',()=>{{
            if(musica){{ musica.volume=.08; const p=musica.play(); if(p&&p.catch)p.catch(()=>{{}}); }}
          }});
          player.addEventListener('pause',()=>{{ if(musica) musica.volume=.42; }});
          player.addEventListener('ended',()=>{{ if(musica) musica.volume=.42; }});
        }})();
        </script>
        """, height=150, scrolling=False)
    else:
        st.markdown("<div class='oraculo-box'>La voz del expediente no pudo ser generada en el servidor.</div>", unsafe_allow_html=True)

    if st.session_state.audio_generado:
        st.download_button(
            "☠️ DESCARGAR SENTENCIA DE ULTRATUMBA",
            data=st.session_state.audio_generado,
            file_name=f"Sentencia_Ultratumba_{r['nombre'].replace(' ','_')}.wav",
            mime="audio/wav",
            use_container_width=True,
            on_click="ignore",
            key="descargar_voz"
        )

    # ========================================================
    # PDF
    # ========================================================
    if st.session_state.pdf_generado is None:
        buffer=io.BytesIO()

        def marco(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#7b2cbf"))
            canvas.setLineWidth(2)
            canvas.rect(20,20,572,752)
            canvas.setLineWidth(.5)
            canvas.rect(24,24,564,744)
            canvas.setFillColor(colors.HexColor("#111111"))
            canvas.rect(530,710,8,40,fill=1,stroke=0)
            canvas.rect(516,732,36,8,fill=1,stroke=0)
            dibujar_codigo_barras(canvas,40,45,sum(ord(c) for c in r['folio']))
            canvas.restoreState()

        doc=SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=100
        )

        styles=getSampleStyleSheet()
        sg=ParagraphStyle("sg",fontName="Helvetica-Bold",fontSize=14,leading=16,alignment=1,textColor=colors.HexColor("#111111"))
        ss=ParagraphStyle("ss",fontName="Helvetica",fontSize=9,leading=11,alignment=1,textColor=colors.HexColor("#444444"))
        sec=ParagraphStyle("sec",fontName="Helvetica-Bold",fontSize=10,leading=12,textColor=colors.white,backColor=colors.HexColor("#4a154b"),borderPadding=4)
        campo=ParagraphStyle("campo",fontName="Helvetica-Bold",fontSize=9,leading=11,textColor=colors.HexColor("#222222"))
        val=ParagraphStyle("val",fontName="Helvetica",fontSize=9,leading=11,textColor=colors.HexColor("#444444"))
        causa=ParagraphStyle("causa",fontName="Helvetica-BoldOblique",fontSize=9.5,leading=14,textColor=colors.HexColor("#8b0000"))

        story=[
            Paragraph("ESTADOS UNIDOS DEL MÁS ALLÁ",sg),
            Paragraph("REGISTRO CIVIL RESTRINGIDO • ACTA DE DEFUNCIÓN",ss),
            Spacer(1,15)
        ]

        story.append(Table([
            [Paragraph(f"<b>CRIPTA LOCAL:</b> Valle de las Sombras",val),
             Paragraph(f"<b>NÚMERO DE CONTROL:</b> {r['folio']}",val)],
            [Paragraph("<b>LIBRO:</b> Destinos Cerrados",val),
             Paragraph(f"<b>FECHA DE SISTEMA:</b> {r['fecha_registro']}",val)]
        ],colWidths=[250,270],style=[
            ("LINEBELOW",(0,0),(-1,-1),.5,colors.HexColor("#CCC")),
            ("PADDING",(0,0),(-1,-1),4)
        ]))

        story.append(Spacer(1,15))
        story.append(Paragraph("I. DATOS DE LA PERSONA",sec))
        story.append(Spacer(1,6))

        story.append(Table([
            [Paragraph("NOMBRE COMPLETO:",campo),Paragraph(html.escape(r['nombre']),val)],
            [Paragraph("SEXO:",campo),Paragraph(html.escape(r['sexo']),val)],
            [Paragraph("FECHA DE NACIMIENTO:",campo),Paragraph(r['nacimiento'],val)],
            [Paragraph("ESTADO CIVIL:",campo),Paragraph(html.escape(r['estado']),val)],
            [Paragraph("ACTIVIDAD:",campo),Paragraph(html.escape(r['ocupacion']),val)],
            [Paragraph("NIVEL DEL VELO:",campo),Paragraph(html.escape(r['nivel']),val)],
            [Paragraph("EDAD AL FALLECER:",campo),Paragraph(f"{r['edad_muerte']} años",val)]
        ],colWidths=[150,370],style=[
            ("INNERGRID",(0,0),(-1,-1),.25,colors.HexColor("#E0E0E0")),
            ("BOX",(0,0),(-1,-1),.5,colors.HexColor("#AAA")),
            ("PADDING",(0,0),(-1,-1),5)
        ]))

        story.append(Spacer(1,15))
        story.append(Paragraph("II. DATOS DEL FALLECIMIENTO",sec))
        story.append(Spacer(1,6))

        story.append(Table([
            [Paragraph("FECHA DEL DECESO:",campo),Paragraph(r['muerte'],val)],
            [Paragraph("EDAD AL FALLECER:",campo),Paragraph(f"{r['edad_muerte']} años",val)],
            [Paragraph("ESCENARIO:",campo),Paragraph(html.escape(r['escenario']),val)],
            [Paragraph("LUGAR:",campo),Paragraph(html.escape(r['lugar']),val)],
            [Paragraph("CAUSA:",campo),Paragraph(html.escape(r['causa']),causa)]
        ],colWidths=[150,370],style=[
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("INNERGRID",(0,0),(-1,-1),.25,colors.HexColor("#E0E0E0")),
            ("BOX",(0,0),(-1,-1),.5,colors.HexColor("#AAA")),
            ("PADDING",(0,0),(-1,-1),6),
            ("BACKGROUND",(1,4),(1,4),colors.HexColor("#FFF2F2"))
        ]))

        story.append(Spacer(1,15))
        story.append(Paragraph("III. LECTURA DEL EXPEDIENTE",sec))
        story.append(Spacer(1,6))
        story.append(Paragraph(html.escape(r['descripcion']+" "+r['detalle']),val))
        story.append(Spacer(1,12))
        story.append(Paragraph("IV. EPITAFIO",sec))
        story.append(Spacer(1,5))
        story.append(Paragraph(f'<i>"{html.escape(r["dedicatoria"])}"</i>',val))
        story.append(Spacer(1,15))
        story.append(Paragraph("V. CADENA DIGITAL DE AUTENTICACIÓN",sec))
        story.append(Spacer(1,5))
        story.append(Paragraph(
            f"<font size=7 color='#666666'>||{r['folio']}||{r['nombre']}||{r['muerte']}||{sum(ord(c) for c in r['folio'])}#PARCAS_AUTENTICACION||</font>",
            ss
        ))
        story.append(Spacer(1,25))
        story.append(Table([[
            Paragraph("_____________________________<br/>Átropos<br/>Oficial Registrador del Hilo",
                      ParagraphStyle("f1",fontName="Helvetica",fontSize=7.5,alignment=1)),
            Paragraph("_____________________________<br/>La Parca Mayor<br/>Interventor del Destino",
                      ParagraphStyle("f2",fontName="Helvetica",fontSize=7.5,alignment=1))
        ]],colWidths=[250,250],style=[("PADDING",(0,0),(-1,-1),2)]))

        doc.build(story,onFirstPage=marco,onLaterPages=marco)
        st.session_state.pdf_generado=buffer.getvalue()

    st.download_button(
        "⚖️ DESCARGAR ACTA DE DEFUNCIÓN",
        data=st.session_state.pdf_generado,
        file_name=f"Acta_Defuncion_{r['nombre'].replace(' ','_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
        on_click="ignore",
        key="descargar_acta"
    )

    st.markdown(f"""
    <div class="lectura-final">
      👁️<br><br>
      Hasta aquí llegaste, {html.escape(r['nombre'])}.<br>
      El expediente <b>{html.escape(r['folio'])}</b> ha sido cerrado.<br><br>
      <span style="color:#777785;">Algunas puertas se abren una sola vez.</span>
    </div>
    """, unsafe_allow_html=True)
