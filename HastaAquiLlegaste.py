# ============================================================
# DIAGNÓSTICO GEMINI AQ - SIN MODIFICAR LA APLICACIÓN PRINCIPAL
# ============================================================
#
# Este archivo prueba la misma clave AQ de Google AI Studio
# mediante las formas de autenticación compatibles con Gemini API:
#
# 1) REST con header x-goog-api-key
# 2) REST con parámetro ?key=
# 3) SDK oficial google-genai (si está instalado)
#
# NO usa OpenAI.
# NO usa DeepSeek.
# NO necesita facturación para hacer la prueba.
#
# IMPORTANTE:
# - NO pegues tu clave dentro de este archivo.
# - Pégala cuando Streamlit la solicite.
# - Si la clave aparece en pantalla, se muestra únicamente enmascarada.
#
# EJECUCIÓN:
#   pip install streamlit requests google-genai
#   streamlit run diagnostico_gemini_aq.py
#
# ============================================================

import json
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="Diagnóstico Gemini AQ",
    page_icon="🧪",
    layout="centered",
)

st.title("🧪 Diagnóstico directo de Gemini")
st.caption("Prueba aislada. NO modifica tu aplicación HASTA AQUÍ LLEGASTE.")

st.markdown("""
Esta herramienta intenta descubrir si el problema está en:

- la clave AQ
- el proyecto de Google AI Studio
- el método de autenticación
- el SDK de Python
- o la API de Gemini
""")

api_key = st.text_input(
    "Pega aquí tu clave Gemini AQ",
    type="password",
    placeholder="AQ...",
)

if not api_key:
    st.info("Pega tu clave AQ para comenzar la prueba.")
    st.stop()

api_key = api_key.strip()

if not api_key.startswith("AQ"):
    st.warning(
        "La clave introducida no empieza con AQ. "
        "Verifica que hayas copiado la clave completa."
    )

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------

def mostrar_resultado(nombre, ok, status_code=None, detalle=""):
    if ok:
        st.success(f"✅ {nombre}: FUNCIONÓ")
    else:
        st.error(f"❌ {nombre}: FALLÓ")

    if status_code is not None:
        st.code(f"HTTP {status_code}")

    if detalle:
        st.code(detalle[:5000])


def respuesta_resumida(response):
    try:
        data = response.json()
        return json.dumps(data, indent=2, ensure_ascii=False)[:5000]
    except Exception:
        return response.text[:5000]


def es_auth_ok(response):
    # Cualquier respuesta que NO sea 401 indica que la credencial
    # fue reconocida por el servidor. Por ejemplo, 200 sería éxito.
    return response.status_code != 401


# ------------------------------------------------------------
# TEST 1 - REST oficial usando x-goog-api-key
# ------------------------------------------------------------

st.divider()
st.subheader("1️⃣ REST: x-goog-api-key")

if st.button("Probar autenticación REST", type="primary"):

    url = "https://generativelanguage.googleapis.com/v1beta/models"

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        ok = response.status_code == 200

        mostrar_resultado(
            "Header x-goog-api-key",
            ok,
            response.status_code,
            respuesta_resumida(response),
        )

        if response.status_code == 401:
            st.warning(
                "Google rechazó la credencial con HTTP 401. "
                "Si vuelve a aparecer ACCESS_TOKEN_TYPE_UNSUPPORTED, "
                "el problema no está en Streamlit."
            )

    except Exception as e:
        st.error(f"Error de conexión: {type(e).__name__}: {e}")


# ------------------------------------------------------------
# TEST 2 - REST con ?key=
# ------------------------------------------------------------

st.divider()
st.subheader("2️⃣ REST: parámetro ?key=")

if st.button("Probar REST con ?key="):

    url = "https://generativelanguage.googleapis.com/v1beta/models"

    try:
        response = requests.get(
            url,
            params={"key": api_key},
            timeout=30,
        )

        ok = response.status_code == 200

        mostrar_resultado(
            "REST ?key=",
            ok,
            response.status_code,
            respuesta_resumida(response),
        )

    except Exception as e:
        st.error(f"Error de conexión: {type(e).__name__}: {e}")


# ------------------------------------------------------------
# TEST 3 - SDK oficial google-genai
# ------------------------------------------------------------

st.divider()
st.subheader("3️⃣ SDK oficial google-genai")

