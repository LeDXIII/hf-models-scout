"""Генерация HTML-отчёта.

Компактные карточки без обложек, единый шрифт, свёрнутые категории по умолчанию.
"""

import html as html_module
from datetime import datetime, timezone
from pathlib import Path

from .filter import group_by_subcategories, subcat_count
from .config import VERIFIED_ORGS, SUBCATEGORIES


def fmt_num(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def category_icon(cat: str) -> str:
    return {
        "Vision / OCR": "👁️",
        "LLM / Text Generation": "🧠",
        "Image Generation / Editing": "🎨",
        "TTS / Audio": "🎙️",
        "Embeddings / Other": "",
        "Video Generation": "🎬",
    }.get(cat, "📋")


def score_color(score: float) -> str:
    if score >= 50:
        return "#238636"
    if score >= 25:
        return "#9e6a03"
    return "#6e7681"


def format_date(date_str: str) -> str:
    if not date_str:
        return "—"
    try:
        dt_str = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d.%m.%Y")
    except (ValueError, AttributeError):
        return "—"


def prepare_model(model: dict) -> dict:
    card_data = model.get("cardData") or {}
    desc = model.get("description", "") or card_data.get("description", "") or ""
    short = desc[:180] + "…" if len(desc) > 180 else desc

    model_id = model.get("id", "?")
    author = model_id.split("/")[0]
    pipeline = model.get("pipeline_tag", "")
    tags = model.get("tags", [])[:8]

    recency = model.get("recency_days", 999)
    kd = model.get("quality_ratio", 0)

    return {
        "id": model_id,
        "author": author,
        "is_verified": model.get("is_verified", False),
        "pipeline_tag": pipeline,
        "likes": model.get("likes", 0),
        "downloads": model.get("downloads", 0),
        "score": model.get("score", 0),
        "source": model.get("_source", ""),
        "description": html_module.escape(short) if short else "",
        "tags": [html_module.escape(t) for t in tags],
        "created_str": format_date(model.get("createdAt")),
        "modified_str": format_date(model.get("lastModified")),
        "has_space": model.get("has_space", False),
        "is_vision_llm": pipeline in ("image-text-to-text", "video-text-to-text"),
        "is_dark_horse": model.get("dark_horse_score", 0) > 0,
        "kd": kd,
        "recency": recency if recency < 999 else None,
        "size_mb": model.get("size_mb", 0),
    }


def _stats_bar(stats: dict) -> str:
    if not stats:
        return ""
    total = stats.get("total", 0)
    med_dl = stats.get("med_downloads", 0)
    med_likes = stats.get("med_likes", 0)
    med_score = stats.get("med_score", 0)
    verified = stats.get("verified_count", 0)
    dark_horses = stats.get("dark_horses_count", 0)
    leader = stats.get("trend_leader")

    parts = [
        f"{total} моделей",
        f" медиана: {fmt_num(med_dl)} скач.",
        f"❤️ {fmt_num(med_likes)} лайков",
        f"⭐ медиана score: {med_score}",
        f"✅ {verified} verified",
        f" {dark_horses} тёмных лошадок",
    ]
    if leader:
        lid = html_module.escape(leader.get("id", "?")[:40])
        ldl = fmt_num(leader.get("downloads", 0))
        parts.append(
            f'🚀 Лидер тренда: {ldl} скач. — '
            f'<a href="https://huggingface.co/{html_module.escape(leader.get("id", ""))}" '
            f'target="_blank">{lid}</a>'
        )

    return f'<div class="stats-bar">{" · ".join(parts)}</div>'


def _formula_html() -> str:
    weights = [
        ("Скачивания", "downloads / max", "12%"),
        ("Лайки", "likes / max", "12%"),
        ("Trending", "модель в тренде", "10%"),
        ("Verified", "известный автор", "10%"),
        ("Свежесть", "1 − дней/30", "8%"),
        ("Тёмная лошадка", "малоизвестна но качественна", "8%"),
        ("HF Space", "есть демо", "7%"),
        ("Model card", "есть описание", "7%"),
        ("K/D", "likes / downloads", "6%"),
        ("Pipeline tag", "указана задача", "5%"),
        ("Anomaly", "штраф за накрутку", "−5%"),
    ]
    rows = "".join(
        f'<tr><td>{name}</td><td>{desc}</td><td>{w}</td></tr>'
        for name, desc, w in weights
    )
    return f'''
<details class="formula-details">
    <summary>Как рассчитывается Total Score</summary>
    <div class="formula-body">
        <table class="formula-table">
            <thead><tr><th>Метрика</th><th>Формула</th><th>Вес</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
</details>'''


def _card(m: dict, rank: int = None) -> str:
    rank_html = ""
    if rank is not None:
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        rank_html = f'<span class="rank">{medal}</span>'

    badges = []
    if m["source"] == "trending":
        badges.append('<span class="badge badge-hot">trending</span>')
    if m["is_verified"]:
        badges.append('<span class="badge badge-ok">verified</span>')
    if m["is_vision_llm"]:
        badges.append('<span class="badge badge-eye">vision</span>')
    if m["is_dark_horse"]:
        badges.append('<span class="badge badge-horse">dark horse</span>')
    if m["has_space"]:
        badges.append('<span class="badge badge-space">space</span>')
    if m["pipeline_tag"]:
        badges.append(f'<span class="badge">{html_module.escape(m["pipeline_tag"])}</span>')

    tags_html = "".join(f'<span class="tag">{t}</span>' for t in m["tags"]) if m["tags"] else ""

    kd_str = f"{m['kd']:.3f}"
    rec_str = str(m["recency"]) if m["recency"] is not None else "—"

    score_col = score_color(m["score"])

    desc_block = f'<div class="desc">{m["description"]}</div>' if m["description"] else ""

    return f'''
<div class="card">
    {rank_html}
    <div class="card-body">
        <div class="card-top">
            <div>
                <a class="card-title" href="https://huggingface.co/{html_module.escape(m["id"])}" target="_blank">{html_module.escape(m["id"])}</a>
                <div class="card-author">{html_module.escape(m["author"])}</div>
            </div>
            <div class="card-score" style="background:{score_col}">⭐ {m["score"]}</div>
        </div>
        <div class="badges-row">{" ".join(badges)}</div>
        {f'<div class="tags-row">{tags_html}</div>' if tags_html else ""}
        <div class="metrics">
            <div class="m"><div class="m-val">❤️ {fmt_num(m["likes"])}</div><div class="m-lbl">лайков</div></div>
            <div class="m"><div class="m-val">{fmt_num(m["downloads"])}</div><div class="m-lbl">скач.</div></div>
            <div class="m"><div class="m-val">{kd_str}</div><div class="m-lbl">K/D</div></div>
            <div class="m"><div class="m-val">{rec_str}</div><div class="m-lbl">дн. назад</div></div>
        </div>
        {desc_block}
        <div class="card-date">📅 {m["created_str"]}</div>
    </div>
</div>'''


def _cards_section(models: list[dict], title: str, desc: str = "", show_rank: bool = True, limit: int = None) -> str:
    items = models[:limit] if limit else models
    cards = "".join(
        _card(m, rank=i + 1 if show_rank else None)
        for i, m in enumerate(items)
    )
    desc_html = f'<p class="sec-desc">{desc}</p>' if desc else ""
    return f'<section><h2>{title}</h2>{desc_html}<div class="grid">{cards}</div></section>'


def _tabs() -> str:
    return '''
<div class="tabs">
    <button class="tab-btn active" data-tab="top"> ТОП</button>
    <button class="tab-btn" data-tab="downloads">📥 По скачиваниям</button>
    <button class="tab-btn" data-tab="likes">❤️ По лайкам</button>
    <button class="tab-btn" data-tab="dark-horses">🐎 Тёмные лошадки</button>
    <button class="tab-btn" data-tab="categories"> По категориям</button>
</div>'''


def generate_html(
    categories: dict[str, list[dict]],
    all_models: list[dict],
    stats: dict,
    output_path: str,
    days: int,
    top_per_category: int = 30,
) -> Path:
    print("\n📝 Генерация HTML-отчёта...")

    prepared = [prepare_model(m) for m in all_models]

    top = sorted(prepared, key=lambda m: m["score"], reverse=True)[:top_per_category * len(categories)]
    by_dl = sorted(prepared, key=lambda m: m["downloads"], reverse=True)[:top_per_category * len(categories)]
    by_likes = sorted(prepared, key=lambda m: m["likes"], reverse=True)[:top_per_category * len(categories)]
    dark_horses = sorted(
        [m for m in prepared if m["is_dark_horse"]],
        key=lambda m: m["score"], reverse=True,
    )

    cat_cards = {}
    for cat, models in categories.items():
        p = [prepare_model(m) for m in models[:top_per_category]]
        p.sort(key=lambda m: m["score"], reverse=True)
        cat_cards[cat] = p

    # Группировка по подкатегориям для таба «По категориям»
    cat_subcats = {}
    for cat, models in categories.items():
        subcats = group_by_subcategories(models[:top_per_category], cat)
        prepared_subcats = {}
        for sn, sm in subcats.items():
            prepared_subcats[sn] = sorted(
                [prepare_model(m) for m in sm], key=lambda m: m["score"], reverse=True
            )
        cat_subcats[cat] = prepared_subcats

    generated_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HF Models Scout Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    background: #667eea;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 24px;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    background: #f5f5f7;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
}}

