"""
example_usage.py -- Demonstrates the ProductBundlingClient SDK.
"""
from client import ProductBundlingClient
import random

def generate_sample_data(seed=42):
    random.seed(seed)
    products = [
        {"id": "P001", "name": "Vitamin C Serum", "price": 34.99, "cost": 8.00, "category": "skincare"},
        {"id": "P002", "name": "Hyaluronic Moisturizer", "price": 28.99, "cost": 7.00, "category": "skincare"},
        {"id": "P003", "name": "SPF 50 Sunscreen", "price": 19.99, "cost": 5.00, "category": "skincare"},
        {"id": "P004", "name": "Retinol Night Cream", "price": 44.99, "cost": 11.00, "category": "skincare"},
        {"id": "P005", "name": "Gentle Face Wash", "price": 16.99, "cost": 4.00, "category": "skincare"},
        {"id": "P006", "name": "Eye Cream", "price": 39.99, "cost": 9.00, "category": "skincare"},
        {"id": "P007", "name": "Toner", "price": 22.99, "cost": 6.00, "category": "skincare"},
        {"id": "P008", "name": "Face Mask Set", "price": 29.99, "cost": 8.00, "category": "skincare"},
    ]
    orders = []
    common_combos = [("P001","P002","P003"), ("P001","P004","P006"), ("P002","P005","P007")]
    for i in range(80):
        combo = random.choice(common_combos)
        extra = random.choice([p["id"] for p in products if p["id"] not in combo])
        orders.append({"order_id": f"O{i:04d}", "product_ids": list(combo) + [extra] if random.random() > 0.5 else list(combo)})
    return products, orders

def main():
    client = ProductBundlingClient(discount_pct=12.0)
    products, orders = generate_sample_data()

    print("[1] Balanced Bundle Strategy")
    result = client.recommend(products, orders, bundle_size=3, strategy="balanced", top_n=3)
    print(f"Strategy: {result['strategy']} | Candidates Evaluated: {result['total_candidates_evaluated']}")
    print("\nTop Bundles:")
    for i, b in enumerate(result["bundles"], 1):
        names = [p["name"] for p in b["products"]]
        print(f"  {i}. {b['bundle_name']}")
        print(f"     Products: {', '.join(names)}")
        print(f"     Original: ${b['original_total_price']} -> Bundle Price: ${b['bundle_price']} (save ${b['savings_usd']})")
        print(f"     Margin: {b['gross_margin_pct']}% | Co-purchase Frequency: {b['co_purchase_frequency']} | Score: {b['score']}")

    print("\n[2] Margin-First Strategy")
    result2 = client.recommend(products, orders, bundle_size=3, strategy="margin_first", top_n=1)
    tb = result2["top_bundle"]
    if tb:
        print(f"Best Margin Bundle: {tb['bundle_name']} | Margin: {tb['gross_margin_pct']}% | Price: ${tb['bundle_price']}")

if __name__ == "__main__":
    main()
