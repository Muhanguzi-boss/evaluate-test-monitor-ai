import json
import os
from pathlib import Path

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase

from agent import run_agent

THRESHOLD = 0.7
RESULTS_FILE = Path(__file__).resolve().parent / "eval_results.json"

judge = AnthropicModel(model=os.getenv("EVAL_MODEL", "claude-haiku-4-5"))

EVAL_CASES = [
    {"input": "What is the price of P002?", "expected": "Correctly reports 15,000 RWF"},
    {"input": "Find the laptop", "expected": "Returns the laptop's catalogue details"},
    {"input": "What is the price of P999?", "expected": "Clearly reports that the product does not exist"},
]


def evaluate_case(case: dict) -> dict:
    result = run_agent(case["input"])

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=result.answer,
        retrieval_context=result.tool_outputs or ["No product information was returned."],
    )

    row = {
        "input": case["input"],
        "expected_behavior": case["expected"],
        "actual_output": result.answer,
        "retrieval_context": test_case.retrieval_context,
        "agent_latency_s": round(result.latency_s, 2),
        "metrics": {},
    }
    for metric in (
        AnswerRelevancyMetric(threshold=THRESHOLD, model=judge, async_mode=False),
        FaithfulnessMetric(threshold=THRESHOLD, model=judge, async_mode=False),
    ):
        metric.measure(test_case)
        row["metrics"][metric.__name__] = {
            "score": round(metric.score, 3),
            "passed": metric.is_successful(),
            "reason": metric.reason,
        }
    return row


def main() -> None:
    rows = [evaluate_case(case) for case in EVAL_CASES]
    RESULTS_FILE.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    for row in rows:
        print(f"\nInput:    {row['input']}")
        print(f"Expected: {row['expected_behavior']}")
        print(f"Answer:   {row['actual_output']}")
        for name, m in row["metrics"].items():
            status = "PASS" if m["passed"] else "FAIL"
            print(f"  {name:<18} {m['score']:.2f}  {status}  - {m['reason']}")

    total = sum(len(r["metrics"]) for r in rows)
    passed = sum(m["passed"] for r in rows for m in r["metrics"].values())
    print(f"\n{passed}/{total} metric checks passed (threshold {THRESHOLD}). "
          f"Saved to {RESULTS_FILE.name}")


if __name__ == "__main__":
    main()
