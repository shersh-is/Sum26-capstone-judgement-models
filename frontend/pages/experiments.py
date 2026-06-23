import streamlit as st
import random

st.set_page_config(
    page_title="Experiments",
    layout="wide"
)
st.title("Experiment cycle")

def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

if "current_spec" not in st.session_state:
    st.session_state.current_spec = "Initial task specification: "
if "spec_quality_history" not in st.session_state:
    st.session_state.spec_quality_history = []
if "iteration" not in st.session_state:
    st.session_state.iteration = 0
if "quality" not in st.session_state:
    st.session_state.quality = "mixed"

def generate_solution(spec, quality="mixed"):
    return f"Solution (quality={quality}) for spec: {spec[:50]}..."

def get_perfect_feedback(solution):
    return "Perfect feedback placeholder"

def diff_spec(current_spec, last_solution, last_feedback):
    return current_spec + " " + last_feedback[:50]

def run_benchmark(spec):
    return random.uniform(0.5, 1.0)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Run a new cycle")

    st.write("**Select solution quality:**")
    q_cols = st.columns(3)
    with q_cols[0]:
        if st.button("Poor", key="btn_poor"):
            st.session_state.quality = "poor"
            st.rerun()
    with q_cols[1]:
        if st.button("Mixed", key="btn_mixed"):
            st.session_state.quality = "mixed"
            st.rerun()
    with q_cols[2]:
        if st.button("Good", key="btn_good"):
            st.session_state.quality = "good"
            st.rerun()
    
    st.markdown(f"**Current selection:** <span style='color: #1e2a3a; font-weight: 600;'>{st.session_state.quality}</span>", unsafe_allow_html=True)
    if st.button("Run", type="primary"):
        quality = st.session_state.quality
        solution = generate_solution(st.session_state.current_spec, quality)
        feedback = get_perfect_feedback(solution)
        new_spec = diff_spec(st.session_state.current_spec, solution, feedback)
        score = run_benchmark(new_spec)

        st.session_state.current_spec = new_spec
        st.session_state.iteration += 1
        st.session_state.spec_quality_history.append(score)
        st.success(f"Iteration {st.session_state.iteration} complete, score: {score:.3f}")
        st.rerun()

    if st.button("Auto‑run several"):
        for i in range(5):
            sol = generate_solution(st.session_state.current_spec, st.session_state.quality)
            fb = get_perfect_feedback(sol)
            new_spec = diff_spec(st.session_state.current_spec, sol, fb)
            score = run_benchmark(new_spec)
            st.session_state.current_spec = new_spec
            st.session_state.spec_quality_history.append(score)
            st.session_state.iteration += 1
        st.rerun()

with col2:
    st.subheader("Last cycle:")
    if st.session_state.iteration > 0:
        st.metric("Iterations run", st.session_state.iteration)
        if st.session_state.spec_quality_history:
            latest = st.session_state.spec_quality_history[-1]
            st.metric("Latest benchmark", f"{latest:.3f}")
            if len(st.session_state.spec_quality_history) > 1:
                prev = st.session_state.spec_quality_history[-2]
                delta = latest - prev
                st.metric("Improvement", f"{delta:+.3f}")
    else:
        st.info("No iterations yet")

    if st.session_state.spec_quality_history:
        st.subheader("Convergence over iterations")
        st.line_chart(st.session_state.spec_quality_history)
