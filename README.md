# product-bundling-strategy-skill

> **GenPark AI Agent Skill** — Generate AI-driven product bundle recommendations using co-occurrence analysis and margin optimization.

## Features

- Purchase co-occurrence analysis from order history
- Three strategies: `frequency_first`, `margin_first`, `balanced`
- Bundle pricing with configurable discount percentage
- Gross margin calculation per bundle
- Auto-generated bundle names
- Fallback bundles when order history is sparse

## Quick Start

```python
from client import ProductBundlingClient

client = ProductBundlingClient(discount_pct=10.0)
result = client.recommend(
    products=[{"id": "A", "name": "Serum", "price": 35, "cost": 8, "category": "skincare"}],
    order_history=[{"order_id": "O1", "product_ids": ["A", "B", "C"]}],
    bundle_size=3,
    strategy="balanced",
)
print(result["top_bundle"])
```

## Installation

```bash
python example_usage.py  # No external dependencies
```

---
Built by [GenPark](https://genpark.ai) | [alphaparkinc](https://github.com/alphaparkinc)
