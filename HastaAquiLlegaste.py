import streamlit as st
import requests

st.set_page_config(
    page_title="Prueba Gemini",
    page_icon="🧪",
    layout="centered"
)

st.title("🧪 Prueba directa de Gemini")
st.write("Esta aplicación prueba únicamente la conexión con Gemini.")
st.write("No utiliza OpenAI ni DeepSeek.")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("No se encontró GEMINI_API_KEY en los Secrets de Streamlit.")
    st.code('GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"')
    st.stop()

# No mostramos la clave completa por seguridad.
if len(api_key) >= 8:
    clave_visible = api_key[:4] + "..." + api_key[-4:]
else:
    clave_visible = "(clave demasiado corta)"

st.info(f"Clave detectada: {clave_visible}")

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.5-flash:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}

data = {
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

if st.button("🚀 PROBAR GEMINI", use_container_width=True):
    try:
        with st.spinner("Conectando con Gemini..."):
            respuesta = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=60
            )

        st.write("Código HTTP:", respuesta.status_code)

        if respuesta.ok:
            resultado = respuesta.json()

            try:
                texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError):
                texto = None

            if texto:
                st.success("✅ GEMINI FUNCIONA")
                st.write("Respuesta de Gemini:")
                st.code(texto)
            else:
                st.warning("Gemini respondió, pero no se encontró el texto esperado.")
                st.json(resultado)
        else:
            st.error("❌ Gemini rechazó la solicitud.")
            st.code(respuesta.text)

            if respuesta.status_code == 401:
                st.warning(
                    "HTTP 401: la credencial fue rechazada. "
                    "Si la clave comienza con AQ., este resultado puede indicar "
                    "un problema de compatibilidad/provisionamiento de la nueva "
                    "Authorization Key y no necesariamente un error de Streamlit."
                )

    except requests.exceptions.Timeout:
        st.error("⏱️ Gemini tardó demasiado en responder.")

    except requests.exceptions.RequestException as e:
        st.error("🌐 No se pudo conectar con Gemini.")
        st.code(str(e))

    except Exception as e:
        st.error("⚠️ Ocurrió un error inesperado.")
        st.code(str(e))
