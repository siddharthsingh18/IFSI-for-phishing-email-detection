"""Controlled Ablation Study Package: m4_ablation_v1."""

from .ablation_engine import (
    AblationConfig,
    CONFIGURATIONS,
    classify_email_ablation,
)

__all__ = [
    "AblationConfig",
    "CONFIGURATIONS",
    "classify_email_ablation",
]

