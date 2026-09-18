from flask import Flask, request, jsonify, render_template
import os
import json
import csv
import io
import re
import urllib.request
import urllib.error
from datetime import datetime


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================================================
# EZKROY AI — SALES AGENT
# CORRECTED + DEBUG VERSION
# =========================================================

app = Flask(__name__)


# =========================================================
# CONFIGURATION
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4o-mini"
)


# =========================================================
# GOOGLE SHEET
# =========================================================

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
# INITIAL PRODUCTS
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
# OPENAI
# =========================================================

client = None

if OpenAI and OPENAI_API_KEY:

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        print(
            "OPENAI CLIENT: CONNECTED"
        )

    except Exception as error:

        print(
            "OPENAI CLIENT ERROR:",
            error
        )

else:

    print(
        "OPENAI CLIENT: NOT CONNECTED"
    )

    if not OPENAI_API_KEY:

        print(
            "REASON: OPENAI_API_KEY not found"
        )


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
    print(
        "=========================================="
    )

    print(
        "GOOGLE SHEET: STARTING DOWNLOAD"
    )

    print(
        "=========================================="
    )

    try:

        req = urllib.request.Request(

            GOOGLE_SHEET_CSV_URL,

            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )


        with urllib.request.urlopen(
            req,
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

                clean_key = str(
                    key
                ).strip().lower()

                clean_value = str(
                    value or ""
                ).strip()

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

        print(
            "=========================================="
        )


        return rows


    except urllib.error.HTTPError as error:

        error_message = (
            f"HTTP {error.code}: "
            f"{error.reason}"
        )

        sheet_cache[
            "last_error"
        ] = error_message


        print(
            "GOOGLE SHEET HTTP ERROR:",
            error_message
        )


        return sheet_cache.get(
            "data",
            []
        )


    except urllib.error.URLError as error:

        error_message = (
            f"URL ERROR: {error.reason}"
        )

        sheet_cache[
            "last_error"
        ] = error_message


        print(
            "GOOGLE SHEET URL ERROR:",
            error_message
        )


        return sheet_cache.get(
            "data",
            []
        )


    except Exception as error:

        error_message = str(
            error
        )

        sheet_cache[
            "last_error"
        ] = error_message


        print(
            "GOOGLE SHEET ERROR:",
            error_message
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

    "212":
        "212 MEN NYC",

    "212 men":
        "212 MEN NYC",

    "dunhill":
        "DUNHILL DESIRE",

    "hawas fire":
        "HAWAS FIRE",

    "hawas":
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

    "tobacco":
        "TOBACCO VANILLE",

    "tobacco vanille":
        "TOBACCO VANILLE",

    "good girl":
        "GOOD GIRL",

    "eros":
        "VERSACE EROS",

    "versace":
        "VERSACE EROS",

    "versace eros":
        "VERSACE EROS",

    "bad boy":
        "BAD BOY"
}


# =========================================================
# FIND PRODUCT
# =========================================================

def find_product(user_message):

    text = normalize_text(
        user_message
    )

    products = get_products()


    # -----------------------------------------
    # Exact product name
    # -----------------------------------------

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


    # -----------------------------------------
    # Alias matching
    # -----------------------------------------

    for alias, product_name in PRODUCT_ALIASES.items():

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
        r"\b(15|30|50)\s*(?:ml|m l)\b",
        text
    )


    if match:

        return (
            match.group(1)
            + "ml"
        )


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

        "taka",

        "tk",

        "cost",

        "how much",

        "how much is"
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
            f"{name} 15ml-এর বর্তমান price "
            f"৳{price}। Regular price ৳{regular}।"
        )


    if size == "30ml":

        price = product.get(
            "price_30ml"
        )

        regular = product.get(
            "regular_30ml"
        )

        return (
            f"{name} 30ml-এর বর্তমান price "
            f"৳{price}। Regular price ৳{regular}।"
        )


    price_15 = product.get(
        "price_15ml"
    )

    price_30 = product.get(
        "price_30ml"
    )


    return (
        f"{name} 15ml ৳{price_15} "
        f"এবং 30ml ৳{price_30}।"
    )


# =========================================================
# PRODUCT DETAIL ANSWER
# =========================================================

