"""Streamlit Landing Page: IFSI Phishing Email Detection & Prompt Injection Benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to sys.path so modules can be imported directly
root_dir = Path(__file__).resolve().parent
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from ui_utils import apply_custom_css, check_ollama_service, get_rag_retriever

st.set_page_config(
    page_title="IFSI Phishing Detection Benchmark",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()

# Header
st.title("🛡️ IFSI: Phishing Detection & Prompt Injection Benchmark")
st.markdown("#### *Injection-First Staged Inference: Balancing Robustness & Reasoning Cost*")

st.divider()

# --- Project Summary Paragraph ---
st.subheader("📌 Project Overview")
st.markdown(
    """
    **Injection-First Staged Inference (IFSI)** investigates the resilience of machine learning and Large Language 
    Model (LLM) email classification pipelines under indirect adversarial prompt injections. While traditional 
    feature-based classifiers (TF-IDF + Logistic Regression) remain immune to natural and marked prompt injections 
    by operating over linear vocabulary distributions, coupled single-call LLM architectures suffer catastrophic evasion 
    when injected attacker instructions hijack the attention heads governing free-form reasoning. This project evaluates 
    whether decoupling inference into an independent injection-detection stage and an isolated boolean phishing assessment 
    can eliminate adversary evasion without imposing an unacceptable false-alarm tax on injected legitimate business correspondence.
    """
)

# --- Key Specifications: Dataset & Models ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📦 Dataset Size & Distribution")
    st.markdown(
        """
        - **Total Stratified Corpus**: **5,223 emails** derived from the verified Nazario phishing archive and Enron legitimate email corpora.
        - **Split Breakdown**:
          - **Train (80%)**: `4,178` emails (indexed into dense vector space with `all-MiniLM-L6-v2` and FAISS).
          - **Validation (10%)**: `523` emails for hyperparameter calibration.
          - **Test Split (10%)**: `522` emails (`128` Phishing, `394` Legitimate Controls).
        - **Adversarial Injections (1,044 test samples)**:
          - `522` **Marked Injections**: Embedded with explicit override delimiters (`[BEGIN EMBEDDED CLASSIFIER MESSAGE]`).
          - `522` **Unmarked Injections**: Naturally blended into realistic email formats (legal confidentiality disclaimers, forward headers, and email signatures).
        """
    )

with col2:
    st.markdown("### 🤖 Evaluated Detection Models")
    st.markdown(
        """
        - **M1: TF-IDF + LogisticRegression Baseline**:
          Classical linear classifier with $V=10,000$ sublinear n-grams. Fast, deterministic, and structurally immune to prompt injections.
        - **M2: Zero-Shot LLM (`qwen2.5:0.5b` & `llama3.2:3b`)**:
          Single-call zero-shot prompt requiring structured JSON output (`verdict`, `confidence`, `reasons`).
        - **M3: RAG Combined Single-Call**:
          Dense FAISS retrieval providing top-$k$ reference exemplars in-context, coupled with free-form reasoning and decision schema in a single call.
        - **M4: RAG Two-Call Decoupled Pipeline**:
          Two strictly independent API calls with zero shared conversational context:
          - *Call 1*: Dedicated prompt injection detector.
          - *Call 2*: Pure boolean phishing classifier with RAG references.
        """
    )

st.divider()

# --- Multi-Page Navigation Links ---
st.subheader("🧭 Explore the Benchmark Pages")
st.markdown("Select a module below or use the sidebar navigation:")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    with st.container(border=True):
        st.markdown("### 🔍 Live Email Tester")
        st.markdown(
            "Test incoming emails in real-time. Compare M1, M2, M3, and M4 side-by-side on custom text or curated preset examples."
        )
        st.page_link("pages/1_Live_Test.py", label="Open Live Test →", icon="🔍", use_container_width=True)

with nav_col2:
    with st.container(border=True):
        st.markdown("### 📊 Benchmark Dashboard")
        st.markdown(
            "Explore full empirical results: metrics matrix, confusion matrices, bootstrap 95% CIs, latency breakdowns, and Holm-Bonferroni McNemar tests."
        )
        st.page_link("pages/2_Dashboard.py", label="Open Dashboard →", icon="📊", use_container_width=True)

with nav_col3:
    with st.container(border=True):
        st.markdown("### 🧪 Prompt Injection Lab")
        st.markdown(
            "Synthesize marked and unmarked adversarial payloads. Inspect how prompt injections manipulate LLM attention vs decoupled architectures."
        )
        st.page_link("pages/3_Injection_Lab.py", label="Open Injection Lab →", icon="🧪", use_container_width=True)

st.divider()

# --- System Environment Status ---
st.subheader("⚡ Local Environment Health")
is_ollama_up, available_models = check_ollama_service()
rag_retriever = get_rag_retriever()

h_col1, h_col2, h_col3 = st.columns(3)

with h_col1:
    if is_ollama_up:
        st.success(f"🟢 **Ollama Daemon**: Connected (`127.0.0.1:11434`)\n\nModels: `{', '.join(available_models) if available_models else 'None'}`")
    else:
        st.warning("🟡 **Ollama Daemon**: Offline or unreachable. Start with `ollama serve`.")

with h_col2:
    if rag_retriever is not None:
        st.success(f"🟢 **FAISS RAG Index**: Loaded (`results/rag_index`)\n\nIndex size: {rag_retriever.index.ntotal} exemplars")
    else:
        st.warning("🟡 **FAISS Index**: Not loaded. Build with `python -m phishbench.rag`.")

with h_col3:
    st.info("ℹ️ **Python Environment**: `Python 3.11`\n\nPackage: `phishbench v0.1.0`")
