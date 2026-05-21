"""HF Models Scout — CLI entry point."""

import argparse
import os
import sys
from pathlib import Path

from .config import MAX_AGE_DAYS, TOP_PER_CATEGORY, MIN_LIKES, MIN_DOWNLOADS
from .fetcher import fetch_all_sources, enrich_models
from .filter import (
    passes_filters_basic,
    passes_filters,
    compute_scores,
    categorize_models,
    sort_by_score,
    compute_stats,
)
from .reporter import generate_html

REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"


def main():
    parser = argparse.ArgumentParser(description="HF Models Scout")
    parser.add_argument("--days", type=int, default=MAX_AGE_DAYS)
    parser.add_argument("--top-per-category", type=int, default=TOP_PER_CATEGORY)
    parser.add_argument("--min-likes", type=int, default=MIN_LIKES)
    parser.add_argument("--min-downloads", type=int, default=MIN_DOWNLOADS)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    REPORTS_DIR.mkdir(exist_ok=True)

    if not args.output:
        from datetime import datetime
        args.output = str(REPORTS_DIR / f"report-{datetime.now():%Y-%m-%d-%H%M}.html")
    elif not os.path.isabs(args.output):
        args.output = str(REPORTS_DIR / args.output)

    print("=" * 60)
    print("🤗 HF Models Scout")
    print("=" * 60)

    all_models = fetch_all_sources(days=args.days)
    if not all_models:
        print("❌ Нет моделей. Проверь интернет.")
        sys.exit(1)

    seen = set()
    unique = []
    for m in all_models:
        mid = m.get("id")
        if mid and mid not in seen:
            seen.add(mid)
            unique.append(m)
    print(f"🔍 Уникальных: {len(unique)}")

    filtered = [m for m in unique if passes_filters_basic(m, args.min_likes, args.min_downloads, args.days)]
    print(f"✅ После фильтрации: {len(filtered)}")

    if not filtered:
        generate_html({}, [], {}, args.output, args.days)
        return

    filtered = enrich_models(filtered)
    filtered = [m for m in filtered if passes_filters(m, args.min_likes, args.min_downloads, args.days)]
    print(f"✅ После обогащения: {len(filtered)}")

    if not filtered:
        generate_html({}, [], {}, args.output, args.days)
        return

    filtered = compute_scores(filtered)
    categories = sort_by_score(categorize_models(filtered))

    top_categories = {cat: lst[:args.top_per_category] for cat, lst in categories.items() if lst}
    total = sum(len(v) for v in top_categories.values())
    print(f"📊 В отчёте: {total}")

    stats = compute_stats(filtered)
    output_path = generate_html(top_categories, filtered, stats, args.output, args.days, args.top_per_category)

    try:
        import webbrowser
        webbrowser.open(f"file://{output_path}")
        print("🌐 Отчёт открыт в браузере")
    except Exception:
        pass

    print("\n✅ Готово!")


if __name__ == "__main__":
    main()
