from flask import Flask, request, jsonify, render_template
import os
import json
import csv
import io
import re
import urllib.request
import urllib.error
from datetime import datetime


# =========================================================
# EZKROY AI — GOOGLE SHEET + PROFILE + SALES AGENT
# =========================================================
#
# ANSWER PRIORITY
#
# 1. Product-specific Google Sheet
# 2. General Google Sheet
# 3. Personal Profile
# 4. Order fallback
# 5. System fallback
#
# IMPORTANT
# - NO OpenAI
# - NO ChatGPT API
# - Google Sheet = Main Knowledge Source
# - Existing products preserved
# - Profile system enabled
# - Portfolio enabled
# - 5121+ Google Sheet rows supported
#
# =========================================================


app = Flask(__name__)


# =========================================================
# GOOGLE SHEET CONFIG
# =========================================================

GOOGLE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"

GOOGLE_SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/export?format=csv"
)


# =========================================================
# PROFILE CONFIG
# =========================================================

PROFILE = {
    "name": "Asad Ullah Mozumder Aiman",
    "short_name": "Aiman",
    "role": "Student, Entrepreneur, Sales & Data Enthusiast",
    "project": "EZKROY",
    "business": "NOIR Fragrance",
    "education": "Geography student",
    "institution": "Dhaka Central University",
    "previous_institution": "Dhaka College",
    "field": "Geography",
    "hometown": "Feni, Bangladesh",
    "country": "Bangladesh",
    "portfolio": "https://sites.google.com/view/aiman-porfolio/home",
    "portfolio_name": "Aiman's Portfolio",
    "about": (
        "Aiman is a student and entrepreneur "
        "with interests in sales, data, technology "
        "and AI. He is also the founder of NOIR "
        "Fragrance and works on EZKROY, an "
        "AI-powered sales assistant project."
    ),
    "projects": ["EZKROY", "NOIR Fragrance"],
    "interests": [
        "Data Analysis",
        "Artificial Intelligence",
        "Sales",
        "Entrepreneurship",
        "Technology",
    ],
    "creator_description": (
        "Aiman is the creator and developer "
        "of the EZKROY project."
    ),
    "contact_note": (
        "For direct contact information, please "
        "refer to Aiman's portfolio."
    ),
}


# =========================================================
# PROFILE INTENTS
# =========================================================

PROFILE_INTENTS = {
    "identity": [
        "who are you",
        "who is aiman",
        "who is asad",
        "aiman ke",
        "asad ke",
        "tumi ke",
        "tomar nam",
        "your name",
        "your creator",
        "who made you",
        "who created you",
        "who designed you",
        "ke banaise",
        "ke banayse",
        "ke banaiছে",
        "ke design korse",
        "creator ke",
        "owner ke",
        "developer ke",
        "malik ke",
        "tomre ke banaise",
        "tomake ke banaise",
        "tomake ke banayse",
        "tomare ke banaise",
        "tomare ke banayse",
    ],
    "name": [
        "your name",
        "tomar nam",
        "naam ki",
        "nam ki",
        "aiman ke",
        "asad ullah aiman",
    ],
    "education": [
        "where do you study",
        "where are you studying",
        "kothay poro",
        "kothay study koro",
        "kon university",
        "kon varsity",
        "university ki",
        "college ki",
        "what do you study",
        "ki niye poro",
        "ki niye study koro",
        "subject ki",
        "department ki",
        "geography",
    ],
    "hometown": [
        "where are you from",
        "where is aiman from",
        "aiman kothay thake",
        "kothay thako",
        "hometown",
        "bari kothay",
        "gram kothay",
        "feni",
    ],
    "business": [
        "what business",
        "business ki",
        "business koren",
        "ki business",
        "noir",
        "noir fragrance",
        "perfume business",
        "perfume business ke kore",
        "who owns noir",
    ],
    "project": [
        "what is ezkroy",
        "ezkroy ki",
        "ezkroy",
        "what project",
        "project ki",
        "ai project",
        "sales ai",
        "sales agent",
    ],
    "portfolio": [
        "portfolio",
        "portfolio link",
        "show portfolio",
        "give portfolio",
        "aiman portfolio",
        "website",
        "personal website",
        "profile website",
    ],
    "about": [
        "tell me about aiman",
        "aiman somporke bolo",
        "asad somporke bolo",
        "who is asad ullah aiman",
        "aiman details",
        "about aiman",
        "aiman ke",
        "tar somporke bolo",
    ],
    "interests": [
        "interest ki",
        "ki niye interested",
        "what are your interests",
        "what does aiman like",
        "ki korte pochondo",
        "interests",
        "passion",
    ],
}


