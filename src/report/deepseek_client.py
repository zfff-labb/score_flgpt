from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key_env: str = "DEEPSEEK_API_KEY"
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-v4-flash"


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig | None = None):
        self.config = config or DeepSeekConfig()
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing environment variable: {self.config.api_key_env}")
        self._client = OpenAI(api_key=api_key, base_url=self.config.base_url)

    def summarize(self, *, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "你是一名零售数据平台的资深分析师。输出必须为中文。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        content = resp.choices[0].message.content or ""
        return content.strip()

