import streamlit as st
from google import genai

st.set_page_config(
    page_title="Prueba directa de Gemini",
    page_icon="🔑"
)

st.title("🔑 Prueba directa de Gemini")

st.write("Esta prueba utiliza únicamente el SDK oficial de Google.")
st.write("No utiliza OpenAI ni DeepSeek.")

api_key = st.text_input(
    "Introduce tu clave Gemini AQ",
    type="password",
    placeholder="AQ..."
)

if st.button("🚀 PROBAR GEMINI", use_container_width=True):

    if not api_key:
        st.error("Introduce primero la clave AQ.")
        st.stop()

    if not api_key.startswith("AQ"):
        st.warning(
            "La clave introducida no comienza con AQ. "
            "Verifica que sea la API Key correcta."
        )

    try:
        st.info("Conectando con Gemini...")

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Responde únicamente con: GEMINI_OK"
        )

        st.success("✅ Gemini respondió correctamente.")

        if response.text:
            st.code(response.text)
        else:
            st.warning("Gemini respondió, pero no devolvió texto.")

    except Exception as e:

        st.error("❌ Gemini rechazó la solicitud.")

        st.code(
            str(e),
            language="text"
        )

        st.markdown("### Diagnóstico")

        error_text = str(e)

        if "401" in error_text or "UNAUTHENTICATED" in error_text:
            st.warning(
                "HTTP 401: Google no aceptó la autenticación. "
                "La clave, el proyecto o el tipo de credencial "
                "pueden no ser compatibles con esta API."
            )

        elif "403" in error_text:
            st.warning(
                "HTTP 403: la autenticación llegó a Google, "
                "pero el proyecto o la API no tienen autorización."
            )

        elif "429" in error_text:
            st.warning(
                "HTTP 429: se alcanzó un límite de solicitudes o cuota."
            )

        elif "404" in error_text:
            st.warning(
                "HTTP 404: el modelo o endpoint solicitado no fue encontrado."
            )

        else:
            st.info(
                "El error no coincide con los códigos anteriores. "
                "Revisa el mensaje completo mostrado arriba."
            )
