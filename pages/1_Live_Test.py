"""Page 1: Live Multi-Method Email Classification Tester across M1-M4."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

# Ensure src is on sys.path
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import streamlit as st
from ui_utils import (
    apply_custom_css,
    apply_unmarked_injection,
    check_ollama_service,
    classify_all_methods,
    classify_email_m1,
    classify_email_m2,
    classify_email_m3,
    classify_email_m4,
    evaluate_method_disagreements,
    get_random_unmarked_injection,
    load_preset_samples,
    load_unmarked_injection_templates,
)

st.set_page_config(
    page_title="Live Email Test - IFSI",
    page_icon="🔍",
    layout="wide",
)

apply_custom_css()

st.title("🔍 Live Email Classification Tester")
st.markdown(
    "Evaluate single emails or run **ALL methods (M1–M4) simultaneously** side-by-side. "
    "Test resilience against authentic unmarked prompt injection templates and observe real-time model disagreements."
)

# Check Ollama service status
is_ollama_up, available_models = check_ollama_service()
default_model = "qwen2.5:0.5b" if "qwen2.5:0.5b" in available_models else (available_models[0] if available_models else "qwen2.5:0.5b")

# =========================================================================
# Sidebar Controls
# =========================================================================
st.sidebar.header("⚙️ Evaluation Settings")

model_choice = st.sidebar.selectbox(
    "Select LLM Model",
    options=available_models if available_models else ["qwen2.5:0.5b", "llama3.2:3b"],
    index=0 if not available_models or default_model not in available_models else available_models.index(default_model),
    help="Local Ollama model used for M2 (Zero-Shot), M3 (RAG Combined), and M4 (RAG Decoupled).",
)

method_choice = st.sidebar.selectbox(
    "Execution Mode",
    options=[
        "Compare All Methods (Side-by-Side)",
        "M1: TF-IDF + LogisticRegression Baseline",
        "M2: Zero-Shot LLM",
        "M3: RAG Combined Single-Call",
        "M4: RAG Two-Call Decoupled",
    ],
    index=0,
    help="Choose whether to evaluate all four architectures simultaneously or run an individual method.",
)

top_k = st.sidebar.slider(
    "RAG Retrieval k Neighbors",
    min_value=1,
    max_value=5,
    value=3,
    help="Number of nearest exemplar emails retrieved from FAISS index for M3 and M4.",
)

st.sidebar.divider()
st.sidebar.markdown(
    """
    **Architecture Legend**:
    - **M1**: Word n-gram linear baseline (immune to prompt injection).
    - **M2**: Zero-shot LLM with structured JSON verdict schema.
    - **M3**: In-context RAG exemplars + free-form reasoning (vulnerable to injection).
    - **M4**: Decoupled two-call pipeline (Injection Detector + Boolean Phish).
    """
)

# =========================================================================
# Preset Selector & Input Fields
# =========================================================================
presets = load_preset_samples()
preset_options = ["-- Custom Email Input --"] + list(presets.keys())

col_sel, col_stat = st.columns([3, 1])
with col_sel:
    selected_preset = st.selectbox(
        "Load Preset Sample Email:",
        options=preset_options,
        index=1,
        help="Select a benchmark sample to test clean vs attacked emails.",
    )
with col_stat:
    if is_ollama_up:
        st.success(f"🟢 Ollama Online ({len(available_models)} models)")
    else:
        st.warning("⚠️ Ollama Offline (M1 active)")

if selected_preset != "-- Custom Email Input --":
    preset_data = presets[selected_preset]
    initial_subject = preset_data["subject"]
    initial_sender = preset_data["sender"]
    initial_body = preset_data["body"]
    st.info(f"Loaded **{selected_preset}** (True Label: `{preset_data['label'].upper()}`, Condition: `{preset_data['condition']}`)")
else:
    initial_subject = ""
    initial_sender = ""
    initial_body = ""

col_sub, col_sender = st.columns([2, 1])
with col_sub:
    subject_input = st.text_input("Email Subject:", value=initial_subject, placeholder="e.g. Action Required: Account Notice")
with col_sender:
    sender_input = st.text_input("Sender / From:", value=initial_sender, placeholder="e.g. alert@banking-service.com")

body_input = st.text_area(
    "Email Body Text:",
    value=initial_body,
    height=200,
    placeholder="Paste raw email body text here...",
)

# =========================================================================
# Adversarial Prompt Injection Testbed (Auto-Inject Toggle)
# =========================================================================
st.markdown("### 🧪 Adversarial Prompt Injection Testbed")
col_tog, col_btn = st.columns([3, 1])

with col_tog:
    auto_inject = st.toggle(
        "Auto-inject random unmarked injection template from data/injections",
        value=st.session_state.get("auto_inject_enabled", False),
        key="auto_inject_toggle",
        help="Embeds an authentic unmarked injection template from data/injections into the email body before classifying, testing live if methods get fooled.",
    )
    st.session_state["auto_inject_enabled"] = auto_inject

if auto_inject:
    if "current_unmarked_template" not in st.session_state:
        st.session_state["current_unmarked_template"] = get_random_unmarked_injection()

    with col_btn:
        if st.button("🎲 Roll New Template", use_container_width=True, help="Draw another random unmarked injection from data/injections"):
            st.session_state["current_unmarked_template"] = get_random_unmarked_injection()
            st.rerun()

    active_template = st.session_state["current_unmarked_template"]
    family = active_template.get("attack_family", "unknown").replace("_", " ").title()
    style = active_template.get("injection_style", "unknown").replace("_", " ").title()
    position = active_template.get("attack_position", "body_start").replace("_", " ").title()

    st.markdown(
        f"""
        <div style="background:#fffbeb; border:1.5px solid #fcd34d; border-radius:10px; padding:12px 16px; margin-bottom:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-weight:700; color:#92400e; font-size:0.92rem;">
                    🎯 Active Unmarked Injection: <code style="background:#fef3c7; color:#78350f;">{style}</code> ({family})
                </span>
                <span class="badge-disagree-warning">Position: {position}</span>
            </div>
            <div style="font-size:0.83rem; color:#78350f; margin-bottom:8px;">
                This authentic template from <code>data/injections/</code> will be blended into the email body before running classification to see whether each method is fooled.
            </div>
            <pre style="background:#ffffff; border:1px solid #fef3c7; border-radius:6px; padding:10px; font-size:0.78rem; color:#1e293b; white-space:pre-wrap; margin:0;">{active_template.get('injected_text')}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )
    classified_body = apply_unmarked_injection(body_input, active_template)
    with st.expander("👀 View Injected Email Body (What Classifiers Will Receive)", expanded=False):
        st.text_area("Injected Body Preview:", value=classified_body, height=130, disabled=True)
