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
# EZKROY / VIREX AI - SALES & ANALYTICS AGENT
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


# আপনার Google Sheet ID
GOOGLE_SHEET_ID = (
    "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"
)


# Google Sheet CSV URL
GOOGLE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{GOOGLE_SHEET_ID}/export?format=csv"
)


# =========================================================
# DATA FILES & INITIAL PRODUCTS JSON SYNC
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

# আপনার প্রদান করা প্রোডাক্ট লিস্টটি স্বয়ংক্রিয়ভাবে `data/products.json` এ সেভ করে দেওয়া হলো
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
    "best_for": ["Daily Wear", "Office", "College", "Dates", "Casual Outings"]
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
    "best_for": ["Office", "Dates", "Evening Wear", "Winter", "Casual Events"]
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
    "best_for": ["Dates", "Night Out", "Parties", "Winter", "Special Events"]
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
    "best_for": ["Parties", "Night Out", "Dates", "Winter", "Special Events"]
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
    "best_for": ["Daily Wear", "Office", "Dates", "Events"]
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
    "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"]
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
    "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"]
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
    "notes": ["Citrus", "Woody", "Aromatic", "Fresh Spicy", "Incense"],
    "longevity": "7–10 Hours",
    "best_for": ["Office", "Daily Wear", "Meetings", "Dates", "Special Events"]
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
    "best_for": ["Night Out", "Parties", "Winter", "Dates", "Special Events"]
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
    "best_for": ["Dates", "Weddings", "Events", "Office", "Evening Wear"]
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
    "best_for": ["Dates", "Winter", "Night Out", "Parties", "Special Moments"]
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
    "best_for": ["Daily Wear", "Office", "College", "Dates", "Casual Outings"]
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
    "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"]
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
    "best_for": ["Date Night", "Evening Wear", "Parties", "Winter Days", "Special Occasions"]
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
    "best_for": ["Daily Wear", "Summer Days", "College", "Office", "Casual Outings"]
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
    "best_for": ["Date Night", "Winter Days", "Parties", "Special Occasions", "Evening Wear"]
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
    "best_for": ["Office", "Date Night", "Parties", "Special Occasions", "Year-Round Wear"]
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
    "best_for": ["Daily Wear", "College", "Casual Outings", "Hangouts", "Daytime Wear"]
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
    "best_for": ["Date Night", "Winter Days", "Evening Wear", "Parties", "Special Occasions"]
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
    "best_for": ["Date Night", "Parties", "Evening Wear", "Special Occasions", "Winter Days"]
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
    "best_for": ["Date Night", "Parties", "College", "Casual Outings", "Evening Wear"]
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
    "best_for": ["Date Night", "Parties", "Evening Wear", "Winter Days", "Special Occasions"]
  }
]

def init_product_file():
    if not os.path.exists(PRODUCT_FILE):
        save_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)

init_product_file()


# =========================================================
# OPENAI CLIENT
# =========================================================

client = None

if OpenAI and OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


# =========================================================
# BASIC FILE HELPERS
# =========================================================

def load_json_file(filename, default=None):
    if default is None:
        default = []
    try:
        if not os.path.exists(filename):
            return default
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
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


def get_products():
    return load_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)


def get_orders():
    return load_json_file(ORDER_FILE, [])


# =========================================================
# GOOGLE SHEET DOWNLOADER (Handling 6000+ Rows)
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None
}


