from flask import Flask, request, jsonify, render_template_string
import os, json, csv, io, re, urllib.request, urllib.error
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)

# =========================================================
# EZKROY AI — ORIGINAL DESIGN + KNOWLEDGE SHEET + GEMINI
# + CONVERSATIONAL ORDER COLLECTION + GOOGLE SHEET SYNC
# =========================================================

KNOWLEDGE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"
KNOWLEDGE_CSV_URL = f"https://docs.google.com/spreadsheets/d/{KNOWLEDGE_SHEET_ID}/export?format=csv"

ORDERS_SHEET_ID = "1OSYvfZzBLqTtIlTo42PECUz0UyaxBVdGFWr8m6xVUso"
# IMPORTANT: set this Render environment variable to your deployed Apps Script /exec URL.
ORDERS_WEBHOOK_URL = os.environ.get("ORDERS_WEBHOOK_URL", "")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = "data"
PRODUCT_FILE = os.path.join(DATA_DIR, "products.json")
ORDER_FILE = os.path.join(DATA_DIR, "orders.json")
os.makedirs(DATA_DIR, exist_ok=True)

INITIAL_PRODUCTS = [
    {"id": 1, "name": "212 MEN NYC", "price_15ml": 299, "price_30ml": 549, "stock": 20, "description": "Fresh, Urban & Confident."},
    {"id": 2, "name": "DUNHILL DESIRE", "price_15ml": 299, "price_30ml": 499, "stock": 20, "description": "Warm, Elegant & Seductive."},
    {"id": 3, "name": "HAWAS FIRE", "price_15ml": 329, "price_30ml": 599, "stock": 20, "description": "Bold, Addictive & Magnetic."},
    {"id": 4, "name": "ONE MILLION", "price_15ml": 249, "price_30ml": 499, "stock": 20, "description": "Bold, Luxurious & Attention-Grabbing."},
    {"id": 5, "name": "DIOR SAUVAGE", "price_15ml": 299, "price_30ml": 599, "stock": 20, "description": "Fresh, Masculine & Long-lasting."},
    {"id": 6, "name": "NAUTICA VOYAGE", "price_15ml": 349, "price_30ml": 599, "stock": 20, "description": "Fresh, Clean & Everyday Confidence."},
    {"id": 7, "name": "HAWAS ICE", "price_15ml": 349, "price_30ml": 549, "stock": 20, "description": "Cool, Fresh & Addictive."},
    {"id": 8, "name": "BLEU DE CHANEL", "price_15ml": 349, "price_30ml": 549, "stock": 20, "description": "Elegant, Fresh & Sophisticated."},
    {"id": 9, "name": "VAMPIRE BLOOD", "price_15ml": 399, "price_30ml": 649, "stock": 20, "description": "Dark, Mysterious & Seductive."},
    {"id": 10, "name": "SRK (Shah Rukh Inspired)", "price_15ml": 299, "price_30ml": 499, "stock": 20, "description": "Classy, Romantic & Royal."},
    {"id": 11, "name": "STRONGER WITH YOU", "price_15ml": 349, "price_30ml": 499, "stock": 20, "description": "Sweet, Warm & Addictive."},
    {"id": 12, "name": "GUCCI FLORA", "price_15ml": 349, "price_30ml": 599, "stock": 20, "description": "Elegant, Feminine & Soft Luxury."},
    {"id": 13, "name": "CK1", "price_15ml": 299, "price_30ml": 499, "stock": 20, "description": "Clean, Iconic & Timeless."},
    {"id": 14, "name": "9PM", "price_15ml": 349, "price_30ml": 549, "stock": 20, "description": "Bold, Sweet & Irresistible."},
    {"id": 15, "name": "COOL WATER", "price_15ml": 299, "price_30ml": 499, "stock": 20, "description": "Fresh, Clean & Timeless."},
    {"id": 16, "name": "LATTAFA KHAMRAH", "price_15ml": 399, "price_30ml": 599, "stock": 20, "description": "Rich, Warm & Addictive."},
    {"id": 17, "name": "CREED AVENTUS", "price_15ml": 399, "price_30ml": 599, "stock": 20, "description": "Bold, Powerful & Legendary."},
    {"id": 18, "name": "BLUEBERRY", "price_15ml": 299, "price_30ml": 499, "stock": 20, "description": "Sweet, Juicy & Addictive."},
    {"id": 19, "name": "TOBACCO VANILLE", "price_15ml": 399, "price_30ml": 599, "stock": 20, "description": "Rich, Warm & Addictive."},
    {"id": 20, "name": "GOOD GIRL", "price_15ml": 399, "price_30ml": 599, "stock": 20, "description": "Sweet, Bold & Irresistible."},
    {"id": 21, "name": "VERSACE EROS", "price_15ml": 349, "price_30ml": 549, "stock": 20, "description": "Fresh, Bold & Irresistible."},
    {"id": 22, "name": "BAD BOY", "price_15ml": 349, "price_30ml": 549, "stock": 20, "description": "Bold, Dark & Unapologetic."}
]

