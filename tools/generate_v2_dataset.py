# tools/generate_v2_dataset.py
import json
import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.v2_data.group_a import GROUP_A_EMAILS
from tools.v2_data.group_b import GROUP_B_EMAILS
from tools.v2_data.group_c import GROUP_C_EMAILS
from tools.v2_data.group_d import GROUP_D_EMAILS
from tools.v2_data.group_e import GROUP_E_EMAILS

def validate_and_generate():
    groups = {
        "A (Ordinary Genuine)": GROUP_A_EMAILS,
        "B (Difficult Genuine)": GROUP_B_EMAILS,
        "C (Conventional Phishing)": GROUP_C_EMAILS,
        "D (Sophisticated Phishing)": GROUP_D_EMAILS,
        "E (Prompt Injection)": GROUP_E_EMAILS
    }

    all_emails = []
    seen_ids = set()

    for grp_name, emails in groups.items():
        print(f"Checking {grp_name}: {len(emails)} items")
        assert len(emails) == 30, f"{grp_name} has {len(emails)} items, expected 30"
        for item in emails:
            assert "id" in item and item["id"], f"Missing id in {item}"
            assert item["id"] not in seen_ids, f"Duplicate id: {item['id']}"
            seen_ids.add(item["id"])
            assert "subject" in item and item["subject"]
            assert "sender" in item and item["sender"]
            assert "body" in item and item["body"]
            assert isinstance(item["is_phishing"], bool)
            assert item["label"] in [0, 1]
            assert (item["is_phishing"] and item["label"] == 1) or (not item["is_phishing"] and item["label"] == 0)
            assert isinstance(item["has_prompt_injection"], bool)
            assert "category" in item
            assert "subcategory" in item
            assert "explanation" in item
            all_emails.append(item)

    assert len(all_emails) == 150, f"Total items is {len(all_emails)}, expected 150"

    num_phish = sum(1 for e in all_emails if e["is_phishing"])
    num_legit = sum(1 for e in all_emails if not e["is_phishing"])
    num_inj = sum(1 for e in all_emails if e["has_prompt_injection"])
    num_inj_phish = sum(1 for e in all_emails if e["has_prompt_injection"] and e["is_phishing"])
    num_inj_legit = sum(1 for e in all_emails if e["has_prompt_injection"] and not e["is_phishing"])

    print("\nDataset Verification Summary:")
    print(f"Total emails: {len(all_emails)}")
    print(f"Phishing emails: {num_phish} (expected 75)")
    print(f"Legitimate emails: {num_legit} (expected 75)")
    print(f"Prompt injection emails: {num_inj} (expected 30)")
    print(f"  - Phishing + Injection: {num_inj_phish} (expected 15)")
    print(f"  - Legitimate + Injection: {num_inj_legit} (expected 15)")

    assert num_phish == 75, f"Expected 75 phishing, got {num_phish}"
    assert num_legit == 75, f"Expected 75 legitimate, got {num_legit}"
    assert num_inj == 30, f"Expected 30 injection, got {num_inj}"
    assert num_inj_phish == 15, f"Expected 15 phishing injection, got {num_inj_phish}"
    assert num_inj_legit == 15, f"Expected 15 legitimate injection, got {num_inj_legit}"

    out_path = os.path.join("data", "evaluation", "live_benchmark_v2.jsonl")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for item in all_emails:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"\nSuccessfully wrote 150 validated emails to {out_path}")

if __name__ == "__main__":
    validate_and_generate()
