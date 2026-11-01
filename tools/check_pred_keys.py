import json
with open("results/m4_ablation_v1/predictions.jsonl", "r", encoding="utf-8") as f:
    line = f.readline()
    print(json.dumps(list(json.loads(line).keys())))

