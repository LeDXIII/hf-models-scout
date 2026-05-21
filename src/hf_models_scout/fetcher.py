"""Сбор и обогащение данных моделей с Hugging Face API."""

import requests
from .config import HF_API


def fetch_models(sort: str, limit: int = 300) -> list[dict]:
    params = {"sort": sort, "limit": limit}
    try:
        resp = requests.get(HF_API, params=params, timeout=30)
        resp.raise_for_status()
        models = resp.json()
        print(f"  ✅ {sort}: {len(models)} моделей")
        return models
    except Exception as e:
        print(f"  ❌ {sort}: {e}")
        return []


def enrich_models(models: list[dict], batch_size: int = 50) -> list[dict]:
    print(f"\n🔎 Обогащение {len(models)} моделей...")
    for i in range(0, len(models), batch_size):
        batch = models[i:i + batch_size]
        n = i // batch_size + 1
        total = (len(models) + batch_size - 1) // batch_size
        print(f"  Пакет {n}/{total}...")
        for m in batch:
            mid = m.get("id")
            if not mid:
                continue
            try:
                resp = requests.get(
                    f"{HF_API}/{mid}",
                    params={"expand[]": ["cardData", "siblings"]},
                    timeout=10,
                )
                if resp.ok:
                    d = resp.json()
                    card = d.get("cardData") or {}
                    m["cardData"] = card
                    m["siblings"] = d.get("siblings") or []
                    m["description"] = card.get("description", "")
                else:
                    m["cardData"] = {}
                    m["siblings"] = []
                    m["description"] = ""
            except Exception:
                m["cardData"] = {}
                m["siblings"] = []
                m["description"] = ""
    print(f"  ✅ Обогащено {len(models)} моделей")
    return models


def fetch_all_sources(days: int = 30) -> list[dict]:
    print("\n🔍 Сбор моделей с Hugging Face...")
    all_models = []

    for sort, src, limit in [
        ("createdAt", "new", 800),
        ("lastModified", "updated", 800),
        ("trendingScore", "trending", 500),
    ]:
        print(f"  📥 {sort} (limit={limit})...")
        for m in fetch_models(sort, limit):
            m["_source"] = src
            all_models.append(m)

    print(f"\n📊 Всего собрано: {len(all_models)}")
    return all_models
