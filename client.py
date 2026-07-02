"""
product-bundling-strategy-skill: Client SDK
Generate product bundle recommendations using co-occurrence analysis and margin optimization.
"""

from __future__ import annotations
from itertools import combinations
from typing import Literal, Optional
from collections import Counter

Strategy = Literal["margin_first", "frequency_first", "balanced"]


class ProductBundlingClient:
    """
    SDK for generating data-driven product bundle recommendations.

    Uses purchase co-occurrence frequency and margin analysis to
    identify high-value, high-affinity product combinations.
    """

    def __init__(self, discount_pct: float = 10.0):
        self.discount_pct = discount_pct

    def recommend(
        self,
        products: list[dict],
        order_history: list[dict],
        bundle_size: int = 3,
        strategy: Strategy = "balanced",
        top_n: int = 5,
    ) -> dict:
        """
        Generate bundle recommendations.

        Args:
            products:      List of dicts with: id, name, price, cost, category.
            order_history: List of dicts with: order_id, product_ids (list of str/int).
            bundle_size:   Number of products per bundle (2-4).
            strategy:      Selection strategy.
            top_n:         Number of bundle recommendations to return.

        Returns:
            dict with: bundles, top_bundle, strategy, co_occurrence_matrix
        """
        bundle_size = max(2, min(bundle_size, 4))
        product_map = {str(p["id"]): p for p in products}

        # Build co-occurrence matrix
        co_occurrence = self._build_co_occurrence(order_history, bundle_size)

        # Generate candidate bundles
        candidates = []
        for combo, freq in co_occurrence.most_common(50):
            bundle_products = [product_map.get(pid) for pid in combo if pid in product_map]
            if len(bundle_products) < bundle_size:
                continue
            bundle = self._build_bundle(bundle_products, freq, strategy)
            candidates.append(bundle)

        # If not enough co-occurrence data, generate margin-based bundles
        if len(candidates) < top_n:
            extra = self._fallback_bundles(products, bundle_size, strategy, top_n - len(candidates))
            candidates.extend(extra)

        # Score and rank
        candidates.sort(key=lambda x: x["score"], reverse=True)
        bundles = candidates[:top_n]

        return {
            "bundles": bundles,
            "top_bundle": bundles[0] if bundles else None,
            "strategy": strategy,
            "total_candidates_evaluated": len(candidates),
        }

    def _build_co_occurrence(self, orders: list[dict], bundle_size: int) -> Counter:
        co: Counter = Counter()
        for order in orders:
            pids = [str(p) for p in order.get("product_ids", [])]
            if len(pids) >= bundle_size:
                for combo in combinations(sorted(set(pids)), bundle_size):
                    co[combo] += 1
        return co

    def _build_bundle(self, products: list[dict], frequency: int, strategy: Strategy) -> dict:
        total_price = sum(float(p["price"]) for p in products)
        total_cost = sum(float(p.get("cost", p["price"] * 0.5)) for p in products)
        discount_amt = round(total_price * self.discount_pct / 100, 2)
        bundle_price = round(total_price - discount_amt, 2)
        margin = bundle_price - total_cost
        margin_pct = round(margin / bundle_price * 100, 1) if bundle_price > 0 else 0

        score = self._score_bundle(frequency, margin_pct, strategy)

        return {
            "products": [{"id": p["id"], "name": p["name"], "price": p["price"]} for p in products],
            "original_total_price": round(total_price, 2),
            "bundle_price": bundle_price,
            "savings_usd": discount_amt,
            "savings_pct": self.discount_pct,
            "gross_margin_pct": margin_pct,
            "co_purchase_frequency": frequency,
            "score": score,
            "bundle_name": self._generate_name(products),
        }

    def _fallback_bundles(self, products: list[dict], bundle_size: int, strategy: Strategy, n: int) -> list[dict]:
        """Generate bundles based on margin when co-occurrence data is sparse."""
        sorted_products = sorted(products, key=lambda p: float(p.get("cost", 0)) / max(float(p["price"]), 0.01))
        bundles = []
        used = set()
        for combo in combinations(range(len(sorted_products)), bundle_size):
            key = tuple(sorted_products[i]["id"] for i in combo)
            if key not in used:
                used.add(key)
                bundle_products = [sorted_products[i] for i in combo]
                bundle = self._build_bundle(bundle_products, 0, strategy)
                bundles.append(bundle)
            if len(bundles) >= n:
                break
        return bundles

    @staticmethod
    def _score_bundle(frequency: int, margin_pct: float, strategy: Strategy) -> float:
        norm_freq = min(frequency / 10.0, 1.0)
        norm_margin = min(margin_pct / 60.0, 1.0)
        if strategy == "frequency_first":
            return round(norm_freq * 0.70 + norm_margin * 0.30, 4)
        elif strategy == "margin_first":
            return round(norm_freq * 0.25 + norm_margin * 0.75, 4)
        else:  # balanced
            return round(norm_freq * 0.50 + norm_margin * 0.50, 4)

    @staticmethod
    def _generate_name(products: list[dict]) -> str:
        categories = list({p.get("category", "Essential") for p in products})
        if len(categories) == 1:
            return f"{categories[0].title()} Bundle"
        return " + ".join(p["name"].split()[0] for p in products[:2]) + " Bundle"
