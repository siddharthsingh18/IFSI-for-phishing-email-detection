import json

counts = {"v2": {True: 0, False: 0}, "heldout": {True: 0, False: 0}}
for dset, path in [("v2", "data/evaluation/live_benchmark_v2.jsonl"), ("heldout", "data/evaluation/heldout_benchmark_v1.jsonl")]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if item.get("has_prompt_injection"):
                is_p = bool(item.get("is_phishing"))
                counts[dset][is_p] += 1
                if not is_p:
                    subj = item.get("subject", "").encode("ascii", "replace").decode("ascii")
                    print(f"{dset} QUOTED: {item['id']} | {subj}")

print("Counts (is_phishing in has_prompt_injection):", counts)

