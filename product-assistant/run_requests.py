from agent import run_agent

REQUESTS = [
    "What is the price of P002?",
    "Find the laptop",
    "What is the price of P999?",
    "Do you sell headphones?",
    "How much is the monitor?",
    "Show me a keyboard and tell me its price",
]


def main() -> None:
    for question in REQUESTS:
        result = run_agent(question)
        status = "OK  " if result.success else "FAIL"
        print(f"{status} {result.latency_s:5.2f}s  tools={len(result.tool_outputs)} "
              f"tool_failures={result.tool_failures}  {question}")
        print(f"     -> {result.answer.splitlines()[0] if result.answer else ''}")


if __name__ == "__main__":
    main()
