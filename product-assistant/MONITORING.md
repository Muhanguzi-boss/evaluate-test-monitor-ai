# Logging and Metrics (Section 4)

- **Configuration:** [logging_config.py](logging_config.py) writes to `logs/app.log`. Tests write to `logs/test.log` instead.
- **Collection:** [run_requests.py](run_requests.py) sends a batch of real requests, and [log_metrics.py](log_metrics.py) parses the log.

```
python run_requests.py   # 6 real requests
python log_metrics.py    # totals, failures, latency, tool calls
```

## What is logged

| Requirement | Log line (example) |
|---|---|
| Request started | `[44ba0743] Request started \| model=claude-haiku-4-5 \| input='What is the price of P002?'` |
| Request completed, success or failure, latency | `[44ba0743] Request completed \| status=success \| latency=5.08s \| tool_calls=1 \| tool_failures=0` |
| Tool calls | `Tool call: check_price(product_id='P002')` and `[44ba0743] Tool check_price -> is_error=False` |
| Tool failures | `Tool failure: check_price raised OSError` (with traceback) |
| Errors and exceptions | `status=failure ... error=APIConnectionError: ...` (with traceback, via `logger.exception`) |
| Security events | `Security: blocked answer with unsupported price(s) [...]` |

No API key is logged: `grep -c "sk-ant" logs/app.log` returns `0`. The key is only read from `.env` by the SDK.

## Batch 1: 6 requests (before the prompt fix)

| Request | Input | Status | Latency | Tool calls |
|---|---|---|---|---|
| 44ba0743 | What is the price of P002? | success | 5.08s | 1 |
| b78f96e8 | Find the laptop | success | 2.47s | 1 |
| c281393f | What is the price of P999? | success | 4.51s | 1 |
| 654731e2 | Do you sell headphones? | success | 3.87s | 1 |
| bb9e08d0 | How much is the monitor? | success | 2.49s | **0** |
| 995bdf50 | Show me a keyboard and tell me its price | success | 4.97s | 1 |

**Total 6, failures 0, tool failures 0, average latency 3.90s.**

**Issue found from the logs:** "How much is the monitor?" made `tool_calls=0`. The agent asked the customer for more details instead of searching, even though a Monitor (P005) is in the catalogue.

## Batch 2: 6 requests (after the prompt fix)

Fix: added a rule to the system prompt: *"When the customer names a product, call search_product with that name. Don't ask them for a product ID."*

| Request | Input | Status | Latency | Tool calls |
|---|---|---|---|---|
| - | What is the price of P002? | success | 4.78s | 1 |
| - | Find the laptop | success | 4.69s | 1 |
| - | What is the price of P999? | success | 4.19s | 1 |
| - | Do you sell headphones? | success | 3.44s | 1 |
| - | How much is the monitor? | success | 2.42s | **1** (answered 180,000 RWF) |
| d3abde11 | Show me a keyboard and tell me its price | success | 3.86s | 1 |

**Total 6, failures 0, tool failures 0, average latency 3.90s.**

## Whole log, all runs (smoke tests, evaluation, batches, security tests)

```
Total requests:     48
Completed:          48
Failures:           0
Latency avg / min / max: 3.90s / 1.50s / 22.04s
Tool calls:         29
Tool failures:      0
Blocked answers:    0  (price guardrail)
```

The 22.04s maximum was the very first request (cold start: client and connection setup). All other requests took between 1.5s and 5.1s.

The tool-failure path is tested in pytest (`test_tool_exception_is_handled`, `test_agent_survives_tool_exception`). Those runs log to `test.log`, which is why `app.log` shows 0 tool failures.
