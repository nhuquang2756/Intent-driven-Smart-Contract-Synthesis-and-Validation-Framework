"""
NODE 1 — Intent Parsing Agent
"""
import json
from models import ParsedIntent
import gemini_client

SYSTEM_PROMPT = """Bạn là chuyên gia phân tích nghiệp vụ cho hợp đồng thông minh Cardano.
Nhiệm vụ: Chuyển đổi yêu cầu tiếng Việt thành dữ liệu cấu trúc JSON.

QUY TẮC:
1. Parties: Dùng danh từ chung tiếng Anh (Buyer, Seller, Lender, Borrower, Admin...).
2. contract_type_hint: Chỉ 1 trong [escrow, vote, loan, dao].
3. Trả về JSON THUẦN TÚY, không markdown, không backtick.

Schema bắt buộc:
{
  "parties": ["Buyer", "Seller"],
  "contract_type_hint": "escrow",
  "value_ada": 500,
  "timeout_days": 7,
  "conditions": ["Buyer nạp tiền", "Seller xác nhận giao hàng"],
  "summary_vi": "Hợp đồng ký quỹ giữa Buyer và Seller với 500 ADA, hạn 7 ngày."
}"""

FALLBACK = ParsedIntent(
    parties=["Buyer", "Seller"],
    contract_type_hint="escrow",
    value_ada=500,
    timeout_days=7,
    conditions=["Bên A nạp tiền", "Bên B xác nhận"],
    summary_vi="Hợp đồng escrow mặc định (AI không phản hồi)."
)


def run(client, user_input: str) -> ParsedIntent:
    print("[Node1] Đang phân tích intent...")
    raw = gemini_client.call(client, SYSTEM_PROMPT, user_input)

    if not raw or raw == "{}":
        print("[Node1] ⚠ AI không trả về dữ liệu, dùng fallback")
        return FALLBACK

    try:
        data = json.loads(raw)
        result = ParsedIntent(**data)
        print(f"[Node1] ✓ Parties: {result.parties} | Type: {result.contract_type_hint}")
        return result
    except Exception as e:
        print(f"[Node1] ⚠ Parse lỗi: {e} — dùng fallback")
        return FALLBACK