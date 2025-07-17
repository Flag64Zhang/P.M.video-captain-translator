# utils/translation_utils.py
# 封装翻译相关操作
from openai import OpenAI
import yaml
import os

# 读取api配置
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
openai_cfg = config.get('openai', {})

client = OpenAI(
    api_key=openai_cfg.get('api_key'),
    base_url=openai_cfg.get('base_url')
)
# ========== 3. 翻译 ==========
def translate(text):
    prompt = (
        f"Translate the following Chinese subtitle into fluent, concise English suitable for video subtitles. "
        f"Only output the English translation itself, with no explanation, notes, or extra content:\n{text}"
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()