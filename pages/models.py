import streamlit as st

st.set_page_config(page_title="Models", layout="wide")
st.title("Judgement models")

if "current_spec" not in st.session_state:
    st.session_state.current_spec = "Initial task specification:"
if "spec_quality_history" not in st.session_state:
    st.session_state.spec_quality_history = []

st.subheader("Current task specification")
st.code(st.session_state.current_spec, language="markdown")

if st.session_state.spec_quality_history:
    st.subheader("Benchmark progress")
    st.line_chart(st.session_state.spec_quality_history)
    st.metric("Total iterations", len(st.session_state.spec_quality_history))
else:
    st.info("No runs yet – go to Experiments")

with st.expander("Edit manually:"):
    new_spec = st.text_area("Task spec", value=st.session_state.current_spec, height=200)
    if st.button("Update spec"):
        st.session_state.current_spec = new_spec
        st.rerun()
