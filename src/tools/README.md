# Command-line tools

推荐先运行 `python -m pip install -e .`。所有脚本均从仓库根目录解析路径，不依赖调用者的
当前目录。可通过 `PYTHON_BIN=/path/to/python` 覆盖默认的 `python3`。

## 数据

```bash
./src/tools/data/fetch_data.sh
./src/tools/data/prepare_data.sh
./src/tools/data/filter_nazario_quality.sh
./src/tools/data/validate_artifacts.sh
```

## Prompt

```bash
./src/tools/prompts/freeze_prompts.sh
./src/tools/prompts/export_portable_prompts.sh
```

## 推理

`run_deepseek_cell.sh` 运行一个 DeepSeek cell；`run_deepseek_matrix.sh` 按
`experiments/config/main_matrix.json` 运行或续跑矩阵。新响应写入
`experiments/work/deepseek/`，不会覆盖已归档的论文结果。

实时推理前只在当前 shell 中设置 `DEEPSEEK_API_KEY`；不要把密钥写入命令、JSON、日志或
tracked `.env`。`--dry-run` 不读取密钥，也不访问网络。

## 评价

- `evaluate_portable_results.py`：连接冻结 prompt 与单个本地模型 JSONL。
- `combine_portable_metrics.py`：合并本地模型/模式的统计。
- `compile_all_experiment_results.py`：统一 DeepSeek 与本地模型口径。
- `build_detailed_comparison.py`：按数据集、模型、模式和三种注入环境生成带合并表头的
  Markdown/HTML 对比表，并可通过 `--latex-output` 同时导出论文用 LaTeX 表格。
- `build_raw_manifests.py`：为解压后的原始 JSONL 生成逐文件哈希与行数清单。
- `rebuild_final_results.sh`：从原始 JSONL 完整重建最终 JSON，不调用模型 API。

## 发布检查

```bash
./src/tools/release/check_public_release.sh
./src/tools/release/export_public_tree.sh /tmp/phishbench-public
```

第一条命令确认私有数据路径仍被忽略，然后执行编译、单元测试和合成样例 dry-run。第二条
命令从父级历史仓库中导出仅包含 v2 可公开文件的独立目录，不会复制被 `.gitignore` 排除的
数据、响应、论文草稿或临时文件。
