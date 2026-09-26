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
    get_worst_mistakes,
    load_benchmark_summary,
    load_email_text_lookup,
    load_pilot_summary,
    load_report_markdown,
)

st.set_page_config(
    page_title="Benchmark Dashboard - IFSI",
    page_icon="📊",
    layout="wide",
)

apply_custom_css()

st.title("📊 Empirical Benchmark & Evaluation Dashboard")
st.markdown(
    "Comparative evaluation of **M1–M4** across **Clean**, **Marked**, and **Unmarked** prompt injections "
    "($N=522$ test split, 50-email comparative pilot)."
)

# Load data
summary_data = load_benchmark_summary()
pilot_data = load_pilot_summary()
report_text = load_report_markdown()

if not summary_data:
    st.error("Benchmark summary not found at `results/full_benchmark_summary.json`. Run the benchmark suite to generate data.")
    st.stop()

cells = summary_data.get("cells", {})
paired_tests = summary_data.get("paired_tests", {})
pilot_methods = pilot_data.get("methods", {})

method_labels = {
    "M1": "M1 (TF-IDF + LogReg)",
    "M2": "M2 (Zero-Shot LLM)",
    "M3": "M3 (RAG Combined)",
    "M4": "M4 (RAG Decoupled)",
}

# =========================================================================
# Sidebar Filters (Live Reactive Updates)
# =========================================================================
st.sidebar.header("🔍 Global Dashboard Filters")

selected_methods = st.sidebar.multiselect(
    "Filter Architectures:",
    options=["M1", "M2", "M3", "M4"],
    default=["M1", "M2", "M3", "M4"],
    format_func=lambda x: method_labels.get(x, x),
    help="Select which detection architectures to include in the metrics, charts, and mistake analysis.",
)

selected_conditions = st.sidebar.multiselect(
    "Filter Attack Conditions:",
    options=["clean", "marked", "unmarked"],
    default=["clean", "marked", "unmarked"],
    format_func=lambda x: x.capitalize(),
    help="Select email conditions: Clean (no injection), Marked (bracketed override), Unmarked (natural blending).",
)

model_filter = st.sidebar.selectbox(
    "Filter Model / Benchmark:",
    options=["All Models", "qwen2.5:0.5b (Full Benchmark)", "llama3.2:3b (Pilot 50)"],
    index=0,
    help="Filter by model family: 0.5b full benchmark (N=522) or 3b comparative pilot (N=50).",
)

st.sidebar.divider()
st.sidebar.caption(
    f"Active Filters: **{len(selected_methods)}** methods | "
    f"**{len(selected_conditions)}** conditions | **{model_filter.split(' ')[0]}**"
)

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
tab_matrix, tab_mistakes, tab_conf, tab_ci, tab_mcnemar, tab_latency, tab_report = st.tabs([
    "📈 Full Metrics Matrix & Charts",
    "🚨 Worst Mistakes (Top 10)",
    "🔲 Confusion Matrices",
    "🎯 Bootstrap 95% CIs",
    "⚖️ McNemar & Holm-Bonferroni",
    "⏱️ Latency & Reliability",
    "📄 Full Markdown Report",
])


