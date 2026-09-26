"""Page 2: Comprehensive Benchmark Dashboard for M1-M4 across Clean, Marked, and Unmarked conditions."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is on sys.path
root_dir = Path(__file__).resolve().parents[1]
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import pandas as pd
import streamlit as st
from ui_utils import (
    apply_custom_css,
    load_benchmark_summary,
    load_report_markdown,
)

st.set_page_config(
    page_title="Benchmark Dashboard - IFSI",
    page_icon="📊",
    layout="wide",
)

apply_custom_css()

st.title("📊 Empirical Benchmark & Evaluation Dashboard")
st.markdown("Comparative evaluation of **M1–M4** across **Clean**, **Marked**, and **Unmarked** prompt injections ($N=522$ test emails).")

# Load summary data
summary_data = load_benchmark_summary()
report_text = load_report_markdown()

if not summary_data:
    st.error("Benchmark summary not found at `results/full_benchmark_summary.json`. Run the benchmark suite to generate data.")
    st.stop()

cells = summary_data.get("cells", {})
paired_tests = summary_data.get("paired_tests", {})

# Top KPI Summary Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Test Split Samples", "522 emails", "128 Phish / 394 Control")
with kpi2:
    st.metric("Experimental Conditions", "3 conditions", "Clean, Marked, Unmarked")
with kpi3:
    st.metric("Evaluated Architectures", "4 methods", "M1, M2, M3, M4")
with kpi4:
    st.metric("Hypothesis Tests", "10 Paired Tests", "Holm-Bonferroni FWER α=0.05")

st.divider()

# Tab Navigation
tab_matrix, tab_conf, tab_ci, tab_mcnemar, tab_latency, tab_report = st.tabs([
    "📈 Full Metrics Matrix",
    "🔲 Confusion Matrices",
    "🎯 Bootstrap 95% CIs",
    "⚖️ McNemar & Holm-Bonferroni",
    "⏱️ Latency & Reliability",
    "📄 Full Markdown Report",
])

# Method and condition display names
method_labels = {
    "M1": "M1 (TF-IDF + LogReg)",
    "M2": "M2 (Zero-Shot LLM 0.5b)",
    "M3": "M3 (RAG Combined 0.5b)",
    "M4": "M4 (RAG Decoupled 0.5b)",
}

# --- Tab 1: Full Metrics Matrix ---
with tab_matrix:
    st.subheader("Classification Performance Matrix")

    # Filters
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_methods = st.multiselect(
            "Filter Methods:",
            options=["M1", "M2", "M3", "M4"],
            default=["M1", "M2", "M3", "M4"],
            format_func=lambda x: method_labels[x],
        )
    with f_col2:
        selected_conditions = st.multiselect(
            "Filter Conditions:",
            options=["clean", "marked", "unmarked"],
            default=["clean", "marked", "unmarked"],
            format_func=lambda x: x.capitalize(),
        )

    rows = []
    for m in selected_methods:
        for c in selected_conditions:
            cell_key = f"{m}_{c}"
            if cell_key in cells:
                m_data = cells[cell_key]["metrics"]
                lat = m_data.get("mean_latency_seconds", 0.0)
                lat_str = f"{lat*1000:.2f} ms" if lat < 1.0 else f"{lat:.4f} s"
                rows.append({
                    "Method": method_labels[m],
                    "Condition": c.capitalize(),
                    "Accuracy": f"{m_data['accuracy']*100:.2f}%",
                    "Recall (Attacked Phish)": f"{m_data['recall']*100:.2f}%",
                    "FPR (Injected Control)": f"{m_data['fpr']*100:.2f}%",
                    "Precision": f"{m_data['precision']*100:.2f}%",
                    "F1 Score": f"{m_data['f1']:.4f}",
                    "Invalid Rate": f"{m_data.get('invalid_rate', 0.0)*100:.2f}%",
                    "Mean Latency": lat_str,
                })

    if rows:
        df_matrix = pd.DataFrame(rows)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one method and condition to display metrics.")

    st.markdown(
        """
        > **Key Takeaway**: Classical **M1** maintains stable high performance (FPR 0.25%, Recall ~91-95%) across all conditions. 
        > In contrast, single-call **M3** collapses from 41.59% recall to 21.05% recall under unmarked prompt injection (78.95% evasion). 
        > Two-call decoupled **M4** eliminates evasion (restoring recall to 96.09%), but incurs a 72.08% False Positive Rate on injected legitimate correspondence.
        """
    )


# --- Tab 2: Confusion Matrices ---
with tab_conf:
    st.subheader("Confusion Matrices Breakdown")

    selected_cell = st.selectbox(
        "Select Method & Condition Cell:",
        options=[f"{m}_{c}" for m in ("M1", "M2", "M3", "M4") for c in ("clean", "marked", "unmarked")],
        format_func=lambda x: f"{method_labels[x.split('_')[0]]} — {x.split('_')[1].capitalize()}",
    )

    if selected_cell in cells:
        c_metrics = cells[selected_cell]["metrics"]
        tp = c_metrics["true_positives"]
        fn = c_metrics["false_negatives"]
        tn = c_metrics["true_negatives"]
        fp = c_metrics["false_positives"]
        inv = c_metrics.get("invalid_count", 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("True Positives (TP)", tp, "Phishing correctly caught")
        c2.metric("False Negatives (FN)", fn, "Phishing missed (Evaded)")
        c3.metric("True Negatives (TN)", tn, "Legitimate allowed")
        c4.metric("False Positives (FP)", fp, "Legitimate false alarm")

        st.markdown("#### 2x2 Contingency Table")
        df_cm = pd.DataFrame(
            [[tn, fp], [fn, tp]],
            columns=["Predicted Legitimate (0)", "Predicted Phishing (1)"],
            index=["Actual Legitimate (0)", "Actual Phishing (1)"],
        )
        st.table(df_cm)

        if inv > 0:
            st.warning(f"⚠️ **{inv} calls ({c_metrics.get('invalid_rate', 0)*100:.1f}%)** failed to produce valid JSON and fell back to default classification.")


# --- Tab 3: Bootstrap 95% Confidence Intervals ---
with tab_ci:
    st.subheader("Bootstrap 95% Confidence Intervals (2,000 Resamples, Seed 42)")

    ci_rows = []
    for m in ("M1", "M2", "M3", "M4"):
        for c in ("clean", "marked", "unmarked"):
            k = f"{m}_{c}"
            if k in cells:
                ci = cells[k].get("bootstrap_95_ci", {})
                met = cells[k]["metrics"]
                ci_rows.append({
                    "Method": method_labels[m],
                    "Condition": c.capitalize(),
                    "Recall (95% CI)": f"{met['recall']:.4f} [{ci.get('recall', [0, 0])[0]:.4f}, {ci.get('recall', [0, 0])[1]:.4f}]",
                    "FPR (95% CI)": f"{met['fpr']:.4f} [{ci.get('fpr', [0, 0])[0]:.4f}, {ci.get('fpr', [0, 0])[1]:.4f}]",
                    "F1 Score (95% CI)": f"{met['f1']:.4f} [{ci.get('f1', [0, 0])[0]:.4f}, {ci.get('f1', [0, 0])[1]:.4f}]",
                    "Precision (95% CI)": f"{met['precision']:.4f} [{ci.get('precision', [0, 0])[0]:.4f}, {ci.get('precision', [0, 0])[1]:.4f}]",
                })

    st.dataframe(pd.DataFrame(ci_rows), use_container_width=True, hide_index=True)


# --- Tab 4: McNemar Paired Tests & Holm-Bonferroni Correction ---
with tab_mcnemar:
    st.subheader("Paired McNemar Hypothesis Tests with Holm-Bonferroni Correction")
    st.markdown(
        """
        Exact two-sided binomial tests evaluate discordant classification pairs on matching original email IDs.
        Holm-Bonferroni step-down correction is applied across all $m=10$ paired tests to control Family-Wise Error Rate (FWER) at $\\alpha = 0.05$.
        """
    )

    hb_rows = []
    # Rank sorted tests
    sorted_tests = sorted(paired_tests.items(), key=lambda x: x[1].get("holm_bonferroni_rank", 999))
    for key, p in sorted_tests:
        rank = p.get("holm_bonferroni_rank", "-")
        mult = p.get("holm_bonferroni_factor", "-")
        raw_p = p.get("raw_p_value", p["p_value"])
        hb_p = p.get("holm_bonferroni_p_value", p["p_value"])
        sig = p.get("significant_after_holm_bonferroni", p.get("significant_alpha_0_05", False))

        label_map = {
            "M2_vs_M3__clean": "M2 vs M3 (Clean)",
            "M2_vs_M3__marked": "M2 vs M3 (Marked)",
            "M2_vs_M3__unmarked": "M2 vs M3 (Unmarked)",
            "marked_vs_unmarked__M1": "M1 (Marked vs Unmarked)",
            "marked_vs_unmarked__M2": "M2 (Marked vs Unmarked)",
            "marked_vs_unmarked__M3": "M3 (Marked vs Unmarked)",
            "marked_vs_unmarked__M4": "M4 (Marked vs Unmarked)",
            "combined_vs_decoupled_M3_vs_M4__clean": "M3 vs M4 (Clean)",
            "combined_vs_decoupled_M3_vs_M4__marked": "M3 vs M4 (Marked)",
            "combined_vs_decoupled_M3_vs_M4__unmarked": "M3 vs M4 (Unmarked)",
        }

        hb_rows.append({
            "Rank (k)": rank,
            "Hypothesis Comparison": label_map.get(key, key),
            "Discordant Pairs (b / c)": f"{p['a_correct_b_wrong (b)']} / {p['a_wrong_b_correct (c)']}",
            "Raw p-value": f"{raw_p:.4e}",
            "Multiplier (m-k+1)": mult,
            "Holm-Bonferroni p-value": f"{hb_p:.4e}",
            "Decision (α=0.05)": "Reject H0 (Significant)" if sig else "Fail to Reject (Not Sig.)",
        })

    st.dataframe(pd.DataFrame(hb_rows), use_container_width=True, hide_index=True)


# --- Tab 5: Latency & Operational Reliability ---
with tab_latency:
    st.subheader("Operational Latency & Format Reliability Breakdown")

    lat_rows = []
    for m in ("M1", "M2", "M3", "M4"):
        for c in ("clean", "marked", "unmarked"):
            k = f"{m}_{c}"
            if k in cells:
                m_data = cells[k]["metrics"]
                rt = m_data.get("total_runtime_seconds", 0.0)
                mean_lat = m_data.get("mean_latency_seconds", 0.0)
                tp = (m_data["total_samples"] / rt) if rt > 0 else 0.0
                lat_rows.append({
                    "Method": method_labels[m],
                    "Condition": c.capitalize(),
                    "Total Emails": m_data["total_samples"],
                    "Valid Output Rate": f"{(1 - m_data.get('invalid_rate', 0.0))*100:.2f}%",
                    "Invalid Count": m_data.get("invalid_count", 0),
                    "Invalid Rate": f"{m_data.get('invalid_rate', 0.0)*100:.2f}%",
                    "Total Batch Runtime": f"{rt:.2f} s",
                    "Mean Latency (per email)": f"{mean_lat*1000:.2f} ms" if mean_lat < 1.0 else f"{mean_lat:.4f} s",
                    "Throughput": f"{tp:.1f} emails/s",
                })

    st.dataframe(pd.DataFrame(lat_rows), use_container_width=True, hide_index=True)


# --- Tab 6: Full Markdown Report ---
with tab_report:
    st.subheader("Full Benchmark Report (`results/report.md`)")

    st.download_button(
        "📥 Download Full Report (report.md)",
        data=report_text,
        file_name="report.md",
        mime="text/markdown",
    )

    st.markdown(report_text)
