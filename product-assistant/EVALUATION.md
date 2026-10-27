# DeepEval Results: Interpretation (Section 2, Step C)

- **Agent model:** `claude-haiku-4-5`
- **Judge model:** `claude-haiku-4-5` (DeepEval `AnthropicModel`)
- **Metrics:** Answer Relevancy and Faithfulness, threshold 0.7 each
- **Context:** Faithfulness is checked against the raw tool outputs the agent received (`retrieval_context`)
- **Raw data:** [eval_results.json](eval_results.json), produced by `python evaluate_agent.py`

## Summary

| # | Input | Answer Relevancy | Faithfulness |
|---|-------|------------------|--------------|
| 1 | What is the price of P002? | 1.00 PASS | 1.00 PASS |
| 2 | Find the laptop | 1.00 PASS | 1.00 PASS |
| 3 | What is the price of P999? | **0.33 FAIL** | 1.00 PASS |

**5/6 metric checks passed.**

## Case 1: "What is the price of P002?"

- **Expected:** Correctly reports 15,000 RWF
- **Tool output:** `Product P002 (Wireless Mouse) costs 15,000 RWF.`
- **Agent answer:** "The price of P002 (Wireless Mouse) is **15,000 RWF**."
- **Answer Relevancy:** 1.00, PASS. The answer addresses the price question directly, with nothing irrelevant.
- **Faithfulness:** 1.00, PASS. The answer doesn't contradict the tool output.
- **Failure reason:** none.

## Case 2: "Find the laptop"

- **Expected:** Returns the laptop's catalogue details
- **Tool output:** `[{"id": "P001", "name": "Laptop", "description": "8GB RAM, 256GB SSD", "price": "750,000 RWF"}]`
- **Agent answer:** Laptop, P001, 8GB RAM, 256GB SSD, 750,000 RWF
- **Answer Relevancy:** 1.00, PASS. The answer covers the request fully and stays on topic.
- **Faithfulness:** 1.00, PASS. Every detail matches the catalogue entry.
- **Failure reason:** none.

## Case 3: "What is the price of P999?"

- **Expected:** Clearly reports that the product does not exist
- **Tool output:** `Product P999 not found in the catalogue.`
- **Agent answer:** "Product P999 is not found in our catalogue. This product ID does not exist. Would you like me to help you search for a different product?"
- **Answer Relevancy:** 0.33, **FAIL**
- **Faithfulness:** 1.00, PASS. The agent didn't invent a price.

**Failure reason:** The judge said the output "fails to address the core request for pricing information" because it doesn't give a price. The agent's behaviour was correct: P999 doesn't exist, so there is no price to give. Answer Relevancy only measures whether the statements in the answer address the literal question. It doesn't check correctness. The "not found" statements and the follow-up offer were scored as not answering "what is the price", which pulled the score down to 0.33.

This shows the lab's point that a score is a metric result, not a measure of factual accuracy. Here the answer is fully correct (Faithfulness 1.00) but still fails relevancy.

## Improvement I would make

Add an `expected_output` to each case and evaluate it with a correctness metric, such as DeepEval `GEval` with the criterion "Does the answer match the expected behaviour?". Answer Relevancy can't tell a correct "this product does not exist" answer apart from an off-topic one, so it shouldn't be the only signal for edge cases like unknown products.

A smaller change in the agent itself would also help: tell it to phrase not-found answers in terms of the question, e.g. "There is no price for P999 because it is not in our catalogue", and to skip unrelated follow-up offers.

## Re-run after the Section 4 and 5 changes

After the fixes (keyword search, the "search by name" prompt rule, ID validation and the price guardrail), `evaluate_agent.py` was run **3 times**:

| Input | Answer Relevancy (runs 1/2/3) | Faithfulness (runs 1/2/3) |
|---|---|---|
| What is the price of P002? | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| Find the laptop | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| What is the price of P999? | **1.00 / 1.00 / 1.00** (was 0.33) | 1.00 / 1.00 / 1.00 |

**18/18 metric checks passed** (before: 5/6).

The new P999 answers are shorter, e.g. "Product P999 does not exist in our catalogue. Would you like me to search for a specific product instead?" The judge now scores them as directly answering the question.

**Caveat:** none of the changes targeted the wording of the P999 answer, and both the agent and the judge are LLMs whose output varies from run to run. The original 0.33 was most likely caused by that particular answer's wording: three statements, two of which the judge counted as off-topic. That's why the correctness-metric improvement above is still worth making: a correct answer shouldn't depend on phrasing to pass.
