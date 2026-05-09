"""
NODE 2 — Game Theory & Logic Agent
"""
import json
from models import ParsedIntent, ContractStructure
import gemini_client

SYSTEM_PROMPT = """Bạn là kiến trúc sư logic Smart Contract.
Dựa vào Intent, thiết kế State Machine an toàn.

Trả về JSON THUẦN TÚY:
{
  "contract_type": "escrow",
  "template_id": "ESCROW_V1",
  "states": ["Khởi tạo", "Chờ xác nhận", "Hoàn tất", "Hoàn tiền"],
  "transitions": ["Buyer nạp tiền -> Chờ xác nhận", "Seller xác nhận -> Hoàn tất"],
  "termination_paths": ["Thành công: tiền về Seller", "Timeout: tiền về Buyer"],
  "risk_notes": ["Cần timeout đủ dài"]
}

contract_type chỉ là 1 trong: escrow, multisig_vote, loan, dao_fund"""

FALLBACK = ContractStructure(
    contract_type="escrow",
    template_id="ESCROW_V1",
    states=["Khởi tạo", "Chờ xác nhận", "Hoàn tất", "Hoàn tiền"],
    transitions=["Nạp tiền thành công", "Xác nhận điều kiện", "Timeout hết hạn"],
    termination_paths=["Thực thi thành công", "Hoàn tiền khi timeout"],
    risk_notes=[]
)


def run(client, intent: ParsedIntent) -> ContractStructure:
    print("[Node2] Thiết kế cấu trúc logic...")
    raw = gemini_client.call(client, SYSTEM_PROMPT, intent.model_dump_json())

    if not raw or raw == "{}":
        print("[Node2] ⚠ AI không trả về dữ liệu, dùng fallback")
        return FALLBACK

    try:
        data = json.loads(raw)
        result = ContractStructure(**data)
        print(f"[Node2] ✓ Type: {result.contract_type} | States: {len(result.states)}")
        return result
    except Exception as e:
        print(f"[Node2] ⚠ Parse lỗi: {e} — dùng fallback")
        return FALLBACK