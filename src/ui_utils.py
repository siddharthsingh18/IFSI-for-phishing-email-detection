"""Shared functions and UI helpers for the Streamlit multi-page application.

Inference logic, model loading, and dataset utilities are imported from `core` (the source of truth).
"""

from __future__ import annotations

from core import (
    apply_unmarked_injection,
    check_ollama_service,
    classify_all_methods,
    classify_email_m1,
    classify_email_m2,
    classify_email_m3,
    classify_email_m4,
    evaluate_method_disagreements,
    get_m1_model,
    get_rag_retriever,
    get_random_unmarked_injection,
    get_worst_mistakes,
    load_attack_family_examples,
    load_benchmark_summary,
    load_email_text_lookup,
    load_pilot_summary,
    load_preset_samples,
    load_report_markdown,
    load_unmarked_injection_templates,
    synthesize_injection,
)
from core.inference import _call_ollama_json


def apply_custom_css() -> None:
    """Inject subtle, modern styling for badges, cards, and code snippets."""
    try:
        import streamlit as st
        st.markdown(
            """
            <style>
            .phish-badge-danger {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            display: inline-block;
            border: 1px solid #f87171;
        }
        .phish-badge-safe {
            background-color: #dcfce7;
            color: #166534;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            display: inline-block;
            border: 1px solid #4ade80;
        }
        .phish-badge-warning {
            background-color: #fef3c7;
            color: #92400e;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            display: inline-block;
            border: 1px solid #fcd34d;
        }
        .card-container {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            background-color: #ffffff;
        }
        .stat-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .stat-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #0f172a;
        }
        .stat-label {
            font-size: 0.82rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .card-consensus {
            border: 1.5px solid #cbd5e1;
            border-radius: 12px;
            padding: 16px;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .card-disagreement-warning {
            border: 2.5px solid #f59e0b !important;
            border-radius: 12px;
            padding: 16px;
            background-color: #fffbeb !important;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.35);
            margin-bottom: 12px;
        }
        .card-disagreement-danger {
            border: 2.5px solid #ef4444 !important;
            border-radius: 12px;
            padding: 16px;
            background-color: #fef2f2 !important;
            box-shadow: 0 0 14px rgba(239, 68, 68, 0.35);
            margin-bottom: 12px;
        }
        .badge-disagree-danger {
            background-color: #fee2e2;
            color: #b91c1c;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            border: 1px solid #ef4444;
            display: inline-block;
            margin-bottom: 8px;
        }
        .badge-disagree-warning {
            background-color: #fef3c7;
            color: #b45309;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            border: 1px solid #f59e0b;
            display: inline-block;
            margin-bottom: 8px;
        }
        .badge-agree {
            background-color: #ecfdf5;
            color: #047857;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.76rem;
            font-weight: 700;
            border: 1px solid #10b981;
            display: inline-block;
            margin-bottom: 8px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
    except ImportError:
        pass


__all__ = [
    "apply_custom_css",
    "load_benchmark_summary",
    "load_report_markdown",
    "load_pilot_summary",
    "load_email_text_lookup",
    "get_worst_mistakes",
    "load_preset_samples",
    "get_m1_model",
    "get_rag_retriever",
    "check_ollama_service",
    "classify_email_m1",
    "_call_ollama_json",
    "classify_email_m2",
    "classify_email_m3",
    "classify_email_m4",
    "classify_all_methods",
    "evaluate_method_disagreements",
    "load_unmarked_injection_templates",
    "get_random_unmarked_injection",
    "apply_unmarked_injection",
    "synthesize_injection",
    "load_attack_family_examples",
]
