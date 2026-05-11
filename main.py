from __future__ import annotations

import argparse
from pathlib import Path

from src.report.report_generator import render_markdown_report
from src.report.pipeline import generate_report_markdown
from src.workflow import run_scoring_workflow


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=Path("sample-data"))
    p.add_argument("--out-report", type=Path, default=Path("outputs") / "sample_report.md")
    p.add_argument("--out-plot", type=Path, default=Path("outputs") / "score_radar.png")
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--no-plot", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_plot.parent.mkdir(parents=True, exist_ok=True)

    if not args.no_llm:
        try:
            md = generate_report_markdown(data_dir=args.data_dir)
        except Exception:
            score_report = run_scoring_workflow(data_dir=args.data_dir)
            md = render_markdown_report(report=score_report, llm_summary="（未配置 DEEPSEEK_API_KEY，跳过 LLM 综合诊断。）")
    else:
        score_report = run_scoring_workflow(data_dir=args.data_dir)
        md = render_markdown_report(report=score_report, llm_summary="（已通过 --no-llm 禁用 LLM 综合诊断。）")

    args.out_report.write_text(md, encoding="utf-8")

    if not args.no_plot:
        from src.report.visualization import save_radar_chart

        score_report = run_scoring_workflow(data_dir=args.data_dir)
        save_radar_chart(report=score_report, output_path=args.out_plot)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

