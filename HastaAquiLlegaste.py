import streamlit as st
import random
import io
import base64
import html
import hashlib
import os
import shutil
import tempfile
import subprocess
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="HASTA AQUÍ LLEGASTE — Voz de Ultratumba",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

PAYPAL_URL = "https://www.paypal.com/ncp/payment/HAALKPRK6DT8G"

# ============================================================
# GEMINI API
# ============================================================
# La aplicación utiliza exclusivamente Google Gemini para generar
# "MI MUERTE MÁS DETALLADA".
#
# La clave se busca en este orden:
#   1) st.secrets["GEMINI_API_KEY"]   <- recomendado para Streamlit Cloud
#   2) variable de entorno GEMINI_API_KEY
#   3) archivo mms.txt mediante una URL RAW de GitHub
#
# RECOMENDADO EN STREAMLIT CLOUD:
# En Settings > Secrets agrega:
# GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"
#
# Si vas a seguir usando mms.txt, coloca ahí SOLO la clave de Gemini
# y configura GEMINI_API_KEY_URL con la URL RAW correspondiente.
GEMINI_API_KEY_URL = "https://github.com/al3crash/hastaaquillegaste/blob/main/mms.txt"

# Modelo estable con nivel gratuito disponible actualmente.
GEMINI_MODEL = "gemini-2.5-flash-lite"


