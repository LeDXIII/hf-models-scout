"""Фильтрация, скоринг и категоризация моделей."""

import math
from datetime import datetime, timezone

from .config import CATEGORIES, SUBCATEGORIES, VERIFIED_ORGS, THRESHOLDS


def parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def is_fresh(model: dict, days: int) -> bool:
    now = datetime.now(timezone.utc)
    created = parse_date(model.get("createdAt"))
    modified = parse_date(model.get("lastModified"))
    return (now - max(created, modified)).days <= days


def passes_filters_basic(model: dict, min_likes: int, min_downloads: int, days: int) -> bool:
    if model.get("likes", 0) < min_likes:
        return False
    if model.get("downloads", 0) < min_downloads:
        return False
    if not is_fresh(model, days):
        return False
    return bool(model.get("tags") or model.get("pipeline_tags"))


def passes_filters(model: dict, min_likes: int, min_downloads: int, days: int) -> bool:
    if model.get("likes", 0) < min_likes:
        return False
    if model.get("downloads", 0) < min_downloads:
        return False
    return bool(model.get("tags") or model.get("pipeline_tags"))


def _norm(value: float, maximum: float) -> float:
    return min(value / maximum, 1.0) if maximum > 0 else 0.0


def compute_scores(models: list[dict]) -> list[dict]:
    """Композитный скоринг: 10 метрик + 1 штраф."""
    if not models:
        return models

    now = datetime.now(timezone.utc)
    max_dl = max((m.get("downloads", 0) for m in models), default=1)
    max_likes = max((m.get("likes", 0) for m in models), default=1)

    for m in models:
        dl = m.get("downloads", 0)
        lk = m.get("likes", 0)

        dl_norm = _norm(dl, max_dl)
        lk_norm = _norm(lk, max_likes)
        kd = lk / dl if dl > 0 else 0

        modified = parse_date(m.get("lastModified"))
        if modified == datetime.min.replace(tzinfo=timezone.utc):
            modified = parse_date(m.get("createdAt"))
        recency = (now - modified).days
        if recency < 0 or recency > 99999:
            recency = 999

        card = m.get("cardData") or {}
        has_card = bool(card.get("description") or card.get("model-index") or m.get("readme"))
        has_space = bool(m.get("spaces") or [])
        author = (m.get("author") or m.get("id", "").split("/")[0]).lower()
        verified = author in VERIFIED_ORGS

        is_dh = (
            dl <= THRESHOLDS["dark_horse_downloads_max"]
            and lk <= THRESHOLDS["dark_horse_likes_max"]
            and kd >= THRESHOLDS["quality_ratio_min"]
        )
        anomaly = kd > THRESHOLDS["anomaly_likes_downloads_ratio_max"] and lk > 100

        score = (
            0.12 * dl_norm
            + 0.12 * lk_norm
            + 0.10 * (1.0 if m.get("_source") == "trending" else 0)
            + 0.08 * max(0, 1 - recency / 30)
            + 0.10 * (1.0 if verified else 0)
            + 0.07 * (1.0 if has_space else 0)
            + 0.07 * (1.0 if has_card else 0)
            + 0.05 * (1.0 if m.get("pipeline_tag") else 0)
            + 0.08 * (0.15 if is_dh else 0)
            + 0.06 * kd
            - 0.05 * (1.0 if anomaly else 0)
        )

        m["score"] = round(max(0, score * 100), 1)
        m["quality_ratio"] = round(kd, 4)
        m["dark_horse_score"] = round(0.15 if is_dh else 0, 4)
        m["recency_days"] = recency
        m["has_space"] = has_space
        m["is_verified"] = verified
        m["trending_score"] = round(dl_norm * (1.0 if m.get("_source") == "trending" else 0.3), 4)

    return models


def classify_model(model: dict) -> str:
    pipeline = (model.get("pipeline_tag") or "").lower()
    tags = [t.lower() for t in (model.get("tags") or [])]

    if pipeline in ("image-text-to-text", "image-to-text", "document-question-answering"):
        if "ocr" in tags:
            return "Vision / OCR"
        return "LLM / Text Generation"
    if not pipeline:
        return "Embeddings / Other"
    for cat, cfg in CATEGORIES.items():
        if pipeline in cfg["pipeline_tags"]:
            return cat
    return "Embeddings / Other"


def categorize_models(models: list[dict]) -> dict[str, list[dict]]:
    raw = {cat: [] for cat in CATEGORIES}
    for m in models:
        raw[classify_model(m)].append(m)
    return raw


def sort_by_score(categories: dict[str, list[dict]]) -> dict[str, list[dict]]:
    return {cat: sorted(lst, key=lambda x: x.get("score", 0), reverse=True)
            for cat, lst in categories.items()}


def get_subcategory(pipeline_tag: str, category: str) -> str:
    for sn, stags in SUBCATEGORIES.get(category, {}).items():
        if pipeline_tag in stags:
            return sn
    subs = SUBCATEGORIES.get(category, {})
    return list(subs.keys())[-1] if subs else "Other"


def group_by_subcategories(models: list[dict], category: str) -> dict[str, list[dict]]:
    result = {}
    for m in models:
        sn = get_subcategory(m.get("pipeline_tag", ""), category)
        result.setdefault(sn, []).append(m)
    return result


def subcat_count(subcats: dict) -> int:
    return sum(len(v) for v in subcats.values())


def compute_stats(models: list[dict]) -> dict:
    if not models:
        return {}

    def median(lst):
        n = len(lst)
        return (lst[n // 2] + lst[~(n // 2)]) / 2 if lst else 0

    sorted_dl = sorted(m.get("downloads", 0) for m in models)
    sorted_lk = sorted(m.get("likes", 0) for m in models)
    sorted_sc = sorted(m.get("score", 0) for m in models)

    cats = {}
    for m in models:
        c = classify_model(m)
        cats[c] = cats.get(c, 0) + 1

    trending = [m for m in models if m.get("_source") == "trending"]
    leader = max(trending, key=lambda m: m.get("downloads", 0)) if trending else None

    return {
        "total": len(models),
        "med_downloads": round(median(sorted_dl)),
        "med_likes": round(median(sorted_lk)),
        "med_score": round(median(sorted_sc), 1),
        "categories": cats,
        "verified_count": sum(1 for m in models if m.get("is_verified")),
        "trend_leader": leader,
        "dark_horses_count": sum(1 for m in models if m.get("dark_horse_score", 0) > 0),
    }
