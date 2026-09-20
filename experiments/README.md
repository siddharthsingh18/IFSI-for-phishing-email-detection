# Experiments

本目录在本地保留论文实验的可回溯输入、唯一原始结果、最终统计和运行配置。公开 Git
仓库默认只提交 `config/`、`results/`、安全的 prompt snapshot，以及顶层完整性清单；含邮件
正文或逐请求响应的 JSONL 由 `.gitignore` 排除。

```text
inputs/   冻结 prompt 快照及可移植的逐请求 JSONL
raw/      按实验 cell/run 分组的原始 JSONL，以及逐文件校验清单
results/  唯一机器可读总表与最终中文报告
config/   主矩阵和 DeepSeek 价格快照
```

本地 `raw/deepseek-v4-main/` 含 72 个 cell、59,472 条结果；每个 cell 单独保留
`results.jsonl` 和运行 `manifest.json`。`raw/qwen3.5-vllm-main/` 含 4 个模型—模式 JSONL、
共 75,472 条结果。两个目录各自的 `MANIFEST.json` 记录逐文件 SHA-256、大小和行数。
这些逐请求文件可能包含邮件正文、完整响应或 reasoning trace，不应直接提交到公开仓库。
顶层 `MANIFEST.json` 保留其规模和哈希，便于验证另行存档的文件。

重新统计：

```bash
BOOTSTRAP_ITERATIONS=2000 ./src/tools/evaluation/rebuild_final_results.sh
```

该命令只读取已保存的 JSONL，不会请求模型服务。`results/all-model-results.json` 可重建；
`results/ALL_EXPERIMENT_RESULTS_ZH.md` 是据此整理的最终论文口径报告。

如果公开仓库中没有本地 raw artifacts，该重建命令会按预期失败；这不影响安装、单元测试、
合成样例 dry-run 或阅读已发布的聚合结果。