def init_files():
    if not os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, "w", encoding="utf-8") as f:
            json.dump(INITIAL_PRODUCTS, f, indent=2, ensure_ascii=False)
    if not os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)

init_files()

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("JSON load error:", e)
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("JSON save error:", e)
        return False

# =========================================================
# KNOWLEDGE GOOGLE SHEET
# =========================================================
sheet_cache = {"data": [], "loaded_at": None}

def fetch_knowledge_sheet():
    try:
        req = urllib.request.Request(KNOWLEDGE_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(raw))
        rows = []
        for r in reader:
            cleaned = {str(k).strip().lower(): str(v or "").strip() for k, v in r.items() if k is not None}
            if any(cleaned.values()):
                rows.append(cleaned)
        sheet_cache["data"] = rows
        sheet_cache["loaded_at"] = datetime.now().isoformat()
        print(f"Knowledge sheet loaded: {len(rows)} rows")
        return rows
    except Exception as e:
        print("Knowledge sheet fetch error:", e)
        return sheet_cache.get("data", [])

def get_knowledge_data():
    # Refresh if empty or older than 5 minutes.
    loaded_at = sheet_cache.get("loaded_at")
    if not sheet_cache["data"] or not loaded_at:
        return fetch_knowledge_sheet()
    try:
        age = (datetime.now() - datetime.fromisoformat(loaded_at)).total_seconds()
        if age > 300:
            return fetch_knowledge_sheet()
    except Exception:
        pass
    return sheet_cache["data"]

def normalize(text):
    text = str(text or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\u0980-\u09ff\s]", " ", text)).strip()

def search_sheet_knowledge(query):
    rows = get_knowledge_data()
    q_norm = normalize(query)
    if not q_norm:
        return None

    # Exact question match first.
    for row in rows:
        question = normalize(row.get("question", ""))
        answer = row.get("answer", "").strip()
        if answer and question and (q_norm == question or q_norm in question or question in q_norm):
            return answer

    # Keyword matching. Supports comma, |, or newline separated keywords.
    best = None
    best_score = 0
    q_words = set(q_norm.split())
    for row in rows:
        answer = row.get("answer", "").strip()
        if not answer:
            continue
        raw_keywords = row.get("keywords", "")
        keywords = [normalize(x) for x in re.split(r"[,|\n]+", raw_keywords) if normalize(x)]
        score = sum(1 for kw in keywords if kw and (kw in q_norm or kw in q_words))
        if score > best_score:
            best_score = score
            best = answer
    return best if best_score > 0 else None

# =========================================================
# GEMINI
# =========================================================
def ask_gemini(query, context=""):
    if not GEMINI_API_KEY:
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are EZKROY AI, a customer-facing sales assistant for NOIR Fragrance.
Answer naturally and professionally. Use Bengali when the customer writes Bengali or Banglish; use English when the customer writes English.
Never invent product prices, stock, policies, delivery promises, or business facts.
If the provided knowledge context does not contain the answer, say that you do not have that information and ask the customer what they want to know.
Keep replies concise and useful.

KNOWLEDGE CONTEXT:
{context}

