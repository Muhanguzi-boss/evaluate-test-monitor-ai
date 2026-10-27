"""The agent's two tools: search_product and check_price."""

import json
import re
from pathlib import Path

from logging_config import get_logger

logger = get_logger("tools")

PRODUCTS_FILE = Path(__file__).resolve().parent / "products.json"
CURRENCY = "RWF"
STOPWORDS = {"a", "an", "the", "find", "show", "me", "i", "want", "need", "looking",
             "for", "do", "you", "have", "any", "some", "please", "is", "there"}


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def format_price(amount: int) -> str:
    return f"{amount:,} {CURRENCY}"


def search_product(query: str) -> str:
    """Search the catalogue by ID, name or description (case-insensitive)."""
    logger.info("Tool call: search_product(query=%r)", query)
    query = (query or "").strip().lower()
    keywords = [w for w in re.findall(r"[a-z0-9]+", query) if w not in STOPWORDS]
    if not keywords:
        return "Error: search query is empty."

    # Score each product by how many keywords it contains; keep the best.
    scored = []
    for p in load_products():
        text = f"{p['id']} {p['name']} {p['description']}".lower()
        hits = sum(1 for w in keywords if w in text)
        if hits:
            scored.append((hits, p))
    best = max((hits for hits, _ in scored), default=0)
    matches = [p for hits, p in scored if hits == best]
    if not matches:
        logger.info("search_product: no match for %r", query)
        return f"No products found matching '{query}'."

    results = [
        {
            "id": p["id"],
            "name": p["name"],
            "description": p["description"],
            "price": format_price(p["price"]),
        }
        for p in matches
    ]
    logger.info("search_product: %d match(es) for %r", len(results), query)
    return json.dumps(results)


def check_price(product_id: str) -> str:
    """Return the price for an exact product ID from the catalogue."""
    logger.info("Tool call: check_price(product_id=%r)", product_id)
    product_id = (product_id or "").strip().upper()

    for p in load_products():
        if p["id"] == product_id:
            return f"Product {p['id']} ({p['name']}) costs {format_price(p['price'])}."

    logger.warning("check_price: product %r not found", product_id)
    return f"Product {product_id} not found in the catalogue."


TOOL_FUNCTIONS = {
    "search_product": search_product,
    "check_price": check_price,
}

TOOL_SCHEMAS = [
    {
        "name": "search_product",
        "description": (
            "Search the shop's product catalogue by keyword (name, description "
            "or product ID). Returns matching products with ID, name, "
            "description and price in RWF."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword, e.g. 'laptop'."}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "check_price",
        "description": (
            "Get the price of one product by its exact product ID (e.g. 'P002'). "
            "Returns the price in RWF, or a not-found message."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product ID such as 'P002'."}
            },
            "required": ["product_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run a tool safely. Returns (result_text, is_error); never raises."""
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        logger.error("Tool failure: unknown tool %r", name)
        return f"Error: unknown tool '{name}'.", True
    try:
        return func(**tool_input), False
    except Exception as exc:
        logger.exception("Tool failure: %s raised %s", name, type(exc).__name__)
        return f"Error: the {name} tool is temporarily unavailable.", True
