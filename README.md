# 🤗 HF Models Scout v1.0

Мониторинг Hugging Face — собирает новые и трендовые модели, фильтрует по метрикам и генерирует HTML-отчёт с рейтингами.

 [Русская документация](#-русская-документация) | 🇧 [English](#-english-documentation)

---

## ✨ Возможности

* **3 источника данных:** новые (`createdAt`), обновлённые (`lastModified`), трендовые (`trendingScore`)
* **Композитный скоринг:** 10 метрик + штраф — взвешенная комбинация (0–100)
* **Тёмные лошадки:** автоматическое обнаружение малоизвестных моделей с высоким качеством
* **6 категорий:** LLM, Vision/OCR, Audio, Image Gen, Video Gen, Embeddings
* **5 вкладок отчёта:** ТОП, по скачиваниям, по лайкам, тёмные лошадки, по категориям
* **Бейджи:** trending, verified, vision, dark horse, space
* **Компактный HTML-отчёт** — один файл, никаких зависимостей для просмотра

##  Требования

| | Минимум | Рекомендация |
|---|---|---|
| ОС | Windows 10/11 | Windows 10/11 |
| Python | 3.10+ | 3.10+ |
| ОЗУ | 2 GB | 4+ GB |
| Диск | 10 MB | 50+ MB |
| Интернет | ✅ | ✅ |

##  Установка

```bash
git clone https://github.com/LeDXIII/hf-models-scout.git
cd hf-models-scout
install.bat
```

`install.bat` автоматически обновит pip и установит зависимости (`requests`, `jinja2`).

Или вручную:

```bash
pip install -e .
```

## 🚀 Запуск

Через батники (рекомендуется):

| Файл | Период | Моделей на категорию |
|------|--------|----------------------|
| `1-quick-scan.bat` | 7 дней | 10 |
| `2-full-scan.bat` | 30 дней | 30 |
| `3-deep-scan.bat` | 90 дней | 50 |
| `4-test-scan.bat` | 3 дня | 5 |

Или через CLI:

```bash
hf-scout --days 30 --top-per-category 30 --min-likes 3 --min-downloads 30
```

## 🎯 Использование

1. **Запустите** один из батников или `hf-scout` в терминале
2. **Дождитесь** сбора и обработки моделей (2100+ моделей с 3 источников)
3. **Отчёт автоматически откроется** в браузере
4. **Отчёт сохраняется** в папку `reports/report-YYYY-MM-DD-HHMM.html`

### Параметры CLI

| Параметр | По умолчанию | Описание |
|----------|-------------|----------|
| `--days` | 30 | Период поиска в днях |
| `--top-per-category` | 30 | Макс. моделей на категорию |
| `--min-likes` | 3 | Минимум лайков |
| `--min-downloads` | 30 | Минимум скачиваний |
| `--output` | `reports/` | Путь к отчёту |

## 📊 Как рассчитывается Total Score

Score (0–100) — взвешенная сумма нормализованных метрик:

| Метрика | Вес | Формула |
|---------|-----|---------|
| Скачивания | 12% | downloads / max_downloads |
| Лайки | 12% | likes / max_likes |
| Trending | 10% | модель в тренде HF |
| Verified | 10% | автор из списка известных |
| Свежесть | 8% | 1 − дней/30 |
| Тёмная лошадка | 8% | малоизвестна но с высоким K/D |
| HF Space | 7% | есть демо |
| Model card | 7% | есть описание |
| K/D | 6% | likes / downloads |
| Pipeline tag | 5% | указана задача |
| Anomaly | −5% | штраф за накрутку |

## 📦 Категории

| Категория | Подкатегории |
|-----------|-------------|
|  LLM / Text Generation | Text Generation, Conversational, Vision-Language, Understanding |
| ️ Vision / OCR | OCR, Image Classification, Object Detection, Segmentation |
| ️ TTS / Audio | Text-to-Speech, Speech Recognition, Audio Processing, Music |
|  Image Generation | Text-to-Image, Image Editing, Image Generation |
| 🎬 Video Generation | Text-to-Video, Video Editing |
| 📦 Embeddings / Other | Embeddings, Other ML |

## 📁 Структура проекта

```
hf-models-scout/
├── src/hf_models_scout/
│   ├── __init__.py       # версия пакета
│   ├── config.py         # категории, пороги, verified-организации
│   ├── fetcher.py        # сбор данных с HF API
│   ├── filter.py         # фильтрация, скоринг, статистика
│   ├── reporter.py       # генерация HTML-отчёта
│   └── scout.py          # CLI entry point
├── reports/              # папка для отчётов
├── install.bat
├── 1-quick-scan.bat
├── 2-full-scan.bat
├── 3-deep-scan.bat
├── 4-test-scan.bat
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 🇬🇧 English Documentation

### Overview
A Hugging Face monitoring tool that collects new and trending models, filters by metrics, and generates an HTML report with rankings.

### Features
* **3 data sources:** new (`createdAt`), updated (`lastModified`), trending (`trendingScore`)
* **Composite scoring:** 10 metrics + penalty — weighted combination (0–100)
* **Dark horses:** automatic discovery of lesser-known models with high quality
* **6 categories:** LLM, Vision/OCR, Audio, Image Gen, Video Gen, Embeddings
* **5 report tabs:** TOP, by downloads, by likes, dark horses, by categories
* **Badges:** trending, verified, vision, dark horse, space
* **Compact HTML report** — single file, no dependencies to view

### Requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10/11 | Windows 10/11 |
| Python | 3.10+ | 3.10+ |
| RAM | 2 GB | 4+ GB |
| Disk | 10 MB | 50+ MB |
| Internet | ✅ | ✅ |

### Installation

```bash
git clone https://github.com/LeDXIII/hf-models-scout.git
cd hf-models-scout
install.bat
```

`install.bat` automatically updates pip and installs dependencies (`requests`, `jinja2`).

Or manually:

```bash
pip install -e .
```

### Launch

Via batch files (recommended):

| File | Period | Models per category |
|------|--------|---------------------|
| `1-quick-scan.bat` | 7 days | 10 |
| `2-full-scan.bat` | 30 days | 30 |
| `3-deep-scan.bat` | 90 days | 50 |
| `4-test-scan.bat` | 3 days | 5 |

Or via CLI:

```bash
hf-scout --days 30 --top-per-category 30 --min-likes 3 --min-downloads 30
```

### Usage

1. **Run** one of the batch files or `hf-scout` in terminal
2. **Wait** for collection and processing (2100+ models from 3 sources)
3. **Report opens automatically** in your browser
4. **Report is saved** to `reports/report-YYYY-MM-DD-HHMM.html`

### CLI Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--days` | 30 | Search period in days |
| `--top-per-category` | 30 | Max models per category |
| `--min-likes` | 3 | Minimum likes |
| `--min-downloads` | 30 | Minimum downloads |
| `--output` | `reports/` | Report output path |

### How Total Score Works

Score (0–100) — weighted sum of normalized metrics:

| Metric | Weight | Formula |
|--------|--------|---------|
| Downloads | 12% | downloads / max_downloads |
| Likes | 12% | likes / max_likes |
| Trending | 10% | model is trending on HF |
| Verified | 10% | author from known orgs list |
| Freshness | 8% | 1 − days/30 |
| Dark Horse | 8% | little-known but high K/D |
| HF Space | 7% | has demo |
| Model Card | 7% | has description |
| K/D | 6% | likes / downloads |
| Pipeline Tag | 5% | task specified |
| Anomaly | −5% | penalty for suspicious patterns |

### Categories

| Category | Subcategories |
|----------|---------------|
| 🧠 LLM / Text Generation | Text Generation, Conversational, Vision-Language, Understanding |
| 👁️ Vision / OCR | OCR, Image Classification, Object Detection, Segmentation |
| 🎙️ TTS / Audio | Text-to-Speech, Speech Recognition, Audio Processing, Music |
| 🎨 Image Generation | Text-to-Image, Image Editing, Image Generation |
| 🎬 Video Generation | Text-to-Video, Video Editing |
|  Embeddings / Other | Embeddings, Other ML |

### Project Structure

```
hf-models-scout/
├── src/hf_models_scout/
│   ├── __init__.py       # package version
│   ├── config.py         # categories, thresholds, verified orgs
│   ├── fetcher.py        # data collection from HF API
│   ├── filter.py         # filtering, scoring, statistics
│   ├── reporter.py       # HTML report generation
│   ── scout.py          # CLI entry point
├── reports/              # report output folder
├── install.bat
├── 1-quick-scan.bat
├── 2-full-scan.bat
├── 3-deep-scan.bat
├── 4-test-scan.bat
── pyproject.toml
├── requirements.txt
└── README.md
```

---

⭐ Star this repository if it was helpful!

## Лицензия

MIT License — свободное использование, модификация и распространение.
