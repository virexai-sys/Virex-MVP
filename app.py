from flask import Flask, request, jsonify, render_template_string
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

app = Flask(__name__)

# =========================================================
# GOOGLE SHEET CONFIG
# =========================================================

GOOGLE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"

GOOGLE_SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv"
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
        "Aiman is a student and entrepreneur with interests in sales, data, technology "
        "and AI. He is also the founder of NOIR Fragrance and works on EZKROY, an "
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
    "creator_description": "Aiman is the creator and developer of the EZKROY project.",
    "contact_note": "For direct contact information, please refer to Aiman's portfolio.",
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
        "creator ke",
        "owner ke",
        "developer ke",
        "malik ke",
        "tomre ke banaise",
        "tomake ke banaise",
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
# PRODUCT CATALOG (Initial fallback)
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
]


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


def init_product_file():
    if not os.path.exists(PRODUCT_FILE):
        save_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)


init_product_file()


def get_products():
    products = load_json_file(PRODUCT_FILE, INITIAL_PRODUCTS)
    return products if isinstance(products, list) else INITIAL_PRODUCTS


def get_orders():
    orders = load_json_file(ORDER_FILE, [])
    return orders if isinstance(orders, list) else []


# =========================================================
# GOOGLE SHEET CACHE & DOWNLOAD
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None,
    "last_error": None,
    "last_url": GOOGLE_SHEET_CSV_URL,
}


def download_google_sheet():
    try:
        request_object = urllib.request.Request(
            GOOGLE_SHEET_CSV_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            },
        )
        with urllib.request.urlopen(request_object, timeout=10) as response:
            text = response.read().decode("utf-8-sig", errors="replace")

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
            if any(value.strip() for value in cleaned.values()):
                rows.append(cleaned)

        sheet_cache["data"] = rows
        sheet_cache["loaded_at"] = datetime.now().isoformat()
        sheet_cache["last_error"] = None
        return rows
    except Exception as error:
        sheet_cache["last_error"] = str(error)
        return sheet_cache.get("data", [])


def get_sheet_data():
    if not sheet_cache["data"]:
        return download_google_sheet()
    return sheet_cache["data"]


# =========================================================
# TEXT NORMALIZATION & TOKENIZE
# =========================================================


def normalize_text(text):
    text = str(text or "").lower().strip()
    replacements = {
        "tmi": "tumi",
        "tmre": "tomare",
        "tmr": "tomar",
        "pls": "please",
        "plz": "please",
        "৳": " taka ",
        "tk": " taka ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[^a-z0-9\u0980-\u09ff\s:/._-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text):
    return set(re.findall(r"[a-z0-9\u0980-\u09ff]+", normalize_text(text)))


# =========================================================
# PROFILE ANSWER BUILDER & MATCHING
# =========================================================


def get_profile_answer(intent):
    if intent == "identity":
        return f"আমি EZKROY-এর AI sales assistant। এই project-এর creator/developer হলেন {PROFILE['name']} ({PROFILE['short_name']})।"
    if intent == "name":
        return f"আমার project-এর creator/developer হলেন {PROFILE['name']}। তাকে সাধারণত {PROFILE['short_name']} নামে ডাকা হয়।"
    if intent == "education":
        return f"Aiman {PROFILE['institution']}-এ {PROFILE['field']} নিয়ে পড়াশোনা করছেন।"
    if intent == "hometown":
        return f"Aiman-এর hometown হলো {PROFILE['hometown']}।"
    if intent == "business":
        return f"Aiman-এর business project-এর মধ্যে {PROFILE['business']} উল্লেখযোগ্য।"
    if intent == "project":
        return f"{PROFILE['project']} হলো Aiman-এর AI-powered sales assistant project।"
    if intent == "portfolio":
        return f"Aiman-এর portfolio দেখতে এখানে যেতে পারেন:\n{PROFILE['portfolio']}"
    if intent == "about":
        return PROFILE["about"]
    if intent == "interests":
        interests = ", ".join(PROFILE["interests"])
        return f"Aiman-এর প্রধান interest হলো: {interests}।"
    return None


def find_profile_answer(message):
    user_text = normalize_text(message)
    if not user_text:
        return None

    for intent, phrases in PROFILE_INTENTS.items():
        for phrase in phrases:
            if normalize_text(phrase) in user_text:
                return get_profile_answer(intent)
    return None


PRODUCT_ALIASES = {
    "dior": "DIOR SAUVAGE",
    "sauvage": "DIOR SAUVAGE",
    "212": "212 MEN NYC",
    "dunhill": "DUNHILL DESIRE",
    "bad boy": "BAD BOY",
}

# =========================================================
# FLASK ROUTES (Frontend & API)
# =========================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>EZKROY AI - Sales Assistant</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .chat-container { width: 100%; max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .chat-box { height: 400px; border: 1px solid #ddd; border-radius: 5px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; background: #fafafa; }
        .message { margin-bottom: 10px; padding: 8px 12px; border-radius: 5px; max-width: 80%; }
        .user { background: #007bff; color: white; margin-left: auto; text-align: right; }
        .bot { background: #e2e3e5; color: #333; }
        .input-group { display: flex; gap: 10px; }
        .input-group input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-group button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>EZKROY AI Sales Assistant</h2>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-group">
            <input type="text" id="userInput" placeholder="আপনার প্রশ্ন এখানে লিখুন..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">পাঠান</button>
        </div>
    </div>
    <script>
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const chatBox = document.getElementById('chatBox');
            const text = input.value.trim();
            if(!text) return;

            chatBox.innerHTML += `<div class="message user">${text}</div>`;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await response.json();

            chatBox.innerHTML += `<div class="message bot">${data.reply}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "")

    # Priority 1: Profile Match
    profile_ans = find_profile_answer(message)
    if profile_ans:
        return jsonify({"reply": profile_ans})

    # Priority 2: Google Sheet Data Search
    sheet_rows = get_sheet_data()
    user_tokens = tokenize(message)
    for row in sheet_rows:
        q_tokens = tokenize(row.get("question", ""))
        kw_tokens = tokenize(row.get("keywords", ""))
        if user_tokens & (q_tokens | kw_tokens):
            return jsonify({"reply": row.get("answer", "উত্তর পাওয়া গেছে।")})

    # Priority 3: Product Match fallback
    products = get_products()
    for prod in products:
        if prod["name"].lower() in message.lower():
            reply = f"প্রোডাক্ট: {prod['name']}\nমূল্য (১৫মিঃলিঃ): {prod.get('price_15ml')} টাকা\nমূল্য (৩০মিঃলিঃ): {prod.get('price_30ml')} টাকা\nবিবরণ: {prod.get('description')}"
            return jsonify({"reply": reply})

    # Priority 4: System Fallback
    return jsonify({
        "reply": "দুঃখিত, বিষয়টি বুঝতে পারিনি। আপনি আমাদের পোর্টফোলিও দেখতে পারেন অথবা নির্দিষ্ট কোনো পারফিউম বা তথ্য সম্পর্কে জানতে চাইলে তা লিখে পাঠান।"
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
