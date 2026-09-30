"""Asistente del convenio colectivo: responde dudas de trabajadores citando el artículo."""

from pathlib import Path

import anthropic
import streamlit as st
from pypdf import PdfReader

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"
MAX_PREGUNTAS = 30  # límite por sesión para controlar el coste de la API
MAX_TURNOS_HISTORIAL = 8  # cuántos mensajes previos se reenvían al modelo

st.set_page_config(page_title="Asistente del convenio", page_icon="📘")


def secreto(nombre: str, defecto: str | None = None) -> str | None:
    """Lee un secreto de Streamlit sin romper si no existe el archivo de secretos."""
    try:
        return st.secrets.get(nombre, defecto)
    except Exception:
        return defecto


MODELO = secreto("ANTHROPIC_MODEL", "claude-sonnet-5-5")


@st.cache_data(show_spinner="Cargando el convenio...")
def cargar_convenio() -> str:
    """Carga data/convenio.pdf o data/convenio.txt y devuelve el texto completo."""
    pdf = DATA_DIR / "convenio.pdf"
    txt = DATA_DIR / "convenio.txt"
    if pdf.exists():
        lector = PdfReader(str(pdf))
        paginas = [p.extract_text() or "" for p in lector.pages]
        return "\n\n".join(paginas)
    if txt.exists():
        return txt.read_text(encoding="utf-8")
    return ""


@st.cache_data
def cargar_instrucciones() -> str:
    return (BASE / "system_prompt.txt").read_text(encoding="utf-8")


def comprobar_acceso() -> None:
    """Si hay APP_PASSWORD definida, pide la contraseña antes de mostrar la app."""
    clave = secreto("APP_PASSWORD")
    if not clave or st.session_state.get("autenticado"):
        return
    intento = st.text_input("Contraseña de acceso", type="password")
    if intento:
        if intento == clave:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()


def generar_respuesta(cliente, bloques_sistema, historial):
    with cliente.messages.stream(
        model=MODELO,
        max_tokens=1200,
        system=bloques_sistema,
        messages=historial,
    ) as flujo:
        for texto in flujo.text_stream:
            yield texto


# ---------- Interfaz ----------
st.title("📘 Asistente del convenio")
st.caption(
    "Consulta dudas sobre licencias, permisos, vacaciones y otras condiciones. "
    "Las respuestas son orientativas y se basan únicamente en el texto del convenio cargado."
)

comprobar_acceso()

convenio = cargar_convenio()
api_key = secreto("ANTHROPIC_API_KEY")

if not convenio:
    st.error("No se encuentra el convenio. Añade `data/convenio.pdf` o `data/convenio.txt` al repositorio.")
    st.stop()
if not api_key:
    st.error("Falta la clave `ANTHROPIC_API_KEY` en los secretos de la app.")
    st.stop()

cliente = anthropic.Anthropic(api_key=api_key)

# El convenio va en un bloque aparte con caché, para abaratar y acelerar las consultas repetidas
bloques_sistema = [
    {"type": "text", "text": cargar_instrucciones()},
    {
        "type": "text",
        "text": f"<convenio>\n{convenio}\n</convenio>",
        "cache_control": {"type": "ephemeral"},
    },
]

with st.sidebar:
    st.subheader("Preguntas frecuentes")
    ejemplos = [
        "¿Cuántos días de licencia me corresponden por matrimonio?",
        "¿Cuántos días de vacaciones tengo al año?",
        "¿Qué licencia tengo por fallecimiento de un familiar?",
        "¿Tengo permiso para acudir al médico en horario de trabajo?",
        "¿Cómo se calculan las horas extraordinarias?",
    ]
    for ejemplo in ejemplos:
        if st.button(ejemplo, use_container_width=True):
            st.session_state["pendiente"] = ejemplo
    st.divider()
    st.warning(
        "No escribas datos personales (DNI, nómina, salud). "
        "Para tu caso concreto, confirma siempre con RRHH."
    )
    if st.button("Nueva conversación"):
        st.session_state["mensajes"] = []
        st.session_state["contador"] = 0
        st.rerun()

st.session_state.setdefault("mensajes", [])
st.session_state.setdefault("contador", 0)

for m in st.session_state["mensajes"]:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

pregunta = st.chat_input("Escribe tu pregunta sobre el convenio")
if st.session_state.get("pendiente"):
    pregunta = st.session_state.pop("pendiente")

if pregunta:
    if st.session_state["contador"] >= MAX_PREGUNTAS:
        st.info("Has alcanzado el límite de preguntas de esta sesión. Inicia una nueva conversación.")
        st.stop()

    st.session_state["mensajes"].append({"role": "user", "content": pregunta})
    st.session_state["contador"] += 1
    with st.chat_message("user"):
        st.markdown(pregunta)

    historial = st.session_state["mensajes"][-MAX_TURNOS_HISTORIAL:]
    with st.chat_message("assistant"):
        try:
            respuesta = st.write_stream(generar_respuesta(cliente, bloques_sistema, historial))
        except anthropic.APIError as e:
            respuesta = "Ha habido un problema al consultar el modelo. Inténtalo de nuevo en unos minutos."
            st.error(respuesta)
            st.caption(f"Detalle técnico: {type(e).__name__}")
    st.session_state["mensajes"].append({"role": "assistant", "content": respuesta})
