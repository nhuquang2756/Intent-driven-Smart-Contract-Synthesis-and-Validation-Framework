"""
evaluate.py — Chạy toàn bộ test cases và xuất báo cáo metric.
Dùng cho phần Experiment trong báo cáo NCKH.
"""

import json
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
import pipeline


def load_test_cases():
    with open(os.path.join(os.path.dirname(__file__), 'test_cases.json'), encoding='utf-8') as f:
        return json.load(f)


def run_evaluation(api_key: str):
    cases = load_test_cases()
    results = []

    print(f"\n{'='*60}")
    print(f"  MarloweAI Evaluation — {len(cases)} test cases")
    print(f"{'='*60}\n")

    for i, case in enumerate(cases, 1):
        print(f"\n[{i}/{len(cases)}] {case['name']}")
        print(f"  Input: {case['input'][:60]}...")

        start = time.time()
        result = pipeline.run(api_key, case['input'])
        elapsed = round(time.time() - start, 2)

        record = {
            "id": i,
            "name": case['name'],
            "expected_type": case.get('expected_type'),
            "success": result.success,
            "iterations": result.iterations,
            "elapsed_sec": elapsed,
            "contract_type": result.structure.contract_type if result.structure else None,
            "type_match": (
                result.structure.contract_type == case.get('expected_type')
                if result.structure and case.get('expected_type') else None
            ),
            "verify_passed": result.verify_result.is_valid if result.verify_result else False,
            "error": result.error_message
        }
        results.append(record)

        status = "✓ PASS" if result.success else "✗ FAIL"
        print(f"  {status} | {result.iterations} vòng | {elapsed}s")

    # ── Tính metrics ───────────────────────────────────
    total = len(results)
    success = sum(1 for r in results if r['success'])
    first_pass = sum(1 for r in results if r['success'] and r['iterations'] == 1)
    avg_iter = sum(r['iterations'] for r in results) / total
    avg_time = sum(r['elapsed_sec'] for r in results) / total
    type_correct = [r for r in results if r['type_match'] is not None]
    type_acc = sum(1 for r in type_correct if r['type_match']) / len(type_correct) if type_correct else 0

    print(f"\n{'='*60}")
    print(f"  KẾT QUẢ EVALUATION")
    print(f"{'='*60}")
    print(f"  Validity Rate:        {success}/{total} = {success/total*100:.1f}%")
    print(f"  First-Pass Rate:      {first_pass}/{total} = {first_pass/total*100:.1f}%")
    print(f"  Avg Iterations:       {avg_iter:.2f}")
    print(f"  Avg Time/Contract:    {avg_time:.2f}s")
    print(f"  Type Accuracy:        {type_acc*100:.1f}%")
    print(f"{'='*60}\n")

    # Lưu kết quả
    output = {
        "metrics": {
            "validity_rate": round(success/total, 3),
            "first_pass_rate": round(first_pass/total, 3),
            "avg_iterations": round(avg_iter, 2),
            "avg_time_sec": round(avg_time, 2),
            "type_accuracy": round(type_acc, 3),
            "total_cases": total
        },
        "details": results
    }

    out_path = os.path.join(os.path.dirname(__file__), 'eval_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"  Kết quả lưu tại: {out_path}")
    return output


if __name__ == "__main__":
    key = os.environ.get("ANTHROPIC_API_KEY") or input("Nhập API Key: ").strip()
    run_evaluation(key)