```python
from flask import Flask, request, jsonify, render_template
import os
import json
import csv
import io
import re
import urllib.request
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================================================
# EZKROY AI — SALES AGENT
# PRODUCT + GOOGLE SHEET + AI
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIG
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o"
)

GOOGLE_SHEET_ID = (
    "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"
)

GOOGLE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/export?format=csv"
)


# =========================================================
# FILES
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

os.makedirs(DATA_DIR, exist_ok=True)


# =========================================================
# PRODUCT DATABASE
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
        "notes": ["Apple", "Orange", "Spicy", "Vanilla", "Woody"],
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
        "notes": ["Sweet", "Spicy", "Aquatic", "Smoky", "Amber"],
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
        "notes": ["Sweet", "Spicy", "Citrus", "Leather", "Woody"],
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
        "notes": ["Woody", "Spicy", "Sweet", "Smoky"],
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
        "notes": ["Aquatic", "Green Apple", "Fresh", "Woody"],
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
        "notes": ["Aquatic", "Citrus", "Sweet", "Musky", "Fresh Spicy"],
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
        "regular_30ml": 1499,
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
        "notes": ["Sweet", "Spicy", "Smoky", "Amber", "Woody"],
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

            return json.load(file)

    except Exception as error:

        print(
            "JSON LOAD ERROR:",
            error
        )

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

        print(
            "JSON SAVE ERROR:",
            error
        )

        return False


# =========================================================
# PRODUCT / ORDER LOADERS
# =========================================================

def init_product_file():

    if not os.path.exists(
        PRODUCT_FILE
    ):

        save_json_file(
            PRODUCT_FILE,
            INITIAL_PRODUCTS
        )


init_product_file()


def get_products():

    products = load_json_file(
        PRODUCT_FILE,
        INITIAL_PRODUCTS
    )

    if isinstance(products, list):
        return products

    return INITIAL_PRODUCTS


def get_orders():

    orders = load_json_file(
        ORDER_FILE,
        []
    )

    if isinstance(orders, list):
        return orders

    return []


# =========================================================
# OPENAI
# =========================================================

client = None

if OpenAI and OPENAI_API_KEY:

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        print("OPENAI CLIENT: CONNECTED")

    except Exception as error:

        print(
            "OPENAI CLIENT ERROR:",
            error
        )


# =========================================================
# GOOGLE SHEET CACHE
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None
}


# =========================================================
# GOOGLE SHEET DOWNLOAD
# =========================================================

def download_google_sheet():

    try:

        print(
            "Downloading Google Sheet..."
        )

        request_obj = urllib.request.Request(
            GOOGLE_SHEET_CSV_URL,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request_obj,
            timeout=20
        ) as response:

            raw_data = response.read()


        text = raw_data.decode(
            "utf-8-sig"
        )


        reader = csv.DictReader(
            io.StringIO(text)
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


            if any(cleaned.values()):

                rows.append(
                    cleaned
                )


        sheet_cache["data"] = rows

        sheet_cache["loaded_at"] = (
            datetime.now()
        )


        print(
            "GOOGLE SHEET CONNECTED:",
            len(rows),
            "rows"
        )


        if rows:

            print(
                "SHEET COLUMNS:",
                list(rows[0].keys())
            )


        return rows


    except Exception as error:

        print(
            "GOOGLE SHEET ERROR:",
            error
        )

        return sheet_cache.get(
            "data",
            []
        )


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

    "dior":
        "DIOR SAUVAGE",

    "sauvage":
        "DIOR SAUVAGE",

    "dior sauvage":
        "DIOR SAUVAGE",

    "vampire":
        "VAMPIRE BLOOD",

    "vempire":
        "VAMPIRE BLOOD",

    "vampire blood":
        "VAMPIRE BLOOD",

    "vempire blood":
        "VAMPIRE BLOOD",

    "212":
        "212 MEN NYC",

    "dunhill":
        "DUNHILL DESIRE",

    "hawas":
        "HAWAS FIRE",

    "hawas fire":
        "HAWAS FIRE",

    "hawas ice":
        "HAWAS ICE",

    "one million":
        "ONE MILLION",

    "nautica":
        "NAUTICA VOYAGE",

    "nautica voyage":
        "NAUTICA VOYAGE",

    "bleu":
        "BLEU DE CHANEL",

    "bleu chanel":
        "BLEU DE CHANEL",

    "srk":
        "SRK (Shah Rukh Inspired)",

    "stronger with you":
        "STRONGER WITH YOU",

    "stronger":
        "STRONGER WITH YOU",

    "gucci":
        "GUCCI FLORA",

    "gucci flora":
        "GUCCI FLORA",

    "ck1":
        "CK1",

    "9pm":
        "9PM",

    "cool water":
        "COOL WATER",

    "khamrah":
        "LATTAFA KHAMRAH",

    "lattafa":
        "LATTAFA KHAMRAH",

    "aventus":
        "CREED AVENTUS",

    "creed":
        "CREED AVENTUS",

    "blueberry":
        "BLUEBERRY",

    "tobacco vanille":
        "TOBACCO VANILLE",

    "tobacco":
        "TOBACCO VANILLE",

    "good girl":
        "GOOD GIRL",

    "eros":
        "VERSACE EROS",

    "versace":
        "VERSACE EROS",

    "bad boy":
        "BAD BOY"
}


# =========================================================
# PRODUCT MATCH
# =========================================================

def find_product(user_message):

    text = normalize_text(
        user_message
    )

    products = get_products()


    # Exact full product name

    for product in products:

        name = normalize_text(
            product.get(
                "name",
                ""
            )
        )

        if (
            name
            and name in text
        ):

            return product


    # Alias matching

    sorted_aliases = sorted(
        PRODUCT_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )


    for alias, product_name in sorted_aliases:

        if alias in text:

            target = normalize_text(
                product_name
            )

            for product in products:

                if (
                    normalize_text(
                        product.get(
                            "name",
                            ""
                        )
                    )
                    == target
                ):

                    return product


    return None


# =========================================================
# SIZE
# =========================================================

def detect_size(message):

    text = normalize_text(
        message
    )


    match = re.search(
        r"\b(15|30|50)\s*(?:ml|m l)?\b",
        text
    )


    if match:

        return (
            match.group(1)
            +
            "ml"
        )


    return None


# =========================================================
# PRICE QUERY
# =========================================================

def is_price_query(message):

    text = normalize_text(
        message
    )


    price_words = [

        "price",

        "price koto",

        "koto",

        "dam",

        "দাম",

        "কত",

        "দাম কত",

        "tk",

        "taka",

        "cost",

        "cost koto",

        "how much"

    ]


    return any(
        word in text
        for word in price_words
    )


# =========================================================
# PRODUCT ANSWER
# =========================================================

def build_product_answer(
    product,
    size=None
):

    name = product.get(
        "name",
        "Product"
    )


    if size == "15ml":

        price = product.get(
            "price_15ml"
        )

        regular = product.get(
            "regular_15ml"
        )

        return (
            f"{name} 15ml-এর "
            f"বর্তমান price ৳{price}। "
            f"Regular price ৳{regular}।"
        )


    if size == "30ml":

        price = product.get(
            "price_30ml"
        )

        regular = product.get(
            "regular_30ml"
        )

        return (
            f"{name} 30ml-এর "
            f"বর্তমান price ৳{price}। "
            f"Regular price ৳{regular}।"
        )


    return (
        f"{name} 15ml ৳"
        f"{product.get('price_15ml')} "
        f"এবং 30ml ৳"
        f"{product.get('price_30ml')}।"
    )


# =========================================================
# SHEET MATCHING
# =========================================================

def find_matching_sheet_answer(
    user_message
):

    rows = get_sheet_data()

    if not rows:
        return None


    user_text = normalize_text(
        user_message
    )

    user_words = tokenize(
        user_message
    )


    # =====================================================
    # EXACT QUESTION
    # =====================================================

    for row in rows:

        question = normalize_text(
            row.get(
                "question",
                ""
            )
        )

        answer = str(
            row.get(
                "answer",
                ""
            )
        ).strip()


        if (
            question
            and answer
            and user_text == question
        ):

            return answer


    # =====================================================
    # BEST MATCH
    # =====================================================

    best_answer = None
    best_score = 0


    for row in rows:

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


        target_words = (
            tokenize(question)
            |
            tokenize(keywords)
        )


        if not target_words:
            continue


        common = (
            user_words
            &
            target_words
        )


        if not common:
            continue


        score = (
            len(common)
            /
            max(
                len(user_words),
                1
            )
        )


        # Prevent weak one-word matches

        if (
            len(common) == 1
            and len(user_words) >= 3
        ):

            continue


        # Question coverage

        question_words = tokenize(
            question
        )


        if question_words:

            question_score = (
                len(
                    user_words
                    &
                    question_words
                )
                /
                len(question_words)
            )

            score = max(
                score,
                question_score * 0.75
            )


        if score > best_score:

            best_score = score

            best_answer = answer


    if best_score >= 0.60:

        return best_answer


    return None


# =========================================================
# KNOWLEDGE BASE
# =========================================================

def build_knowledge_base():

    products = get_products()

    kb = [
        "=== EZKROY PRODUCT CATALOG ==="
    ]


    for product in products:

        kb.append(
            json.dumps(
                product,
                ensure_ascii=False
            )
        )


    return "\n".join(kb)


# =========================================================
# ORDER DETECTION
# =========================================================

def is_order_request(message):

    text = normalize_text(
        message
    )


    order_phrases = [

        "order",

        "order korte chai",

        "order korbo",

        "nibo",

        "nib",

        "nite chai",

        "nitte chai",

        "kinbo",

        "kinte chai",

        "buy",

        "book",

        "অর্ডার",

        "অর্ডার করতে চাই",

        "নিব",

        "নিতে চাই",

        "কিনবো",

        "কিনতে চাই"

    ]


    return any(
        phrase in text
        for phrase in order_phrases
    )


# =========================================================
# AI
# =========================================================

SYSTEM_PROMPT = """
You are EZKROY AI, a professional AI sales assistant.

BUSINESS:
EZKROY is an online perfume business.

LANGUAGE:
- Understand Bangla, Banglish and English.
- Reply naturally in the customer's language/style.
- Keep replies short and friendly.

PRODUCT RULE:
- Product prices MUST come from the supplied product catalog.
- Never invent product prices.
- Never change product names.
- If product information is available in the catalog, use it.

GOOGLE SHEET RULE:
- Google Sheet contains verified business FAQ information.
- Use a Sheet answer ONLY when it directly matches the customer's question.
- Never use an unrelated Sheet answer.
- Never mention the Sheet itself unless necessary.

GREETING:
For hi, hello, hey, salam, assalamu alaikum, etc. respond with a natural greeting.
Do not give delivery information unless asked.

ORDER:
If customer wants to order, collect:
1. Product
2. Size
3. Quantity
4. Name
5. Phone
6. Address

STYLE:
- Short
- Friendly
- Professional
- Helpful
- Sales-focused
- No unnecessary explanation

IMPORTANT:
Never invent business policies, delivery charges, prices or product information.
"""


def ask_ai(
    user_message,
    context_info=""
):

    if not client:

        return (
            "EZKROY AI server-এর সাথে "
            "connect হয়নি। "
            "OPENAI_API_KEY check করুন।"
        )


    catalog = build_knowledge_base()


    prompt = f"""
{SYSTEM_PROMPT}

=== PRODUCT CATALOG ===

{catalog}

=== VERIFIED CONTEXT ===

{context_info}

=== CUSTOMER MESSAGE ===

{user_message}

Answer the customer naturally.
"""


    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[

                {
                    "role":
                        "system",

                    "content":
                        SYSTEM_PROMPT
                },

                {
                    "role":
                        "user",

                    "content":
                        prompt
                }

            ],

            temperature=0.3
        )


        reply = (
            response
            .choices[0]
            .message
            .content
        )


        return (
            reply.strip()
            if reply
            else
            "দুঃখিত, এই মুহূর্তে উত্তর দেওয়া যাচ্ছে না।"
        )


    except Exception as error:

        print(
            "OPENAI ERROR:",
            error
        )


        return (
            "দুঃখিত, AI server-এর সাথে "
            "এই মুহূর্তে যোগাযোগ করা যাচ্ছে না।"
        )


# =========================================================
# SAVE ORDER
# =========================================================

def extract_order_information(
    message
):

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

        except:

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


def save_order(
    message,
    customer_details=None
):

    customer_details = (
        customer_details
        or {}
    )


    order_info = (
        extract_order_information(
            message
        )
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

        except:

            next_id = (
                len(orders)
                + 1
            )


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
# PRODUCTS
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
# ORDERS
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
# KNOWLEDGE
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
            (
                sheet_cache["loaded_at"].isoformat()
                if sheet_cache["loaded_at"]
                else None
            ),

        "columns":
            (
                list(rows[0].keys())
                if rows
                else []
            )

    })


# =========================================================
# REFRESH SHEET
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

        "status":
            "connected"
            if rows
            else "empty",

        "columns":
            (
                list(rows[0].keys())
                if rows
                else []
            )

    })


# =========================================================
# CHAT
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
                False

        })


    print(
        "\nCUSTOMER:",
        message
    )


    # =====================================================
    # PRODUCT
    # =====================================================

    product = find_product(
        message
    )

    size = detect_size(
        message
    )


    # =====================================================
    # PRICE
    # =====================================================

    if (
        product
        and is_price_query(message)
    ):

        reply = build_product_answer(
            product,
            size
        )


        print(
            "PRODUCT PRICE RESPONSE:",
            reply
        )


        return jsonify({

            "reply":
                reply,

            "order_created":
                False,

            "product":
                product.get("name"),

            "size":
                size

        })


    # =====================================================
    # GREETING
    # =====================================================

    normalized = normalize_text(
        message
    )


    greetings = [

        "hi",

        "hello",

        "hey",

        "হাই",

        "হ্যালো",

        "salam",

        "assalamualaikum",

        "আসসালামু আলাইকুম"

    ]


    if normalized in greetings:

        return jsonify({

            "reply":
                "হ্যালো! 👋 "
                "আমি EZKROY AI Assistant। "
                "আপনি perfume-এর price, details "
                "বা order সম্পর্কে জানতে পারেন।",

            "order_created":
                False

        })


    # =====================================================
    # ORDER
    # =====================================================

    if is_order_request(
        message
    ):

        if product:

            product_name = product.get(
                "name",
                "এই perfume"
            )


            if size:

                reply = (
                    f"অবশ্যই! 😊 "
                    f"{product_name} {size} order করতে পারবেন। "
                    f"Order complete করতে আপনার নাম, "
                    f"ফোন নম্বর এবং delivery address দিন।"
                )

            else:

                reply = (
                    f"অবশ্যই! 😊 "
                    f"{product_name} order করতে পারবেন। "
                    f"আপনি কোন size চান — 15ml নাকি 30ml? "
                    f"তারপর আপনার নাম, ফোন নম্বর "
                    f"এবং delivery address দিন।"
                )


        else:

            reply = (
                "অবশ্যই! 😊 "
                "কোন perfumeটি order করতে চান "
                "তার নাম বলুন।"
            )


        return jsonify({

            "reply":
                reply,

            "order_created":
                False

        })


    # =====================================================
    # PRODUCT INFORMATION
    # =====================================================

    if product:

        product_info = json.dumps(
            product,
            ensure_ascii=False,
            indent=2
        )


        reply = ask_ai(

            message,

            f"""
The customer is asking about this exact product.

Use ONLY this product information:

{product_info}

Do not use an unrelated Google Sheet answer.
"""

        )


        return jsonify({

            "reply":
                reply,

            "order_created":
                False,

            "product":
                product.get("name")

        })


    # =====================================================
    # GOOGLE SHEET
    # =====================================================

    verified_answer = (
        find_matching_sheet_answer(
            message
        )
    )


    if verified_answer:

        print(
            "SHEET ANSWER FOUND:",
            verified_answer
        )


        reply = ask_ai(

            message,

            f"""
A verified business FAQ answer was found.

Use this answer because it directly matches
the customer's question.

Verified answer:
{verified_answer}

Do not add unrelated information.
"""

        )


    else:

        print(
            "NO SHEET MATCH"
        )


        reply = ask_ai(

            message,

            """
No directly matching Google Sheet FAQ was found.

Answer naturally using the EZKROY product catalog
and general sales-assistant behavior.

Do not invent prices or business policies.
"""

        )


    return jsonify({

        "reply":
            reply,

        "order_created":
            False

    })


# =========================================================
# HEALTH
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

        "google_sheet_rows":
            len(rows),

        "google_sheet":
            bool(rows),

        "total_products":
            len(
                get_products()
            ),

        "total_orders":
            len(
                get_orders()
            ),

        "openai":
            bool(client)

    })


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "       EZKROY AI SALES AGENT"
    )

    print(
        "====================================\n"
    )


    # Load Google Sheet on startup

    download_google_sheet()


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )
```