# =========================================================
# FILE PATHS
# =========================================================

DATA_DIR = "data"
PRODUCT_FILE = os.path.join(DATA_DIR, "products.json")
ORDER_FILE = os.path.join(DATA_DIR, "orders.json")

os.makedirs(DATA_DIR, exist_ok=True)


# =========================================================
# PRODUCT CATALOG
# =========================================================

INITIAL_PRODUCTS = [
    {
        "id": 1,
        "name": "212 MEN NYC",
        "price_15ml": 299,
        "regular_15ml": 599,
        "price_30ml": 549,
        "regular_30ml": 799,
        "stock": 20,
        "description": "Fresh, Urban & Confident.",
        "notes": ["Citrus", "Green", "Woody", "Spicy", "Musky"],
        "longevity": "6–8 Hours",
        "best_for": ["Daily Wear", "Office", "College", "Dates", "Casual Outings"],
    },
    {
        "id": 2,
        "name": "DUNHILL DESIRE",
        "price_15ml": 299,
        "regular_15ml": 999,
        "price_30ml": 499,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Warm, Elegant & Seductive.",
        "notes": ["Apple", "Orange", "Spicy", "Vanilla", "Woody"],
        "longevity": "6–8 Hours",
        "best_for": ["Office", "Dates", "Evening Wear", "Winter", "Casual Events"],
    },
    {
        "id": 3,
        "name": "HAWAS FIRE",
        "price_15ml": 329,
        "regular_15ml": 999,
        "price_30ml": 599,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Bold, Addictive & Magnetic.",
        "notes": ["Sweet", "Spicy", "Aquatic", "Smoky", "Amber"],
        "longevity": "7–9 Hours",
        "best_for": ["Dates", "Night Out", "Parties", "Winter", "Special Events"],
    },
    {
        "id": 4,
        "name": "ONE MILLION",
        "price_15ml": 249,
        "regular_15ml": 999,
        "price_30ml": 499,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Bold, Luxurious & Attention-Grabbing.",
        "notes": ["Sweet", "Spicy", "Citrus", "Leather", "Woody"],
        "longevity": "7–10 Hours",
        "best_for": ["Parties", "Night Out", "Dates", "Winter", "Special Events"],
    },
    {
        "id": 5,
        "name": "DIOR SAUVAGE",
        "price_15ml": 299,
        "regular_15ml": 999,
        "price_30ml": 599,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Fresh, Masculine & Long-lasting.",
        "notes": ["Woody", "Spicy", "Sweet", "Smoky"],
        "longevity": "6–8 Hours",
        "best_for": ["Daily Wear", "Office", "Dates", "Events"],
    },
    {
        "id": 6,
        "name": "NAUTICA VOYAGE",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 599,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Fresh, Clean & Everyday Confidence.",
        "notes": ["Aquatic", "Green Apple", "Fresh", "Woody"],
        "longevity": "5–7 Hours",
        "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"],
    },
    {
        "id": 7,
        "name": "HAWAS ICE",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 549,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Cool, Fresh & Addictive.",
        "notes": ["Aquatic", "Citrus", "Sweet", "Musky", "Fresh Spicy"],
        "longevity": "7–9 Hours",
        "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"],
    },
    {
        "id": 8,
        "name": "BLEU DE CHANEL",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 549,
        "regular_30ml": 999,
        "stock": 20,
        "description": "Elegant, Fresh & Sophisticated.",
        "notes": ["Citrus", "Woody", "Aromatic", "Fresh Spicy", "Incense"],
        "longevity": "7–10 Hours",
        "best_for": ["Office", "Daily Wear", "Meetings", "Dates", "Special Events"],
    },
    {
        "id": 9,
        "name": "VAMPIRE BLOOD",
        "price_15ml": 399,
        "regular_15ml": 999,
        "price_30ml": 649,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Dark, Mysterious & Seductive.",
        "notes": ["Sweet", "Spicy", "Smoky", "Amber", "Woody"],
        "longevity": "7–9 Hours",
        "best_for": ["Night Out", "Parties", "Winter", "Dates", "Special Events"],
    },
    {
        "id": 10,
        "name": "SRK (Shah Rukh Inspired)",
        "price_15ml": 299,
        "regular_15ml": 999,
        "price_30ml": 499,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Classy, Romantic & Royal.",
        "notes": ["Fresh", "Woody", "Spicy", "Soft Floral", "Amber"],
        "longevity": "6–8 Hours",
        "best_for": ["Dates", "Weddings", "Events", "Office", "Evening Wear"],
    },
    {
        "id": 11,
        "name": "STRONGER WITH YOU",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 499,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Sweet, Warm & Addictive.",
        "notes": ["Chestnut", "Vanilla", "Sweet Spicy", "Amber", "Woody"],
        "longevity": "7–10 Hours",
        "best_for": ["Dates", "Winter", "Night Out", "Parties", "Special Moments"],
    },
    {
        "id": 12,
        "name": "GUCCI FLORA",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 599,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Elegant, Feminine & Soft Luxury.",
        "notes": ["Floral", "Citrus", "Sweet", "Powdery", "Soft Woody"],
        "longevity": "5–7 Hours",
        "best_for": ["Daily Wear", "Office", "College", "Dates", "Casual Outings"],
    },
    {
        "id": 13,
        "name": "CK1",
        "price_15ml": 299,
        "regular_15ml": 799,
        "price_30ml": 499,
        "regular_30ml": 1299,
        "stock": 20,
        "description": "Clean, Iconic & Timeless.",
        "notes": ["Citrus", "Green", "Fresh Spicy", "Aromatic", "Woody"],
        "longevity": "6–8 Hours",
        "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"],
    },
    {
        "id": 14,
        "name": "9PM",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 549,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Bold, Sweet & Irresistible.",
        "notes": ["Vanilla", "Sweet", "Fruity", "Amber", "Warm Spicy"],
        "longevity": "8–10 Hours",
        "best_for": ["Date Night", "Evening Wear", "Parties", "Winter Days", "Special Occasions"],
    },
    {
        "id": 15,
        "name": "COOL WATER",
        "price_15ml": 299,
        "regular_15ml": 799,
        "price_30ml": 499,
        "regular_30ml": 1299,
        "stock": 20,
        "description": "Fresh, Clean & Timeless.",
        "notes": ["Aquatic", "Marine", "Green", "Aromatic", "Fresh Spicy"],
        "longevity": "6–8 Hours",
        "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"],
    },
    {
        "id": 16,
        "name": "LATTAFA KHAMRAH",
        "price_15ml": 399,
        "regular_15ml": 1099,
        "price_30ml": 599,
        "regular_30ml": 1699,
        "stock": 20,
        "description": "Rich, Warm & Addictive.",
        "notes": ["Cinnamon", "Vanilla", "Sweet", "Amber", "Woody", "Warm Spicy"],
        "longevity": "8–12 Hours",
        "best_for": ["Date Night", "Winter Days", "Parties", "Special Occasions", "Evening Wear"],
    },
    {
        "id": 17,
        "name": "CREED AVENTUS",
        "price_15ml": 399,
        "regular_15ml": 1199,
        "price_30ml": 599,
        "regular_30ml": 1799,
        "stock": 20,
        "description": "Bold, Powerful & Legendary.",
        "notes": ["Pineapple", "Bergamot", "Smoky", "Woody", "Musky"],
        "longevity": "8–10 Hours",
        "best_for": ["Office", "Date Night", "Parties", "Special Occasions", "Year-Round Wear"],
    },
    {
        "id": 18,
        "name": "BLUEBERRY",
        "price_15ml": 299,
        "regular_15ml": 799,
        "price_30ml": 499,
        "regular_30ml": 1299,
        "stock": 20,
        "description": "Sweet, Juicy & Addictive.",
        "notes": ["Blueberry", "Fruity", "Sweet", "Fresh", "Musky"],
        "longevity": "6–8 Hours",
        "best_for": ["Daily Wear", "College", "Casual Outings", "Hangouts", "Daytime Wear"],
    },
    {
        "id": 19,
        "name": "TOBACCO VANILLE",
        "price_15ml": 399,
        "regular_15ml": 1099,
        "price_30ml": 599,
        "regular_30ml": 1699,
        "stock": 20,
        "description": "Rich, Warm & Addictive.",
        "notes": ["Tobacco", "Vanilla", "Sweet", "Warm Spicy", "Woody"],
        "longevity": "8–12 Hours",
        "best_for": ["Date Night", "Winter Days", "Evening Wear", "Parties", "Special Occasions"],
    },
    {
        "id": 20,
        "name": "GOOD GIRL",
        "price_15ml": 399,
        "regular_15ml": 1099,
        "price_30ml": 599,
        "regular_30ml": 1699,
        "stock": 20,
        "description": "Sweet, Bold & Irresistible.",
        "notes": ["Vanilla", "White Floral", "Sweet", "Warm Spicy", "Cacao"],
        "longevity": "8–10 Hours",
        "best_for": ["Date Night", "Parties", "Evening Wear", "Special Occasions", "Winter Days"],
    },
    {
        "id": 21,
        "name": "VERSACE EROS",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 549,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Fresh, Bold & Irresistible.",
        "notes": ["Mint", "Vanilla", "Apple", "Citrus", "Woody", "Fresh Spicy"],
        "longevity": "8–10 Hours",
        "best_for": ["Date Night", "Parties", "College", "Casual Outings", "Evening Wear"],
    },
    {
        "id": 22,
        "name": "BAD BOY",
        "price_15ml": 349,
        "regular_15ml": 999,
        "price_30ml": 549,
        "regular_30ml": 1499,
        "stock": 20,
        "description": "Bold, Dark & Unapologetic.",
        "notes": ["Cocoa", "Tonka Bean", "Amber", "Citrus", "Woody", "Aromatic"],
        "longevity": "8–10 Hours",
        "best_for": ["Date Night", "Parties", "Evening Wear", "Winter Days", "Special Occasions"],
    },
]


