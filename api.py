from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pipeline  # Import file pipeline bạn vừa gửi
from models import ContractRequest, PipelineResult

app = FastAPI()

# Cấu hình CORS để Frontend (index.html) có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate")
async def generate_contract(request: ContractRequest):
    print(f"\n[API] Nhận yêu cầu tạo hợp đồng...")
    print(f"[API] Nội dung: {request.user_input[:50]}...")

    try:
        # Gọi trực tiếp hàm run của pipeline bạn đã cung cấp
        # Vì pipeline của bạn là đồng bộ (synchronous), ta gọi trực tiếp
        result: PipelineResult = pipeline.run(
            api_key=request.api_key, 
            user_input=request.user_input
        )

        if result.success:
            print("[API] Pipeline chạy thành công!")
            return {
                "success": True,
                "summary_vi": result.intent.summary_vi if result.intent else "Thành công",
                "contract_json": result.contract_json, # Đây là mã Marlowe DSL thực tế từ Node 3
                "detail": f"Hoàn thành sau {result.iterations} vòng lặp."
            }
        else:
            print(f"[API] Pipeline thất bại: {result.error_message}")
            return {
                "success": False,
                "error": result.error_message,
                "summary_vi": "Không thể tạo hợp đồng an toàn."
            }

    except Exception as e:
        print(f"[API] Lỗi hệ thống: {str(e)}")
        return {
            "success": False, 
            "error": f"Lỗi Server: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    # Khởi chạy server tại port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)