if st.button("Probar SDK oficial"):

    try:
        from google import genai

        st.write("SDK google-genai detectado.")

        client = genai.Client(api_key=api_key)

        # models.list() es una prueba limpia de autenticación.
        # No depende de que un modelo concreto esté disponible.
        models = client.models.list()

        encontrados = []
        for i, model in enumerate(models):
            if i >= 5:
                break
            name = getattr(model, "name", None)
            if name:
                encontrados.append(name)

        st.success("✅ SDK: AUTENTICACIÓN ACEPTADA")
        st.write("Primeros modelos devueltos:")
        st.code("\n".join(encontrados) if encontrados else "La API respondió correctamente.")

    except ImportError:
        st.error(
            "No está instalado google-genai. Ejecuta:\n\n"
            "pip install -U google-genai"
        )

    except Exception as e:
        st.error("❌ SDK: FALLÓ")
        st.code(f"{type(e).__name__}: {e}")


# ------------------------------------------------------------
# TEST 4 - GenerateContent directo
# ------------------------------------------------------------

st.divider()
st.subheader("4️⃣ GenerateContent directo")

st.caption(
    "Esta prueba usa REST directamente, sin OpenAI, DeepSeek ni SDK."
)

if st.button("Probar generación con Gemini"):

    # Modelo actual de la familia Gemini 2.5, adecuado para
    # una prueba sencilla de texto.
    model = "gemini-2.5-flash"

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
    )

    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Responde únicamente: GEMINI FUNCIONA"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code == 200:
            st.success("🎉 GEMINI FUNCIONA")
            st.json(response.json())

        else:
            st.error(f"❌ Gemini rechazó la solicitud. HTTP {response.status_code}")
            st.code(respuesta_resumida(response))

    except Exception as e:
        st.error(f"Error de conexión: {type(e).__name__}: {e}")


# ------------------------------------------------------------
# TEST 5 - Diagnóstico automático
# ------------------------------------------------------------

st.divider()
st.subheader("5️⃣ Diagnóstico automático")

if st.button("🚀 Ejecutar todas las pruebas"):

    resultados = []

    # A. Header
    try:
        r1 = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        resultados.append(("x-goog-api-key", r1.status_code, respuesta_resumida(r1)))

    except Exception as e:
        resultados.append(("x-goog-api-key", "ERROR", str(e)))

    time.sleep(0.3)

    # B. Query parameter
    try:
        r2 = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key},
            timeout=30,
        )

        resultados.append(("?key=", r2.status_code, respuesta_resumida(r2)))

    except Exception as e:
        resultados.append(("?key=", "ERROR", str(e)))

    time.sleep(0.3)

    # C. SDK
    sdk_result = None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        models = client.models.list()

        first_model = None
        for model in models:
            first_model = getattr(model, "name", None)
            if first_model:
                break

        sdk_result = ("SDK google-genai", 200, first_model or "API respondió")

    except ImportError:
        sdk_result = (
            "SDK google-genai",
            "NO INSTALADO",
            "Instala con: pip install -U google-genai",
        )

    except Exception as e:
        sdk_result = ("SDK google-genai", "ERROR", f"{type(e).__name__}: {e}")

    resultados.append(sdk_result)

    # --------------------------------------------------------
    # Mostrar resumen
    # --------------------------------------------------------

    st.markdown("### 📊 Resultado")

    for nombre, codigo, detalle in resultados:

        if codigo == 200:
            st.success(f"🟢 {nombre}: OK")
        elif codigo == 401:
            st.error(f"🔴 {nombre}: HTTP 401")
        else:
            st.warning(f"🟡 {nombre}: {codigo}")

        st.code(str(detalle)[:3000])

    codigos_401 = [
        codigo for _, codigo, _ in resultados
        if codigo == 401
    ]

    if len(codigos_401) >= 2:
        st.markdown("---")
        st.error(
            "🚨 DIAGNÓSTICO: la clave AQ está siendo rechazada "
            "por más de un método de acceso."
        )

        st.write(
            "Esto apunta fuertemente a un problema de autenticación/"
            "provisión de la clave o del proyecto en Google, "
            "no a tu aplicación Streamlit."
        )

        st.info(
            "Guarda una captura de esta sección. El HTTP 401 y "
            "ACCESS_TOKEN_TYPE_UNSUPPORTED son la evidencia importante."
        )

    elif any(codigo == 200 for _, codigo, _ in resultados):
        st.success(
            "🎉 La clave fue aceptada por al menos uno de los métodos. "
            "Ya podemos usar el método que haya funcionado en tu aplicación."
        )

    else:
        st.warning(
            "No se obtuvo una autenticación válida. "
            "Revisa el detalle de cada prueba."
        )

st.divider()

st.caption(
    "Diagnóstico independiente. La clave se utiliza únicamente durante "
    "la sesión actual de Streamlit y no se escribe en este archivo."
)
