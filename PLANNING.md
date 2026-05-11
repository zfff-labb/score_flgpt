# 品牌多维度评分 Workflow - 整体规划文档

## 1. 项目概述
本项目旨在为零售数据平台构建一套品牌健康度自动评估系统。通过分析品牌基础信息、发展历史、产品数据、流量数据和用户评价数据，计算品牌在多个维度的得分，并结合 LLM 生成综合诊断报告。

## 2. 模块划分与开发流程

本项目严格按照模块化开发，并使用 Git 进行版本管理。每个模块将在独立的分支中开发，完成后立即推送到远程仓库，最后合并至 `main` 分支。

### 模块 1：初始化项目结构与依赖项
- **分支名**：`init-project`
- **任务内容**：
  - 初始化 Git 仓库并绑定远程地址。
  - 创建基础目录结构（如 `src/`, `data/`, `notebooks/` 等）。
  - 创建并配置 `requirements.txt`（包含 pandas, jupyter, openai, matplotlib 等依赖）。
  - 创建基础工具文件（如配置加载器等）。

### 模块 2：数据探查 (Jupyter Notebook)
- **分支名**：`data-exploration`
- **任务内容**：
  - 编写 `notebooks/data_exploration.ipynb`。
  - 加载 `sample-data` 下的所有 JSON 数据。
  - 分析数据结构、字段缺失情况以及可用于指标计算的关键特征。
  - 为后续的指标设计提供数据可行性验证。

### 模块 3：指标设计与评分引擎
- **分支名**：`scoring-engine`
- **任务内容**：
  - 在 `src/scoring/` 下实现各个维度的评分逻辑。
  - **初定维度**：
    1. **品牌成熟度**：基于成立年份、全渠道覆盖数等。
    2. **产品质量**：基于好评率、评分数据提取。
    3. **市场需求匹配度**：基于销量、评论数。
    4. **性价比**：基于价格区间与用户情感反馈。
  - 实现统一的评分合并机制，输出结构化的评分字典。

### 模块 4：工作流实现
- **分支名**：`workflow-implementation`
- **任务内容**：
  - 在 `src/workflow/` 下实现主工作流引擎 `main_workflow.py`。
  - 将数据加载、指标计算进行串联。
  - 提供标准的输入输出接口。

### 模块 5：LLM 诊断与报告生成
- **分支名**：`llm-report`
- **任务内容**：
  - 在 `src/report/` 下实现 LLM 接口调用（指定使用 `deepseek-v4-flash` 模型）。
  - 组装 Prompt：将评分结果传入 LLM，要求生成 100-200 字的中文综合总结。
  - 生成最终的分析报告文本，并可选择生成雷达图等可视化图表。

### 模块 6：添加 ReadMe 文件和示例输出
- **分支名**：`docs-and-readme`
- **任务内容**：
  - 编写详细的 `README.md`，包含环境说明、运行方式、架构设计和结果说明。
  - 运行工作流生成 `sample_report.md` 和评分图表，并保存。
  - 最终将主流程代码和文档准备完毕，最后全部推送到 `main` 分支。

## 3. 技术栈
- **语言**：Python 3.8+
- **数据处理**：Pandas, JSON
- **LLM 接口**：OpenAI SDK (调用 DeepSeek API)
- **可视化**：Matplotlib / Seaborn (雷达图/柱状图)
- **环境管理**：`pip` + `requirements.txt`

## 4. API 配置
- **LLM 供应商**：DeepSeek
- **模型名**：`deepseek-v4-flash`
- **API Key**：通过环境变量 `DEEPSEEK_API_KEY` 提供（不写入代码/仓库）

## 5. 预期交付物
1. Git 远程仓库：`https://github.com/zfff-labb/score_flgpt`（包含完整的模块提交记录）。
2. 可直接执行的工作流主脚本 `main.py`。
3. 结构化的综合分析报告与多维度评分。
