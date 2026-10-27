# Pytest Results (Section 3)

Run from `product-assistant/`:

```
pytest -v               # all 11 tests (2 call the real API)
pytest -v -m "not live" # offline only (9 tests)
```

Test runs log to `logs/test.log`, so they don't skew the `app.log` request metrics.

## Coverage of the lab requirements

| Requirement | Tests |
|---|---|
| 1. Searching for an existing product returns the correct product | `test_search_existing_product`, `test_search_with_natural_phrase`, `test_search_unknown_product` |
| 2. Checking P002 returns 15,000 RWF | `test_check_price_p002`, `test_agent_reports_p002_price` (live) |
| 3. Checking P999 does not return an invented price | `test_unknown_product_price`, `test_agent_does_not_invent_p999_price` (live) |
| 4. A simulated tool exception is handled gracefully | `test_tool_exception_is_handled`, `test_unknown_tool_is_handled`, `test_agent_survives_tool_exception`, `test_agent_handles_api_failure` |

## Run 1: before the fix

**10 passed, 1 failed**

```
FAILED test_agent.py::test_search_with_natural_phrase
s = "No products found matching 'the laptop'."
```

**Cause:** `search_product` matched the whole query as one substring. `"laptop"` found P001, but `"the laptop"` found nothing, because no product contains the exact text "the laptop". The model often passes the customer's wording straight to the tool, so the agent would wrongly say the product doesn't exist.

**Fix (`tools.py`):** the query is now split into keywords and filler words ("the", "find", "show me", ...) are removed. Each product is scored by how many keywords appear in its ID, name or description, and only the best-scoring products are returned.

## Run 2: after the fix

**11 passed, 0 failed** (10.14s)
