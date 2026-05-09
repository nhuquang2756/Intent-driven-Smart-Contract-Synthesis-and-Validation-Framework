from pydantic import BaseModel, Field
from typing import Optional

class ParsedIntent(BaseModel):
    """Output của Node 1."""
    parties: list[str] = Field(description="Danh sách các bên tham gia")
    contract_type_hint: str = Field(description="Gợi ý loại contract: escrow|vote|loan|dao|other")
    value_ada: Optional[int] = Field(default=None, description="Giá trị ADA")
    timeout_days: Optional[int] = Field(default=None, description="Thời hạn tính bằng ngày")
    conditions: list[str] = Field(default=[], description="Danh sách điều kiện")
    summary_vi: str = Field(description="Tóm tắt bằng tiếng Việt")

class ContractStructure(BaseModel):
    """Output của Node 2."""
    contract_type: str = Field(description="Loại contract: escrow|multisig_vote|loan|dao_fund")
    template_id: str = Field(description="ID template: ESCROW_V1|VOTE_V1|LOAN_V1|DAO_V1")
    states: list[str] = Field(description="Danh sách trạng thái")
    transitions: list[str] = Field(description="Điều kiện chuyển trạng thái")
    termination_paths: list[str] = Field(description="Các đường kết thúc")
    risk_notes: list[str] = Field(default=[], description="Ghi chú rủi ro")

class VerifyCheck(BaseModel):
    """Một kiểm tra đơn lẻ trong quá trình verify."""
    name: str
    passed: bool
    detail: str

class VerifyResult(BaseModel):
    """Output của Node 4."""
    is_valid: bool
    checks: list[VerifyCheck]
    error_type: Optional[str] = None
    fix_hint: Optional[str] = None

# --- ĐÂY LÀ CLASS QUAN TRỌNG ĐANG BỊ THIẾU ---
class PipelineResult(BaseModel):
    """Output cuối cùng của toàn bộ pipeline."""
    success: bool
    iterations: int
    intent: Optional[ParsedIntent] = None
    structure: Optional[ContractStructure] = None
    contract_json: Optional[dict] = None
    verify_result: Optional[VerifyResult] = None
    error_message: Optional[str] = None
    summary_vi: Optional[str] = None

class ContractRequest(BaseModel):
    """Dữ liệu nhận từ Frontend (index.html)."""
    api_key: str = Field(..., description="Google AI Studio API Key")
    user_input: str = Field(..., description="Yêu cầu từ người dùng")