CUSTOMER MESSAGE:
{query}
"""
        response = model.generate_content(prompt)
        if response and getattr(response, "text", None):
            return response.text.strip()
    except Exception as e:
        print("Gemini API error:", e)
    return None

# =========================================================
# ORDER SYSTEM
# =========================================================
def new_order_id():
    return "EZK-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def find_product(name):
    products = load_json(PRODUCT_FILE, INITIAL_PRODUCTS)
    n = normalize(name)
    if not n:
        return None
    for p in products:
        pn = normalize(p.get("name", ""))
        if n == pn or n in pn or pn in n:
            return p
    return None

def save_order_locally(order):
    orders = load_json(ORDER_FILE, [])
    orders.append(order)
    return save_json(ORDER_FILE, orders)

def send_order_to_google_sheet(order):
    if not ORDERS_WEBHOOK_URL:
        print("ORDERS_WEBHOOK_URL is not set. Order saved locally only.")
        return False, "webhook_missing"
    try:
        payload = json.dumps(order, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            ORDERS_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "EZKROY/1.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if 200 <= resp.status < 300:
                print("Order synced to Google Sheet:", body[:300])
                return True, body
            return False, f"HTTP {resp.status}"
    except Exception as e:
        print("Google Sheet order sync error:", e)
        return False, str(e)

def complete_order(draft):
    product = find_product(draft.get("product", ""))
    if not product:
        return None, "দুঃখিত, এই প্রোডাক্টটি আমাদের বর্তমান ক্যাটালগে খুঁজে পাচ্ছি না। অন্য কোনো প্রোডাক্টের নাম দিন।"

    size = str(draft.get("size", "15ml")).lower().replace(" ", "")
    if size not in ("15ml", "30ml"):
        size = "15ml"
    unit_price = int(product.get("price_" + size, 0) or 0)
    quantity = max(1, int(draft.get("quantity", 1) or 1))
    total = unit_price * quantity
    order_id = new_order_id()

    order = {
        "Order ID": order_id,
        "Customer Name": draft.get("name", "").strip(),
        "Phone": draft.get("phone", "").strip(),
        "Address": draft.get("address", "").strip(),
        "Product": product.get("name", ""),
        "Size": size,
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Total Price": total,
        "Payment Status": "Pending",
        "Order Status": "New",
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Notes": draft.get("notes", "")
    }

    save_order_locally(order)
    synced, _ = send_order_to_google_sheet(order)
    return order, synced

# In-memory conversation drafts. For a production multi-instance deployment,
# replace this with Redis/database storage.
order_sessions = {}

def is_order_intent(message):
    m = normalize(message)
    triggers = ["order", "অর্ডার", "kinte chai", "নিতে চাই", "buy", "কিনব", "অর্ডার করব"]
    return any(t in m for t in triggers)

def parse_order_from_message(message):
    """Best-effort parser for simple labelled order text."""
    out = {}
    patterns = {
        "product": r"(?:product|পণ্য)\s*[:=-]\s*([^,\n]+)",
        "size": r"(?:size|সাইজ)\s*[:=-]\s*(15ml|30ml)",
        "quantity": r"(?:quantity|qty|পরিমাণ)\s*[:=-]\s*(\d+)",
        "name": r"(?:name|নাম)\s*[:=-]\s*([^,\n]+)",
        "phone": r"(?:phone|mobile|নম্বর|মোবাইল)\s*[:=-]\s*([+\d\- ]{8,20})",
        "address": r"(?:address|ঠিকানা)\s*[:=-]\s*(.+)$"
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, message, flags=re.I)
        if m:
            out[key] = m.group(1).strip()
    return out

def next_order_question(draft):
    if not draft.get("product"):
        return "অবশ্যই 😊 কোন প্রোডাক্টটি অর্ডার করতে চান?"
    if not draft.get("size"):
        p = find_product(draft["product"])
        if p:
            return f"{p['name']} — 15ml ৳{p.get('price_15ml')} / 30ml ৳{p.get('price_30ml')}। কোন সাইজটি চান?"
        return "কোন সাইজটি চান—15ml নাকি 30ml?"
    if not draft.get("quantity"):
        return "কতটি নিতে চান?"
    if not draft.get("name"):
        return "আপনার নামটি দিন।"
    if not draft.get("phone"):
        return "আপনার ফোন নম্বরটি দিন।"
    if not draft.get("address"):
        return "ডেলিভারির সম্পূর্ণ ঠিকানাটি দিন।"
    return None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EZKROY AI Sales Agent</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col font-sans">
    <header class="bg-slate-900 border-b border-slate-800 p-4 shadow-md flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="bg-indigo-600 p-2 rounded-xl text-white font-bold"><i class="fa-solid fa-robot"></i></div>
            <div>
                <h1 class="font-bold text-lg text-indigo-400">EZKROY AI</h1>
                <p class="text-xs text-slate-400">NOIR Fragrance Smart Sales Assistant</p>
            </div>
        </div>
        <div class="flex items-center space-x-2">
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-xs text-slate-300 font-medium">Online</span>
        </div>
    </header>

    <main class="flex-1 max-w-4xl w-full mx-auto p-4 flex flex-col">
        <div id="chat-container" class="flex-1 bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-4 overflow-y-auto space-y-4 mb-4 min-h-[450px] max-h-[60vh]">
            <div class="flex items-start space-x-3">
                <div class="bg-indigo-600 text-white rounded-full w-8 h-8 flex items-center justify-center shrink-0"><i class="fa-solid fa-robot text-xs"></i></div>
                <div class="bg-slate-800 text-slate-200 p-3 rounded-2xl max-w-[80%] text-sm leading-relaxed shadow">
                    স্বাগতম! আমি EZKROY AI। NOIR Fragrance-এর পারফিউম ও ক্যাটালগ সম্পর্কে যেকোনো প্রশ্ন করতে পারেন অথবা সরাসরি অর্ডার প্লেস করতে পারেন। কীভাবে সাহায্য করতে পারি?
                </div>
            </div>
        </div>

        <form id="chat-form" class="flex gap-2 bg-slate-900 p-2 rounded-2xl border border-slate-800 shadow-lg">
            <input type="text" id="user-input" placeholder="আপনার প্রশ্ন লিখুন বা অর্ডার করতে চান বলুন..." class="flex-1 bg-transparent px-4 py-2 text-sm text-slate-100 focus:outline-none">
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2 rounded-xl text-sm font-medium transition cursor-pointer flex items-center justify-center"><i class="fa-solid fa-paper-plane"></i></button>
        </form>
    </main>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const chatForm = document.getElementById('chat-form');
        const userInput = document.getElementById('user-input');

        function appendMessage(sender, text) {
            const isUser = sender === 'user';
            const wrapper = document.createElement('div');
            wrapper.className = `flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`;
            const avatar = document.createElement('div');
            avatar.className = `rounded-full w-8 h-8 flex items-center justify-center shrink-0 ${isUser ? 'bg-emerald-600 text-white' : 'bg-indigo-600 text-white'}`;
            avatar.innerHTML = `<i class="fa-solid ${isUser ? 'fa-user' : 'fa-robot'} text-xs"></i>`;
            const bubble = document.createElement('div');
            bubble.className = `p-3 rounded-2xl max-w-[80%] text-sm leading-relaxed shadow whitespace-pre-wrap ${isUser ? 'bg-emerald-600/20 border border-emerald-500/30 text-emerald-100' : 'bg-slate-800 text-slate-200'}`;
            bubble.innerText = text;
            wrapper.appendChild(avatar);
            wrapper.appendChild(bubble);
            chatContainer.appendChild(wrapper);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = userInput.value.trim();
            if (!text) return;
            appendMessage('user', text);
            userInput.value = '';
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                appendMessage('bot', data.reply || 'দুঃখিত, কোনো উত্তর পাওয়া যায়নি।');
            } catch (err) {
                appendMessage('bot', 'সার্ভার কানেকশন ত্রুটি। দয়া করে আবার চেষ্টা করুন।');
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "knowledge_rows": len(get_knowledge_data()),
        "gemini_configured": bool(GEMINI_API_KEY),
        "order_webhook_configured": bool(ORDERS_WEBHOOK_URL)
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    session_id = str(data.get("session_id") or request.remote_addr or "default")

    if not message:
        return jsonify({"reply": "অনুগ্রহ করে আপনার বার্তা লিখুন।"})

    # Existing draft, or new order intent.
    draft = order_sessions.get(session_id, {})
    if is_order_intent(message) or draft:
        draft.update(parse_order_from_message(message))

        # If the first message is just "I want to order", enter order mode.
        order_sessions[session_id] = draft
        question = next_order_question(draft)

        if question:
            return jsonify({"reply": question, "order_mode": True})

        order, sync_result = complete_order(draft)
        order_sessions.pop(session_id, None)
        if not order:
            return jsonify({"reply": str(sync_result)})

        if sync_result is True:
            sync_text = "আপনার অর্ডারটি Google Sheet-এ সংরক্ষণ করা হয়েছে।"
        elif sync_result == "webhook_missing":
            sync_text = "অর্ডারটি সিস্টেমে নেওয়া হয়েছে, তবে Google Sheet webhook এখনো সেট করা হয়নি।"
        else:
            sync_text = "অর্ডারটি সিস্টেমে নেওয়া হয়েছে; Google Sheet sync-এ সাময়িক সমস্যা হয়েছে।"

        return jsonify({
            "reply": f"অর্ডার কনফার্ম হয়েছে! 🎉\n\nOrder ID: {order['Order ID']}\nProduct: {order['Product']}\nSize: {order['Size']}\nQuantity: {order['Quantity']}\nTotal: ৳{order['Total Price']}\n\n{sync_text}",
            "order_mode": False,
            "order": order
        })

    # 1. Knowledge Sheet answer first.
    sheet_ans = search_sheet_knowledge(message)
    if sheet_ans:
        return jsonify({"reply": sheet_ans, "source": "knowledge_sheet"})

    # 2. Give Gemini the relevant sheet rows as context when possible.
    rows = get_knowledge_data()
    context_rows = []
    for row in rows[:80]:
        q = row.get("question", "")
        a = row.get("answer", "")
        if q or a:
            context_rows.append(f"Q: {q}\nA: {a}")
    context = "\n\n".join(context_rows)
    gemini_ans = ask_gemini(message, context)
    if gemini_ans:
        return jsonify({"reply": gemini_ans, "source": "gemini"})

    return jsonify({"reply": "দুঃখিত, এই প্রশ্নের নির্ভরযোগ্য উত্তর আমার কাছে এখন নেই। আপনি অন্যভাবে প্রশ্নটি লিখে চেষ্টা করতে পারেন।"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
