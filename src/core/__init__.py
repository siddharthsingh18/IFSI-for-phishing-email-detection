"""Core package providing inference, model loading, and dataset loaders with zero Streamlit dependencies."""

from .data_loaders import (
    get_worst_mistakes,
    load_benchmark_summary,
    load_email_text_lookup,
    load_pilot_summary,
    load_preset_samples,
    load_report_markdown,
)
from .inference import (
    classify_all_methods,
    classify_email_m1,
    classify_email_m2,
    classify_email_m3,
    classify_email_m4,
    evaluate_method_disagreements,
)
from .injections import (
    apply_unmarked_injection,
    get_random_unmarked_injection,
    load_attack_family_examples,
    load_unmarked_injection_templates,
    synthesize_injection,
)
from .models import (
    check_ollama_service,
    get_m1_model,
    get_rag_retriever,
)

__all__ = [
    "load_benchmark_summary",
    "load_report_markdown",
    "load_pilot_summary",
    "load_email_text_lookup",
    "get_worst_mistakes",
    "load_preset_samples",
    "get_m1_model",
    "get_rag_retriever",
    "check_ollama_service",
    "load_unmarked_injection_templates",
    "get_random_unmarked_injection",
    "apply_unmarked_injection",
    "synthesize_injection",
    "load_attack_family_examples",
    "classify_email_m1",
    "classify_email_m2",
    "classify_email_m3",
    "classify_email_m4",
    "classify_all_methods",
    "evaluate_method_disagreements",
]