def build_product_detail_answer(
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


    notes_text = ", ".join(
        notes
    )

    best_for_text = ", ".join(
        best_for
    )


    return (
        f"{name} — {description}\n"
        f"Price: 15ml ৳{product.get('price_15ml')} | "
        f"30ml ৳{product.get('price_30ml')}\n"
        f"Longevity: {longevity}\n"
        f"Notes: {notes_text}\n"
        f"Best for: {best_for_text}"
    )


# =========================================================
# SHEET ANSWER MATCHING
# =========================================================

def find_matching_sheet_answer(
    user_message
):

    rows = get_sheet_data()


    if not rows:

        print(
            "SHEET MATCH: No sheet rows available"
        )

        return None


    user_text = normalize_text(
        user_message
    )

    user_words = tokenize(
        user_message
    )


    print(
        "SHEET MATCH USER:",
        user_text
    )


    best_answer = None
    best_score = 0
    best_question = None


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


        # Strong penalty for weak generic matches
        if (
            len(common) == 1
            and len(user_words) >= 3
        ):

            score *= 0.25


        print(
            "SHEET CANDIDATE:",
            question,
            "| common:",
            common,
            "| score:",
            round(score, 3)
        )


        if score > best_score:

            best_score = score

            best_answer = answer

            best_question = question


    if best_score >= 0.60:

        print(
            "SHEET MATCH FOUND:",
            best_question,
            "| score:",
            best_score
        )

        return best_answer


    print(
        "SHEET MATCH: NO STRONG MATCH"
    )


    return None


# =========================================================
# GREETING DETECTION
# =========================================================

def is_greeting(message):

    text = normalize_text(
        message
    )


    greetings = [

        "hi",

        "hello",

        "hey",

        "hii",

        "hiii",

        "assalamualaikum",

        "assalamu alaikum",

        "salam",

        "হাই",

        "হ্যালো",

        "আসসালামু আলাইকুম"
    ]


    return text in greetings


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

        "order dibo",

        "nibo",

        "nite chai",

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
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """

You are EZKROY AI, a professional AI sales assistant.

BUSINESS:
EZKROY is an online perfume business.

LANGUAGE:
- Understand Bangla, Banglish and English.
- Reply in the same language/style as the customer.
- Keep replies short and natural.

PRODUCT RULE:
- Use ONLY the supplied product catalog.
- Never invent product prices.
- Never invent stock.
- Never invent sizes.
- Never invent product information.

GOOGLE SHEET:
- The verified Google Sheet contains business FAQ information.
- Use sheet information only when it clearly matches the customer's question.
- Never use an unrelated sheet answer.
- Never force delivery information into a product question.

GREETING:
If customer says hi/hello/hey/etc:
Reply naturally.
Do not give delivery information unless asked.

PRODUCT:
If customer asks about a specific perfume:
Answer about that perfume.
If asking price, provide exact price from catalog.
If asking size, provide available sizes.
If asking notes/longevity/occasion, use catalog.

ORDER:
If customer wants to order:
Guide them to provide:
1. Product
2. Size
3. Quantity
4. Name
5. Phone
6. Address

Do not claim that an order is completed unless the required information has actually been collected.

STYLE:
Friendly.
Professional.
Short.
Natural.
Helpful.
"""


# =========================================================
# ASK AI
# =========================================================

def ask_ai(
    user_message,
    context_info=""
):

    if not client:

        return (
            "EZKROY AI চালু আছে, কিন্তু OpenAI API connection পাওয়া যাচ্ছে না। "
            "OPENAI_API_KEY check করুন।"
        )


    catalog = build_knowledge_base()


    user_prompt = f"""
PRODUCT CATALOG:
{catalog}

VERIFIED SHEET INFORMATION:
{context_info or "No directly matched sheet information."}

CUSTOMER MESSAGE:
{user_message}

Answer the customer's message directly.
"""


    try:

        print("")
        print(
            "OPENAI REQUEST START"
        )

        print(
            "MODEL:",
            MODEL
        )


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
                        user_prompt
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


        print(
            "OPENAI RESPONSE SUCCESS"
        )


        if reply:

            return reply.strip()


        return (
            "দুঃখিত, কোনো উত্তর পাওয়া যায়নি।"
        )


    except Exception as error:

        print("")
        print(
            "=========================================="
        )

        print(
            "OPENAI ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "=========================================="
        )


        return (
            "AI response তৈরি করতে সমস্যা হচ্ছে। "
            "Debug page থেকে OpenAI status check করুন।"
        )


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


    return "\n".join(
        kb
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
            sheet_cache.get(
                "loaded_at"
            ),

        "last_error":
            sheet_cache.get(
                "last_error"
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

        "openai": {

            "installed":
                bool(OpenAI),

            "api_key_found":
                bool(OPENAI_API_KEY),

            "client_connected":
                bool(client),

            "model":
                MODEL
        },

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
# TEST PRODUCT API
# =========================================================

@app.route(
    "/api/test/product",
    methods=["GET"]
)
def test_product():

    message = request.args.get(
        "q",
        "dior sauvage koto"
    )


    product = find_product(
        message
    )

    size = detect_size(
        message
    )


    price_query = is_price_query(
        message
    )


    result = {

        "message":
            message,

        "normalized":
            normalize_text(
                message
            ),

        "product_found":
            bool(product),

        "product":
            product,

        "size":
            size,

        "price_query":
            price_query
    }


    if product and price_query:

        result[
            "direct_answer"
        ] = build_product_answer(
            product,
            size
        )


    return jsonify(
        result
    )


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


    print("")
    print(
        "=========================================="
    )

    print(
        "CUSTOMER:",
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


    print(
        "PRODUCT FOUND:",
        product.get("name")
        if product
        else None
    )

    print(
        "SIZE:",
        size
    )


    # =====================================================
    # GREETING
    # =====================================================

    if is_greeting(message):

        return jsonify({

            "reply":
                "হ্যালো! 👋 আমি EZKROY AI Assistant। "
                "কোন perfume সম্পর্কে জানতে চান?",

            "order_created":
                False
        })


    # =====================================================
    # PRODUCT PRICE
    # =====================================================

    if (
        product
        and is_price_query(message)
    ):

        direct_answer = (
            build_product_answer(
                product,
                size
            )
        )


        print(
            "DIRECT PRODUCT PRICE ANSWER:",
            direct_answer
        )


        return jsonify({

            "reply":
                direct_answer,

            "order_created":
                False
        })


    # =====================================================
    # PRODUCT DETAIL
    # =====================================================

    product_words = [

        "details",

        "detail",

        "notes",

        "note",

        "longevity",

        "lasting",

        "কেমন",

        "নোট",

        "লাস্টিং",

        "lasting koto"
    ]


    normalized_message = normalize_text(
        message
    )


    if (
        product
        and any(
            word in normalized_message
            for word in product_words
        )
    ):

        answer = build_product_detail_answer(
            product
        )


        return jsonify({

            "reply":
                answer,

            "order_created":
                False
        })


    # =====================================================
    # SHEET FAQ
    # =====================================================

    verified_answer = (
        find_matching_sheet_answer(
            message
        )
    )


    print(
        "VERIFIED SHEET ANSWER:",
        verified_answer
    )


    # =====================================================
    # DIRECT SHEET ANSWER
    # =====================================================

    if verified_answer:

        print(
            "DIRECT SHEET RESPONSE"
        )


        return jsonify({

            "reply":
                verified_answer,

            "order_created":
                False
        })


    # =====================================================
    # ORDER REQUEST
    # =====================================================

    if is_order_request(message):

        order_info = (
            extract_order_information(
                message
            )
        )


        print(
            "ORDER INFO:",
            order_info
        )


        product_name = (
            order_info["product"]
        )

        detected_size = (
            order_info["size"]
        )


        if not product_name:

            return jsonify({

                "reply":
                    "অবশ্যই! 😊 কোন perfume টি নিতে চান? "
                    "যেমন: Dior Sauvage, Vampire Blood, Hawas Fire ইত্যাদি।",

                "order_created":
                    False
            })


        if not detected_size:

            return jsonify({

                "reply":
                    f"{product_name} নিতে পারবেন। "
                    f"15ml নাকি 30ml চান?",

                "order_created":
                    False
            })


        return jsonify({

            "reply":
                f"ঠিক আছে! {product_name} {detected_size}। "
                f"এখন আপনার নাম, phone number এবং full address দিন।",

            "order_created":
                False
        })


    # =====================================================
    # AI FALLBACK
    # =====================================================

    reply = ask_ai(
        message,
        ""
    )


    return jsonify({

        "reply":
            reply,

        "order_created":
            False
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
            ),

        "openai":
            bool(client),

        "openai_key":
            bool(OPENAI_API_KEY),

        "model":
            MODEL
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print("")
    print(
        "=========================================="
    )

    print(
        "          EZKROY AI SALES AGENT"
    )

    print(
        "=========================================="
    )

    print(
        "OPENAI KEY:",
        "FOUND"
        if OPENAI_API_KEY
        else "NOT FOUND"
    )

    print(
        "OPENAI CLIENT:",
        "CONNECTED"
        if client
        else "NOT CONNECTED"
    )

    print(
        "MODEL:",
        MODEL
    )

    print(
        "GOOGLE SHEET ID:",
        GOOGLE_SHEET_ID
    )

    print(
        "=========================================="
    )


    # Load Google Sheet immediately
    download_google_sheet()


    print(
        "SERVER STARTING..."
    )


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
