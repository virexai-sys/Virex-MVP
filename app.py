from flask import Flask, request, jsonify, render_template_string
import os
import json
import csv
import io
import re
import urllib.request
import urllib.error
from datetime import datetime
import google.generativeai as genai

# =========================================================
# EZKROY AI — DESIGN + GOOGLE SHEET + GEMINI API + ORDER SYNC
# =========================================================

app = Flask(__name__)

# =========================================================
# CONFIGURATIONS & GOOGLE SHEETS
# =========================================================

# 1. Knowledge Base Google Sheet (Q&A)
KNOWLEDGE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"
KNOWLEDGE_CSV_URL = f"https://docs.google.com/spreadsheets/d/{KNOWLEDGE_SHEET_ID}/export?format=csv"

# 2. Orders Google Sheet (Order logging via Google Apps Script Webhook or direct CSV mapping)
# Note: For sending orders to a Google Sheet via Python, a Google Apps Script web app URL is usually deployed.
ORDERS_SHEET_ID = "1OSYvfZzBLqTtIlTo42PECUz0UyaxBVdGFWr8m6xVUso"
ORDERS_WEBHOOK_URL = os.environ.get("ORDERS_WEBHOOK_URL", "") # Google Apps Script URL if available

# 3. Gemini API Configuration
# Make sure to set your Gemini API key in environment variables or put it here directly
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
    "portfolio": "https://sites.google.com/view/aiman-porfolio/home"
}

# =========================================================
# FILE PATHS & INITIAL DATA
# =========================================================
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
            json.dump(INITIAL_PRODUCTS, f, indent=2)
    if not os.path.exists(ORDER_FILE):
        with open(ORDER_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

init_files()

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# =========================================================
# KNOWLEDGE SHEET CACHE & FETCHER
# =========================================================
sheet_cache = {"data": [], "loaded_at": None}

def fetch_knowledge_sheet():
    try:
        req = urllib.request.Request(KNOWLEDGE_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            lines = resp.read().decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(lines))
            rows = []
            for r in reader:
                cleaned = {str(k).strip().lower(): str(v).strip() for k, v in r.items() if k is not None}
                if any(cleaned.values()):
                    rows.append(cleaned)
            sheet_cache["data"] = rows
            sheet_cache["loaded_at"] = datetime.now().isoformat()
            return rows
    except Exception as e:
        print("Sheet fetch error:", e)
        return sheet_cache.get("data", [])

def get_knowledge_data():
    if not sheet_cache["data"]:
        return fetch_knowledge_sheet()
    return sheet_cache["data"]

def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\u0980-\u09ff\s]", " ", str(text).lower())).strip()

def search_sheet_knowledge(query):
    rows = get_knowledge_data()
    q_norm = normalize(query)
    if not q_norm:
        return None
    
    # Exact or keyword matching
    for row in rows:
        question = normalize(row.get("question", ""))
        keywords = normalize(row.get("keywords", ""))
        answer = row.get("answer", "")
        
        if q_norm in question or question in q_norm:
            if answer: return answer
        if keywords and any(kw in q_norm for kw in keywords.split(",")):
            if answer: return answer
            
    return None

# =========================================================
# GEMINI API FALLBACK
# =========================================================
def ask_gemini_fallback(query):
    if not GEMINI_API_KEY:
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"You are EZKROY, an AI sales assistant for NOIR Fragrance created by Aiman. Answer the customer query politely and professionally in Bengali or English based on the query: {query}"
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        print("Gemini API Error:", e)
    return None

# =========================================================
# HTML TEMPLATE (Preserving Original Clean UI Design)
# =========================================================
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

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"reply": "অনুগ্রহ করে আপনার বার্তা লিখুন।"})

    # 1. Check Knowledge Sheet
    sheet_ans = search_sheet_knowledge(message)
    if sheet_ans:
        return jsonify({"reply": sheet_ans})

    # 2. Check Order Intent or Products Catalog Match
    products = load_json(PRODUCT_FILE, INITIAL_PRODUCTS)
    msg_lower = message.lower()
    
    if "order" in msg_lower or "অর্ডার" in msg_lower or "kinte chai" in msg_lower or "নিতে চাই" in msg_lower:
        # Simple interactive order prompt guidance
        product_list_str = "\n".join([f"- {p['name']} (15ml: ৳{p.get('price_15ml')}, 30ml: {p.get('price_30ml', 'N/A')})" for p in products[:10]])
        return jsonify({
            "reply": f"অর্ডার করতে চাইলে নিচের ফরম্যাটে আপনার তথ্য দিন:\n\nঅর্ডার: [পণ্যের নাম], [সাইজ যেমন 15ml/30ml], [নাম], [ফোন নম্বর], [ঠিকানা]\n\nআমাদের কিছু জনপ্রিয় প্রোডাক্ট:\n{product_list_str}"
        })

    # 3. Check Gemini API Fallback
    gemini_ans = ask_gemini_fallback(message)
    if gemini_ans:
        return jsonify({"reply": gemini_ans})

    # 4. Default fallback
    return jsonify({"reply": "আপনার প্রশ্নটি বুঝতে পেরেছি। NOIR Fragrance-এর যেকোনো পারফিউম সম্পর্কে জানতে বা অর্ডার করতে আমাদের সাথে যোগাযোগ করতে পারেন!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