# =========================================================================
# Tab 1: Full Metrics Matrix & Live Charts
# =========================================================================
with tab_matrix:
    st.subheader("Classification Performance Matrix (Live Filtered)")

    rows: list[dict[str, Any]] = []
    chart_rows: list[dict[str, Any]] = []

    # 1. Full Benchmark rows (qwen2.5:0.5b and M1)
    if model_filter in ("All Models", "qwen2.5:0.5b (Full Benchmark)"):
        for m in selected_methods:
            for c in selected_conditions:
                cell_key = f"{m}_{c}"
                if cell_key in cells:
                    m_data = cells[cell_key]["metrics"]
                    lat = m_data.get("mean_latency_seconds", 0.0)
                    lat_str = f"{lat*1000:.2f} ms" if lat < 1.0 else f"{lat:.4f} s"
                    model_tag = "TF-IDF" if m == "M1" else "qwen2.5:0.5b"

                    rows.append({
                        "Method": method_labels[m],
                        "Model": model_tag,
                        "Condition": c.capitalize(),
                        "Accuracy": f"{m_data['accuracy']*100:.2f}%",
                        "Recall (Catch)": f"{m_data['recall']*100:.2f}%",
                        "FPR (Alarm)": f"{m_data['fpr']*100:.2f}%",
                        "Precision": f"{m_data['precision']*100:.2f}%",
                        "F1 Score": f"{m_data['f1']:.4f}",
                        "Invalid Rate": f"{m_data.get('invalid_rate', 0.0)*100:.2f}%",
                        "Mean Latency": lat_str,
                    })

                    chart_rows.append({
                        "Method & Condition": f"{m} ({c.capitalize()}) - {model_tag}",
                        "Recall (%)": round(m_data["recall"] * 100, 2),
                        "FPR (%)": round(m_data["fpr"] * 100, 2),
                        "Accuracy (%)": round(m_data["accuracy"] * 100, 2),
                        "F1 Score (x100)": round(m_data["f1"] * 100, 2),
                        "Latency (ms)": round(lat * 1000, 2),
                    })

    # 2. Pilot Benchmark rows (llama3.2:3b)
    if model_filter in ("All Models", "llama3.2:3b (Pilot 50)"):
        for m in selected_methods:
            if m in pilot_methods and "unmarked" in [cond.lower() for cond in selected_conditions]:
                p_data = pilot_methods[m]["metrics"]
                tot = p_data.get("total_samples", 50)
                lat = (p_data.get("runtime_seconds", 0.0) / tot) if tot > 0 else 0.0
                lat_str = f"{lat*1000:.2f} ms" if lat < 1.0 else f"{lat:.4f} s"

                rows.append({
                    "Method": method_labels[m],
                    "Model": "llama3.2:3b",
                    "Condition": "Unmarked",
                    "Accuracy": f"{p_data['accuracy']*100:.2f}%",
                    "Recall (Catch)": f"{p_data['recall']*100:.2f}%",
                    "FPR (Alarm)": f"{p_data['fpr']*100:.2f}%",
                    "Precision": f"{p_data['precision']*100:.2f}%",
                    "F1 Score": f"{p_data['f1']:.4f}",
                    "Invalid Rate": f"{p_data.get('invalid_rate', 0.0)*100:.2f}%",
                    "Mean Latency": lat_str,
                })

                chart_rows.append({
                    "Method & Condition": f"{m} (Unmarked) - llama3.2:3b",
                    "Recall (%)": round(p_data["recall"] * 100, 2),
                    "FPR (%)": round(p_data["fpr"] * 100, 2),
                    "Accuracy (%)": round(p_data["accuracy"] * 100, 2),
                    "F1 Score (x100)": round(p_data["f1"] * 100, 2),
                    "Latency (ms)": round(lat * 1000, 2),
                })

    if rows:
        df_matrix = pd.DataFrame(rows)
        st.dataframe(df_matrix, use_container_width=True, hide_index=True)
    else:
        st.info("No matching benchmark results found for the selected filters.")

    # Live Charts Section
    if chart_rows:
        st.markdown("#### 📊 Live Comparative Charts")
        df_chart = pd.DataFrame(chart_rows)

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            st.markdown("**🛡️ Phishing Catch Rate (Recall) vs. False Positive Rate (FPR)**")
            st.caption("Catch Rate (higher is better) vs. False Alarm Rate on control emails (lower is better)")
            df_rf = df_chart.set_index("Method & Condition")[["Recall (%)", "FPR (%)"]]
            st.bar_chart(df_rf, height=320)

        with c_chart2:
            st.markdown("**🎯 F1 Score & Accuracy Comparison**")
            st.caption("Harmonic balance (F1 Score x100) and overall classification accuracy across conditions")
            df_acc = df_chart.set_index("Method & Condition")[["Accuracy (%)", "F1 Score (x100)"]]
            st.bar_chart(df_acc, height=320)

        st.markdown("**⏱️ Inference Latency Comparison (per Email)**")
        st.caption("Operational response time in milliseconds per email")
        df_lat = df_chart.set_index("Method & Condition")[["Latency (ms)"]]
        st.bar_chart(df_lat, height=240)

    st.markdown(
        """
        > **Key Empirical Takeaways**:
        > 1. **M1 (TF-IDF Baseline)**: Demonstrates total immunity to prompt injections (Recall ~91-95%, FPR 0.25%) because vocabulary frequency distributions ignore prompt instructions.
        > 2. **M3 (RAG Combined)**: Suffers severe adversarial collapse under unmarked injection (recall drops to 21.05%, representing **78.95% evasion**).
        > 3. **M4 (RAG Decoupled)**: Successfully eliminates evasion (restoring recall to 96.09%), but incurs a **72.08% False Positive Rate** on legitimate correspondence containing security/disclaimer notices (False Alarm Tax).
        """
    )