# =========================================================
# JSON HELPERS
# =========================================================

def load_json_file(filename, default=None):
    if default is None:
        default = []
    try:
        if not os.path.exists(filename):
            return default
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except Exception as error:
        print("JSON LOAD ERROR:", error)
        return default


def save_json_file(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as error:
        print("JSON SAVE ERROR:", error)
        return False


# =========================================================
# INITIALIZE PRODUCTS
# =========================================================

def init_product_file():
    if not os.path.exists(PRODUCT_FILE):
        save_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)


init_product_file()


# =========================================================
# PRODUCTS
# =========================================================

def get_products():
    products = load_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)
    if isinstance(products, list):
        return products
    return INITIAL_PRODUCTS


# =========================================================
# ORDERS
# =========================================================

def get_orders():
    orders = load_json_file(ORDER_FILE, [])
    if isinstance(orders, list):
        return orders
    return []


# =========================================================
# GOOGLE SHEET CACHE
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None,
    "last_error": None,
    "last_url": GOOGLE_SHEET_CSV_URL,
}


# =========================================================
# GOOGLE SHEET DOWNLOAD
# =========================================================

def download_google_sheet():
    print("")
    print("=" * 70)
    print("GOOGLE SHEET: STARTING DOWNLOAD")
    print("=" * 70)
    try:
        request_object = urllib.request.Request(
            GOOGLE_SHEET_CSV_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
        )
        with urllib.request.urlopen(request_object, timeout=30) as response:
            raw_data = response.read()
            status_code = response.getcode()

        print("GOOGLE SHEET HTTP STATUS:", status_code)
        text = raw_data.decode("utf-8-sig", errors="replace")
        print("GOOGLE SHEET RAW LENGTH:", len(text))

        reader = csv.DictReader(io.StringIO(text))
        print("GOOGLE SHEET HEADERS:", reader.fieldnames)

        if not reader.fieldnames:
            raise Exception("Google Sheet CSV has no headers.")

        rows = []
        for row in reader:
            cleaned = {}
            for key, value in row.items():
                if key is None:
                    continue
                clean_key = str(key).strip().lower()
                clean_value = str(value or "").strip()
                cleaned[clean_key] = clean_value

            if any(value.strip() for value in cleaned.values()):
                rows.append(cleaned)

        required_columns = {"question", "answer", "keywords"}
        available_columns = set(rows[0].keys()) if rows else set()
        missing_columns = required_columns - available_columns

        if missing_columns:
            raise Exception(
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        sheet_cache["data"] = rows
        sheet_cache["loaded_at"] = datetime.now().isoformat()
        sheet_cache["last_error"] = None
        print("GOOGLE SHEET ROWS:", len(rows))
        if rows:
            print("FIRST SHEET ROW:", rows[0])
        print("GOOGLE SHEET: SUCCESS")
        print("=" * 70)
        return rows

    except urllib.error.HTTPError as error:
        message = f"HTTP {error.code}: {error.reason}"
        sheet_cache["last_error"] = message
        print("GOOGLE SHEET HTTP ERROR:", message)
        return sheet_cache.get("data", [])

    except urllib.error.URLError as error:
        message = f"URL ERROR: {error.reason}"
        sheet_cache["last_error"] = message
        print("GOOGLE SHEET URL ERROR:", message)
        return sheet_cache.get("data", [])

    except Exception as error:
        message = str(error)
        sheet_cache["last_error"] = message
        print("GOOGLE SHEET ERROR:", message)
        return sheet_cache.get("data", [])


# =========================================================
# GET SHEET DATA
# =========================================================

def get_sheet_data():
    if not sheet_cache["data"]:
        return download_google_sheet()
    return sheet_cache["data"]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    text = str(text or "").lower().strip()
    replacements = {
        "tmi": "tumi",
        "tmre": "tomare",
        "tmr": "tomar",
        "tmra": "tomra",
        "apnr": "apnar",
        "pls": "please",
        "plz": "please",
        "15 ml": "15ml",
        "30 ml": "30ml",
        "50 ml": "50ml",
        "৳": " taka ",
        "tk": " taka ",
        "bdt": " taka ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9\u0980-\u09ff\s:/._-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================================================
# TOKENIZE
# =========================================================

def tokenize(text):
    return set(re.findall(r"[a-z0-9\u0980-\u09ff]+", normalize_text(text)))


# =========================================================
# PROFILE ANSWER BUILDER
# =========================================================

def get_profile_answer(intent):
    if intent == "identity":
        return (
            "আমি EZKROY-এর AI sales assistant। "
            f"এই project-এর creator/developer হলেন {PROFILE['name']} ({PROFILE['short_name']})।"
        )
    if intent == "name":
        return (
            f"আমার project-এর creator/developer হলেন {PROFILE['name']}। "
            f"তাকে সাধারণত {PROFILE['short_name']} নামে ডাকা হয়।"
        )
    if intent == "education":
        return (
            f"Aiman {PROFILE['institution']}-এ {PROFILE['field']} নিয়ে পড়াশোনা করছেন। "
            f"তিনি আগে {PROFILE['previous_institution']}-এর সাথেও যুক্ত ছিলেন।"
        )
    if intent == "hometown":
        return f"Aiman-এর hometown হলো {PROFILE['hometown']}।"
    if intent == "business":
        return (
            f"Aiman-এর business project-এর মধ্যে {PROFILE['business']} উল্লেখযোগ্য। "
            "এটি একটি fragrance/perfume business।"
        )
    if intent == "project":
        return (
            f"{PROFILE['project']} হলো Aiman-এর AI-powered sales assistant project। "
            "এর লক্ষ্য হলো business-এর customer questions এবং sales process সহজ করা।"
        )
    if intent == "portfolio":
        return (
            "Aiman-এর portfolio দেখতে এখানে যেতে পারেন:\n"
            f"{PROFILE['portfolio']}"
        )
    if intent == "about":
        return PROFILE["about"]
    if intent == "interests":
        interests = ", ".join(PROFILE["interests"])
        return f"Aiman-এর প্রধান interest হলো: {interests}।"
    return None


# =========================================================
# PROFILE MATCHING (Fixed & Completed)
# =========================================================

def find_profile_answer(message):
    user_text = normalize_text(message)
    if not user_text:
        return None

    # Portfolio priority
    portfolio_terms = [
        "portfolio",
        "portfolio link",
        "website",
        "personal website",
        "show portfolio",
        "give portfolio",
        "aiman portfolio",
    ]

    for term in portfolio_terms:
        if normalize_text(term) in user_text:
            return get_profile_answer("portfolio")

    best_intent = None
    best_score = 0
    user_words = tokenize(user_text)

    for intent, phrases in PROFILE_INTENTS.items():
        score = 0
        for phrase in phrases:
            phrase_normalized = normalize_text(phrase)
            if not phrase_normalized:
                continue

            if user_text == phrase_normalized:
                score += 20
            elif phrase_normalized in user_text:
                score += 10

            phrase_words = tokenize(phrase)
            common = user_words & phrase_words
            if common:
                score += len(common) * 5

        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score >= 5 and best_intent:
        return get_profile_answer(best_intent)

    return None
