"""
PIPELINE — Central Orchestrator (Bản hoàn chỉnh)
"""
import gemini_client
import node1_parser as node1
import node2_classifier as node2
import node3_generator as node3
import node4_verifier as node4
from models import PipelineResult

MAX_ITERATIONS = 3

def run(api_key: str, user_input: str) -> PipelineResult:
    try:
        # 1. Khởi tạo Client
        client = gemini_client.make_client(api_key)

        # 2. Phân tích Intent & Structure (Chỉ chạy 1 lần để giữ tính nhất quán)
        intent = node1.run(client, user_input)
        structure = node2.run(client, intent)

        # 3. Vòng lặp Tự sửa lỗi (Self-Correction Loop)
        last_error = None
        
        for iteration in range(1, MAX_ITERATIONS + 1):
            # Sinh mã
            current_contract = node3.run(
                client, 
                intent, 
                structure, 
                error_feedback=last_error,
                iteration=iteration
            )

            if not current_contract:
                last_error = "Node 3 không tạo được JSON hợp lệ."
                continue

            # Kiểm định an toàn (Node 4)
            verify_result = node4.run(client, current_contract)

            if verify_result.is_valid:
                print(f"[Pipeline] ✓ Thành công tại vòng {iteration}")
                return PipelineResult(
                    success=True,
                    iterations=iteration,
                    intent=intent,
                    structure=structure,
                    contract_json=current_contract,
                    verify_result=verify_result
                )
            
            # Nếu không pass, lưu lỗi để vòng sau AI sửa
            last_error = f"Lỗi loại {verify_result.error_type}: {verify_result.fix_hint}"
            print(f"[Pipeline] ✗ Thất bại vòng {iteration}: {last_error}")

        return PipelineResult(
            success=False,
            iterations=MAX_ITERATIONS,
            error_message="Đã thử tối đa 3 lần nhưng không thể tạo hợp đồng an toàn."
        )

    except Exception as e:
        print(f"[Pipeline Fatal Error] {str(e)}")
        return PipelineResult(
            success=False,
            iterations=0,
            error_message=f"Lỗi hệ thống: {str(e)}"
        )