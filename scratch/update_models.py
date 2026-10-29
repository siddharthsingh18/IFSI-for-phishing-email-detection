from pathlib import Path

p = Path("src/core/models.py")
t = p.read_text(encoding="utf-8")
t = t.replace(
    "clf = LogisticRegression(C=1.0, random_state=42, max_iter=200)",
    'clf = LogisticRegression(C=1.0, random_state=42, max_iter=200, class_weight="balanced")'
)
p.write_text(t, encoding="utf-8")
print("Updated models.py with class_weight='balanced'")

