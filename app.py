```python
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
# EZKROY AI — SHEET ONLY SALES AGENT
# =========================================================
#
# IMPORTANT:
# - NO OpenAI
# - NO ChatGPT
# - NO AI fallback
# - Answers come ONLY from Google Sheet
# - Product catalog is used only for product recognition
# - If Sheet has no matching answer, bot says so
#
# =========================================================


app = Flask(__name__)


# =========================================================
# GOOGLE SHEET CONFIG
# =========================================================

GOOGLE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"

GOOGLE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/export?format=csv"
)


# =========================================================
# FILE PATHS
# =========================================================

DATA_DIR = "data"

PRODUCT_FILE = os.path.join(
    DATA_DIR,
    "products.json"
)

ORDER_FILE = os.path.join(
    DATA_DIR,
    "orders.json"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


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
        "notes": [
            "Citrus",
            "Green",
            "Woody",
            "Spicy",
            "Musky"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Daily Wear",
            "Office",
            "College",
            "Dates",
            "Casual Outings"
        ]
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
        "notes": [
            "Apple",
            "Orange",
            "Spicy",
            "Vanilla",
            "Woody"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Office",
            "Dates",
            "Evening Wear",
            "Winter",
            "Casual Events"
        ]
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
        "notes": [
            "Sweet",
            "Spicy",
            "Aquatic",
            "Smoky",
            "Amber"
        ],
        "longevity": "7–9 Hours",
        "best_for": [
            "Dates",
            "Night Out",
            "Parties",
            "Winter",
            "Special Events"
        ]
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
        "notes": [
            "Sweet",
            "Spicy",
            "Citrus",
            "Leather",
            "Woody"
        ],
        "longevity": "7–10 Hours",
        "best_for": [
            "Parties",
            "Night Out",
            "Dates",
            "Winter",
            "Special Events"
        ]
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
        "notes": [
            "Woody",
            "Spicy",
            "Sweet",
            "Smoky"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Daily Wear",
            "Office",
            "Dates",
            "Events"
        ]
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
        "notes": [
            "Aquatic",
            "Green Apple",
            "Fresh",
            "Woody"
        ],
        "longevity": "5–7 Hours",
        "best_for": [
            "Daily Wear",
            "Summer Days",
            "College",
            "Office",
            "Casual Outings"
        ]
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
        "notes": [
            "Aquatic",
            "Citrus",
            "Sweet",
            "Musky",
            "Fresh Spicy"
        ],
        "longevity": "7–9 Hours",
        "best_for": [
            "Daily Wear",
            "Summer Days",
            "College",
            "Office",
            "Casual Outings"
        ]
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
        "notes": [
            "Citrus",
            "Woody",
            "Aromatic",
            "Fresh Spicy",
            "Incense"
        ],
        "longevity": "7–10 Hours",
        "best_for": [
            "Office",
            "Daily Wear",
            "Meetings",
            "Dates",
            "Special Events"
        ]
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
        "notes": [
            "Sweet",
            "Spicy",
            "Smoky",
            "Amber",
            "Woody"
        ],
        "longevity": "7–9 Hours",
        "best_for": [
            "Night Out",
            "Parties",
            "Winter",
            "Dates",
            "Special Events"
        ]
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
        "notes": [
            "Fresh",
            "Woody",
            "Spicy",
            "Soft Floral",
            "Amber"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Dates",
            "Weddings",
            "Events",
            "Office",
            "Evening Wear"
        ]
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
        "notes": [
            "Chestnut",
            "Vanilla",
            "Sweet Spicy",
            "Amber",
            "Woody"
        ],
        "longevity": "7–10 Hours",
        "best_for": [
            "Dates",
            "Winter",
            "Night Out",
            "Parties",
            "Special Moments"
        ]
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
        "notes": [
            "Floral",
            "Citrus",
            "Sweet",
            "Powdery",
            "Soft Woody"
        ],
        "longevity": "5–7 Hours",
        "best_for": [
            "Daily Wear",
            "Office",
            "College",
            "Dates",
            "Casual Outings"
        ]
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
        "notes": [
            "Citrus",
            "Green",
            "Fresh Spicy",
            "Aromatic",
            "Woody"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Daily Wear",
            "Summer Days",
            "College",
            "Office",
            "Casual Outings"
        ]
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
        "notes": [
            "Vanilla",
            "Sweet",
            "Fruity",
            "Amber",
            "Warm Spicy"
        ],
        "longevity": "8–10 Hours",
        "best_for": [
            "Date Night",
            "Evening Wear",
            "Parties",
            "Winter Days",
            "Special Occasions"
        ]
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
        "notes": [
            "Aquatic",
            "Marine",
            "Green",
            "Aromatic",
            "Fresh Spicy"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Daily Wear",
            "Summer Days",
            "College",
            "Office",
            "Casual Outings"
        ]
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
        "notes": [
            "Cinnamon",
            "Vanilla",
            "Sweet",
            "Amber",
            "Woody",
            "Warm Spicy"
        ],
        "longevity": "8–12 Hours",
        "best_for": [
            "Date Night",
            "Winter Days",
            "Parties",
            "Special Occasions",
            "Evening Wear"
        ]
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
        "notes": [
            "Pineapple",
            "Bergamot",
            "Smoky",
            "Woody",
            "Musky"
        ],
        "longevity": "8–10 Hours",
        "best_for": [
            "Office",
            "Date Night",
            "Parties",
            "Special Occasions",
            "Year-Round Wear"
        ]
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
        "notes": [
            "Blueberry",
            "Fruity",
            "Sweet",
            "Fresh",
            "Musky"
        ],
        "longevity": "6–8 Hours",
        "best_for": [
            "Daily Wear",
            "College",
            "Casual Outings",
            "Hangouts",
            "Daytime Wear"
        ]
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
        "notes": [
            "Tobacco",
            "Vanilla",
            "Sweet",
            "Warm Spicy",
            "Woody"
        ],
        "longevity": "8–12 Hours",
        "best_for": [
            "Date Night",
            "Winter Days",
            "Evening Wear",
            "Parties",
            "Special Occasions"
        ]
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
        "notes": [
            "Vanilla",
            "White Floral",
            "Sweet",
            "Warm Spicy",
            "Cacao"
        ],
        "longevity": "8–10 Hours",
        "best_for": [
            "Date Night",
            "Parties",
            "Evening Wear",
            "Special Occasions",
            "Winter Days"
        ]
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
        "notes": [
            "Mint",
            "Vanilla",
            "Apple",
            "Citrus",
            "Woody",
            "Fresh Spicy"
        ],
        "longevity": "8–10 Hours",
        "best_for": [
            "Date Night",
            "Parties",
            "College",
            "Casual Outings",
            "Evening Wear"
        ]
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
        "notes": [
            "Cocoa",
            "Tonka Bean",
            "Amber",
            "Citrus",
            "Woody",
            "Aromatic"
        ],
        "longevity": "8–10 Hours",
        "best_for": [
            "Date Night",
            "Parties",
            "Evening Wear",
            "Winter Days",
            "Special Occasions"
        ]
    }
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

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except Exception as error:

        print("JSON LOAD ERROR:", error)

        return default


def save_json_file(filename, data):

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception as error:

        print("JSON SAVE ERROR:", error)

        return False


# =========================================================
# INITIALIZE PRODUCT FILE
# =========================================================

def init_product_file():

    if not os.path.exists(PRODUCT_FILE):

        save_json_file(
            PRODUCT_FILE,
            INITIAL_PRODUCTS
        )


init_product_file()


# =========================================================
# PRODUCTS
# =========================================================

def get_products():

    products = load_json_file(
        PRODUCT_FILE,
        INITIAL_PRODUCTS
    )

    if isinstance(products, list):
        return products

    return INITIAL_PRODUCTS


# =========================================================
# ORDERS
# =========================================================

def get_orders():

    orders = load_json_file(
        ORDER_FILE,
        []
    )

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

    "last_url": GOOGLE_SHEET_CSV_URL
}


# =========================================================
# GOOGLE SHEET DOWNLOAD
# =========================================================

def download_google_sheet():

    print("")
    print("=" * 60)
    print("GOOGLE SHEET: STARTING DOWNLOAD")
    print("=" * 60)

    try:

        request_object = urllib.request.Request(
            GOOGLE_SHEET_CSV_URL,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request_object,
            timeout=20
        ) as response:

            raw_data = response.read()

            status_code = response.getcode()

        print(
            "GOOGLE SHEET HTTP STATUS:",
            status_code
        )

        text = raw_data.decode(
            "utf-8-sig"
        )

        print(
            "GOOGLE SHEET RAW LENGTH:",
            len(text)
        )

        reader = csv.DictReader(
            io.StringIO(text)
        )

        print(
            "GOOGLE SHEET HEADERS:",
            reader.fieldnames
        )

        if not reader.fieldnames:

            raise Exception(
                "Google Sheet CSV has no headers."
            )

        rows = []

        for row in reader:

            cleaned = {}

            for key, value in row.items():

                if key is None:
                    continue

                clean_key = (
                    str(key)
                    .strip()
                    .lower()
                )

                clean_value = (
                    str(value or "")
                    .strip()
                )

                cleaned[
                    clean_key
                ] = clean_value

            if any(
                value.strip()
                for value in cleaned.values()
            ):

                rows.append(
                    cleaned
                )

        sheet_cache["data"] = rows

        sheet_cache["loaded_at"] = (
            datetime.now().isoformat()
        )

        sheet_cache["last_error"] = None

        print(
            "GOOGLE SHEET ROWS:",
            len(rows)
        )

        if rows:

            print(
                "FIRST SHEET ROW:",
                rows[0]
            )

        print(
            "GOOGLE SHEET: SUCCESS"
        )

        print("=" * 60)

        return rows

    except urllib.error.HTTPError as error:

        message = (
            f"HTTP {error.code}: "
            f"{error.reason}"
        )

        sheet_cache["last_error"] = message

        print(
            "GOOGLE SHEET HTTP ERROR:",
            message
        )

        return sheet_cache.get(
            "data",
            []
        )

    except urllib.error.URLError as error:

        message = (
            f"URL ERROR: {error.reason}"
        )

        sheet_cache["last_error"] = message

        print(
            "GOOGLE SHEET URL ERROR:",
            message
        )

        return sheet_cache.get(
            "data",
            []
        )

    except Exception as error:

        message = str(error)

        sheet_cache["last_error"] = message

        print(
            "GOOGLE SHEET ERROR:",
            message
        )

        return sheet_cache.get(
            "data",
            []
        )


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

    text = str(
        text or ""
    ).lower()

    # Common Banglish variations
    replacements = {

        "tmi": "tumi",
        "tmre": "tomare",
        "tmr": "tomar",
        "koto": "koto",
        "dam": "dam",
        "dite": "dite",
        "chai": "chai",

        "15 ml": "15ml",
        "30 ml": "30ml",
        "50 ml": "50ml"
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    text = text.replace(
        "৳",
        " taka "
    )

    text = text.replace(
        "tk",
        " taka "
    )

    text = re.sub(
        r"[^a-z0-9\u0980-\u09ff\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# TOKENIZE
# =========================================================

def tokenize(text):

    return set(
        re.findall(
            r"[a-z0-9\u0980-\u09ff]+",
            normalize_text(text)
        )
    )


# =========================================================
# PRODUCT ALIASES
# =========================================================

PRODUCT_ALIASES = {

    "dior": "DIOR SAUVAGE",
    "sauvage": "DIOR SAUVAGE",
    "dior sauvage": "DIOR SAUVAGE",

    "vampire": "VAMPIRE BLOOD",
    "vempire": "VAMPIRE BLOOD",
    "vempire blood": "VAMPIRE BLOOD",
    "vampire blood": "VAMPIRE BLOOD",

    "212": "212 MEN NYC",
    "212 men": "212 MEN NYC",

    "dunhill": "DUNHILL DESIRE",

    "hawas fire": "HAWAS FIRE",
    "hawas ice": "HAWAS ICE",

    "hawas": "HAWAS FIRE",

    "one million": "ONE MILLION",

    "nautica": "NAUTICA VOYAGE",
    "nautica voyage": "NAUTICA VOYAGE",

    "bleu": "BLEU DE CHANEL",
    "bleu chanel": "BLEU DE CHANEL",

    "srk": "SRK (Shah Rukh Inspired)",

    "stronger": "STRONGER WITH YOU",
    "stronger with you": "STRONGER WITH YOU",

    "gucci": "GUCCI FLORA",
    "gucci flora": "GUCCI FLORA",

    "ck1": "CK1",

    "9pm": "9PM",

    "cool water": "COOL WATER",

    "khamrah": "LATTAFA KHAMRAH",
    "lattafa": "LATTAFA KHAMRAH",

    "aventus": "CREED AVENTUS",
    "creed": "CREED AVENTUS",

    "blueberry": "BLUEBERRY",

    "tobacco": "TOBACCO VANILLE",
    "tobacco vanille": "TOBACCO VANILLE",

    "good girl": "GOOD GIRL",

    "eros": "VERSACE EROS",
    "versace": "VERSACE EROS",
    "versace eros": "VERSACE EROS",

    "bad boy": "BAD BOY"
}


# =========================================================
# FIND PRODUCT
# =========================================================

def find_product(message):

    text = normalize_text(
        message
    )

    products = get_products()

    # Exact full product name first
    for product in products:

        product_name = normalize_text(
            product.get(
                "name",
                ""
            )
        )

        if (
            product_name
            and product_name in text
        ):

            return product

    # Alias
    aliases_sorted = sorted(
        PRODUCT_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )

    for alias, product_name in aliases_sorted:

        alias_normalized = normalize_text(
            alias
        )

        if alias_normalized in text:

            target = normalize_text(
                product_name
            )

            for product in products:

                current = normalize_text(
                    product.get(
                        "name",
                        ""
                    )
                )

                if current == target:

                    return product

    return None


# =========================================================
# SIZE DETECTION
# =========================================================

def detect_size(message):

    text = normalize_text(
        message
    )

    match = re.search(
        r"\b(15|30|50)\s*ml\b",
        text
    )

    if match:

        return (
            match.group(1)
            + "ml"
        )

    return None


# =========================================================
# STRICT SHEET MATCHING
# =========================================================

def find_matching_sheet_answer(message):

    rows = get_sheet_data()

    if not rows:

        print(
            "SHEET MATCH: NO DATA"
        )

        return None

    user_text = normalize_text(
        message
    )

    user_words = tokenize(
        message
    )

    print("")
    print(
        "SHEET SEARCH:",
        user_text
    )

    candidates = []

    for index, row in enumerate(rows):

        question = normalize_text(
            row.get(
                "question",
                ""
            )
        )

        keywords = normalize_text(
            row.get(
                "keywords",
                ""
            )
        )

        answer = str(
            row.get(
                "answer",
                ""
            )
        ).strip()

        if not answer:
            continue

        question_words = tokenize(
            question
        )

        keyword_words = tokenize(
            keywords
        )

        all_target_words = (
            question_words
            |
            keyword_words
        )

        if not all_target_words:
            continue

        # -------------------------------------------------
        # Exact question
        # -------------------------------------------------

        if question:

            if user_text == question:

                print(
                    "EXACT QUESTION MATCH:",
                    question
                )

                return answer

        # -------------------------------------------------
        # Exact keyword phrase
        # -------------------------------------------------

        keyword_phrases = [
            k.strip()
            for k in keywords.split(",")
            if k.strip()
        ]

        for phrase in keyword_phrases:

            phrase_normalized = normalize_text(
                phrase
            )

            if (
                phrase_normalized
                and phrase_normalized in user_text
            ):

                candidates.append({
                    "score": 100,
                    "answer": answer,
                    "question": question,
                    "index": index
                })

                break

        # -------------------------------------------------
        # Question phrase inside message
        # -------------------------------------------------

        if (
            question
            and len(question.split()) >= 2
            and question in user_text
        ):

            candidates.append({
                "score": 95,
                "answer": answer,
                "question": question,
                "index": index
            })

        # -------------------------------------------------
        # Token scoring
        # -------------------------------------------------

        common = (
            user_words
            &
            all_target_words
        )

        if not common:
            continue

        # Important:
        # Don't allow one generic word like
        # "price", "koto", "good", etc. to match.
        generic_words = {
            "price",
            "dam",
            "koto",
            "taka",
            "tk",
            "cost",
            "details",
            "detail",
            "good",
            "best",
            "ki",
            "konta",
            "what",
            "how",
            "is",
            "the",
            "a",
            "ami",
            "chai",
            "want"
        }

        meaningful_common = {
            word
            for word in common
            if word not in generic_words
        }

        if (
            not meaningful_common
            and len(user_words) > 1
        ):

            continue

        coverage = (
            len(meaningful_common)
            /
            max(
                len(
                    user_words
                ),
                1
            )
        )

        target_coverage = (
            len(meaningful_common)
            /
            max(
                len(
                    all_target_words
                ),
                1
            )
        )

        score = (
            coverage * 60
            +
            target_coverage * 40
        )

        # If question contains the product,
        # strongly prefer it.
        product = find_product(
            message
        )

        if product:

            product_name = normalize_text(
                product.get(
                    "name",
                    ""
                )
            )

            if (
                product_name
                and product_name in question
            ):

                score += 50

        if score >= 45:

            candidates.append({
                "score": score,
                "answer": answer,
                "question": question,
                "index": index
            })

    # -----------------------------------------------------
    # Pick strongest candidate
    # -----------------------------------------------------

    if not candidates:

        print(
            "SHEET MATCH: NOTHING FOUND"
        )

        return None

    candidates.sort(
        key=lambda item: (
            item["score"],
            -item["index"]
        ),
        reverse=True
    )

    best = candidates[0]

    print(
        "SHEET MATCH FOUND:",
        best["question"],
        "| SCORE:",
        round(
            best["score"],
            2
        )
    )

    return best["answer"]


# =========================================================
# PRODUCT INFORMATION FROM SHEET ONLY
# =========================================================
#
# IMPORTANT:
# Product catalog is NOT used to generate answers.
# It is only used to understand which product customer means.
#
# The actual answer MUST come from Google Sheet.
#
# =========================================================


def find_product_sheet_answer(message):

    product = find_product(
        message
    )

    if not product:

        return None

    rows = get_sheet_data()

    if not rows:

        return None

    product_name = normalize_text(
        product.get(
            "name",
            ""
        )
    )

    aliases_for_product = []

    for alias, target in PRODUCT_ALIASES.items():

        if normalize_text(target) == product_name:

            aliases_for_product.append(
                normalize_text(alias)
            )

    user_text = normalize_text(
        message
    )

    candidates = []

    for index, row in enumerate(rows):

        question = normalize_text(
            row.get(
                "question",
                ""
            )
        )

        keywords = normalize_text(
            row.get(
                "keywords",
                ""
            )
        )

        answer = str(
            row.get(
                "answer",
                ""
            )
        ).strip()

        if not answer:
            continue

        combined = (
            question
            + " "
            + keywords
        )

        if product_name not in combined:

            product_alias_found = any(
                alias in combined
                for alias in aliases_for_product
            )

            if not product_alias_found:
                continue

        user_words = tokenize(
            user_text
        )

        target_words = tokenize(
            combined
        )

        common = (
            user_words
            &
            target_words
        )

        score = len(common)

        # Question phrase gets priority
        if (
            question
            and question in user_text
        ):

            score += 20

        if score > 0:

            candidates.append({
                "score": score,
                "answer": answer,
                "question": question,
                "index": index
            })

    if not candidates:

        return None

    candidates.sort(
        key=lambda item: (
            item["score"],
            -item["index"]
        ),
        reverse=True
    )

    best = candidates[0]

    print(
        "PRODUCT SHEET MATCH:",
        product.get("name"),
        "|",
        best["question"],
        "| SCORE:",
        best["score"]
    )

    return best["answer"]


# =========================================================
# ORDER DETECTION
# =========================================================

def is_order_request(message):

    text = normalize_text(
        message
    )

    phrases = [

        "order",

        "order korte chai",

        "order korbo",

        "order dibo",

        "nibo",

        "nite chai",

        "kinbo",

        "kinte chai",

        "buy",

        "book",

        "অর্ডার",

        "নিব",

        "নিতে চাই",

        "কিনবো",

        "কিনতে চাই"
    ]

    return any(
        phrase in text
        for phrase in phrases
    )


# =========================================================
# EXTRACT ORDER INFO
# =========================================================

def extract_order_information(message):

    product = find_product(
        message
    )

    size = detect_size(
        message
    )

    quantity = 1

    quantity_match = re.search(
        r"(?:x|qty|quantity|পরিমাণ)\s*(\d+)",
        normalize_text(message)
    )

    if quantity_match:

        try:

            quantity = int(
                quantity_match.group(1)
            )

        except Exception:

            quantity = 1

    return {

        "product":
            product.get("name")
            if product
            else None,

        "size":
            size,

        "quantity":
            quantity
    }


# =========================================================
# SAVE ORDER
# =========================================================

def save_order(
    message,
    customer_details=None
):

    customer_details = (
        customer_details
        or {}
    )

    order_info = extract_order_information(
        message
    )

    orders = get_orders()

    next_id = 1

    if orders:

        try:

            next_id = (
                max(
                    int(
                        order.get(
                            "id",
                            0
                        )
                    )
                    for order in orders
                )
                + 1
            )

        except Exception:

            next_id = len(
                orders
            ) + 1

    order = {

        "id":
            next_id,

        "customer_name":
            customer_details.get(
                "name",
                ""
            ),

        "phone":
            customer_details.get(
                "phone",
                ""
            ),

        "address":
            customer_details.get(
                "address",
                ""
            ),

        "product":
            order_info["product"]
            or "Not specified",

        "size":
            order_info["size"]
            or "Not specified",

        "quantity":
            order_info["quantity"],

        "status":
            "pending",

        "created_at":
            datetime.now().isoformat()
    }

    orders.append(
        order
    )

    save_json_file(
        ORDER_FILE,
        orders
    )

    return order


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# PRODUCTS API
# =========================================================

@app.route(
    "/api/products",
    methods=["GET"]
)
def products_api():

    return jsonify(
        get_products()
    )


# =========================================================
# ORDERS API
# =========================================================

@app.route(
    "/api/orders",
    methods=["GET"]
)
def orders_api():

    return jsonify(
        get_orders()
    )


# =========================================================
# KNOWLEDGE API
# =========================================================

@app.route(
    "/api/knowledge",
    methods=["GET"]
)
def knowledge_api():

    rows = get_sheet_data()

    return jsonify({

        "rows":
            len(rows),

        "status":
            "connected"
            if rows
            else "empty",

        "loaded_at":
            sheet_cache.get(
                "loaded_at"
            ),

        "last_error":
            sheet_cache.get(
                "last_error"
            ),

        "headers":
            list(
                rows[0].keys()
            )
            if rows
            else []
    })


# =========================================================
# REFRESH GOOGLE SHEET
# =========================================================

@app.route(
    "/api/knowledge/refresh",
    methods=["POST"]
)
def refresh_knowledge():

    rows = download_google_sheet()

    return jsonify({

        "success":
            bool(rows),

        "rows":
            len(rows),

        "loaded_at":
            sheet_cache.get(
                "loaded_at"
            ),

        "error":
            sheet_cache.get(
                "last_error"
            )
    })


# =========================================================
# DEBUG API
# =========================================================

@app.route(
    "/api/debug",
    methods=["GET"]
)
def debug_api():

    rows = get_sheet_data()

    return jsonify({

        "ezkroy":
            "online",

        "ai_mode":
            "GOOGLE_SHEET_ONLY",

        "openai":
            "DISABLED",

        "google_sheet": {

            "sheet_id":
                GOOGLE_SHEET_ID,

            "csv_url":
                GOOGLE_SHEET_CSV_URL,

            "rows":
                len(rows),

            "loaded_at":
                sheet_cache.get(
                    "loaded_at"
                ),

            "last_error":
                sheet_cache.get(
                    "last_error"
                ),

            "headers":
                list(
                    rows[0].keys()
                )
                if rows
                else [],

            "first_row":
                rows[0]
                if rows
                else None
        },

        "products": {

            "total":
                len(
                    get_products()
                ),

            "dior":
                find_product(
                    "DIOR SAUVAGE"
                ),

            "vampire":
                find_product(
                    "vempire blood"
                )
        },

        "orders": {

            "total":
                len(
                    get_orders()
                )
        }
    })


# =========================================================
# TEST SHEET API
# =========================================================

@app.route(
    "/api/test/sheet",
    methods=["GET"]
)
def test_sheet():

    message = request.args.get(
        "q",
        ""
    ).strip()

    if not message:

        return jsonify({

            "success":
                False,

            "message":
                "Use ?q=your question"
        })

    answer = find_matching_sheet_answer(
        message
    )

    product_answer = (
        find_product_sheet_answer(
            message
        )
    )

    return jsonify({

        "message":
            message,

        "normalized":
            normalize_text(
                message
            ),

        "general_sheet_answer":
            answer,

        "product_sheet_answer":
            product_answer,

        "final_answer":
            product_answer
            or answer,

        "sheet_rows":
            len(
                get_sheet_data()
            )
    })


# =========================================================
# CHAT API
# =========================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()

    if not message:

        return jsonify({

            "reply":
                "আপনার প্রশ্নটি লিখুন।",

            "order_created":
                False,

            "source":
                "system"
        })

    print("")
    print("=" * 60)
    print(
        "CUSTOMER:",
        message
    )

    # -----------------------------------------------------
    # PRODUCT DETECTION
    # -----------------------------------------------------

    product = find_product(
        message
    )

    print(
        "PRODUCT:",
        product.get("name")
        if product
        else None
    )

    # -----------------------------------------------------
    # FIRST: PRODUCT-SPECIFIC SHEET ANSWER
    # -----------------------------------------------------

    product_answer = (
        find_product_sheet_answer(
            message
        )
    )

    if product_answer:

        print(
            "FINAL SOURCE: PRODUCT SHEET"
        )

        return jsonify({

            "reply":
                product_answer,

            "order_created":
                False,

            "source":
                "google_sheet_product"
        })

    # -----------------------------------------------------
    # SECOND: GENERAL SHEET ANSWER
    # -----------------------------------------------------

    sheet_answer = (
        find_matching_sheet_answer(
            message
        )
    )

    if sheet_answer:

        print(
            "FINAL SOURCE: GOOGLE SHEET"
        )

        return jsonify({

            "reply":
                sheet_answer,

            "order_created":
                False,

            "source":
                "google_sheet"
        })

    # -----------------------------------------------------
    # ORDER REQUEST
    #
    # IMPORTANT:
    # We DO NOT generate AI answers.
    # We only use Sheet.
    # -----------------------------------------------------

    if is_order_request(message):

        return jsonify({

            "reply":
                "অর্ডার সংক্রান্ত তথ্য Google Sheet-এ পাওয়া যায়নি। "
                "অনুগ্রহ করে Sheet-এ এই প্রশ্নের উত্তর যোগ করুন।",

            "order_created":
                False,

            "source":
                "google_sheet_missing"
        })

    # -----------------------------------------------------
    # NOTHING FOUND
    # -----------------------------------------------------

    return jsonify({

        "reply":
            "দুঃখিত, এই প্রশ্নের উত্তর আমার Google Sheet-এ পাওয়া যায়নি।",

        "order_created":
            False,

        "source":
            "google_sheet_missing"
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    rows = get_sheet_data()

    return jsonify({

        "status":
            "online",

        "mode":
            "GOOGLE_SHEET_ONLY",

        "openai":
            False,

        "google_sheet_rows":
            len(rows),

        "google_sheet_connected":
            bool(rows),

        "google_sheet_error":
            sheet_cache.get(
                "last_error"
            ),

        "total_products":
            len(
                get_products()
            ),

        "total_orders":
            len(
                get_orders()
            )
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("")
    print("=" * 60)
    print("           EZKROY AI SALES AGENT")
    print("=" * 60)

    print(
        "MODE:",
        "GOOGLE SHEET ONLY"
    )

    print(
        "OPENAI:",
        "DISABLED"
    )

    print(
        "GOOGLE SHEET ID:",
        GOOGLE_SHEET_ID
    )

    print("=" * 60)

    # Load Sheet immediately
    download_google_sheet()

    print(
        "SERVER STARTING..."
    )

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
```
