"""Verification script: Ensure no benchmark shortcuts or email-specific hardcoding."""

import re
from pathlib import Path

CODE_FILES = [
    Path("src/core/inference_m4_v2.py"),
    Path("src/core/domain_analyzer.py"),
    Path("src/core/sanitizer.py"),
    Path("src/core/balanced_retriever.py"),
]

def verify_code():
    forbidden_patterns = [
        r"v2-[a-z]{3}-\d{2}",
        r"heldout-[a-z]{3}-\d{2}",
        r"v1-[a-z]{3}-\d{2}",
        r"benchmark_v2",
        r"heldout_benchmark",
    ]

    clean = True
    for p in CODE_FILES:
        text = p.read_text(encoding="utf-8")
        for pat in forbidden_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            if matches:
                print(f"[VIOLATION] Found pattern '{pat}' in {p.name}: {matches}")
                clean = False

    if clean:
        print("ALL VERIFICATIONS PASSED: Zero benchmark shortcuts or email IDs found in source code.")
    else:
        raise ValueError("Code contains benchmark shortcuts or sample-specific hardcoding!")

if __name__ == "__main__":
    verify_code()

