import streamlit as st

st.set_page_config(
    page_title="Judgement Model",
    layout="wide"
)

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def init_session_state():
    if "current_spec" not in st.session_state:
        st.session_state.current_spec = "Initial task specification:"
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = []
    if "iteration" not in st.session_state:
        st.session_state.iteration = 0
    if "spec_quality_history" not in st.session_state:
        st.session_state.spec_quality_history = []

init_session_state()

if "username" not in st.session_state:
    st.session_state.username = ""

with st.sidebar:
    name = st.text_input("Your name", value=st.session_state.username)
    if name:
        st.session_state.username = name
    st.write(f"Welcome, **{st.session_state.username or 'Guest'}**")

st.title("Judgement Model")
st.markdown("""
Converge towards a perfect expert model by iterating:
1. Generate a solution
2. Get feedback from perfect model
3. Diff task specifications without perfect model
4. Run quality benchmark
""")
st.info("Use the sidebar or the menu to go to **Models** or **Experiments**.")
