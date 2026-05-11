from __future__ import annotations

from pathlib import Path

from src.report.deepseek_client import DeepSeekClient, DeepSeekConfig
from src.report.prompting import build_diagnosis_prompt
from src.report.report_generator import render_markdown_report
from src.workflow import run_scoring_workflow


def generate_report_markdown(*, data_dir: Path, model: str = "deepseek-v4-flash") -> str:
    score_report = run_scoring_workflow(data_dir=data_dir)
    prompt = build_diagnosis_prompt(score_report)
    client = DeepSeekClient(DeepSeekConfig(model=model))
    summary = client.summarize(prompt=prompt)
    return render_markdown_report(report=score_report, llm_summary=summary)

