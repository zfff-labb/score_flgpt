# 品牌多维度评分 Workflow

本项目基于 `sample-data/` 中的多源零售数据，对目标品牌进行多维度量化评分，并生成结构化分析报告（含 LLM 综合诊断与可视化图表）。

## 目录结构

- `sample-data/`：题目提供的样例数据
- `notebooks/`：数据探查 Notebook
- `src/scoring/`：指标设计与评分引擎
- `src/workflow/`：Workflow 串联（数据加载 → 评分计算）
- `src/report/`：LLM 诊断与报告生成、可视化
- `main.py`：主入口

## 环境依赖

```bash
pip install -r requirements.txt
```

## 运行方式

### 1) 仅生成评分报告（不调用 LLM）

```bash
python main.py --no-llm
```

默认输出：
- `outputs/sample_report.md`
- `outputs/score_radar.png`

### 2) 生成带 LLM 综合诊断的报告（DeepSeek）

本项目 LLM 使用 `deepseek-v4-flash`，通过环境变量提供 Key：

```bash
set DEEPSEEK_API_KEY=你的Key
python main.py
```

## 数据探查

Notebook 位于 `notebooks/data_exploration.ipynb`。