def download_google_sheet():
    try:
        print("Downloading knowledge from Google Sheet...")
        req = urllib.request.Request(
            GOOGLE_SHEET_CSV_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            raw_data = response.read()

        text = raw_data.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        rows = []
        for row in reader:
            cleaned = {}
            for key, value in row.items():
                if key is None:
                    continue
                clean_key = str(key).strip().lower()
                clean_value = str(value or "").strip()
                cleaned[clean_key] = clean_value

            if any(cleaned.values()):
                rows.append(cleaned)

        sheet_cache["data"] = rows
        sheet_cache["loaded_at"] = datetime.now()
        print(f"Google Sheet successfully loaded: {len(rows)} rows")
        return rows

    except Exception as error:
        print("GOOGLE SHEET ERROR:", error)
        return sheet_cache.get("data", [])


def get_sheet_data():
    if not sheet_cache["data"]:
        return download_google_sheet()
    return sheet_cache["data"]


# =========================================================
# SMART KEYWORD & Q&A MATCHING (Optimized for 6000+ Rows)
# =========================================================

def normalize_text(text):
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_matching_sheet_answer(user_message):
    rows = get_sheet_data()
    if not rows:
        return None

    user_text = normalize_text(user_message)
    user_words = set(re.findall(r"\w+", user_text))

    best_answer = None
    highest_score = 0

    for row in rows:
        q_text = normalize_text(row.get("question", ""))
        kw_text = normalize_text(row.get("keywords", ""))
        ans_text = row.get("answer", "")

        if not ans_text:
            continue

        if user_text and user_text == q_text:
            return ans_text

        keywords_set = set(re.findall(r"\w+", kw_text))
        q_words_set = set(re.findall(r"\w+", q_text))
        target_words = keywords_set.union(q_words_set)

        if not target_words:
            continue

        common_words = user_words.intersection(target_words)
        score = len(common_words) / max(len(target_words), 1)

        if score > highest_score:
            highest_score = score
            best_answer = ans_text

    if highest_score >= 0.25:
        return best_answer

    return None


# =========================================================
# BUILD FULL CONTEXT (Products + Sheet)
# =========================================================

def build_knowledge_base():
    products = get_products()
    kb = ["=== PERFUME PRODUCTS CATALOG ==="]
    for p in products:
        kb.append(json.dumps(p, ensure_ascii=False))
    return "\n".join(kb)


# =========================================================
# ORDER EXTRACTION & AUTO-SAVE TO LOCAL FILE
# =========================================================

def extract_order_information(message):
    text = str(message or "").strip()
    lower = text.lower()

    product = None
    size = None
    quantity = 1

    # সাইজ ডিটেক্ট করা
    size_match = re.search(r"\b(15|30|50)\s*ml\b", lower)
    if size_match:
        size = size_match.group(1) + "ml"

    # প্রোডাক্ট ক্যাটালগ থেকে নাম ম্যাচ করা
    products = get_products()
    for item in products:
        name = str(item.get("name", "")).strip()
        if name and name.lower() in lower:
            product = name
            break
    
    if not product:
        for item in products:
            name_parts = item.get("name", "").lower().split()
            if any(part in lower for part in name_parts if len(part) > 3):
                product = item.get("name")
                break

    return {
        "product": product or "General Perfume",
        "size": size | "Not specified" if 'size' in locals() and size else (size or "15ml"),
        "quantity": quantity
    }


def save_order(message, customer_details=None):
    order_info = extract_order_information(message)
    orders = get_orders()

    next_id = 1
    if orders:
        try:
            next_id = max([int(o.get("id", 0)) for o in orders]) + 1
        except:
            next_id = len(orders) + 1

    order = {
        "id": next_id,
        "customer_name": customer_details.get("name", "") if customer_details else "",
        "phone": customer_details.get("phone", "") if customer_details else "",
        "address": customer_details.get("address", "") if customer_details else "",
        "product": order_info["product"],
        "size": order_info["size"],
        "quantity": order_info["quantity"],
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    orders.append(order)
    save_json_file(ORDER_FILE, orders)
    return order


# =========================================================
# AI SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are EZKROY AI Sales Assistant, an intelligent sales agent for a perfume store.
Your job is to help customers choose perfumes, explain prices/notes, answer queries, and help them place orders seamlessly in a polite and friendly way.

RULES:
1. Understand Bangla, Banglish, and English.
2. Reply in the exact same language/style used by the customer.
3. Keep replies short, precise, and professional.
4. Always utilize the verified products catalog and sheet database provided below.
5. If a customer wants to place an order, collect their Name, Phone Number, Address, Product, and Size step by step.
"""


def ask_ai(user_message, context_info=""):
    if not client:
        return "EZKROY AI server-এর সাথে connect হয়নি। OPENAI_API_KEY চেক করুন।"

    catalog = build_knowledge_base()

    full_prompt = f"""
{SYSTEM_PROMPT}

PRODUCTS CATALOG & PRICES:
{catalog}

VERIFIED SHEET MATCHED ANSWER:
{context_info}

CUSTOMER MESSAGE:
{user_message}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        return reply.strip() if reply else "দুঃখিত, এই মুহূর্তে উত্তর তৈরি করা যাচ্ছে না।"
    except Exception as error:
        print("OPENAI ERROR:", error)
        return "দুঃখিত, AI server-এর সাথে এই মুহূর্তে যোগাযোগ করা যাচ্ছে না।"


# =========================================================
# ROUTES & API ENDPOINTS
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/products", methods=["GET"])
def products_api():
    return jsonify(get_products())


@app.route("/api/orders", methods=["GET"])
def orders_api():
    return jsonify(get_orders())


@app.route("/api/knowledge", methods=["GET"])
def knowledge_api():
    rows = get_sheet_data()
    return jsonify({
        "rows": len(rows),
        "status": "connected" if rows else "empty"
    })


@app.route("/api/knowledge/refresh", methods=["POST"])
def refresh_knowledge():
    rows = download_google_sheet()
    return jsonify({"success": True, "rows": len(rows)})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"reply": "আপনার প্রশ্নটি লিখুন।"})

    print("\nCUSTOMER:", message)

    # ১. গুগল শিট থেকে স্মার্ট ম্যাচিং করে উত্তর খোঁজা
    verified_answer = find_matching_sheet_answer(message)

    # ২. AI এর মাধ্যমে রেসপন্স জেনারেট করা
    reply = ask_ai(message, verified_answer or "No direct sheet Q&A found, use product catalog and store info.")

    # ৩. অর্ডার ডিটেক্ট করা এবং স্বয়ংক্রিয়ভাবে লোকাল ফাইলে সংরক্ষণ করা
    order = None
    order_keywords = ["order", "অর্ডার", "নিব", "নিতে চাই", "চাই", "দাও", "book", "korte cchai"]
    lower_message = message.lower()

    if any(kw in lower_message for kw in order_keywords):
        order = save_order(message)

    response_data = {
        "reply": reply,
        "order_created": bool(order)
    }

    if order:
        response_data["order"] = order

    return jsonify(response_data)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "google_sheet_rows": len(get_sheet_data()),
        "total_products": len(get_products()),
        "total_orders": len(get_orders())
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    print("\n====================================")
    print("      EZKROY AI SALES ASSISTANT     ")
    print("====================================\n")
    download_google_sheet()
    app.run(host="0.0.0.0", port=5000, debug=True)