def obtener_api_key():
    """Obtiene la clave de Gemini de forma segura y sin pedirla al usuario."""
    import urllib.request

    # 1. Streamlit Secrets: opción recomendada para Streamlit Cloud.
    try:
        clave = st.secrets.get("GEMINI_API_KEY")
        if clave:
            clave = str(clave).strip().strip('"').strip("'")
            if clave:
                return clave
    except Exception:
        pass

    # 2. Variable de entorno.
    clave = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if clave:
        return clave

    # 3. Compatibilidad con el método anterior basado en mms.txt.
    if not GEMINI_API_KEY_URL or "TU_USUARIO" in GEMINI_API_KEY_URL or "TU_REPOSITORIO" in GEMINI_API_KEY_URL:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY. Configúrala en Streamlit Secrets "
            "como GEMINI_API_KEY. Si utilizas mms.txt, configura también "
            "GEMINI_API_KEY_URL con la URL RAW de tu archivo."
        )

    try:
        request = urllib.request.Request(
            GEMINI_API_KEY_URL,
            headers={"User-Agent": "HastaAquiLlegaste-Gemini/1.0"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            clave = response.read().decode("utf-8", errors="strict").strip()
    except Exception as exc:
        raise RuntimeError(
            "No se pudo leer la clave de Gemini desde mms.txt. "
            f"Verifica la URL RAW y que el archivo exista. Detalle: {exc}"
        ) from exc

    clave = clave.strip().strip('"').strip("'")

    if not clave:
        raise RuntimeError("La fuente de la clave está vacía o no contiene una API key válida.")

    return clave


def generar_muerte_detallada_con_ia(resultado):
    """Genera la reconstrucción detallada exclusivamente con Google Gemini."""
    import urllib.request
    import urllib.error
    import json

    try:
        api_key = obtener_api_key()
    except Exception as exc:
        return None, str(exc)

    try:
        prompt = f"""
Eres el narrador ficticio de un expediente paranormal llamado
"HASTA AQUÍ LLEGASTE". Debes escribir una reconstrucción narrativa
oscura, cinematográfica y perturbadora basada exclusivamente en los
datos proporcionados.

IMPORTANTE:
- Esto es ficción y entretenimiento.
- NO presentes el texto como una predicción real.
- NO afirmes que puedes saber cuándo o cómo morirá realmente una persona.
- No uses gore explícito ni describas mutilaciones.
- No des instrucciones peligrosas.
- No inventes datos médicos reales.
- No cambies la causa principal del expediente.
- Mantén la narración en español.
- Usa segunda persona.
- Hazla bastante más detallada que la sentencia normal.
- Incluye ambiente, momento del día, señales previas, desarrollo del
  incidente, instante decisivo, reacción del entorno y cierre del expediente.
- No menciones que eres una IA.
- No uses encabezados excesivos. Puede ser una narración continua con
  pequeños apartados si ayudan a la lectura.

DATOS DEL EXPEDIENTE:
Nombre: {resultado["nombre"]}
Edad actual: {resultado["edad"]}
Sexo: {resultado["sexo"]}
Ocupación: {resultado["ocupacion"]}
Transporte: {resultado["transporte"]}
Horario: {resultado["horario"]}
Visibilidad: {resultado["visibilidad"]}
Entorno: {resultado["entorno"]}
Clima: {resultado["clima"]}
Sueño: {resultado["sueño"]}
Fatiga: {resultado["fatiga"]}
Atención: {resultado["atencion"]}
Lugar habitual: {resultado["lugar_frecuente"]}
Lugar: {resultado["lugar"]}
Escenario principal: {resultado["escenario"]}
Causa narrativa: {resultado["causa"]}
Miedo principal: {resultado["miedo"]}
Segundo miedo: {resultado["segundo_miedo"]}

Escribe una reconstrucción de aproximadamente 700 a 1000 palabras.
El tono debe parecer un expediente secreto del "Más Allá", oscuro,
serio y cinematográfico, pero claramente ficticio.
"""

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 1800,
                "thinkingConfig": {"thinkingBudget": 0}
            }
        }

        # JSON ASCII: Unicode queda representado como \uXXXX.
        # Así urllib nunca intenta convertir emojis o acentos a Latin-1.
        cuerpo = json.dumps(
            payload,
            ensure_ascii=True,
            separators=(",", ":")
        ).encode("ascii")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent"
        )

        request = urllib.request.Request(
            url,
            data=cuerpo,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": "HastaAquiLlegaste-Gemini/1.0",
            },
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            respuesta_bytes = response.read()

        respuesta_json = json.loads(
            respuesta_bytes.decode("utf-8", errors="replace")
        )

        candidatos = respuesta_json.get("candidates") or []
        if not candidatos:
            bloqueos = respuesta_json.get("promptFeedback")
            detalle = respuesta_json.get("error")
            if detalle:
                return None, f"Gemini devolvió un error: {detalle}"
            if bloqueos:
                return None, f"Gemini no generó la respuesta. Detalle: {bloqueos}"
            return None, "Gemini respondió, pero no devolvió candidatos de texto."

        partes = candidatos[0].get("content", {}).get("parts", [])
        textos = [
            str(parte.get("text", ""))
            for parte in partes
            if parte.get("text")
        ]
        texto = "\n".join(textos).strip()

        if not texto:
            motivo = candidatos[0].get("finishReason", "desconocido")
            return None, (
                "Gemini terminó la generación sin devolver texto. "
                f"Motivo: {motivo}"
            )

        texto = texto.replace("\r\n", "\n").replace("\r", "\n")
        return texto, None

    except urllib.error.HTTPError as exc:
        try:
            detalle = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detalle = str(exc)

        if exc.code == 400:
            return None, (
                "Gemini rechazó la solicitud (HTTP 400).\n"
                "Revisa que la API key sea válida y que el modelo esté disponible "
                f"para tu proyecto.\nDetalle: {detalle[:1600]}"
            )

        if exc.code == 403:
            return None, (
                "Gemini rechazó la API key (HTTP 403).\n"
                "Verifica que la clave pertenezca a un proyecto de Google AI Studio "
                f"con acceso a la Gemini API.\nDetalle: {detalle[:1600]}"
            )

        if exc.code == 404:
            return None, (
                "El modelo de Gemini no está disponible en este endpoint (HTTP 404).\n"
                f"Modelo configurado: {GEMINI_MODEL}\n"
                f"Detalle: {detalle[:1600]}"
            )

        if exc.code == 429:
            return None, (
                "Gemini alcanzó temporalmente el límite de solicitudes del nivel gratuito "
                "(HTTP 429). Espera un momento y vuelve a intentarlo.\n"
                f"Detalle: {detalle[:1600]}"
            )

        return None, (
            f"Gemini rechazó la solicitud (HTTP {exc.code}).\n"
            f"Detalle: {detalle[:1600]}"
        )

    except urllib.error.URLError as exc:
        return None, (
            "No fue posible conectar con la API de Gemini.\n"
            f"{type(exc).__name__}: {exc}"
        )

    except UnicodeError as exc:
        return None, (
            "Se produjo un problema de codificación de texto.\n"
            f"{type(exc).__name__}: {exc}"
        )

    except Exception as exc:
        return None, (
            f"No fue posible consultar Gemini.\n"
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# ENCABEZADO
# ============================================================
st.markdown("<h1>⛧ HASTA AQUÍ LLEGASTE ⛧</h1>", unsafe_allow_html=True)
instalar_ambiente()


# ============================================================
# PANTALLA INICIAL
# ============================================================
if not st.session_state.ritual_iniciado:
    st.markdown(
        "<p style='text-align:center;color:#8a2be2;font-size:16px;font-weight:bold;'>"
        "EL ALTAR ESTÁ APAGADO</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:#666;'>"
        "La presencia de ultratumba aguarda. Cuando cruces el umbral, no cierres los ojos.</p>",
        unsafe_allow_html=True
    )

    st.markdown('<div class="contenedor-centrado">', unsafe_allow_html=True)

    if st.button("👁️ INICIAR EL RITUAL OMINOSO", use_container_width=False):
        st.session_state.ritual_iniciado = True
        st.session_state.resultado_generado = False
        st.session_state.resultado = None
        st.session_state.audio_generado = None
        st.session_state.audio_error = None
        st.session_state.pdf_generado = None
        st.session_state.ia_detalle = None
        st.session_state.ia_error = None

        st.components.v1.html("""
        <script>
        try {
            window.parent.document.documentElement.dataset.oraculoIniciado='1';
            const a=window.parent.document.getElementById(
                'oraculo-ambiente-persistente'
            );
            if(a){
                a.loop=true;
                a.volume=.42;
                const p=a.play();
                if(p&&p.catch)p.catch(()=>{});
            }
        } catch(e) {}
        </script>
        """, height=0)

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


st.components.v1.html("""
<script>
try {
    window.parent.document.documentElement.dataset.oraculoIniciado='1';
    const a=window.parent.document.getElementById(
        'oraculo-ambiente-persistente'
    );
    if(a){
        a.loop=true;
        if(a.paused){
            const p=a.play();
            if(p&&p.catch)p.catch(()=>{});
        }
    }
} catch(e) {}
</script>
""", height=0)

st.markdown(
    "<p style='text-align:center;color:#4e4e6a !important;font-style:italic;'>"
    "El velo se ha roto. Algo ha escuchado tu nombre.</p>",
    unsafe_allow_html=True
)
st.write("---")


# ============================================================
# CONFIGURACIÓN DE IA
# ============================================================
# La API key se obtiene automáticamente desde mms.txt en GitHub.
# No se solicita al usuario desde la interfaz.


# ============================================================
# CUESTIONARIO
# ============================================================
with st.form("ritual_mortal_completo"):
    st.markdown("### 👁️ Bloque I: Datos de Amarra Corporal")

    nombre = st.text_input(
        "Tu nombre completo y apellidos verdaderos:",
        max_chars=120,
        key="campo_nombre"
    )
    sexo = st.radio(
        "Sexo:",
        ["Masculino", "Femenino"],
        horizontal=True,
        key="campo_sexo"
    )
    fecha_nacimiento = st.date_input(
        "Fecha de nacimiento:",
        min_value=datetime(1910, 1, 1),
        max_value=datetime.today(),
        value=datetime(2000, 1, 1),
        key="campo_fecha"
    )
    estado_civil = st.radio(
        "Estado civil:",
        ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a / Separado/a"],
        key="campo_estado"
    )
    personas_dependientes = st.selectbox(
        "¿Cuántas personas dependen directamente de ti?",
        ["Ninguna", "1", "2", "3", "4 o más"],
        key="campo_dependientes"
    )

    st.write("---")
    st.markdown("### 🏢 Bloque II: Exposición Física y Tránsito")

    ocupacion = st.selectbox(
        "¿A qué dedicas tu energía durante el día?",
        [
            "Construcción / Trabajo Operativo / Alturas",
            "Conductor / Repartidor / Tránsito continuo",
            "Oficina / Desarrollo / Trabajo Digital",
            "Comercio / Servicios / Multitudes",
            "Estudiante / Trabajo principalmente en casa",
            "Trabajo nocturno / Turnos variables"
        ],
        key="campo_ocupacion"
    )
    piso = st.slider(
        "¿En qué nivel o piso permaneces más tiempo?",
        1, 60, 1, key="campo_piso"
    )
    transporte_principal = st.selectbox(
        "¿En qué te desplazas regularmente?",
        [
            "Automóvil",
            "Motocicleta / Bicicleta",
            "Metro / Tren",
            "Metrobús / Autobús",
            "Camión urbano / Microbús / Combi",
            "Cablebús / Teleférico",
            "Avión",
            "Principalmente a pie"
        ],
        key="campo_transporte"
    )
    tiempo_desplazamiento = st.selectbox(
        "¿Cuánto tiempo pasas desplazándote al día?",
        [
            "Menos de 30 minutos",
            "30 minutos a 1 hora",
            "1 a 2 horas",
            "2 a 4 horas",
            "Más de 4 horas"
        ],
        key="campo_tiempo"
    )
    horario_mayor_riesgo = st.selectbox(
        "¿En qué horario realizas la mayor parte de tus trayectos?",
        ["Mañana", "Mediodía", "Tarde", "Noche", "Madrugada"],
        key="campo_horario"
    )
    entorno_urbano = st.radio(
        "¿Qué tan hostil es el entorno habitual de tus trayectos?",
        ["Bajo", "Moderado", "Alto", "Crítico"],
        key="campo_entorno"
    )
    sismos_zona = st.radio(
        "¿La zona donde vives o trabajas presenta actividad sísmica?",
        ["No", "Sí, ocasional", "Sí, frecuente"],
        key="campo_sismos"
    )
    clima_exposicion = st.selectbox(
        "¿A qué condiciones ambientales estás más expuesto?",
        [
            "Clima estable",
            "Lluvia frecuente",
            "Calor intenso",
            "Frío intenso",
            "Tormentas eléctricas",
            "Cambios extremos"
        ],
        key="campo_clima"
    )

    st.write("---")
    st.markdown("### 🕯️ Bloque III: Hábitos y Umbral del Riesgo")

    actividad_fisica = st.selectbox(
        "¿Cuál describe mejor tu actividad física?",
        ["Frecuente", "Moderada", "Poca", "Casi ninguna"],
        key="campo_actividad"
    )
    deportes_extremos = st.radio(
        "¿Realizas actividades de alta adrenalina o riesgo físico?",
        ["Nunca", "Pocas veces", "Frecuentemente", "Constantemente"],
        key="campo_extremos"
    )
    sueño = st.selectbox(
        "¿Cuántas horas duermes normalmente?",
        ["Menos de 4", "4 a 5", "5 a 6", "6 a 7", "7 a 8", "Más de 8"],
        key="campo_sueno"
    )
    fatiga = st.select_slider(
        "Nivel habitual de fatiga:",
        options=["Mínimo", "Estrés común", "Alto", "Agotamiento extremo"],
        key="campo_fatiga"
    )
    tabaco = st.radio(
        "¿Consumes tabaco o vapores?",
        ["No", "Ocasionalmente", "Diariamente"],
        key="campo_tabaco"
    )
    alcohol = st.radio(
        "Consumo de alcohol:",
        ["Nulo", "Moderado", "Frecuente"],
        key="campo_alcohol"
    )
    sustancias = st.radio(
        "¿Consumes alguna sustancia ilegal?",
        ["No", "Ocasional", "Regular"],
        key="campo_sustancias"
    )

    st.write("---")
    st.markdown("### 🔮 Bloque IV: El Entorno")

    vivienda = st.selectbox(
        "¿Dónde pasas la mayor parte de tus noches?",
        [
            "Casa independiente",
            "Departamento",
            "Casa compartida",
            "Lugar aislado",
            "Hotel / alojamiento temporal",
            "Otro"
        ],
        key="campo_vivienda"
    )
    escaleras = st.radio(
        "¿Tu rutina incluye escaleras, azoteas o desniveles?",
        ["Casi nunca", "A veces", "Frecuentemente"],
        key="campo_escaleras"
    )
    agua = st.radio(
        "¿Pasas tiempo cerca de cuerpos de agua?",
        ["No", "A veces", "Frecuentemente"],
        key="campo_agua"
    )
    maquinaria = st.radio(
        "¿Trabajas cerca de maquinaria, herramientas o instalaciones eléctricas?",
        ["No", "A veces", "Frecuentemente"],
        key="campo_maquinaria"
    )
    conducir_cansado = st.radio(
        "¿Has conducido estando muy cansado/a?",
        ["Nunca", "Alguna vez", "Frecuentemente"],
        key="campo_cansado"
    )
    objetos_riesgo = st.radio(
        "¿Tienes en casa objetos o instalaciones potencialmente peligrosos?",
        ["No", "Algunos", "Varios"],
        key="campo_objetos"
    )
    visibilidad = st.selectbox(
        "¿Cómo suele ser la visibilidad en tus trayectos?",
        ["Buena", "Variable", "Mala", "Muy mala"],
        key="campo_visibilidad"
    )
    atencion = st.select_slider(
        "¿Qué tan atento sueles estar cuando estás bajo presión?",
        options=["Muy atento", "Atento", "Distraído", "Agotado"],
        key="campo_atencion"
    )
    lugar_frecuente = st.selectbox(
        "¿Cuál de estos lugares forma parte de tu rutina?",
        [
            "Carretera",
            "Edificio alto",
            "Obra",
            "Taller",
            "Oficina",
            "Centro comercial",
            "Estación de transporte",
            "Casa"
        ],
        key="campo_lugar"
    )

    st.write("---")
    st.markdown("### 📿 Bloque V: Inclinaciones Ocultas")

    creencias = st.selectbox(
        "¿Qué lugar ocupa lo sobrenatural en tu vida?",
        [
            "Ninguno",
            "Curiosidad",
            "Creo en energías / fenómenos",
            "Creo firmemente en lo sobrenatural"
        ],
        key="campo_creencias"
    )
    aficion_terror = st.radio(
        "¿Consumes historias de ultratumba, casas embrujadas o terror psicológico?",
        ["Me aterra", "Consumo ocasional", "Me fascina"],
        key="campo_terror"
    )
    reliquias = st.radio(
        "¿Posees algún objeto antiguo, heredado o extraño?",
        ["No", "Sí, uno", "Sí, varios"],
        key="campo_reliquias"
    )
    lugar_temido = st.selectbox(
        "¿Qué escenario te produce mayor incomodidad?",
        [
            "Ninguno en particular",
            "El mar / agua profunda",
            "Un volcán",
            "Un terremoto",
            "Una carretera vacía",
            "Una caída desde altura",
            "Un incendio",
            "Una tormenta eléctrica",
            "Un edificio abandonado",
            "Un ascensor / espacio cerrado",
            "Un bosque de noche",
            "La oscuridad total",
            "Estar completamente solo",
            "Una multitud",
            "Un accidente aéreo",
            "Un accidente automovilístico",
            "Animales agresivos",
            "No poder pedir ayuda"
        ],
        key="campo_temor"
    )
    segundo_temor = st.selectbox(
        "¿Y cuál de estos peligros te inquieta en segundo lugar?",
        [
            "Ninguno",
            "Agua profunda",
            "Fuego",
            "Alturas",
            "Terremotos",
            "Volcanes",
            "Tormentas",
            "Accidentes",
            "Espacios cerrados",
            "Soledad",
            "Oscuridad",
            "Perder el control",
            "Quedar atrapado"
        ],
        key="campo_segundo_temor"
    )

    enviar = st.form_submit_button(
        "REVELAR SENTENCIA DE ULTRATUMBA 👁️",
        use_container_width=True
    )


st.button(
    "🕯️ LIMPIAR CAMPOS Y CERRAR EL EXPEDIENTE",
    on_click=limpiar_todo,
    use_container_width=True
)


# ============================================================
# GENERAR RESULTADO
# ============================================================
if enviar:
    if not nombre.strip():
        st.error("La presencia de ultratumba necesita un nombre para abrir el expediente.")
    else:
        nombre_str = nombre.strip().upper()

        with st.spinner("☠️ EL VELO SE ESTÁ ABRIENDO... GENERANDO LÁPIDA Y SENTENCIA DE ULTRATUMBA"):
            semilla = generar_semilla(
                nombre_str, sexo, fecha_nacimiento, estado_civil,
                personas_dependientes, ocupacion, piso, transporte_principal,
                tiempo_desplazamiento, horario_mayor_riesgo, entorno_urbano,
                sismos_zona, clima_exposicion, actividad_fisica,
                deportes_extremos, sueño, fatiga, tabaco, alcohol, sustancias,
                vivienda, escaleras, agua, maquinaria, conducir_cansado,
                objetos_riesgo, visibilidad, atencion, lugar_frecuente,
                creencias, aficion_terror, reliquias, lugar_temido,
                segundo_temor
            )

            rng = random.Random(semilla)

            # ------------------------------------------------
            # ÍNDICE NARRATIVO ORIGINAL, CONSERVADO
            # ------------------------------------------------
            riesgo = 8
            riesgo += {"Bajo": 0, "Moderado": 5, "Alto": 10, "Crítico": 18}[entorno_urbano]
            riesgo += {
                "Menos de 30 minutos": 0,
                "30 minutos a 1 hora": 2,
                "1 a 2 horas": 5,
                "2 a 4 horas": 8,
                "Más de 4 horas": 12
            }[tiempo_desplazamiento]
            riesgo += {
                "Mañana": 0,
                "Mediodía": 1,
                "Tarde": 3,
                "Noche": 8,
                "Madrugada": 10
            }[horario_mayor_riesgo]
            riesgo += {
                "Buena": 0,
                "Variable": 3,
                "Mala": 7,
                "Muy mala": 11
            }[visibilidad]
            riesgo += {
                "Muy atento": 0,
                "Atento": 2,
                "Distraído": 6,
                "Agotado": 10
            }[atencion]

            if "Motocicleta" in transporte_principal:
                riesgo += 15
            elif "Automóvil" in transporte_principal:
                riesgo += 7

            if "Sí, frecuente" in sismos_zona:
                riesgo += 7
            elif "Sí, ocasional" in sismos_zona:
                riesgo += 3

            if "Tormentas" in clima_exposicion:
                riesgo += 5

            if "Constantemente" in deportes_extremos:
                riesgo += 15
            elif "Frecuentemente" in deportes_extremos:
                riesgo += 8

            riesgo += {
                "Menos de 4": 10,
                "4 a 5": 6,
                "5 a 6": 3,
                "6 a 7": 1,
                "7 a 8": 0,
                "Más de 8": 0
            }[sueño]

            riesgo += {
                "Mínimo": 0,
                "Estrés común": 2,
                "Alto": 5,
                "Agotamiento extremo": 9
            }[fatiga]

            if tabaco == "Diariamente":
                riesgo += 5
            if alcohol == "Frecuente":
                riesgo += 4

            if sustancias == "Regular":
                riesgo += 8
            elif sustancias == "Ocasional":
                riesgo += 3

            if conducir_cansado == "Frecuentemente":
                riesgo += 10
            elif conducir_cansado == "Alguna vez":
                riesgo += 3

            if maquinaria == "Frecuentemente":
                riesgo += 8
            if escaleras == "Frecuentemente":
                riesgo += 5
            if agua == "Frecuentemente":
                riesgo += 4

            riesgo = min(98, max(5, riesgo + rng.randint(-4, 7)))

            nivel = (
                "UMBRAL CRÍTICO" if riesgo >= 75
                else "SOMBRA ELEVADA" if riesgo >= 55
                else "VIGILIA" if riesgo >= 35
                else "BAJO EL VELO"
            )

            edad_actual = max(
                1,
                (datetime.now().date() - fecha_nacimiento).days // 365
            )

            horizonte = rng.randint(8, 46)

            if riesgo >= 75:
                horizonte = rng.randint(4, 24)
            elif riesgo >= 55:
                horizonte = rng.randint(8, 30)
            elif riesgo < 35:
                horizonte = rng.randint(18, 46)

            fecha_muerte = datetime.now() + timedelta(
                days=int(horizonte * 365.25) + rng.randint(-180, 180)
            )

            edad_muerte = calcular_edad_en_fecha(
                fecha_nacimiento,
                fecha_muerte
            )

            # ------------------------------------------------
            # CAUSA NUEVA, BASADA EN PUNTUACIÓN
            # ------------------------------------------------
            titulo_escenario, descripcion_escenario, puntuacion_causa = determinar_causa(
                transporte_principal,
                tiempo_desplazamiento,
                horario_mayor_riesgo,
                entorno_urbano,
                sismos_zona,
                clima_exposicion,
                deportes_extremos,
                sueño,
                fatiga,
                escaleras,
                agua,
                maquinaria,
                conducir_cansado,
                visibilidad,
                atencion,
                lugar_frecuente,
                lugar_temido,
                segundo_temor,
                piso,
                vivienda,
                rng,
            )

            lugares = []

            if "Automóvil" in transporte_principal:
                lugares.append("una avenida de tránsito rápido")
            if "Motocicleta" in transporte_principal:
                lugares.append("una vía urbana con pavimento irregular")
            if horario_mayor_riesgo in ["Noche", "Madrugada"]:
                lugares.append("una calle con iluminación intermitente")
            if piso >= 10:
                lugares.append(f"un edificio situado en el nivel {piso}")
            if vivienda == "Departamento":
                lugares.append("un edificio residencial")
            if vivienda == "Lugar aislado":
                lugares.append("una propiedad alejada del tránsito habitual")
            if lugar_frecuente == "Carretera":
                lugares.append("un tramo de carretera de circulación rápida")
            if lugar_frecuente == "Obra":
                lugares.append("una zona de trabajo en construcción")
            if lugar_frecuente == "Taller":
                lugares.append("un taller con maquinaria en funcionamiento")
            if lugar_frecuente == "Estación de transporte":
                lugares.append(
                    "una estación de transporte durante una hora de alta circulación"
                )

            if not lugares:
                lugares.append("un entorno cotidiano que conocías perfectamente")

            lugar_final = elegir(lugares, rng)

            detalle_psicologico = elegir([
                "Lo inquietante es que durante los días anteriores habías notado pequeños detalles fuera de lugar.",
                "Existe un instante previo en el que todo parece demasiado silencioso.",
                "El último recuerdo claro corresponde a un detalle completamente insignificante.",
                "Quienes reconstruyen la escena descubren que una decisión aparentemente pequeña cambió toda la secuencia.",
                "La parte más perturbadora es que el lugar era completamente familiar.",
                "Horas antes, el expediente registra una rutina exactamente igual a muchas otras. Nadie esperaba que esa fuera la última.",
            ], rng)

            if segundo_temor != "Ninguno":
                detalle_psicologico += (
                    " El expediente también registra una inquietud secundaria relacionada con "
                    + segundo_temor.lower() + "."
                )

            pareja_memoria = "esposa" if sexo == "Masculino" else "esposo"

            dedicatoria = (
                f"En memoria de tu {pareja_memoria}, tus amigos y seres queridos, "
                "que conservan tu recuerdo y las pequeñas cosas que dejaste atrás."
            )

            causa_final = (
                f"{descripcion_escenario} El incidente ocurrió en {lugar_final}. "
                f"{detalle_psicologico}"
            )

            nacimiento_str = fecha_nacimiento.strftime("%d/%m/%Y")
            muerte_str = fecha_muerte.strftime("%d/%m/%Y")
            folio_num = f"DEF-{rng.randint(100000, 999999)}-2026"

            texto_a_leer = (
                f"Hasta aquí llegaste, {nombre_str}. La Voz de Ultratumba ha cerrado tu expediente. "
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
                fecha_registro=datetime.now().strftime("%d/%m/%Y"),
                transporte=transporte_principal,
                horario=horario_mayor_riesgo,
                visibilidad=visibilidad,
                entorno=entorno_urbano,
                clima=clima_exposicion,
                sueño=sueño,
                fatiga=fatiga,
                atencion=atencion,
                lugar_frecuente=lugar_frecuente,
                puntuacion_causa=puntuacion_causa,
            )

            st.session_state.resultado = resultado
            st.session_state.folio = folio_num
            st.session_state.resultado_generado = True
            st.session_state.pdf_generado = None
            st.session_state.ia_detalle = None
            st.session_state.ia_error = None

            audio, error_audio = generar_voz_ultratumba(texto_a_leer)

            st.session_state.audio_generado = audio
            st.session_state.audio_error = error_audio


# ============================================================
# MOSTRAR RESULTADO
# ============================================================
if st.session_state.resultado_generado and st.session_state.resultado:
    r = st.session_state.resultado

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
      <b>ESTADO DEL VELO:</b> {html.escape(texto_pdf_seguro(r['nivel']))}<br>
      <b>ÍNDICE NARRATIVO:</b> {r['riesgo']} / 100<br>
      <b>ESCENARIO:</b> {html.escape(texto_pdf_seguro(r['escenario']))}<br>
      <b>ENTORNO:</b> {html.escape(texto_pdf_seguro(r['lugar']))}<br>
      <b>EDAD ACTUAL:</b> {r['edad']} años<br>
      <b>EDAD AL FALLECER:</b> {r['edad_muerte']} años<br>
      <b>FECHA DEL REGISTRO:</b> {r['fecha_registro']}
    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # MI MUERTE MÁS DETALLADA
    # ========================================================
    st.markdown("### 🕯️ Reconstrucción del Expediente")

    st.markdown(
        '<div class="oraculo-box">'
        '<div class="oraculo-status">🤖 MODO DE NARRACIÓN AVANZADA</div>'
        '<div style="color:#b5b5c3;font-family:monospace;font-size:11px;line-height:1.6;">'
        "La lectura utiliza la causa generada por el expediente y tus respuestas "
        "para construir una reconstrucción ficticia mucho más detallada."
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🩸 MI MUERTE MÁS DETALLADA",
        use_container_width=True,
        key="boton_muerte_detallada"
    ):
        with st.spinner("☠️ LA PARCA ESTÁ RECONSTRUYENDO LA ÚLTIMA SECUENCIA..."):
            detalle, error = generar_muerte_detallada_con_ia(r)

        st.session_state.ia_detalle = detalle
        st.session_state.ia_error = error
        st.rerun()

    if st.session_state.ia_detalle:
        texto_ia = html.escape(st.session_state.ia_detalle).replace("\n", "<br>")

        st.markdown(
            f"""
            <div class="ia-detalle">
                <h4>☠️ RECONSTRUCCIÓN CONFIDENCIAL</h4>
                {texto_ia}
                <br><br>
                <div style="text-align:center;color:#777785;font-size:10px;">
                    ESTA RECONSTRUCCIÓN ES FICCIÓN NARRATIVA Y NO REPRESENTA
                    UNA PREDICCIÓN REAL DEL FUTURO.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.ia_error:
        st.markdown(
            f"""
            <div class="oraculo-box">
                <b>⚠️ LA RECONSTRUCCIÓN NO PUDO SER GENERADA</b>
                <div class="error-voz">{html.escape(st.session_state.ia_error)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # VOZ
    # ========================================================
    st.markdown("### 🎙️ Sentencia de Voz de Ultratumba")

    if st.session_state.audio_generado:
        audio_b64 = base64.b64encode(
            st.session_state.audio_generado
        ).decode("ascii")

        st.components.v1.html(f"""
        <div style="text-align:center;background:#110b1a;padding:18px;border:1px solid #9d4edd;border-radius:8px;font-family:monospace;color:#00ff66;">
          <div style="margin-bottom:12px;">🔊 VOZ DE ULTRATUMBA ACTIVA</div>
          <audio id="sentencia-oraculo" controls preload="metadata"
                 style="width:94%;height:48px;">
            <source src="data:audio/wav;base64,{audio_b64}" type="audio/wav">
          </audio>
        </div>

        <script>
        (() => {{
          const player=document.getElementById('sentencia-oraculo');
          const parent=window.parent.document;
          const musica=parent.getElementById('oraculo-ambiente-persistente');

          if(!player) return;

          player.addEventListener('play',()=>{{
            if(musica){{
              musica.volume=.08;
              const p=musica.play();
              if(p&&p.catch)p.catch(()=>{{}});
            }}
          }});

          player.addEventListener('pause',()=>{{
            if(musica) musica.volume=.42;
          }});

          player.addEventListener('ended',()=>{{
            if(musica) musica.volume=.42;
          }});
        }})();
        </script>
        """, height=150, scrolling=False)

        st.download_button(
            "☠️ DESCARGAR SENTENCIA DE ULTRATUMBA",
            data=st.session_state.audio_generado,
            file_name=(
                f"Sentencia_Ultratumba_"
                f"{r['nombre'].replace(' ', '_')}.wav"
            ),
            mime="audio/wav",
            use_container_width=True,
            on_click="ignore",
            key="descargar_voz"
        )

    else:
        mensaje = st.session_state.audio_error or (
            "La voz del expediente no pudo ser generada."
        )

        st.markdown(f"""
        <div class="oraculo-box">
            <b>⚠️ LA VOZ DEL EXPEDIENTE NO PUDO SER GENERADA</b>
            <div class="error-voz">{html.escape(mensaje)}</div>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # PDF
    # ========================================================
    if st.session_state.pdf_generado is None:
        buffer = io.BytesIO()

        def marco(canvas, doc):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#7b2cbf"))
            canvas.setLineWidth(2)
            canvas.rect(20, 20, 572, 752)
            canvas.setLineWidth(.5)
            canvas.rect(24, 24, 564, 744)
            canvas.setFillColor(colors.HexColor("#111111"))
            canvas.rect(530, 710, 8, 40, fill=1, stroke=0)
            canvas.rect(516, 732, 36, 8, fill=1, stroke=0)
            dibujar_codigo_barras(
                canvas,
                40,
                45,
                sum(ord(c) for c in r['folio'])
            )
            canvas.restoreState()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=100
        )

        styles = getSampleStyleSheet()

        sg = ParagraphStyle(
            "sg",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=16,
            alignment=1,
            textColor=colors.HexColor("#111111")
        )
        ss = ParagraphStyle(
            "ss",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            alignment=1,
            textColor=colors.HexColor("#444444")
        )
        sec = ParagraphStyle(
            "sec",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.white,
            backColor=colors.HexColor("#4a154b"),
            borderPadding=4
        )
        campo = ParagraphStyle(
            "campo",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#222222")
        )
        val = ParagraphStyle(
            "val",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#444444")
        )
        causa = ParagraphStyle(
            "causa",
            fontName="Helvetica-BoldOblique",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#8b0000")
        )

        story = [
            Paragraph("ESTADOS UNIDOS DEL MÁS ALLÁ", sg),
            Paragraph(
                "REGISTRO CIVIL RESTRINGIDO • ACTA DE DEFUNCIÓN",
                ss
            ),
            Spacer(1, 15)
        ]

        story.append(Table(
            [
                [
                    Paragraph(
                        "<b>CRIPTA LOCAL:</b> Valle de las Sombras",
                        val
                    ),
                    Paragraph(
                        f"<b>NÚMERO DE CONTROL:</b> {r['folio']}",
                        val
                    )
                ],
                [
                    Paragraph(
                        "<b>LIBRO:</b> Destinos Cerrados",
                        val
                    ),
                    Paragraph(
                        f"<b>FECHA DE SISTEMA:</b> {r['fecha_registro']}",
                        val
                    )
                ]
            ],
            colWidths=[250, 270],
            style=[
                ("LINEBELOW", (0, 0), (-1, -1), .5, colors.HexColor("#CCC")),
                ("PADDING", (0, 0), (-1, -1), 4)
            ]
        ))

        story.append(Spacer(1, 15))
        story.append(Paragraph("I. DATOS DE LA PERSONA", sec))
        story.append(Spacer(1, 6))

        story.append(Table(
            [
                [Paragraph("NOMBRE COMPLETO:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['nombre'])), val)],
                [Paragraph("SEXO:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['sexo'])), val)],
                [Paragraph("FECHA DE NACIMIENTO:", campo),
                 Paragraph(r['nacimiento'], val)],
                [Paragraph("ESTADO CIVIL:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['estado'])), val)],
                [Paragraph("ACTIVIDAD:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['ocupacion'])), val)],
                [Paragraph("NIVEL DEL VELO:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['nivel'])), val)],
                [Paragraph("EDAD AL FALLECER:", campo),
                 Paragraph(f"{r['edad_muerte']} años", val)]
            ],
            colWidths=[150, 370],
            style=[
                ("INNERGRID", (0, 0), (-1, -1), .25, colors.HexColor("#E0E0E0")),
                ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#AAA")),
                ("PADDING", (0, 0), (-1, -1), 5)
            ]
        ))

        story.append(Spacer(1, 15))
        story.append(Paragraph("II. DATOS DEL FALLECIMIENTO", sec))
        story.append(Spacer(1, 6))

        story.append(Table(
            [
                [Paragraph("FECHA DEL DECESO:", campo),
                 Paragraph(r['muerte'], val)],
                [Paragraph("EDAD AL FALLECER:", campo),
                 Paragraph(f"{r['edad_muerte']} años", val)],
                [Paragraph("ESCENARIO:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['escenario'])), val)],
                [Paragraph("LUGAR:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['lugar'])), val)],
                [Paragraph("CAUSA:", campo),
                 Paragraph(html.escape(texto_pdf_seguro(r['causa'])), causa)]
            ],
            colWidths=[150, 370],
            style=[
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("INNERGRID", (0, 0), (-1, -1), .25, colors.HexColor("#E0E0E0")),
                ("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#AAA")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (1, 4), (1, 4), colors.HexColor("#FFF2F2"))
            ]
        ))

        story.append(Spacer(1, 15))
        story.append(Paragraph("III. LECTURA DEL EXPEDIENTE", sec))
        story.append(Spacer(1, 6))
        story.append(
            Paragraph(
                html.escape(texto_pdf_seguro(r['descripcion'] + " " + r['detalle'])),
                val
            )
        )

        story.append(Spacer(1, 12))
        story.append(Paragraph("IV. EPITAFIO", sec))
        story.append(Spacer(1, 5))
        story.append(
            Paragraph(
                f'<i>"{html.escape(texto_pdf_seguro(r["dedicatoria"]))}"</i>',
                val
            )
        )

        story.append(Spacer(1, 15))
        story.append(Paragraph(
            "V. CADENA DIGITAL DE AUTENTICACIÓN",
            sec
        ))
        story.append(Spacer(1, 5))
        story.append(
            Paragraph(
                f"<font size=7 color='#666666'>"
                f"||{r['folio']}||{r['nombre']}||{r['muerte']}||"
                f"{sum(ord(c) for c in r['folio'])}"
                f"#PARCAS_AUTENTICACION||</font>",
                ss
            )
        )

        story.append(Spacer(1, 25))
        story.append(Table(
            [[
                Paragraph(
                    "_____________________________<br/>"
                    "Átropos<br/>Oficial Registrador del Hilo",
                    ParagraphStyle(
                        "f1",
                        fontName="Helvetica",
                        fontSize=7.5,
                        alignment=1
                    )
                ),
                Paragraph(
                    "_____________________________<br/>"
                    "La Parca Mayor<br/>Interventor del Destino",
                    ParagraphStyle(
                        "f2",
                        fontName="Helvetica",
                        fontSize=7.5,
                        alignment=1
                    )
                )
            ]],
            colWidths=[250, 250],
            style=[("PADDING", (0, 0), (-1, -1), 2)]
        ))

        doc.build(
            story,
            onFirstPage=marco,
            onLaterPages=marco
        )

        st.session_state.pdf_generado = buffer.getvalue()

    st.download_button(
        "⚖️ DESCARGAR ACTA DE DEFUNCIÓN",
        data=st.session_state.pdf_generado,
        file_name=(
            f"Acta_Defuncion_{r['nombre'].replace(' ', '_')}.pdf"
        ),
        mime="application/pdf",
        use_container_width=True,
        on_click="ignore",
        key="descargar_acta"
    )

    st.markdown(f"""
    <div class="lectura-final">
      👁️<br><br>
      Hasta aquí llegaste, {html.escape(texto_pdf_seguro(r['nombre']))}.<br>
      El expediente <b>{html.escape(r['folio'])}</b> ha sido cerrado.<br><br>
      <span style="color:#777785;">Algunas puertas se abren una sola vez.</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PIE DE PÁGINA / VISITAS / APOYO
# ============================================================
VISITAS_FALSAS = 27843

st.markdown(
    f"""
    <div class="contador-visitas">
        ☠️ VISITAS AL PORTAL
        <div style="margin-top:8px;">
            <span style="display:inline-block; background:#1a0033; color:#00ff66; border:1px solid #00ff66; border-radius:4px; padding:4px 10px; font-family:'Courier New',monospace; font-size:14px; font-weight:bold; letter-spacing:2px; box-shadow:0 0 12px rgba(0,255,102,.15);">
                {VISITAS_FALSAS:,}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="apoyar-proyecto">
        <a href="{html.escape(PAYPAL_URL, quote=True)}" target="_blank" rel="noopener noreferrer">
            🖤 APOYAR PROYECTO
        </a>
    </div>
    <div class="footer-alex">CREATED BY ALEX A.</div>
    """,
    unsafe_allow_html=True
)
