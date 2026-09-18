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
# EZKROY AI — SALES & ANALYTICS BACKEND
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
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
# OPENAI CLIENT
# =========================================================

client = None

if OpenAI and OPENAI_API_KEY:

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        print(
            "OPENAI: Connected"
        )

    except Exception as error:

        print(
            "OPENAI CLIENT ERROR:",
            error
        )

else:

    print(
        "OPENAI: API key not found"
    )


# =========================================================
# GOOGLE SHEET CACHE
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None,
    "error": None
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
                "User-Agent": "Mozilla/5.0"
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


        if not reader.fieldnames:

            raise Exception(
                "Google Sheet has no headers."
            )


        print(
            "Google Sheet headers:",
            reader.fieldnames
        )


        rows = []


        for row in reader:

            cleaned = {}


            for key, value in row.items():

                if key is None:
                    continue


                clean_key = normalize_header(
                    key
                )


                clean_value = str(
                    value or ""
                ).strip()


                cleaned[
                    clean_key
                ] = clean_value


            if any(
                cleaned.values()
            ):

                rows.append(
                    cleaned
                )


        sheet_cache["data"] = rows

        sheet_cache["loaded_at"] = (
            datetime.now()
        )

        sheet_cache["error"] = None


        print(
            f"Google Sheet loaded successfully: {len(rows)} rows"
        )


        return rows


    except Exception as error:

        print(
            "GOOGLE SHEET ERROR:",
            error
        )


        sheet_cache["error"] = str(
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
# HEADER NORMALIZATION
# =========================================================

def normalize_header(header):

    header = str(
        header or ""
    ).strip().lower()


    header = re.sub(
        r"[^a-z0-9]+",
        "_",
        header
    )


    return header.strip("_")


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):

    text = str(
        text or ""
    ).lower()


    replacements = {

        "৳": " taka ",

        "tk.": " taka ",

        "tk": " taka ",

        "taka": " taka ",

        "vempire": " vampire ",

        "vampire": " vampire ",

        "dior sauvage": " dior sauvage ",

        "sauvage": " sauvage ",

        "perfumes": " perfume ",

        "fragrances": " fragrance "
    }


    for old, new in replacements.items():

        text = text.replace(
            old,
            new
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

    "dunhill desire": "DUNHILL DESIRE",

    "hawas fire": "HAWAS FIRE",

    "hawas": "HAWAS FIRE",

    "hawas ice": "HAWAS ICE",

    "one million": "ONE MILLION",

    "1 million": "ONE MILLION",

    "nautica": "NAUTICA VOYAGE",

    "nautica voyage": "NAUTICA VOYAGE",

    "bleu": "BLEU DE CHANEL",

    "bleu de chanel": "BLEU DE CHANEL",

    "srk": "SRK (Shah Rukh Inspired)",

    "stronger with you": "STRONGER WITH YOU",

    "swy": "STRONGER WITH YOU",

    "gucci": "GUCCI FLORA",

    "gucci flora": "GUCCI FLORA",

    "ck1": "CK1",

    "ck one": "CK1",

    "9pm": "9PM",

    "cool water": "COOL WATER",

    "khamrah": "LATTAFA KHAMRAH",

    "lattafa": "LATTAFA KHAMRAH",

    "aventus": "CREED AVENTUS",

    "creed aventus": "CREED AVENTUS",

    "creed": "CREED AVENTUS",

    "blueberry": "BLUEBERRY",

    "tobacco vanille": "TOBACCO VANILLE",

    "tobacco": "TOBACCO VANILLE",

    "good girl": "GOOD GIRL",

    "eros": "VERSACE EROS",

    "versace": "VERSACE EROS",

    "versace eros": "VERSACE EROS",

    "bad boy": "BAD BOY"
}


# =========================================================
# PRODUCT MATCHING
# =========================================================

def find_product(user_message):

    text = normalize_text(
        user_message
    )

    products = get_products()


    # -----------------------------------------------------
    # Exact/full product names
    # -----------------------------------------------------

    product_matches = []


    for product in products:

        name = normalize_text(
            product.get(
                "name",
                ""
            )
        )


        if not name:
            continue


        if name in text:

            product_matches.append(
                (
                    len(name),
                    product
                )
            )


    if product_matches:

        product_matches.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return product_matches[0][1]


    # -----------------------------------------------------
    # Alias matching
    # -----------------------------------------------------

    aliases = sorted(
        PRODUCT_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    )


    for alias, product_name in aliases:

        if normalize_text(alias) in text:

            target = normalize_text(
                product_name
            )


            for product in products:

                current_name = normalize_text(
                    product.get(
                        "name",
                        ""
                    )
                )


                if current_name == target:

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
        r"\b(15|30|50)\s*(?:ml|m\s*l)\b",
        text
    )


    if match:

        return (
            match.group(1)
            + "ml"
        )


    # Bangla / normal number without ml
    if re.search(
        r"\b15\b",
        text
    ):

        return "15ml"


    if re.search(
        r"\b30\b",
        text
    ):

        return "30ml"


    if re.search(
        r"\b50\b",
        text
    ):

        return "50ml"


    return None


