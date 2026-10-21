"""Typed inference failure categories shared by API and model clients."""

from typing import Literal

FailureType = Literal[
    "timeout",
    "unavailable",
    "invalid_json",
    "schema_error",
    "unsupported_verdict",
    "retrieval_error",
]
