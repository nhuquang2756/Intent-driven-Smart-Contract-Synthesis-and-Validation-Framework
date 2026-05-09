"""
NODE 3 — Marlowe Generator Agent (Bản hoàn chỉnh)
"""
import json
import time
import gemini_client

SYSTEM_PROMPT_BASE = """Bạn là chuyên gia lập trình Marlowe DSL trên Cardano.
Nhiệm vụ: Chuyển đổi logic hợp đồng thành mã JSON Marlowe Core hợp lệ.

QUY TẮC BẮT BUỘC:
1. Chỉ trả về JSON THUẦN TÚY. Không giải thích, không markdown.
2. Đơn vị: Luôn dùng 'lovelace' (1 ADA = 1,000,000 lovelace).
3. Timeout: Dùng UNIX Timestamp (mili giây).
4. Nếu có 'Error feedback', bạn phải sửa lỗi đó triệt để trong mã mới.
"""

def run(client, intent, structure, error_feedback: str = None, iteration: int = 1) -> dict | None:
    print(f"[Node3] Vòng {iteration}: Đang sinh mã Marlowe DSL...")
    
    current_ms = int(time.time() * 1000)
    # Tính toán deadline an toàn
    timeout_days = getattr(intent, 'timeout_days', 1) or 1
    deadline_ms = current_ms + (timeout_days * 86400000)

    # FIX: Ép kiểu an toàn cho value_ada để tránh lỗi nhân với None hoặc String
    try:
        raw_ada = getattr(intent, 'value_ada', 0)
        ada_value = float(raw_ada) if raw_ada is not None else 0.0
    except (ValueError, TypeError):
        ada_value = 0.0
        
    lovelace_value = int(ada_value * 1_000_000)

    user_msg = f"""
    INTENT: {intent.model_dump_json()}
    STRUCTURE: {structure.model_dump_json()}
    DEADLINE_MS: {deadline_ms}
    VALUE_LOVELACE: {lovelace_value}
    PREVIOUS_ERROR: {error_feedback if error_feedback else "None"}
    """

    try:
        raw_response = gemini_client.call(client, SYSTEM_PROMPT_BASE, user_msg)
        # Làm sạch chuỗi JSON khỏi markdown rác
        cleaned = raw_response.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned)
    except Exception as e:
        print(f"[Node3 Error] Không thể tạo JSON: {e}")
        return None