# =========================================================
# PRICE QUERY DETECTION
# =========================================================

def is_price_query(message):

    text = normalize_text(
        message
    )


    price_patterns = [

        r"\bprice\b",

        r"\bprice koto\b",

        r"\bkoto\b",

        r"\bdam\b",

        r"\bdam koto\b",

        r"\btaka\b",

        r"\btk\b",

        r"\bhow much\b",

        r"দাম",

        r"কত",

        r"মূল্য",

        r"কতো"
    ]


    return any(
        re.search(
            pattern,
            text
        )
        for pattern in price_patterns
    )


# =========================================================
# PRODUCT INFORMATION QUERY
# =========================================================

def is_product_info_query(message):

    text = normalize_text(
        message
    )


    words = [
        "notes",
        "note",
        "longevity",
        "long lasting",
        "lasting",
        "description",
        "smell",
        "fragrance",
        "perfume",
        "which",
        "best",
        "কেমন",
        "ঘ্রাণ",
        "স্মেল",
        "কতক্ষণ",
        "স্থায়ী"
    ]


    return any(
        word in text
        for word in words
    )


# =========================================================
# BUILD PRODUCT ANSWER
# =========================================================

def build_product_answer(
    product,
    size=None
):

    name = product.get(
        "name",
        "Product"
    )


    price_15 = product.get(
        "price_15ml"
    )

    price_30 = product.get(
        "price_30ml"
    )


    regular_15 = product.get(
        "regular_15ml"
    )

    regular_30 = product.get(
        "regular_30ml"
    )


    if size == "15ml":

        return (
            f"{name} 15ml-এর current price "
            f"৳{price_15}। "
            f"Regular price ৳{regular_15}।"
        )


    if size == "30ml":

        return (
            f"{name} 30ml-এর current price "
            f"৳{price_30}। "
            f"Regular price ৳{regular_30}।"
        )


    return (
        f"{name} এর price:\n"
        f"• 15ml — ৳{price_15}\n"
        f"• 30ml — ৳{price_30}"
    )


# =========================================================
# PRODUCT DETAIL ANSWER
# =========================================================

def build_product_info_answer(
    product
):

    name = product.get(
        "name",
        "Product"
    )


    description = product.get(
        "description",
        ""
    )


    notes = product.get(
        "notes",
        []
    )


    longevity = product.get(
        "longevity",
        ""
    )


    best_for = product.get(
        "best_for",
        []
    )


    answer_parts = [
        f"**{name}**"
    ]


    if description:

        answer_parts.append(
            description
        )


    if notes:

        answer_parts.append(
            "Notes: "
            + ", ".join(
                str(note)
                for note in notes
            )
        )


    if longevity:

        answer_parts.append(
            f"Longevity: {longevity}"
        )


    if best_for:

        answer_parts.append(
            "Best for: "
            + ", ".join(
                str(item)
                for item in best_for[:4]
            )
        )


    return "\n".join(
        answer_parts
    )


# =========================================================
# GENERAL GREETING DETECTION
# =========================================================

def is_greeting(message):

    text = normalize_text(
        message
    )


    greetings = {

        "hi",
        "hello",
        "hey",
        "hii",
        "hiii",
        "assalamu alaikum",
        "salam",
        "আসসালামু আলাইকুম",
        "হাই",
        "হ্যালো",
        "সালাম"
    }


    return text in greetings


# =========================================================
# ORDER DETECTION
# =========================================================

def is_order_request(message):

    text = normalize_text(
        message
    )


    order_patterns = [

        r"\border\b",

        r"\border korte chai\b",

        r"\border korbo\b",

        r"\bnibo\b",

        r"\bnib\b",

        r"\bnite chai\b",

        r"\bnitte chai\b",

        r"\bkinbo\b",

        r"\bkinte chai\b",

        r"\bbuy\b",

        r"\bbook\b",

        r"অর্ডার",

        r"নিব",

        r"নিতে চাই",

        r"কিনবো",

        r"কিনতে চাই"
    ]


    return any(
        re.search(
            pattern,
            text
        )
        for pattern in order_patterns
    )


# =========================================================
# GENERAL SHEET QUESTION DETECTION
# =========================================================

