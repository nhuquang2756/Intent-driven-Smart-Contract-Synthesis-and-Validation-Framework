"""
gemini_client.py — Dùng google-genai (package mới 2025)
Thay thế google-generativeai đã bị deprecated.

Cài đặt: pip install google-genai
"""

from google import genai
from google.genai import types

# Model mới nhất, miễn phí, nhanh
MODEL = "gemini-2.0-flash"


def make_client(api_key: str):
    """Khởi tạo Gemini client."""
    if not api_key or not api_key.startswith("AIza"):
        raise ValueError("API Key không hợp lệ. Key Gemini bắt đầu bằng 'AIza...'")
    return genai.Client(api_key=api_key)


def call(client: genai.Client, system_prompt: str, user_input: str) -> str:
    """
    Gọi Gemini API và trả về text response.
    Tự động làm sạch markdown nếu model trả về ```json ... ```
    """
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"{system_prompt}\n\nUSER INPUT:\n{user_input}",
            config=types.GenerateContentConfig(
                temperature=0.3,       # thấp = ổn định hơn, ít hallucination
                max_output_tokens=2000,
            )
        )

        text = response.text or "{}"

        # Làm sạch markdown nếu có
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Bỏ dòng đầu (```json) và dòng cuối (```)
            cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return cleaned.strip()

    except Exception as e:
        print(f"[Gemini Error] {str(e)}")
        return "{}"