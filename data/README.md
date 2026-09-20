# v2 Data

本地工作区保存 v2 新建的数据、清单与生成报告。公开仓库只提交 `metadata/`；`raw/` 与
`processed/` 由 `.gitignore` 排除，因为其中包含邮件正文且再分发许可尚未完全确认。

计划结构：

```text
data/
├── raw/phishfuzzer/
├── processed/phishfuzzer_seed_42/
├── processed/nazario_enron_reused/
├── attacks/
├── splits/
└── metadata/
```

原始研究工作区复用了相邻 v1 目录中的冻结数据：

- Nazario 原始 mbox：`../../v1/data/raw/nazario/phishing3.mbox`
- Enron 原始压缩包：`../../v1/data/raw/enron/enron_mail_20150507.tar.gz`
- Nazario+Enron 已处理划分：`../../v1/data/processed/nazario_enron/`
- 原处理脚本（只读参考）：`../../v1/src/data/prepare_nazario_enron.py`

公开用户不能假设存在 `../v1/`。若要重建 Nazario+Enron 条件，应通过
`python -m phishbench.prepare --v1-test PATH --v1-report PATH --v1-nazario PATH --v1-enron PATH`
显式提供已取得和处理的本地文件。PhishFuzzer 数据的公开再分发许可也需要单独确认；在此
之前只发布来源、固定 commit、文件哈希和处理规则，不提交数据副本。

## 已冻结产物

- `raw/phishfuzzer/upstream/`：官方 GitHub 仓库的浅克隆，固定 commit 见 `metadata/source_manifest.json`。
- `processed/phishfuzzer_seed_42/`：去重后以 seed 42 抽取的 1,000 phishing + 1,000 legitimate。
- `processed/nazario_enron_reused/`：v1 固定 test 的规范化副本、逐字节副本和配对攻击条件。
- 每个 processed 数据集下均有 `clean.jsonl`、`attacked_phishing.jsonl`、
  `injected_legitimate_control.jsonl`、`attack_manifest.jsonl` 和 `test_ids.txt`。
- `metadata/source_manifest.json`：URL、commit/版本、本地路径、SHA-256 和许可核查状态。
- `metadata/preparation_report.json`：过滤、去重、抽样、条件规模及所有产物哈希。

攻击数据由人工模板确定性生成，不依赖 LLM。每条攻击只插入文本、不删除原文或改变标签；
attack manifest 可由 `original_id + template_id + position + seed` 回查和复现。