# =========================================================================
# Tab 2: Worst Mistakes (Top 10 Highest-Confidence Errors per Method)
# =========================================================================
with tab_mistakes:
    st.subheader("🚨 Worst Classification Mistakes (Top 10 Highest-Confidence Errors per Method)")
    st.markdown(
        """
        Loaded directly from the saved benchmark prediction files (`results/*_predictions.jsonl`).
        These records represent the **10 highest-confidence erroneous predictions per method** (where `predicted_label != true_label`),
        highlighting severe failures where architectures were maximally confident yet completely wrong.
        Email snippets are truncated to 200 characters.
        """
    )

    worst_mistakes = get_worst_mistakes(
        methods=tuple(selected_methods),
        conditions=tuple(selected_conditions),
        model_choice=model_filter,
        top_n_per_method=10,
    )

    if not worst_mistakes:
        st.info("No wrong predictions found matching current filter criteria.")
    else:
        # Mistake method breakdown selector
        m_counts: dict[str, int] = {}
        for item in worst_mistakes:
            m_counts[item["method"]] = m_counts.get(item["method"], 0) + 1

        col_m_view, col_stat_m = st.columns([3, 1])
        with col_m_view:
            avail_methods = ["All Filtered Methods"] + sorted(list(m_counts.keys()))
            selected_mistake_method = st.selectbox(
                "Filter Mistakes by Method:",
                options=avail_methods,
                index=0,
                format_func=lambda x: f"{x} ({m_counts[x]} errors)" if x in m_counts else x,
            )
        with col_stat_m:
            st.metric("Total Worst Mistakes Shown", len(worst_mistakes), f"Top 10 per method")

        # Filter display records
        if selected_mistake_method != "All Filtered Methods":
            display_records = [r for r in worst_mistakes if r["method"] == selected_mistake_method]
        else:
            display_records = worst_mistakes

        df_mistakes = pd.DataFrame(display_records)
        df_display = df_mistakes.copy()
        df_display["confidence"] = df_display["confidence"].apply(lambda c: f"{c*100:.2f}%")

        # Reorder and rename columns
        df_table = df_display[[
            "method", "condition", "model", "true_label", "predicted_label", "confidence", "snippet"
        ]].rename(columns={
            "method": "Method",
            "condition": "Condition",
            "model": "Model",
            "true_label": "True Label",
            "predicted_label": "Predicted Label",
            "confidence": "Confidence",
            "snippet": "Email Snippet (<=200 chars)",
        })

        st.dataframe(df_table, use_container_width=True, hide_index=True)

        # Deep-Dive Inspector Expander
        with st.expander("🔍 Deep-Dive: Inspect Full Unabbreviated Email Text for any Mistake", expanded=False):
            mistake_labels = [
                f"#{idx+1} [{row['method']} | {row['condition']}] True: {row['true_label']} ➔ Pred: {row['predicted_label']} (Conf: {row['confidence']:.2f}) - {row['id']}"
                for idx, row in enumerate(display_records)
            ]
            chosen_idx = st.selectbox(
                "Select Mistake to Inspect:",
                options=range(len(mistake_labels)),
                format_func=lambda i: mistake_labels[i],
            )
            if chosen_idx is not None and chosen_idx < len(display_records):
                chosen_row = display_records[chosen_idx]
                lookup = load_email_text_lookup()
                raw_full_text = lookup.get(chosen_row["id"]) or lookup.get(chosen_row["id"].split("-")[1] if "-" in chosen_row["id"] else "", "No text available")

                st.markdown(
                    f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; margin-bottom:10px;">
                        <b>Email ID:</b> <code>{chosen_row['id']}</code> | <b>Method:</b> {chosen_row['method']} | <b>Model:</b> {chosen_row['model']} | <b>Condition:</b> {chosen_row['condition']}<br>
                        <b>True Label:</b> <span class="phish-badge-safe" style="padding:2px 8px; font-size:0.75rem;">{chosen_row['true_label']}</span> ➔ 
                        <b>Predicted Label:</b> <span class="phish-badge-danger" style="padding:2px 8px; font-size:0.75rem;">{chosen_row['predicted_label']}</span> | 
                        <b>Confidence:</b> <b>{chosen_row['confidence']*100:.2f}%</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area("Full Unabbreviated Email Body:", value=raw_full_text, height=220, disabled=True)


# =========================================================================
# Tab 3: Confusion Matrices
# =========================================================================
with tab_conf:
    st.subheader("Confusion Matrices Breakdown")

    available_cells = [
        f"{m}_{c}" for m in selected_methods for c in selected_conditions if f"{m}_{c}" in cells
    ]

    if not available_cells:
        st.info("No matching cells for current filter selection.")
    else:
        selected_cell = st.selectbox(
            "Select Method & Condition Cell:",
            options=available_cells,
            format_func=lambda x: f"{method_labels.get(x.split('_')[0], x.split('_')[0])} — {x.split('_')[1].capitalize()}",
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
                st.warning(f"⚠️ **{inv} calls ({c_metrics.get('invalid_rate', 0)*100:.1f}%)** failed to produce valid JSON.")


# =========================================================================
# Tab 4: Bootstrap 95% Confidence Intervals
# =========================================================================
with tab_ci:
    st.subheader("Bootstrap 95% Confidence Intervals (2,000 Resamples, Seed 42)")

    ci_rows: list[dict[str, Any]] = []
    for m in selected_methods:
        for c in selected_conditions:
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

    if ci_rows:
        st.dataframe(pd.DataFrame(ci_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No matching bootstrap intervals found for current filters.")


# =========================================================================
# Tab 5: McNemar Paired Tests & Holm-Bonferroni Correction
# =========================================================================
with tab_mcnemar:
    st.subheader("Paired McNemar Hypothesis Tests with Holm-Bonferroni Correction")
    st.markdown(
        """
        Exact two-sided binomial tests evaluate discordant classification pairs on matching original email IDs.
        Holm-Bonferroni step-down correction is applied across all $m=10$ paired tests to control Family-Wise Error Rate (FWER) at $\\alpha = 0.05$.
        """
    )

    hb_rows: list[dict[str, Any]] = []
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


# =========================================================================
# Tab 6: Latency & Operational Reliability
# =========================================================================
with tab_latency:
    st.subheader("Operational Latency & Format Reliability Breakdown")

    lat_rows: list[dict[str, Any]] = []
    for m in selected_methods:
        for c in selected_conditions:
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

    if lat_rows:
        st.dataframe(pd.DataFrame(lat_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No matching latency records found for current filters.")


# =========================================================================
# Tab 7: Full Markdown Report
# =========================================================================
with tab_report:
    st.subheader("Full Benchmark Report (`results/report.md`)")

    st.download_button(
        "📥 Download Full Report (report.md)",
        data=report_text,
        file_name="report.md",
        mime="text/markdown",
    )

    st.markdown(report_text)
