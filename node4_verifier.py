"""
NODE 4 — Static Verifier (Hybrid)
"""
import json
from models import VerifyResult, VerifyCheck
import gemini_client

VERIFY_SYSTEM = """Bạn là quan tòa Smart Contract. Hãy kiểm tra JSON Marlowe này có kẹt tiền không.

Kiểm tra:
1. Fund Lock: Tiền có luôn được trả lại cho ai đó nếu hết hạn không?
2. Double Pay: Có nguy cơ trả tiền 2 lần không?

Trả về JSON:
{
  "is_valid": true/false,
  "checks": [{"name": "Tiêu chí", "passed": true, "detail": "Lý do"}],
  "error_type": "FUND_LOCK|SYNTAX|LOGIC",
  "fix_hint": "Hướng dẫn cụ thể cho Node 3 sửa"
}"""

def run(client, contract: dict) -> VerifyResult:
    print("[Node4] Đang thẩm định mã nguồn...")
    
    # Gửi code JSON sang Gemini để thẩm định logic sâu
    raw = gemini_client.call(client, VERIFY_SYSTEM, json.dumps(contract))
    cleaned = raw.strip().replace("```json", "").replace("```", "")

    try:
        data = json.loads(cleaned)
        # Chuyển đổi list dict thành list đối tượng VerifyCheck
        checks = [VerifyCheck(**c) for c in data.get("checks", [])]
        return VerifyResult(
            is_valid=data.get("is_valid", False),
            checks=checks,
            error_type=data.get("error_type"),
            fix_hint=data.get("fix_hint")
        )
    except:
        return VerifyResult(is_valid=False, checks=[], error_type="PARSE_ERROR", fix_hint="JSON thẩm định lỗi")