h1 {{
    text-align: center;
    font-size: 1.8em;
    color: #1a1a2e;
    margin-bottom: 4px;
}}

.gen-date {{
    text-align: center;
    color: #888;
    font-size: 0.85em;
    margin-bottom: 20px;
}}

.stats-bar {{
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
    padding: 10px 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    font-size: 0.85em;
    text-align: center;
}}
.stats-bar a {{ color: #ffd700; text-decoration: none; }}
.stats-bar a:hover {{ text-decoration: underline; }}

.formula-details {{
    background: #fff;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    overflow: hidden;
}}
.formula-details summary {{
    padding: 10px 16px;
    cursor: pointer;
    font-weight: 600;
    color: #667eea;
    font-size: 0.9em;
    list-style: none;
}}
.formula-details summary::-webkit-details-marker {{ display: none; }}
.formula-details summary::before {{
    content: '▶';
    display: inline-block;
    margin-right: 6px;
    font-size: 10px;
    transition: transform .2s;
}}
.formula-details[open] summary::before {{ transform: rotate(90deg); }}
.formula-body {{ padding: 12px 16px; border-top: 1px solid #eee; }}
.formula-table {{ width: 100%; border-collapse: collapse; font-size: 0.85em; }}
.formula-table th {{ background: #667eea; color: #fff; padding: 6px 10px; text-align: left; }}
.formula-table td {{ padding: 5px 10px; border-bottom: 1px solid #eee; }}
.formula-table tr:last-child td {{ border-bottom: none; }}

.tabs {{
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    justify-content: center;
}}
.tab-btn {{
    background: #fff;
    border: 2px solid #ddd;
    padding: 8px 18px;
    border-radius: 24px;
    cursor: pointer;
    font-size: 0.9em;
    font-weight: 500;
    transition: all .2s;
}}
.tab-btn:hover, .tab-btn.active {{
    background: #667eea;
    color: #fff;
    border-color: #667eea;
}}

.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

section {{ margin-bottom: 32px; }}
section h2 {{
    font-size: 1.3em;
    color: #1a1a2e;
    margin-bottom: 6px;
    padding-bottom: 6px;
    border-bottom: 2px solid #667eea;
}}
.sec-desc {{
    color: #888;
    font-size: 0.9em;
    font-style: italic;
    margin-bottom: 16px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 12px;
}}

.card {{
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    padding: 14px 16px;
    transition: transform .15s, box-shadow .15s;
    position: relative;
}}
.card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.18);
}}

.rank {{
    position: absolute;
    top: 12px;
    left: 12px;
    font-size: 0.85em;
    font-weight: 700;
    background: rgba(0,0,0,0.06);
    border-radius: 50%;
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.card-body {{ padding: 0 12px 0 44px; }}

.card-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 6px;
}}
.card-title {{
    font-size: 1em;
    font-weight: 700;
    color: #667eea;
    text-decoration: none;
    word-break: break-word;
}}
.card-title:hover {{ text-decoration: underline; }}
.card-author {{ color: #888; font-size: 0.85em; }}

.card-score {{
    padding: 4px 10px;
    border-radius: 14px;
    font-weight: 700;
    font-size: 0.85em;
    color: #fff;
    white-space: nowrap;
}}

.badges-row {{
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}}
.badge {{
    padding: 1px 7px;
    border-radius: 5px;
    font-size: 0.7em;
    background: #f0f0f0;
    color: #555;
    border: 1px solid #ddd;
}}
.badge-hot {{ background: #fff3e0; border-color: #ff9800; color: #e65100; }}
.badge-ok {{ background: #e8f5e9; border-color: #4caf50; color: #2e7d32; }}
.badge-eye {{ background: #e3f2fd; border-color: #2196f3; color: #1565c0; }}
.badge-horse {{ background: #fff8e1; border-color: #ffc107; color: #f57f17; }}
.badge-space {{ background: #e8f5e9; border-color: #4caf50; color: #2e7d32; }}

.tags-row {{
    display: flex;
    gap: 3px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}}
.tag {{
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.65em;
    background: #f5f5f5;
    color: #777;
}}

.metrics {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4px;
    margin-bottom: 8px;
}}
.m {{
    text-align: center;
    background: #f8f9fa;
    padding: 6px 2px;
    border-radius: 6px;
}}
.m-val {{ font-weight: 700; font-size: 0.9em; color: #1a1a2e; }}
.m-lbl {{ font-size: 0.7em; color: #999; }}

.desc {{
    color: #666;
    font-size: 0.85em;
    margin-bottom: 6px;
    line-height: 1.4;
}}

.card-date {{
    font-size: 0.75em;
    color: #aaa;
}}

/* Категории-аккордеон */
.cat-accordion {{
    background: #fff;
    border-radius: 10px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    overflow: hidden;
}}
.cat-accordion > summary {{
    padding: 12px 16px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1.05em;
    color: #1a1a2e;
    list-style: none;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.cat-accordion > summary::-webkit-details-marker {{ display: none; }}
.cat-accordion > summary::before {{
    content: '▶';
    display: inline-block;
    font-size: 10px;
    transition: transform .2s;
}}
.cat-accordion[open] > summary::before {{ transform: rotate(90deg); }}
.cat-accordion > summary:hover {{ background: #f8f9fa; }}

.subcat {{
    background: #fafafa;
    padding: 8px 16px 8px 28px;
    border-top: 1px solid #eee;
}}
.subcat-title {{
    font-weight: 600;
    font-size: 0.9em;
    color: #667eea;
    margin-bottom: 8px;
}}

.no-data {{
    text-align: center;
    padding: 40px;
    color: #888;
    font-size: 1.1em;
}}

@media (max-width: 768px) {{
    .grid {{ grid-template-columns: 1fr; }}
    .metrics {{ grid-template-columns: repeat(2, 1fr); }}
    .tabs {{ gap: 4px; }}
    .tab-btn {{ padding: 6px 12px; font-size: 0.8em; }}
    h1 {{ font-size: 1.4em; }}
}}
</style>
</head>
<body>
<div class="container">
    <h1>🤗 HF Models Scout Report</h1>
    <div class="gen-date">{generated_at} · Поиск за {days} дней</div>

    {_stats_bar(stats)}
    {_formula_html()}
    {_tabs()}

    <div id="tab-top" class="tab-content active">
        {_cards_section(top, "🏆 ТОП моделей", "Лучшие модели по композитному скорингу")}
    </div>
    <div id="tab-downloads" class="tab-content">
        {_cards_section(by_dl, "📥 ТОП по скачиваниям", "Модели с наибольшим количеством скачиваний")}
    </div>
    <div id="tab-likes" class="tab-content">
        {_cards_section(by_likes, "❤️ ТОП по лайкам", "Модели с наибольшим количеством лайков")}
    </div>
    <div id="tab-dark-horses" class="tab-content">
        {f'<section><h2>🐎 Тёмные лошадки</h2><p class="sec-desc">Малоизвестные модели с высоким K/D</p><div class="grid">{"".join(_card(m) for m in dark_horses)}</div></section>' if dark_horses else '<div class="no-data">Тёмных лошадок не найдено</div>'}
    </div>
    <div id="tab-categories" class="tab-content">
'''

    # По категориям — аккордеон, свёрнут по умолчанию
    cat_parts = []
    for cat, subcats in cat_subcats.items():
        if not subcats:
            continue
        icon = category_icon(cat)
        subcat_html = ""
        for sn, sm in subcats.items():
            cards = "".join(_card(m) for m in sm)
            subcat_html += f'<div class="subcat"><div class="subcat-title">{sn} ({len(sm)})</div><div class="grid">{cards}</div></div>'

        cat_parts.append(
            f'<details class="cat-accordion">'
            f'<summary>{icon} {cat}</summary>'
            f'{subcat_html}'
            f'</details>'
        )

    html += "".join(cat_parts)
    html += '''
    </div>
</div>

<script>
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        btn.classList.add('active');
    });
});
</script>
</body>
</html>'''

    output = Path(output_path).resolve()
    output.write_text(html, encoding="utf-8")
    print(f"✅ Отчёт сохранён: {output}")
    return output
