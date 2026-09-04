import json
import re
import time
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, request, render_template

BASE = Path(__file__).parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

app = Flask(__name__)


# =========================================================
# VIREX / NOIR PRODUCT DATABASE
# =========================================================

PRODUCTS = [
    {
        "name": "212 MEN NYC",
        "aliases": ["212", "212 men", "212 nyc"],
        "notes": "Citrus, Green, Woody, Spicy, Musky",
        "longevity": "6–8 Hours",
        "best_for": "Daily Wear, Office, College, Dates, Casual Outings",
        "price_15": 299,
        "regular_15": 599,
        "price_30": 549,
        "regular_30": 799,
    },
    {
        "name": "DUNHILL DESIRE",
        "aliases": ["dunhill", "dunhill desire"],
        "notes": "Apple, Orange, Spicy, Vanilla, Woody",
        "longevity": "6–8 Hours",
        "best_for": "Office, Dates, Evening Wear, Winter, Casual Events",
        "price_15": 299,
        "regular_15": 999,
        "price_30": 499,
        "regular_30": 1499,
    },
    {
        "name": "HAWAS FIRE",
        "aliases": ["hawas fire"],
        "notes": "Sweet, Spicy, Aquatic, Smoky, Amber",
        "longevity": "7–9 Hours",
        "best_for": "Dates, Night Out, Parties, Winter, Special Events",
        "price_15": 329,
        "regular_15": 999,
        "price_30": 599,
        "regular_30": 1499,
    },
    {
        "name": "ONE MILLION",
        "aliases": ["1 million", "one million", "one-million"],
        "notes": "Sweet, Spicy, Citrus, Leather, Woody",
        "longevity": "7–10 Hours",
        "best_for": "Parties, Night Out, Dates, Winter, Special Events",
        "price_15": 249,
        "regular_15": 999,
        "price_30": 499,
        "regular_30": 1499,
    },
    {
        "name": "DIOR SAUVAGE",
        "aliases": ["dior", "dior sauvage", "sauvage"],
        "notes": "Woody, Spicy, Sweet, Smoky",
        "longevity": "6–8 Hours",
        "best_for": "Daily Wear, Office, Dates, Events",
        "price_15": 299,
        "regular_15": 999,
        "price_30": 599,
        "regular_30": 1499,
    },
    {
        "name": "NAUTICA VOYAGE",
        "aliases": ["nautica", "nautica voyage", "voyage"],
        "notes": "Aquatic, Green Apple, Fresh, Woody",
        "longevity": "5–7 Hours",
        "best_for": "Daily Wear, Summer Days, College, Office, Casual Outings",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 599,
        "regular_30": 1499,
    },
    {
        "name": "HAWAS ICE",
        "aliases": ["hawas ice"],
        "notes": "Aquatic, Citrus, Sweet, Musky, Fresh Spicy",
        "longevity": "7–9 Hours",
        "best_for": "Daily Wear, Summer Days, College, Office, Casual Outings",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 549,
        "regular_30": 1499,
    },
    {
        "name": "BLEU DE CHANEL",
        "aliases": ["bleu", "bleu de chanel", "bdc"],
        "notes": "Citrus, Woody, Aromatic, Fresh Spicy, Incense",
        "longevity": "7–10 Hours",
        "best_for": "Office, Daily Wear, Meetings, Dates, Special Events",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 549,
        "regular_30": 1499,
    },
    {
        "name": "VAMPIRE BLOOD",
        "aliases": ["vampire", "vampire blood"],
        "notes": "Sweet, Spicy, Smoky, Amber, Woody",
        "longevity": "7–9 Hours",
        "best_for": "Night Out, Parties, Winter, Dates, Special Events",
        "price_15": 399,
        "regular_15": 999,
        "price_30": 649,
        "regular_30": 1499,
    },
    {
        "name": "SRK",
        "aliases": ["srk", "shah rukh", "shahrukh", "shah rukh inspired"],
        "notes": "Fresh, Woody, Spicy, Soft Floral, Amber",
        "longevity": "6–8 Hours",
        "best_for": "Dates, Weddings, Events, Office, Evening Wear",
        "price_15": 299,
        "regular_15": 999,
        "price_30": 499,
        "regular_30": 1499,
    },
    {
        "name": "STRONGER WITH YOU",
        "aliases": ["stronger with you", "sw y", "swy"],
        "notes": "Chestnut, Vanilla, Sweet Spicy, Amber, Woody",
        "longevity": "7–10 Hours",
        "best_for": "Dates, Winter, Night Out, Parties, Special Moments",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 499,
        "regular_30": 1499,
    },
    {
        "name": "GUCCI FLORA",
        "aliases": ["gucci flora", "flora", "gucci"],
        "notes": "Floral, Citrus, Sweet, Powdery, Soft Woody",
        "longevity": "5–7 Hours",
        "best_for": "Daily Wear, Office, College, Dates, Casual Outings",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 599,
        "regular_30": 1499,
    },
    {
        "name": "CK1",
        "aliases": ["ck1", "ck 1", "calvin klein"],
        "notes": "Citrus, Green, Fresh Spicy, Aromatic, Woody",
        "longevity": "6–8 Hours",
        "best_for": "Daily Wear, Summer Days, College, Office, Casual Outings",
        "price_15": 299,
        "regular_15": 799,
        "price_30": 499,
        "regular_30": 1299,
    },
    {
        "name": "9PM",
        "aliases": ["9pm", "9 pm", "nine pm"],
        "notes": "Vanilla, Sweet, Fruity, Amber, Warm Spicy",
        "longevity": "8–10 Hours",
        "best_for": "Date Night, Evening Wear, Parties, Winter Days, Special Occasions",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 549,
        "regular_30": 1499,
    },
    {
        "name": "COOL WATER",
        "aliases": ["cool water", "coolwater"],
        "notes": "Aquatic, Marine, Green, Aromatic, Fresh Spicy",
        "longevity": "6–8 Hours",
        "best_for": "Daily Wear, Summer Days, College, Office, Casual Outings",
        "price_15": 299,
        "regular_15": 799,
        "price_30": 499,
        "regular_30": 1299,
    },
    {
        "name": "LATTAFA KHAMRAH",
        "aliases": ["khamrah", "lattafa", "lattafa khamrah"],
        "notes": "Cinnamon, Vanilla, Sweet, Amber, Woody, Warm Spicy",
        "longevity": "8–12 Hours",
        "best_for": "Date Night, Winter Days, Parties, Special Occasions, Evening Wear",
        "price_15": 399,
        "regular_15": 1099,
        "price_30": 599,
        "regular_30": 1699,
    },
    {
        "name": "CREED AVENTUS",
        "aliases": ["creed", "creed aventus", "aventus"],
        "notes": "Pineapple, Bergamot, Smoky, Woody, Musky",
        "longevity": "8–10 Hours",
        "best_for": "Office, Date Night, Parties, Special Occasions, Year-Round Wear",
        "price_15": 399,
        "regular_15": 1199,
        "price_30": 599,
        "regular_30": 1799,
    },
    {
        "name": "BLUEBERRY",
        "aliases": ["blueberry"],
        "notes": "Blueberry, Fruity, Sweet, Fresh, Musky",
        "longevity": "6–8 Hours",
        "best_for": "Daily Wear, College, Casual Outings, Hangouts, Daytime Wear",
        "price_15": 299,
        "regular_15": 799,
        "price_30": 499,
        "regular_30": 1299,
    },
    {
        "name": "TOBACCO VANILLE",
        "aliases": ["tobacco", "tobacco vanille", "tobacco vanilla"],
        "notes": "Tobacco, Vanilla, Sweet, Warm Spicy, Woody",
        "longevity": "8–12 Hours",
        "best_for": "Date Night, Winter Days, Evening Wear, Parties, Special Occasions",
        "price_15": 399,
        "regular_15": 1099,
        "price_30": 599,
        "regular_30": 1699,
    },
    {
        "name": "GOOD GIRL",
        "aliases": ["good girl"],
        "notes": "Vanilla, White Floral, Sweet, Warm Spicy, Cacao",
        "longevity": "8–10 Hours",
        "best_for": "Date Night, Parties, Evening Wear, Special Occasions, Winter Days",
        "price_15": 399,
        "regular_15": 1099,
        "price_30": 599,
        "regular_30": 1699,
    },
    {
        "name": "VERSACE EROS",
        "aliases": ["eros", "versace", "versace eros"],
        "notes": "Mint, Vanilla, Apple, Citrus, Woody, Fresh Spicy",
        "longevity": "8–10 Hours",
        "best_for": "Date Night, Parties, College, Casual Outings, Evening Wear",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 549,
        "regular_30": 1499,
    },
    {
        "name": "BAD BOY",
        "aliases": ["bad boy"],
        "notes": "Cocoa, Tonka Bean, Amber, Citrus, Woody, Aromatic",
        "longevity": "8–10 Hours",
        "best_for": "Date Night, Parties, Evening Wear, Winter Days, Special Occasions",
        "price_15": 349,
        "regular_15": 999,
        "price_30": 549,
        "regular_30": 1499,
    },
]


