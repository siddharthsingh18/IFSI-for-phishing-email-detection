# Source

- `phishbench/`：v2 核心库，包括数据准备、攻击构造、prompt、调用、解析与统计。
- `tools/data/`：数据获取、清洗和验证入口。
- `tools/prompts/`：冻结与导出 prompt 的入口。
- `tools/inference/`：DeepSeek 单元及矩阵推理入口。
- `tools/evaluation/`：本地模型结果评分、跨模型合并和最终结果重建。

所有命令均从项目根目录执行，详见 `tools/README.md`。实现仅依赖 Python 标准库。

公开仓库可通过 `python -m pip install -e .` 安装，随后直接使用
`phishbench-run`、`phishbench-freeze-prompts` 和 `phishbench-validate`。数据完整性验证需要
本地存在未公开的数据文件；单元测试和 `examples/` dry-run 不需要这些文件。
