"""Конфигурация: категории, подкатегории, пороги, verified-организации."""

# ─── Пороги ────────────────────────────────────────────────────────────────────

MIN_LIKES = 3
MIN_DOWNLOADS = 30
MAX_AGE_DAYS = 30
TOP_PER_CATEGORY = 30

# ─── Веса метрик ───────────────────────────────────────────────────────────────

THRESHOLDS = {
    "dark_horse_downloads_max": 10_000,
    "dark_horse_likes_max": 50,
    "quality_ratio_min": 0.05,
    "anomaly_likes_downloads_ratio_max": 0.5,
}

# ─── Категории ─────────────────────────────────────────────────────────────────

CATEGORIES = {
    "LLM / Text Generation": {
        "pipeline_tags": [
            "text-generation", "text2text-generation", "fill-mask",
            "token-classification", "question-answering", "text-classification",
            "zero-shot-classification", "conversational",
            "image-text-to-text", "video-text-to-text",
        ],
    },
    "Vision / OCR": {
        "pipeline_tags": [
            "image-to-text", "image-classification", "object-detection",
            "depth-estimation", "image-segmentation", "image-feature-extraction",
            "zero-shot-image-classification", "mask-generation",
            "document-question-answering", "visual-question-answering",
            "video-classification", "keypoint-detection",
        ],
    },
    "TTS / Audio": {
        "pipeline_tags": [
            "text-to-speech", "text-to-audio", "automatic-speech-recognition",
            "audio-classification", "audio-to-audio", "voice-activity-detection",
            "music-generation", "audio-text-to-text",
        ],
    },
    "Image Generation / Editing": {
        "pipeline_tags": [
            "text-to-image", "image-to-image",
            "unconditional-image-generation", "class-conditional-image-generation",
        ],
    },
    "Video Generation": {
        "pipeline_tags": ["text-to-video", "video-to-video", "image-to-video"],
    },
    "Embeddings / Other": {
        "pipeline_tags": [
            "feature-extraction", "sentence-similarity", "reinforcement-learning",
            "robotics", "tabular-classification", "tabular-regression",
            "zero-shot-object-detection", "graph-ml",
            "time-series-forecasting", "any-to-any",
        ],
    },
}

# ─── Подкатегории ──────────────────────────────────────────────────────────────

SUBCATEGORIES = {
    "LLM / Text Generation": {
        "Text Generation": ["text-generation", "text2text-generation"],
        "Conversational / Chat": ["conversational"],
        "Vision-Language": ["image-text-to-text", "video-text-to-text"],
        "Understanding / Classification": [
            "fill-mask", "token-classification", "question-answering",
            "text-classification", "zero-shot-classification",
        ],
    },
    "Vision / OCR": {
        "OCR": ["image-to-text"],
        "Image Classification": [
            "image-classification", "zero-shot-image-classification",
            "image-feature-extraction",
        ],
        "Object Detection": ["object-detection", "keypoint-detection"],
        "Segmentation / Depth": [
            "image-segmentation", "mask-generation", "depth-estimation",
        ],
        "Video Understanding": ["video-classification"],
        "Other Vision": ["document-question-answering", "visual-question-answering"],
    },
    "TTS / Audio": {
        "Text-to-Speech": ["text-to-speech", "text-to-audio"],
        "Speech Recognition": ["automatic-speech-recognition", "audio-text-to-text"],
        "Audio Processing": ["audio-classification", "audio-to-audio", "voice-activity-detection"],
        "Music Generation": ["music-generation"],
    },
    "Image Generation / Editing": {
        "Text-to-Image": ["text-to-image"],
        "Image Editing": ["image-to-image"],
        "Image Generation": ["unconditional-image-generation", "class-conditional-image-generation"],
    },
    "Video Generation": {
        "Text-to-Video": ["text-to-video"],
        "Video Editing": ["video-to-video", "image-to-video"],
    },
    "Embeddings / Other": {
        "Embeddings": ["feature-extraction", "sentence-similarity"],
        "Other ML": [
            "reinforcement-learning", "robotics", "tabular-classification",
            "tabular-regression", "zero-shot-object-detection", "graph-ml",
            "time-series-forecasting", "any-to-any",
        ],
    },
}

# ─── Verified организации ──────────────────────────────────────────────────────

VERIFIED_ORGS = [
    "meta-llama", "deepseek-ai", "stabilityai", "Qwen", "mistralai",
    "openai", "black-forest-labs", "microsoft", "google", "zai-org",
    "moonshotai", "hexgrad", "nvidia", "bigscience", "facebook",
    "tiiuae", "tencent", "minimaxai", "coqui", "openai-community",
    "briaai", "pyannote", "bigcode", "baai", "openbmb", "xai-org",
    "sesame", "huggingfaceh4", "coherelabs", "docling-project",
    "google-bert", "compvis", "lllyasviel", "prompthero",
    "tongyi-mai", "lightricks", "warriormama777", "phr00t",
    "h94", "hakurei", "xinsir", "2noise", "nanonets", "nari-labs",
    "jackrong", "mattshumer", "dreamlike-art",
    "unsloth", "thebloke", "bartowski", "maziyarpanahi",
    "sakanai", "thudm", "01-ai", "internlm", "cohereforai",
    "cohere", "kohya-ss", "jeromeku", "cagliostrolab",
    "laion", "common-pool", "facebookresearch", "google-research",
    "vikhyatk", "lmms-lab", "byteflow", "kwai-kolors",
    "tencentarc", "felixhugo", "distilabel", "plabs",
    "salesforce", "amazon", "intel", "amd", "alibaba",
]

HF_API = "https://huggingface.co/api/models"