# =========================================================
# ORDER STORAGE
# =========================================================

def load_orders():
    path = DATA / "orders.json"

    if not path.exists():
        path.write_text("[]", encoding="utf-8")
        return []

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


orders = load_orders()


def save_orders():
    path = DATA / "orders.json"
    path.write_text(
        json.dumps(orders, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# =========================================================
# HELPERS
# =========================================================

def normalize(text):
    text = str(text or "").lower().strip()
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def find_product(message):
    text = normalize(message)
    matches = []

    for product in PRODUCTS:
        for alias in product["aliases"]:
            alias_normalized = normalize(alias)

            if alias_normalized in text:
                matches.append((len(alias_normalized), product))

    if matches:
        matches.sort(key=lambda item: item[0], reverse=True)
        return matches[0][1]

    return None


def detect_size(message):
    text = normalize(message)

    if re.search(r"\b30\s*ml\b", text):
        return "30ml"

    if re.search(r"\b15\s*ml\b", text):
        return "15ml"

    return None


def price_text(product, size=None):

    if size == "15ml":
        return (
            f"Regular Price: ৳{product['regular_15']}\n"
            f"Offer Price: ৳{product['price_15']}"
        )

    if size == "30ml":
        return (
            f"Regular Price: ৳{product['regular_30']}\n"
            f"Offer Price: ৳{product['price_30']}"
        )

    return (
        f"15ml — Regular ৳{product['regular_15']} → Offer ৳{product['price_15']}\n"
        f"30ml — Regular ৳{product['regular_30']} → Offer ৳{product['price_30']}"
    )


def greeting():
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "শুভ সকাল"
    elif 12 <= hour < 17:
        return "শুভ অপরাহ্ন"
    elif 17 <= hour < 21:
        return "শুভ সন্ধ্যা"
    else:
        return "শুভ রাত্রি"


# =========================================================
# SALES AGENT
# =========================================================

def ai_reply(message):

    text = normalize(message)

    if not text:
        return (
            f"{greeting()} 👋\n\n"
            "আমি Virex AI Sales Agent।\n"
            "NOIR Fragrance-এর product, price, fragrance, longevity, "
            "recommendation এবং order সম্পর্কে সাহায্য করতে পারি।"
        )

    product = find_product(text)
    size = detect_size(text)

    greeting_words = [
        "hi",
        "hello",
        "hey",
        "হাই",
        "হ্যালো",
        "হাই ভাই",
        "আসসালামু আলাইকুম",
        "assalamualaikum",
    ]

    if any(word in text for word in greeting_words):
        return (
            f"{greeting()} 👋\n\n"
            "NOIR Fragrance-এ স্বাগতম!\n\n"
            "আমি Virex AI Sales Agent। আপনি চাইলে আমাকে জিজ্ঞেস করতে পারেন:\n"
            "• কোন perfume আপনার জন্য ভালো\n"
            "• Price\n"
            "• Fragrance notes\n"
            "• Longevity\n"
            "• 15ml / 30ml price\n"
            "• Order"
        )

    # General recommendation
    recommendation_words = [
        "recommend",
        "suggest",
        "best",
        "recommendation",
        "ভালো",
        "সেরা",
        "কোনটা",
        "কোন perfume",
        "পারফিউম সাজেস্ট",
        "সাজেস্ট",
    ]

    if any(word in text for word in recommendation_words) and not product:

        return (
            "অবশ্যই! 😊 আপনার প্রয়োজন অনুযায়ী কয়েকটি ভালো option:\n\n"
            "🔥 **HAWAS FIRE** — Date, Party, Night Out\n"
            "🌊 **HAWAS ICE** — Fresh, Summer, Daily Wear\n"
            "💎 **BLEU DE CHANEL** — Office, Meeting, Smart Look\n"
            "🍍 **CREED AVENTUS** — Premium & versatile\n"
            "🌙 **9PM** — Date Night & Evening\n\n"
            "আপনি চাইলে আপনার budget বা কোথায় ব্যবহার করবেন সেটা বলুন—"
            "আমি একটি specific perfume recommend করব।"
        )

    if product:

        if any(word in text for word in [
            "price",
            "দাম",
            "কত",
            "tk",
            "টাকা",
            "মূল্য"
        ]):
            return (
                f"💜 **{product['name']}**-এর price:\n\n"
                f"{price_text(product, size)}"
            )

        if any(word in text for word in [
            "longevity",
            "lasting",
            "last",
            "স্থায়িত্ব",
            "কতক্ষণ",
            "লাস্টিং",
            "টেকে",
        ]):
            return (
                f"⏱️ **{product['name']}** সাধারণত "
                f"**{product['longevity']}** পর্যন্ত lasting দিতে পারে।"
            )

        if any(word in text for word in [
            "note",
            "notes",
            "smell",
            "fragrance",
            "গন্ধ",
            "ফ্র্যাগরেন্স",
            "স্মেল",
        ]):
            return (
                f"🌿 **{product['name']}** fragrance profile:\n\n"
                f"{product['notes']}\n\n"
                f"⏱️ Longevity: **{product['longevity']}**\n"
                f"✨ Best For: {product['best_for']}"
            )

        if any(word in text for word in [
            "order",
            "অর্ডার",
            "নিতে চাই",
            "নিব",
            "কিনতে চাই",
            "কিনবো",
        ]):
            return (
                f"অবশ্যই! 🛍️ **{product['name']}** order করা যাবে।\n\n"
                f"{price_text(product, size)}\n\n"
                "Order confirm করার জন্য লাগবে:\n"
                "1. Product name\n"
                "2. Size — 15ml / 30ml\n"
                "3. Quantity\n"
                "4. Name\n"
                "5. Phone number\n"
                "6. Full address"
            )

        return (
            f"💜 **{product['name']}**\n\n"
            f"🌿 Fragrance: {product['notes']}\n"
            f"⏱️ Longevity: {product['longevity']}\n"
            f"✨ Best For: {product['best_for']}\n\n"
            f"{price_text(product, size)}"
        )

    # Product catalogue
    if any(word in text for word in [
        "catalogue",
        "catalog",
        "product list",
        "products",
        "সব perfume",
        "সবগুলো",
        "প্রোডাক্ট",
        "লিস্ট",
    ]):
        names = [product["name"] for product in PRODUCTS]

        return (
            "💜 NOIR Fragrance-এর available products:\n\n"
            + "\n".join(f"• {name}" for name in names)
            + "\n\n"
            "আপনি যেকোনো perfume-এর নাম লিখলে আমি তার details জানিয়ে দেব।"
        )

    # Men
    if any(word in text for word in [
        "men",
        "male",
        "পুরুষ",
        "ছেলেদের",
        "ছেলেদের জন্য",
    ]):
        names = [
            product["name"]
            for product in PRODUCTS
            if product["name"] not in ["GUCCI FLORA", "GOOD GIRL"]
        ]

        return (
            "👔 Men's fragrance-এর মধ্যে কিছু জনপ্রিয় option:\n\n"
            + " • ".join(names[:12])
            + "\n\n"
            "আপনার পছন্দ—fresh, sweet, woody নাকি strong—বললে "
            "আমি আরও specific recommendation দিতে পারি।"
        )

    # Women
    if any(word in text for word in [
        "women",
        "female",
        "মেয়েদের",
        "মহিলাদের",
    ]):
        return (
            "🌸 Women's fragrance-এর জন্য:\n\n"
            "• GUCCI FLORA\n"
            "• GOOD GIRL\n\n"
            "চাইলে আমি দুটির fragrance ও price compare করে দিতে পারি।"
        )

    # Delivery
    if any(word in text for word in [
        "delivery",
        "ডেলিভারি",
        "delivery charge",
        "চার্জ",
    ]):
        return (
            "🚚 Delivery charge location অনুযায়ী পরিবর্তিত হতে পারে।\n\n"
            "আপনার location লিখলে delivery সম্পর্কে সাহায্য করতে পারি।"
        )

    # Order general
    if any(word in text for word in [
        "order",
        "অর্ডার",
    ]):
        return (
            "🛍️ Order করতে আমাকে এই information দিন:\n\n"
            "1. Product name\n"
            "2. Size — 15ml / 30ml\n"
            "3. Quantity\n"
            "4. Name\n"
            "5. Phone number\n"
            "6. Full address"
        )

    return (
        "জি 😊 আমি **Virex AI Sales Agent**।\n\n"
        "আমি NOIR Fragrance-এর:\n"
        "• Product\n"
        "• Price\n"
        "• Fragrance\n"
        "• Longevity\n"
        "• Recommendation\n"
        "• Order\n\n"
        "সম্পর্কে সাহায্য করতে পারি।\n\n"
        "যেমন লিখতে পারেন: **Dior Sauvage price**"
    )


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.get("/api/products")
def get_products():

    result = []

    for index, product in enumerate(PRODUCTS, start=1):

        result.append({
            "id": index,
            "name": product["name"],
            "description": product["notes"],
            "notes": product["notes"],
            "longevity": product["longevity"],
            "best_for": product["best_for"],
            "price_15": product["price_15"],
            "price_30": product["price_30"],
            "regular_15": product["regular_15"],
            "regular_30": product["regular_30"],
            "price": product["price_15"],
            "stock": "Available",
        })

    return jsonify(result)


@app.get("/api/orders")
def get_orders():
    return jsonify(orders)


@app.post("/api/chat")
def chat():

    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    # Small natural delay
    time.sleep(1.2)

    reply = ai_reply(message)

    return jsonify({
        "reply": reply
    })


@app.post("/api/orders")
def create_order():

    data = request.get_json(silent=True) or {}

    try:
        quantity = int(data.get("quantity", 1))
    except Exception:
        quantity = 1

    order = {
        "id": len(orders) + 1,
        "customer_name": data.get("customer_name", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "product": data.get("product", ""),
        "size": data.get("size", ""),
        "quantity": quantity,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    orders.append(order)
    save_orders()

    return jsonify(order), 201


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)