def is_general_sheet_question(
    message
):

    text = normalize_text(
        message
    )


    general_keywords = [

        "delivery",
        "delivery charge",
        "shipping",
        "charge",
        "payment",
        "cash on delivery",
        "cod",
        "return",
        "exchange",
        "refund",
        "available",
        "collection",
        "perfume",
        "fragrance",
        "size",
        "order",
        "অর্ডার",
        "ডেলিভারি",
        "চার্জ",
        "পেমেন্ট",
        "রিটার্ন",
        "এক্সচেঞ্জ",
        "সাইজ"
    ]


    return any(
        keyword in text
        for keyword in general_keywords
    )


# =========================================================
# GOOGLE SHEET Q&A MATCHING
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


    if not user_words:

        return None


    # -----------------------------------------------------
    # Exact question
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Score each row
    # -----------------------------------------------------

    best_answer = None
    best_score = 0
    best_common_count = 0


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


        # User words matched
        user_score = (
            len(common)
            /
            max(
                len(user_words),
                1
            )
        )


        # Target words matched
        target_score = (
            len(common)
            /
            max(
                len(target_words),
                1
            )
        )


        score = (
            user_score * 0.65
            +
            target_score * 0.35
        )


        # Strong boost for multiple keyword matches
        if len(common) >= 2:

            score += 0.15


        # Weak single-word matches are dangerous
        if (
            len(common) == 1
            and len(user_words) >= 3
        ):

            score *= 0.35


        if (
            score > best_score
            or
            (
                score == best_score
                and len(common) > best_common_count
            )
        ):

            best_score = score
            best_answer = answer
            best_common_count = len(
                common
            )


    # -----------------------------------------------------
    # Minimum confidence
    # -----------------------------------------------------

    if best_score >= 0.50:

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


    rows = get_sheet_data()


    if rows:

        kb.append(
            "\n=== VERIFIED GOOGLE SHEET ==="
        )


        for row in rows:

            kb.append(
                json.dumps(
                    row,
                    ensure_ascii=False
                )
            )


    return "\n".join(
        kb
    )


