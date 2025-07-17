# utils/translation_utils.py
# 封装翻译相关操作
from openai import OpenAI


client = OpenAI(
    api_key="zhangxuhao2005@shu.edu.cn",
    base_url="https://api.deepseek.com/v1"
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