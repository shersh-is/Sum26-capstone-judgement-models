import streamlit as st
import random

st.set_page_config(page_title="Experiments", layout="wide")
st.title("Experiment cycle")

if "current_spec" not in st.session_state:
    st.session_state.current_spec = "Initial task specification: "
if "spec_quality_history" not in st.session_state:
    st.session_state.spec_quality_history = []
if "iteration" not in st.session_state:
    st.session_state.iteration = 0

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
    quality = st.select_slider("Solution quality bias", options=["poor", "mixed", "good"], value="mixed")
    if st.button("run", type="primary"):
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
            sol = generate_solution(st.session_state.current_spec, "mixed")
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
