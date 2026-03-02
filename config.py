import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = DATA_DIR

PRODUCTION = os.getenv("PRODUCTION", "false").lower() in ("true", "1", "yes")

SSH_CONFIG = {
    "enabled": os.getenv("SSH_ENABLED", "false").lower() in ("true", "1", "yes"),
    "host": os.getenv("SSH_HOST", ""),
    "port": int(os.getenv("SSH_PORT", 22)),
    "user": os.getenv("SSH_USER", ""),
    "password": os.getenv("SSH_PASSWORD", "") or None,
    "key_path": os.getenv("SSH_KEY_PATH", "") or None,
}

PG_CONFIG = {
    "host": os.getenv("PG_HOST", "127.0.0.1"),
    "port": int(os.getenv("PG_PORT", 5432)),
    "database": os.getenv("PG_DATABASE", "telegram_news"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", ""),
    "remote_port": int(os.getenv("PG_REMOTE_PORT", 0) or os.getenv("PG_PORT", 5432)),
    "table_name": os.getenv("PG_TABLE_NAME", "") or None,
}

CSV_DATA_PATH = os.getenv("CSV_DATA_PATH", str(DATA_DIR / "messages.csv"))
CACHE_PATH = str(CACHE_DIR / "cache.parquet")

if PRODUCTION and not PG_CONFIG["password"]:
    logger.warning("PRODUCTION mode but PG_PASSWORD is not set!")

# Categories from the actual data
EVENT_CATEGORIES = ["security", "accident", "politics", "general", "international"]

CATEGORY_LABELS = {
    "security": {"ru": "Безопасность", "en": "Security", "color": "#ff4444"},
    "accident": {"ru": "Происшествия", "en": "Accidents", "color": "#ffa502"},
    "politics": {"ru": "Политика", "en": "Politics", "color": "#7bed9f"},
    "general": {"ru": "Общее", "en": "General", "color": "#70a1ff"},
    "international": {"ru": "Международное", "en": "International", "color": "#a29bfe"},
}

# Known data sources from the dataset
DATA_SOURCES = {
    "חדשות 100שטח": "Yediot News 25 (HE)",
    "ИнтеллиНьюз - Израиль и Ближний Восток. Все о безопасности": "IntelliNews (RU)",
    "🔞 חדשות ישראל | ללא צנזורה חדשות ישראל": "Israel News Uncensored (HE)",
    "חדשות ישראל בטלגרם": "Israel News Telegram (HE)",
}

# Keywords for escalation signal detection (used on translation columns)
IRAN_KEYWORDS = {
    "ru": [
        "иран", "тегеран", "хаменеи", "ксир", "натанз", "фордо",
        "ормузский", "хезболла", "ядерная программа", "обогащение урана",
        "баллистическ", "ракетный удар", "прокси", "ось сопротивления",
        "санкции против ирана", "иранская угроза", "цахал", "операция",
        "массированн", "бомбардировщик", "перехват", "сирена", "укрытие",
        "эскалация", "корпус стражей", "пезешкиан",
    ],
    "en": [
        "iran", "tehran", "khamenei", "irgc", "natanz", "fordow",
        "hormuz", "hezbollah", "nuclear program", "uranium enrichment",
        "ballistic", "missile strike", "proxy", "axis of resistance",
        "iran sanctions", "iranian threat", "centrifuge", "idf",
        "operation", "b-2", "intercept", "siren", "shelter", "escalation",
        "revolutionary guard", "pezeshkian",
    ],
    "he": [
        "איראן", "טהרן", "חמינאי", "משמרות המהפכה", "נתנז",
        "פורדו", "הורמוז", "חיזבאללה", "גרעין", "העשרת אורניום",
        "בליסטי", "ציר ההתנגדות", "סנקציות", "צה\"ל", "מבצע",
        "תקיפה", "יירוט", "אזעקה", "מקלט", "הסלמה",
    ],
}

ESCALATION_CATEGORIES = {
    "military_action": {
        "ru": ["удар", "атака", "бомбардировка", "тегеран", "операция", "истребитель",
               "волна атак", "уничтожил", "потопил", "b-2", "цахал"],
        "en": ["strike", "attack", "bombing", "tehran", "operation", "fighter jet",
               "wave of attacks", "destroyed", "sank", "b-2", "idf"],
    },
    "casualties_damage": {
        "ru": ["погибш", "ранен", "пострадавш", "жертв", "разрушен", "обломк",
               "эвакуац", "спасательн", "попадание", "падение ракеты"],
        "en": ["killed", "injured", "casualt", "victim", "destroyed", "rubble",
               "evacuat", "rescue", "direct hit", "missile fall"],
    },
    "diplomatic_political": {
        "ru": ["нетаньяху", "заявление", "совещание", "санкции", "ультиматум",
               "дипломат", "президент", "министр", "переговор"],
        "en": ["netanyahu", "statement", "meeting", "sanctions", "ultimatum",
               "diplomat", "president", "minister", "negotiat"],
    },
    "missile_defense": {
        "ru": ["сирена", "перехват", "укрытие", "командование тыла",
               "цева адом", "воздушное пространство", "ракета", "дрон", "бпла"],
        "en": ["siren", "intercept", "shelter", "home front command",
               "red alert", "airspace", "missile", "drone", "uav"],
    },
    "regional_escalation": {
        "ru": ["абу-даби", "дубай", "бахрейн", "хуситы", "бин салман",
               "маэрск", "баб-эль-мандеб", "оманский залив"],
        "en": ["abu dhabi", "dubai", "bahrain", "houthi", "bin salman",
               "maersk", "bab-el-mandeb", "gulf of oman"],
    },
}

SENTIMENT_MODEL = "cardiffnlp/twitter-xlm-roberta-base-sentiment-multilingual"
NER_MODEL = "Davlan/xlm-roberta-large-ner-hrl"
