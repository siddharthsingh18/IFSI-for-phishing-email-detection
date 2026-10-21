"""Core package with lazy exports to avoid model-client import cycles."""

from importlib import import_module

_EXPORTS = {
    "load_benchmark_summary": (".data_loaders", "load_benchmark_summary"),
    "load_report_markdown": (".data_loaders", "load_report_markdown"),
    "load_pilot_summary": (".data_loaders", "load_pilot_summary"),
    "load_email_text_lookup": (".data_loaders", "load_email_text_lookup"),
    "get_worst_mistakes": (".data_loaders", "get_worst_mistakes"),
    "load_preset_samples": (".data_loaders", "load_preset_samples"),
    "get_m1_model": (".models", "get_m1_model"),
    "get_rag_retriever": (".models", "get_rag_retriever"),
    "check_ollama_service": (".models", "check_ollama_service"),
    "load_unmarked_injection_templates": (".injections", "load_unmarked_injection_templates"),
    "get_random_unmarked_injection": (".injections", "get_random_unmarked_injection"),
    "apply_unmarked_injection": (".injections", "apply_unmarked_injection"),
    "synthesize_injection": (".injections", "synthesize_injection"),
    "load_attack_family_examples": (".injections", "load_attack_family_examples"),
    "classify_email_m1": (".inference", "classify_email_m1"),
    "classify_email_m2": (".inference", "classify_email_m2"),
    "classify_email_m3": (".inference", "classify_email_m3"),
    "classify_email_m4": (".inference", "classify_email_m4"),
    "classify_all_methods": (".inference", "classify_all_methods"),
    "evaluate_method_disagreements": (".inference", "evaluate_method_disagreements"),
    "discover_models": (".model_config", "discover_models"),
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(name)
    module_name, attribute = _EXPORTS[name]
    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value