else:
    classified_body = body_input

email_full_text = f"Subject: {subject_input}\nFrom: {sender_input}\n\n{classified_body}".strip()

# =========================================================================
# Result Card Renderer
# =========================================================================
def display_verdict_card(
    result: dict[str, Any],
    title: str,
    method_key: str,
    eval_summary: dict[str, Any] | None = None,
) -> None:
    """Render a clean result card showing verdict, confidence, has_prompt_injection, and latency,
    highlighting disagreements in contrasting colors."""
    is_phish = result.get("is_phishing", False)
    conf = float(result.get("confidence", 0.0))
    lat = float(result.get("latency_ms", 0.0))
    is_valid = result.get("is_valid", True)
    has_injection = bool(result.get("has_prompt_injection", False))
    inj_display = str(result.get("has_prompt_injection_display", "No (N/A)"))

    # Styling resolution from disagreement evaluation
    style_info = eval_summary["method_styles"].get(method_key, {}) if eval_summary else {}
    card_class = style_info.get("card_class", "card-consensus")
    badge_html = style_info.get("badge_html", "")
    note_text = style_info.get("note", "")

    # Verdict badge & progress bar
    if is_phish:
        verdict_badge = '<span class="phish-badge-danger">🚨 PHISHING</span>'
        progress_color = "#ef4444"
    else:
        verdict_badge = '<span class="phish-badge-safe">✅ LEGITIMATE</span>'
        progress_color = "#10b981"

    # Injection status styling
    if has_injection:
        inj_color = "#b91c1c"
    elif "No" in inj_display or "CLEAN" in inj_display:
        inj_color = "#166534"
    else:
        inj_color = "#475569"

    lat_display = f"{lat:.1f} ms" if lat < 1000 else f"{lat/1000:.2f} s"

    note_html = ""
    if note_text and eval_summary and eval_summary.get("has_disagreement"):
        note_html = f"""
        <div style="margin-top:10px; padding:6px 8px; border-radius:6px; background:rgba(0,0,0,0.03); font-size:0.78rem; color:#475569;">
            💡 {note_text}
        </div>
        """

    card_html = f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
            <span style="font-weight:700; font-size:1.02rem; color:#0f172a;">{title}</span>
            {badge_html}
        </div>
        
        <div style="margin-bottom:10px;">
            <span style="font-size:0.72rem; text-transform:uppercase; color:#64748b; font-weight:700; display:block; margin-bottom:4px;">Verdict</span>
            {verdict_badge}
        </div>

        <div style="background:rgba(255,255,255,0.85); border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px; margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; font-size:0.80rem; margin-bottom:4px;">
                <span style="color:#64748b; font-weight:600;">Confidence:</span>
                <span style="font-weight:700; color:#0f172a;">{conf * 100:.1f}%</span>
            </div>
            <div style="width:100%; background:#e2e8f0; height:6px; border-radius:3px; overflow:hidden;">
                <div style="width:{min(100.0, max(0.0, conf * 100)):.1f}%; background:{progress_color}; height:6px;"></div>
            </div>
        </div>

        <div style="background:rgba(255,255,255,0.85); border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px; margin-bottom:8px;">
            <span style="font-size:0.72rem; text-transform:uppercase; color:#64748b; font-weight:700; display:block; margin-bottom:2px;">Prompt Injection:</span>
            <span style="font-weight:700; font-size:0.84rem; color:{inj_color};">{inj_display}</span>
        </div>

        <div style="background:rgba(255,255,255,0.85); border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px;">
            <span style="font-size:0.72rem; text-transform:uppercase; color:#64748b; font-weight:700; display:block; margin-bottom:2px;">Latency:</span>
            <span style="font-weight:700; font-size:0.92rem; color:#0f172a;">{lat_display}</span>
        </div>

        {note_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    if not is_valid:
        st.warning("⚠️ Model output did not strictly conform to target JSON schema.")

    with st.expander("🔍 Evidence & Breakdown", expanded=False):
        st.markdown("**Reasons / Model Evidence:**")
        for r in result.get("reasons", []):
            st.markdown(f"- {r}")

        # Decoupled breakdown
        if "is_phishing_only" in result:
            st.markdown("---")
            st.markdown("**Decoupled Two-Call Breakdown:**")
            st.markdown(f"- **Call 1 (Injection Detector):** `{'DETECTED 🚨' if result.get('has_injection') else 'CLEAN ✅'}`")
            st.markdown(f"- **Call 2 (Boolean Classifier):** `{'PHISHING 🚨' if result.get('is_phishing_only') else 'LEGITIMATE ✅'}`")

        # Retrieved RAG exemplars
        if result.get("retrieved_samples"):
            st.markdown("---")
            st.markdown(f"**Retrieved FAISS Exemplars ({len(result['retrieved_samples'])}):**")
            for idx, sample in enumerate(result["retrieved_samples"], 1):
                sim = sample.get("similarity", 0.0)
                lbl = "Phishing" if sample.get("label") == 1 else "Legitimate"
                st.caption(f"**#{idx} [{lbl}]** (Sim: `{sim:.3f}`): {sample.get('text', '')[:160]}...")

        with st.expander("Raw Output", expanded=False):
            st.code(result.get("raw_response") or result.get("raw_response_call2") or "No raw response text")


# =========================================================================
# Action Button & Execution
# =========================================================================
if method_choice == "Compare All Methods (Side-by-Side)":
    btn_label = "⚡ Run ALL Methods (M1–M4) on Injected Email" if auto_inject else "⚡ Run ALL Methods (M1–M4) on Email"
else:
    btn_label = f"🚀 Run {method_choice.split(':')[0]} on Email"

btn_run = st.button(btn_label, type="primary", use_container_width=True)

if btn_run:
    if not email_full_text or not body_input.strip():
        st.warning("Please provide email body text before running classification.")
    else:
        st.divider()
        st.subheader("📋 Classification Results (Side-by-Side Comparison)")

        if method_choice == "Compare All Methods (Side-by-Side)":
            with st.spinner(f"Evaluating email across M1, M2, M3, and M4 using {model_choice}..."):
                all_results = classify_all_methods(email_full_text, model=model_choice, top_k=top_k)

            # Evaluate agreement vs disagreement
            eval_summary = evaluate_method_disagreements(all_results)

            # Prominent Disagreement or Consensus Alert Banner
            if eval_summary["has_disagreement"]:
                st.markdown(
                    f"""
                    <div style="background:#fffbeb; border:2px solid #f59e0b; border-radius:10px; padding:14px 18px; margin-bottom:16px;">
                        <h4 style="margin:0 0 6px 0; color:#b45309; font-weight:700;">{eval_summary['summary_title']}</h4>
                        <p style="margin:0; font-size:0.92rem; color:#78350f;">{eval_summary['summary_detail']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background:#ecfdf5; border:2px solid #10b981; border-radius:10px; padding:14px 18px; margin-bottom:16px;">
                        <h4 style="margin:0 0 6px 0; color:#047857; font-weight:700;">{eval_summary['summary_title']}</h4>
                        <p style="margin:0; font-size:0.92rem; color:#065f46;">{eval_summary['summary_detail']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Four Side-by-Side Columns
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)

            with col_m1:
                display_verdict_card(all_results["M1"], "M1 (TF-IDF + LogReg)", "M1", eval_summary)
            with col_m2:
                display_verdict_card(all_results["M2"], f"M2 (Zero-Shot {model_choice})", "M2", eval_summary)
            with col_m3:
                display_verdict_card(all_results["M3"], f"M3 (RAG Combined k={top_k})", "M3", eval_summary)
            with col_m4:
                display_verdict_card(all_results["M4"], f"M4 (Decoupled k={top_k})", "M4", eval_summary)

            # Architectural Security Takeaway
            st.markdown("### 💡 Architectural Security Takeaway")
            m1_phish = all_results["M1"]["is_phishing"]
            m2_phish = all_results["M2"]["is_phishing"]
            m3_phish = all_results["M3"]["is_phishing"]
            m4_phish = all_results["M4"]["is_phishing"]

            if m1_phish and not m3_phish:
                st.error(
                    "⚠️ **Adversarial Evasion Confirmed in M3!** Classical baseline M1 flagged the email as phishing, "
                    "but RAG Combined (M3) was deceived into marking it legitimate by following the prompt injection payload."
                )
            if m1_phish and m4_phish and not m3_phish:
                st.success(
                    "🛡️ **Decoupled Architecture (M4) Successfully Blocked the Evasion!** While single-call M3 collapsed, "
                    "the decoupled pipeline correctly flagged the injection in Call 1, maintaining the overall Phishing verdict."
                )
            if not m1_phish and not m3_phish and m4_phish and all_results["M4"].get("has_prompt_injection"):
                st.warning(
                    "🚨 **False Alarm Tax in M4!** On legitimate correspondence containing defense/security language, "
                    "M4's Call 1 triggered an injection alert, converting a clean message into a false alarm."
                )

        elif "M1" in method_choice:
            with st.spinner("Running M1 TF-IDF + LogisticRegression..."):
                res = classify_email_m1(email_full_text)
            display_verdict_card(res, "M1: TF-IDF + LogisticRegression", "M1")

        elif "M2" in method_choice:
            with st.spinner(f"Running M2 Zero-Shot LLM ({model_choice})..."):
                res = classify_email_m2(email_full_text, model=model_choice)
            display_verdict_card(res, f"M2: Zero-Shot LLM ({model_choice})", "M2")

        elif "M3" in method_choice:
            with st.spinner(f"Running M3 RAG Combined Single-Call (k={top_k}, {model_choice})..."):
                res = classify_email_m3(email_full_text, model=model_choice, top_k=top_k)
            display_verdict_card(res, f"M3: RAG Combined (k={top_k}, {model_choice})", "M3")

        elif "M4" in method_choice:
            with st.spinner(f"Running M4 RAG Two-Call Decoupled ({model_choice})..."):
                res = classify_email_m4(email_full_text, model=model_choice, top_k=top_k)
            display_verdict_card(res, f"M4: RAG Two-Call Decoupled ({model_choice})", "M4")
