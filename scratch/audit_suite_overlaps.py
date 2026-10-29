import json
from pathlib import Path

train_t = {json.loads(l)['text'] for l in open('data/splits/review_seed42/train.jsonl', encoding='utf-8') if l.strip()}
test_t = {json.loads(l)['text'] for l in open('data/splits/review_seed42/test.jsonl', encoding='utf-8') if l.strip()}
val_t = {json.loads(l)['text'] for l in open('data/splits/review_seed42/val.jsonl', encoding='utf-8') if l.strip()}

d_raw = json.load(open('data/diagnostic_suite.json', encoding='utf-8'))
d_texts = set()
for x in d_raw:
    if x.get('text'):
        d_texts.add(x['text'])
    else:
        d_texts.add(f"Subject: {x.get('subject','')}\nFrom: {x.get('sender','')}\n\n{x.get('body','')}")

enron_clean = {json.loads(l)['text'] for l in open('data/processed/enron_ingested/enron_clean_500.jsonl', encoding='utf-8') if l.strip()}
enron_train = {json.loads(l)['text'] for l in open('data/splits/enron_augmented/train.jsonl', encoding='utf-8') if l.strip()}

print("--- OVERLAP MATRIX ---")
print(f"train (1000) & test (522): {len(train_t & test_t)}")
print(f"train (1000) & val (100): {len(train_t & val_t)}")
print(f"test (522) & val (100): {len(test_t & val_t)}")
print(f"diagnostic (20) & train (1000): {len(d_texts & train_t)}")
print(f"diagnostic (20) & test (522): {len(d_texts & test_t)}")
print(f"diagnostic (20) & val (100): {len(d_texts & val_t)}")
print(f"enron_clean (500) & train_baseline: {len(enron_clean & train_t)}")
print(f"enron_clean (500) & test_baseline: {len(enron_clean & test_t)}")
print(f"enron_clean (500) & val_baseline: {len(enron_clean & val_t)}")
print(f"enron_clean (500) & diagnostic (20): {len(enron_clean & d_texts)}")

