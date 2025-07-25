import os
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

CRAWL_SETTINGS = {
    "delay_range": (1, 3),
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "ArrowScraper/1.0 (Educational Research)"
}

MANUFACTURERS = {
    "easton": {
        "name": "Easton Archery",
        "base_url": "https://eastonarchery.com",
        "categories": {
            "hunting": "https://eastonarchery.com/huntingarrows/",
            "indoor": "https://eastonarchery.com/indoor/",
            "outdoor": "https://eastonarchery.com/outdoor/",
            "3d": "https://eastonarchery.com/3d/",
            "target": "https://eastonarchery.com/targetarrows/",
            "recreational": "https://eastonarchery.com/recreational/"
        }
    },
    "goldtip": {
        "name": "Gold Tip",
        "base_url": "https://www.goldtip.com",
        "categories": {
            "hunting": "https://www.goldtip.com/hunting-arrows/",
            "target": "https://www.goldtip.com/target-arrows/"
        }
    },
    "victory": {
        "name": "Victory Archery",
        "base_url": "https://www.victoryarchery.com",
        "categories": {
            "hunting": "https://www.victoryarchery.com/arrows-hunting/",
            "target": "https://www.victoryarchery.com/arrows-target/"
        }
    },
    "skylon": {
        "name": "Skylon Archery",
        "base_url": "https://www.skylonarchery.com",
        "arrows": [
            "https://www.skylonarchery.com/arrows/id-3-2/performa",
            "https://www.skylonarchery.com/arrows/id-3-2/precium",
            "https://www.skylonarchery.com/arrows/id-3-2/paragon"
        ]
    }
}

ARROW_SCHEMA = {
    "required_fields": [
        "manufacturer",
        "model_name",
        "spine_options",
        "diameter",
        "gpi_weight"
    ],
    "optional_fields": [
        "length_options",
        "straightness_tolerance",
        "weight_tolerance",
        "material",
        "carbon_content",
        "arrow_type",
        "recommended_use",
        "price_range",
        "availability"
    ]
}