# =========================================================
# ORDER INFORMATION
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


    normalized = normalize_text(
        message
    )


    quantity_patterns = [

        r"(?:x|qty|quantity)\s*(\d+)",

        r"(?:পরিমাণ)\s*(\d+)",

        r"(\d+)\s*(?:pcs|piece|pieces)"
    ]


    for pattern in quantity_patterns:

        match = re.search(
            pattern,
            normalized
        )


        if match:

            try:

                quantity = int(
                    match.group(1)
                )

            except Exception:

                quantity = 1


            break


    return {

        "product": (
            product.get("name")
            if product
            else None
        ),

        "size": size,

        "quantity": quantity
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

        except Exception:

            next_id = (
                len(orders)
                + 1
            )


    order = {

        "id": next_id,

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
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are EZKROY AI, a professional AI sales assistant for an online perfume business.

LANGUAGE:
- Understand Bangla, Banglish and English.
- Reply naturally in the same language/style as the customer.
- Keep replies short, friendly and useful.

CRITICAL RULES:

1. PRODUCT DATA
Use ONLY the supplied product catalog for:
- Product names
- Prices
- Sizes
- Stock
- Notes
- Longevity
- Product descriptions

Never invent a product or price.

2. PRICE
If the backend gives you a product price answer, use that exact price.
Do not replace it with the Google Sheet general price range.

3. GOOGLE SHEET
The Google Sheet contains verified business Q&A.

Use a Sheet answer ONLY when it is clearly relevant to the customer's question.

Never force an unrelated Sheet answer.

For example:
Customer: "hi"
Do NOT reply with delivery charge.

Customer: "DIOR SAUVAGE KOTO"
Use the product catalog price.

Customer: "delivery charge koto"
Use the relevant Sheet answer if available.

4. GREETING
For simple greetings such as:
- hi
- hello
- hey
- assalamu alaikum
- হাই
- হ্যালো

Reply naturally and briefly.

5. ORDER
If customer wants to order, collect:
1. Product
2. Size
3. Quantity
4. Name
5. Phone
6. Full address

Do not pretend an order is confirmed unless the required information is available.

6. STYLE
- Friendly
- Professional
- Short
- Natural
- Helpful
- No unnecessary explanations

7. LANGUAGE STYLE
For Banglish customers, Banglish is acceptable.
For Bangla customers, Bangla is preferred.
For English customers, English is preferred.

8. SOURCE PRIORITY
For product-specific information:
PRODUCT CATALOG > GOOGLE SHEET

For general business policies:
GOOGLE SHEET > AI knowledge

Never invent information that is not provided.
"""


# =========================================================
# AI RESPONSE
# =========================================================

def ask_ai(
    user_message,
    context_info=""
):

    if not client:

        return (
            "EZKROY AI এখন connect হয়নি। "
            "OPENAI_API_KEY check করুন।"
        )


    catalog = build_knowledge_base()


    full_prompt = f"""
{SYSTEM_PROMPT}

=== EZKROY DATA ===
{catalog}

=== VERIFIED CONTEXT FOR THIS CUSTOMER ===
{context_info or "No specific verified context found."}

=== CUSTOMER MESSAGE ===
{user_message}

Answer ONLY the customer's actual question.
Do not use unrelated information.
"""


    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": full_prompt
                }

            ],

            temperature=0.2
        )


        reply = (
            response
            .choices[0]
            .message
            .content
        )


        if reply:

            return reply.strip()


        return (
            "দুঃখিত, এই মুহূর্তে উত্তর তৈরি করা যাচ্ছে না।"
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
            (
                sheet_cache["loaded_at"].isoformat()
                if sheet_cache["loaded_at"]
                else None
            ),

        "error":
            sheet_cache.get(
                "error"
            )
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

        "status":
            "connected"
            if rows
            else "empty",

        "error":
            sheet_cache.get(
                "error"
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
                False
        })


    print(
        "\nCUSTOMER:",
        message
    )


    # -----------------------------------------------------
    # GREETING
    # -----------------------------------------------------

    if is_greeting(message):

        reply = (
            "হ্যালো! 👋 "
            "আমি EZKROY AI Assistant। "
            "আপনি কোন perfume বা price সম্পর্কে জানতে চান?"
        )


        return jsonify({

            "reply":
                reply,

            "order_created":
                False
        })


    # -----------------------------------------------------
    # PRODUCT DETECTION
    # -----------------------------------------------------

    product = find_product(
        message
    )


    size = detect_size(
        message
    )


    # -----------------------------------------------------
    # ORDER REQUEST
    # -----------------------------------------------------

    order_requested = (
        is_order_request(
            message
        )
    )


    # -----------------------------------------------------
    # PRODUCT PRICE
    # -----------------------------------------------------

    if (
        product
        and is_price_query(message)
    ):

        reply = build_product_answer(
            product,
            size
        )


        # Let AI make the answer natural,
        # but give it the exact verified product answer.

        if client:

            reply = ask_ai(
                message,
                reply
            )


    # -----------------------------------------------------
    # PRODUCT INFORMATION
    # -----------------------------------------------------

    elif (
        product
        and is_product_info_query(message)
    ):

        product_info = (
            build_product_info_answer(
                product
            )
        )


        if client:

            reply = ask_ai(
                message,
                product_info
            )

        else:

            reply = product_info


    # -----------------------------------------------------
    # ORDER REQUEST
    # -----------------------------------------------------

    elif order_requested:

        order_info = (
            extract_order_information(
                message
            )
        )


        context = json.dumps(
            order_info,
            ensure_ascii=False
        )


        if client:

            reply = ask_ai(
                message,
                context
            )

        else:

            if order_info["product"]:

                reply = (
                    f"{order_info['product']} order করতে "
                    f"size, আপনার নাম, phone number এবং "
                    f"full address দিন।"
                )

            else:

                reply = (
                    "অর্ডার করতে perfume-এর নাম, size, "
                    "quantity, আপনার নাম, phone number "
                    "এবং full address দিন।"
                )


    # -----------------------------------------------------
    # GOOGLE SHEET Q&A
    # -----------------------------------------------------

    else:

        verified_answer = (
            find_matching_sheet_answer(
                message
            )
        )


        if verified_answer:

            # IMPORTANT:
            # If a verified Sheet answer exists,
            # return it directly.
            #
            # This prevents AI from changing
            # business information.

            reply = verified_answer


        else:

            # -------------------------------------------------
            # GENERAL AI
            # -------------------------------------------------

            reply = ask_ai(
                message,
                "No directly verified Sheet answer found."
            )


    # -----------------------------------------------------
    # SAVE ORDER
    # -----------------------------------------------------

    order = None


    # IMPORTANT:
    # We only save an order if the message
    # contains an order request AND a product.
    #
    # This prevents messages such as
    # "ami order korte chai"
    # from creating an empty order.

    if (
        order_requested
        and product
    ):

        order = save_order(
            message
        )


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    response_data = {

        "reply":
            reply,

        "order_created":
            bool(order)
    }


    if order:

        response_data[
            "order"
        ] = order


    return jsonify(
        response_data
    )


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

        "google_sheet_rows":
            len(rows),

        "google_sheet":
            (
                "connected"
                if rows
                else "not connected"
            ),

        "total_products":
            len(
                get_products()
            ),

        "total_orders":
            len(
                get_orders()
            ),

        "openai":
            bool(client),

        "model":
            MODEL,

        "sheet_error":
            sheet_cache.get(
                "error"
            )
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "       EZKROY AI SALES AGENT"
    )

    print(
        "===================================="
    )

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Google Sheet ID: {GOOGLE_SHEET_ID}"
    )


    # Load Google Sheet on startup

    download_google_sheet()


    print(
        "\nServer starting..."
    )


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
```
