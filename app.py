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

app = Flask(__name__)

# =========================================================
# EZKROY AI — SALES AGENT
# =========================================================
# FEATURES
# - EZKROY branded chat dashboard
# - Preview page
# - Google Knowledge Sheet
# - Gemini AI fallback
# - Conversational order collection
# - Local order backup
# - Google Sheet order webhook
# - Health/status endpoint
# =========================================================


# =========================================================
# CONFIGURATION
# =========================================================

KNOWLEDGE_SHEET_ID = "1jS_EIWfTfaqyieN3vUFCnXoA-3IE91_wclG_WnXzRSw"

KNOWLEDGE_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{KNOWLEDGE_SHEET_ID}/export?format=csv"
)

ORDERS_SHEET_ID = "1OSYvfZzBLqTtIlTo42PECUz0UyaxBVdGFWr8m6xVUso"

# Render Environment Variable
ORDERS_WEBHOOK_URL = os.environ.get(
    "ORDERS_WEBHOOK_URL",
    ""
)

GEMINI_API_KEY = os.environ.get(
    "GEMINI_API_KEY",
    ""
)

if GEMINI_API_KEY:
    genai.configure(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# LOCAL DATA
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
# DEFAULT PRODUCTS
# =========================================================

INITIAL_PRODUCTS = [
    {
        "id": 1,
        "name": "212 MEN NYC",
        "price_15ml": 299,
        "price_30ml": 549,
        "stock": 20,
        "description": "Fresh, Urban & Confident."
    },
    {
        "id": 2,
        "name": "DUNHILL DESIRE",
        "price_15ml": 299,
        "price_30ml": 499,
        "stock": 20,
        "description": "Warm, Elegant & Seductive."
    },
    {
        "id": 3,
        "name": "HAWAS FIRE",
        "price_15ml": 329,
        "price_30ml": 599,
        "stock": 20,
        "description": "Bold, Addictive & Magnetic."
    },
    {
        "id": 4,
        "name": "ONE MILLION",
        "price_15ml": 249,
        "price_30ml": 499,
        "stock": 20,
        "description": "Bold, Luxurious & Attention-Grabbing."
    },
    {
        "id": 5,
        "name": "DIOR SAUVAGE",
        "price_15ml": 299,
        "price_30ml": 599,
        "stock": 20,
        "description": "Fresh, Masculine & Long-lasting."
    },
    {
        "id": 6,
        "name": "NAUTICA VOYAGE",
        "price_15ml": 349,
        "price_30ml": 599,
        "stock": 20,
        "description": "Fresh, Clean & Everyday Confidence."
    },
    {
        "id": 7,
        "name": "HAWAS ICE",
        "price_15ml": 349,
        "price_30ml": 549,
        "stock": 20,
        "description": "Cool, Fresh & Addictive."
    },
    {
        "id": 8,
        "name": "BLEU DE CHANEL",
        "price_15ml": 349,
        "price_30ml": 549,
        "stock": 20,
        "description": "Elegant, Fresh & Sophisticated."
    },
    {
        "id": 9,
        "name": "VAMPIRE BLOOD",
        "price_15ml": 399,
        "price_30ml": 649,
        "stock": 20,
        "description": "Dark, Mysterious & Seductive."
    },
    {
        "id": 10,
        "name": "SRK (Shah Rukh Inspired)",
        "price_15ml": 299,
        "price_30ml": 499,
        "stock": 20,
        "description": "Classy, Romantic & Royal."
    },
    {
        "id": 11,
        "name": "STRONGER WITH YOU",
        "price_15ml": 349,
        "price_30ml": 499,
        "stock": 20,
        "description": "Sweet, Warm & Addictive."
    },
    {
        "id": 12,
        "name": "GUCCI FLORA",
        "price_15ml": 349,
        "price_30ml": 599,
        "stock": 20,
        "description": "Elegant, Feminine & Soft Luxury."
    },
    {
        "id": 13,
        "name": "CK1",
        "price_15ml": 299,
        "price_30ml": 499,
        "stock": 20,
        "description": "Clean, Iconic & Timeless."
    },
    {
        "id": 14,
        "name": "9PM",
        "price_15ml": 349,
        "price_30ml": 549,
        "stock": 20,
        "description": "Bold, Sweet & Irresistible."
    },
    {
        "id": 15,
        "name": "COOL WATER",
        "price_15ml": 299,
        "price_30ml": 499,
        "stock": 20,
        "description": "Fresh, Clean & Timeless."
    },
    {
        "id": 16,
        "name": "LATTAFA KHAMRAH",
        "price_15ml": 399,
        "price_30ml": 599,
        "stock": 20,
        "description": "Rich, Warm & Addictive."
    },
    {
        "id": 17,
        "name": "CREED AVENTUS",
        "price_15ml": 399,
        "price_30ml": 599,
        "stock": 20,
        "description": "Bold, Powerful & Legendary."
    },
    {
        "id": 18,
        "name": "BLUEBERRY",
        "price_15ml": 299,
        "price_30ml": 499,
        "stock": 20,
        "description": "Sweet, Juicy & Addictive."
    },
    {
        "id": 19,
        "name": "TOBACCO VANILLE",
        "price_15ml": 399,
        "price_30ml": 599,
        "stock": 20,
        "description": "Rich, Warm & Addictive."
    },
    {
        "id": 20,
        "name": "GOOD GIRL",
        "price_15ml": 399,
        "price_30ml": 599,
        "stock": 20,
        "description": "Sweet, Bold & Irresistible."
    },
    {
        "id": 21,
        "name": "VERSACE EROS",
        "price_15ml": 349,
        "price_30ml": 549,
        "stock": 20,
        "description": "Fresh, Bold & Irresistible."
    },
    {
        "id": 22,
        "name": "BAD BOY",
        "price_15ml": 349,
        "price_30ml": 549,
        "stock": 20,
        "description": "Bold, Dark & Unapologetic."
    }
]


# =========================================================
# FILE INITIALIZATION
# =========================================================

def init_files():

    if not os.path.exists(PRODUCT_FILE):

        with open(
            PRODUCT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                INITIAL_PRODUCTS,
                f,
                indent=2,
                ensure_ascii=False
            )

    if not os.path.exists(ORDER_FILE):

        with open(
            ORDER_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                [],
                f,
                indent=2,
                ensure_ascii=False
            )


init_files()


# =========================================================
# JSON HELPERS
# =========================================================

def load_json(path, default):

    try:

        if os.path.exists(path):

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

    except Exception as e:

        print(
            "JSON load error:",
            e
        )

    return default


def save_json(path, data):

    try:

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception as e:

        print(
            "JSON save error:",
            e
        )

        return False


# =========================================================
# KNOWLEDGE GOOGLE SHEET
# =========================================================

sheet_cache = {
    "data": [],
    "loaded_at": None
}


def fetch_knowledge_sheet():

    try:

        req = urllib.request.Request(
            KNOWLEDGE_CSV_URL,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as resp:

            raw = resp.read().decode(
                "utf-8-sig",
                errors="replace"
            )

        reader = csv.DictReader(
            io.StringIO(raw)
        )

        rows = []

        for row in reader:

            cleaned = {
                str(k).strip().lower():
                str(v or "").strip()

                for k, v in row.items()

                if k is not None
            }

            if any(cleaned.values()):

                rows.append(cleaned)

        sheet_cache["data"] = rows

        sheet_cache["loaded_at"] = (
            datetime.now().isoformat()
        )

        print(
            f"Knowledge sheet loaded: {len(rows)} rows"
        )

        return rows

    except Exception as e:

        print(
            "Knowledge sheet fetch error:",
            e
        )

        return sheet_cache.get(
            "data",
            []
        )


def get_knowledge_data():

    loaded_at = sheet_cache.get(
        "loaded_at"
    )

    if (
        not sheet_cache["data"]
        or not loaded_at
    ):

        return fetch_knowledge_sheet()

    try:

        age = (
            datetime.now()
            - datetime.fromisoformat(
                loaded_at
            )
        ).total_seconds()

        if age > 300:

            return fetch_knowledge_sheet()

    except Exception:

        pass

    return sheet_cache["data"]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize(text):

    text = str(
        text or ""
    ).lower()

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
# SEARCH KNOWLEDGE SHEET
# =========================================================

def search_sheet_knowledge(query):

    rows = get_knowledge_data()

    q_norm = normalize(query)

    if not q_norm:

        return None

    # Exact / partial question match

    for row in rows:

        question = normalize(
            row.get(
                "question",
                ""
            )
        )

        answer = row.get(
            "answer",
            ""
        ).strip()

        if (
            answer
            and question
            and (
                q_norm == question
                or q_norm in question
                or question in q_norm
            )
        ):

            return answer

    # Keyword match

    best = None
    best_score = 0

    q_words = set(
        q_norm.split()
    )

    for row in rows:

        answer = row.get(
            "answer",
            ""
        ).strip()

        if not answer:

            continue

        raw_keywords = row.get(
            "keywords",
            ""
        )

        keywords = [
            normalize(x)

            for x in re.split(
                r"[,|\n]+",
                raw_keywords
            )

            if normalize(x)
        ]

        score = 0

        for keyword in keywords:

            if (
                keyword in q_norm
                or keyword in q_words
            ):

                score += 1

        if score > best_score:

            best_score = score
            best = answer

    if best_score > 0:

        return best

    return None


# =========================================================
# GEMINI
# =========================================================

def ask_gemini(
    query,
    context=""
):

    if not GEMINI_API_KEY:

        return None

    try:

        genai.configure(
            api_key=GEMINI_API_KEY
        )

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        prompt = f"""
You are EZKROY AI, a customer-facing sales assistant for NOIR Fragrance.

Answer naturally and professionally.

Language rules:
- Bengali customer -> Bengali
- Banglish customer -> natural Banglish/Bengali
- English customer -> English

IMPORTANT:
Never invent:
- product prices
- stock
- delivery promises
- business policies
- product facts
- discounts
- payment information

Only use the provided knowledge context.

If the context does not contain the answer, say that you don't currently have that information.

Keep answers concise, friendly and useful.

KNOWLEDGE CONTEXT:
{context}

CUSTOMER MESSAGE:
{query}
"""

        response = model.generate_content(
            prompt
        )

        if (
            response
            and getattr(
                response,
                "text",
                None
            )
        ):

            return response.text.strip()

    except Exception as e:

        print(
            "Gemini API error:",
            e
        )

    return None


# =========================================================
# ORDER SYSTEM
# =========================================================

def new_order_id():

    return (
        "EZK-"
        + datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )
    )


def find_product(name):

    products = load_json(
        PRODUCT_FILE,
        INITIAL_PRODUCTS
    )

    n = normalize(name)

    if not n:

        return None

    for product in products:

        pn = normalize(
            product.get(
                "name",
                ""
            )
        )

        if (
            n == pn
            or n in pn
            or pn in n
        ):

            return product

    return None


def save_order_locally(order):

    orders = load_json(
        ORDER_FILE,
        []
    )

    orders.append(order)

    return save_json(
        ORDER_FILE,
        orders
    )


# =========================================================
# GOOGLE SHEET ORDER WEBHOOK
# =========================================================

def send_order_to_google_sheet(order):

    if not ORDERS_WEBHOOK_URL:

        print(
            "ORDERS_WEBHOOK_URL is not set."
        )

        return False, "webhook_missing"

    try:

        payload = json.dumps(
            order,
            ensure_ascii=False
        ).encode("utf-8")

        req = urllib.request.Request(
            ORDERS_WEBHOOK_URL,
            data=payload,
            headers={
                "Content-Type":
                    "application/json",
                "User-Agent":
                    "EZKROY/1.0"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            req,
            timeout=15
        ) as resp:

            body = resp.read().decode(
                "utf-8",
                errors="replace"
            )

            if (
                200
                <= resp.status
                < 300
            ):

                print(
                    "Order synced:",
                    body[:300]
                )

                return True, body

            return False, (
                f"HTTP {resp.status}"
            )

    except Exception as e:

        print(
            "Google Sheet order sync error:",
            e
        )

        return False, str(e)


# =========================================================
# COMPLETE ORDER
# =========================================================

def complete_order(draft):

    product = find_product(
        draft.get(
            "product",
            ""
        )
    )

    if not product:

        return (
            None,
            "দুঃখিত, এই প্রোডাক্টটি আমাদের বর্তমান "
            "ক্যাটালগে খুঁজে পাচ্ছি না।"
        )

    size = str(
        draft.get(
            "size",
            "15ml"
        )
    ).lower().replace(
        " ",
        ""
    )

    if size not in (
        "15ml",
        "30ml"
    ):

        size = "15ml"

    unit_price = int(
        product.get(
            "price_" + size,
            0
        )
        or 0
    )

    try:

        quantity = max(
            1,
            int(
                draft.get(
                    "quantity",
                    1
                )
                or 1
            )
        )

    except Exception:

        quantity = 1

    total = (
        unit_price
        * quantity
    )

    order_id = new_order_id()

    order = {

        "Order ID":
            order_id,

        "Customer Name":
            draft.get(
                "name",
                ""
            ).strip(),

        "Phone":
            draft.get(
                "phone",
                ""
            ).strip(),

        "Address":
            draft.get(
                "address",
                ""
            ).strip(),

        "Product":
            product.get(
                "name",
                ""
            ),

        "Size":
            size,

        "Quantity":
            quantity,

        "Unit Price":
            unit_price,

        "Total Price":
            total,

        "Payment Status":
            "Pending",

        "Order Status":
            "New",

        "Date":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "Notes":
            draft.get(
                "notes",
                ""
            )
    }

    local_saved = save_order_locally(
        order
    )

    if not local_saved:

        print(
            "WARNING: Local order save failed."
        )

    synced, sync_body = (
        send_order_to_google_sheet(
            order
        )
    )

    if synced:

        sync_result = True

    elif sync_body == "webhook_missing":

        sync_result = "webhook_missing"

    else:

        sync_result = False

    return order, sync_result


# =========================================================
# ORDER SESSION
# =========================================================

order_sessions = {}


def is_order_intent(message):

    m = normalize(message)

    triggers = [
        "order",
        "অর্ডার",
        "kinte chai",
        "নিতে চাই",
        "buy",
        "কিনব",
        "অর্ডার করব",
        "order korbo",
        "order korte chai",
        "purchase"
    ]

    return any(
        trigger in m
        for trigger in triggers
    )


# =========================================================
# ORDER PARSER
# =========================================================

def parse_order_from_message(message):

    out = {}

    patterns = {

        "product":
            r"(?:product|পণ্য)\s*[:=-]\s*([^,\n]+)",

        "size":
            r"(?:size|সাইজ)\s*[:=-]\s*(15ml|30ml)",

        "quantity":
            r"(?:quantity|qty|পরিমাণ)\s*[:=-]\s*(\d+)",

        "name":
            r"(?:name|নাম)\s*[:=-]\s*([^,\n]+)",

        "phone":
            r"(?:phone|mobile|নম্বর|মোবাইল)\s*[:=-]\s*([+\d\- ]{8,20})",

        "address":
            r"(?:address|ঠিকানা)\s*[:=-]\s*(.+)$"
    }

    for key, pattern in patterns.items():

        match = re.search(
            pattern,
            message,
            flags=re.I
        )

        if match:

            out[key] = (
                match.group(1)
                .strip()
            )

    return out


# =========================================================
# NEXT ORDER QUESTION
# =========================================================

def next_order_question(draft):

    if not draft.get(
        "product"
    ):

        return (
            "অবশ্যই 😊 কোন প্রোডাক্টটি "
            "অর্ডার করতে চান?"
        )

    if not draft.get(
        "size"
    ):

        product = find_product(
            draft["product"]
        )

        if product:

            return (
                f"{product['name']} — "
                f"15ml ৳{product.get('price_15ml')} / "
                f"30ml ৳{product.get('price_30ml')}। "
                f"কোন সাইজটি চান?"
            )

        return (
            "কোন সাইজটি চান—15ml নাকি 30ml?"
        )

    if not draft.get(
        "quantity"
    ):

        return (
            "কতটি নিতে চান?"
        )

    if not draft.get(
        "name"
    ):

        return (
            "আপনার নামটি দিন।"
        )

    if not draft.get(
        "phone"
    ):

        return (
            "আপনার ফোন নম্বরটি দিন।"
        )

    if not draft.get(
        "address"
    ):

        return (
            "ডেলিভারির সম্পূর্ণ ঠিকানাটি দিন।"
        )

    return None


# =========================================================
# MAIN CHAT HTML
# =========================================================

HTML_TEMPLATE = r"""
<!DOCTYPE html>

<html lang="bn">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>EZKROY AI Sales Agent</title>

<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

<link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
>

<style>

body {
    background:
        radial-gradient(
            circle at top right,
            rgba(14,165,233,.12),
            transparent 35%
        ),
        #020617;
}

.glass {
    background: rgba(15,23,42,.72);
    backdrop-filter: blur(18px);
}

.send-btn {
    transition: .2s ease;
}

.send-btn:hover {
    transform: translateY(-1px) scale(1.03);
}

.preview-btn {
    transition: .25s ease;
}

.preview-btn:hover {
    transform: translateY(-2px);
}

</style>

</head>


<body class="text-slate-100 min-h-screen flex flex-col font-sans">


<!-- HEADER -->

<header
    class="bg-slate-900/90 border-b border-slate-800
    p-4 shadow-md flex justify-between items-center"
>

    <div class="flex items-center space-x-3">

        <div
            class="bg-sky-500 p-2 rounded-xl
            text-white font-bold shadow-lg shadow-sky-500/20"
        >

            <i class="fa-solid fa-bolt"></i>

        </div>

        <div>

            <h1
                class="font-bold text-lg text-sky-400"
            >
                EZKROY AI
            </h1>

            <p
                class="text-xs text-slate-400"
            >
                AI Sales Agent for Modern Businesses
            </p>

        </div>

    </div>


    <div class="flex items-center gap-3">

        <!-- PREVIEW BUTTON -->

        <a
            href="/preview"
            class="preview-btn
            hidden sm:flex items-center gap-2
            bg-sky-500/10
            border border-sky-400/30
            text-sky-300
            px-4 py-2
            rounded-xl
            text-xs font-semibold
            hover:bg-sky-500/20"
        >

            <i class="fa-solid fa-eye"></i>

            Preview

        </a>


        <div class="flex items-center space-x-2">

            <span
                class="inline-block
                w-2.5 h-2.5
                rounded-full
                bg-emerald-500
                animate-pulse"
            ></span>

            <span
                class="text-xs
                text-slate-300
                font-medium"
            >
                Online
            </span>

        </div>

    </div>

</header>


<!-- MAIN -->

<main
    class="flex-1 max-w-4xl
    w-full mx-auto p-4
    flex flex-col"
>


    <!-- CHAT -->

    <div
        id="chat-container"
        class="flex-1 glass
        border border-slate-800
        rounded-2xl p-4
        overflow-y-auto
        space-y-4
        mb-4
        min-h-[450px]
        max-h-[65vh]"
    >

        <div
            class="flex items-start space-x-3"
        >

            <div
                class="bg-sky-500
                text-white rounded-full
                w-8 h-8
                flex items-center
                justify-center shrink-0"
            >

                <i
                    class="fa-solid fa-bolt text-xs"
                ></i>

            </div>


            <div
                class="bg-slate-800
                text-slate-200
                p-3 rounded-2xl
                max-w-[80%]
                text-sm
                leading-relaxed
                shadow"
            >

                স্বাগতম! আমি EZKROY AI ⚡

                <br><br>

                NOIR Fragrance-এর
                পারফিউম সম্পর্কে জানতে,
                দাম জানতে অথবা সরাসরি
                অর্ডার করতে পারেন।

                <br><br>

                কীভাবে সাহায্য করতে পারি?

            </div>

        </div>

    </div>


    <!-- INPUT -->

    <form
        id="chat-form"
        class="flex gap-2
        bg-slate-900
        p-2 rounded-2xl
        border border-slate-800
        shadow-lg"
    >

        <input
            type="text"
            id="user-input"
            autocomplete="off"
            placeholder="আপনার প্রশ্ন লিখুন..."
            class="flex-1
            bg-transparent
            px-4 py-2
            text-sm
            text-slate-100
            focus:outline-none"
        >


        <button
            type="submit"
            class="send-btn
            bg-sky-500
            hover:bg-sky-400
            text-white
            px-5 py-2
            rounded-xl
            text-sm
            font-medium
            transition
            cursor-pointer
            flex items-center
            justify-center"
        >

            <i
                class="fa-solid fa-paper-plane"
            ></i>

        </button>

    </form>


    <!-- MOBILE PREVIEW -->

    <a
        href="/preview"
        class="sm:hidden mt-3
        flex items-center justify-center
        gap-2
        bg-sky-500/10
        border border-sky-400/30
        text-sky-300
        px-4 py-3
        rounded-xl
        text-sm font-semibold"
    >

        <i class="fa-solid fa-eye"></i>

        Open Preview

    </a>


</main>


<script>

const chatContainer =
    document.getElementById(
        'chat-container'
    );

const chatForm =
    document.getElementById(
        'chat-form'
    );

const userInput =
    document.getElementById(
        'user-input'
    );


/* =====================================================
   SESSION ID
===================================================== */

let sessionId =
    localStorage.getItem(
        'ezkroy_session_id'
    );

if (!sessionId) {

    sessionId =
        crypto.randomUUID();

    localStorage.setItem(
        'ezkroy_session_id',
        sessionId
    );
}


/* =====================================================
   MESSAGE
===================================================== */

function appendMessage(
    sender,
    text
) {

    const isUser =
        sender === 'user';


    const wrapper =
        document.createElement(
            'div'
        );

    wrapper.className =
        `flex items-start space-x-3
        ${isUser
            ? 'flex-row-reverse space-x-reverse'
            : ''
        }`;


    const avatar =
        document.createElement(
            'div'
        );

    avatar.className =
        `rounded-full w-8 h-8
        flex items-center
        justify-center shrink-0
        ${
            isUser
            ? 'bg-emerald-600 text-white'
            : 'bg-sky-500 text-white'
        }`;


    avatar.innerHTML =
        `<i class="fa-solid ${
            isUser
            ? 'fa-user'
            : 'fa-bolt'
        } text-xs"></i>`;


    const bubble =
        document.createElement(
            'div'
        );

    bubble.className =
        `p-3 rounded-2xl
        max-w-[80%]
        text-sm
        leading-relaxed
        shadow
        whitespace-pre-wrap
        ${
            isUser
            ? 'bg-emerald-600/20 border border-emerald-500/30 text-emerald-100'
            : 'bg-slate-800 text-slate-200'
        }`;


    bubble.innerText =
        text;


    wrapper.appendChild(
        avatar
    );

    wrapper.appendChild(
        bubble
    );

    chatContainer.appendChild(
        wrapper
    );


    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


/* =====================================================
   TYPING
===================================================== */

function showTyping() {

    const typing =
        document.createElement(
            'div'
        );

    typing.id =
        'typing-indicator';

    typing.className =
        'flex items-start space-x-3';


    typing.innerHTML = `

        <div
            class="bg-sky-500
            text-white rounded-full
            w-8 h-8
            flex items-center
            justify-center"
        >

            <i class="fa-solid fa-bolt text-xs"></i>

        </div>

        <div
            class="bg-slate-800
            text-slate-400
            p-3 rounded-2xl
            text-sm"
        >

            <i class="fa-solid fa-circle-notch fa-spin"></i>

            &nbsp; EZKROY AI is typing...

        </div>

    `;


    chatContainer.appendChild(
        typing
    );

    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}


function removeTyping() {

    const typing =
        document.getElementById(
            'typing-indicator'
        );

    if (typing) {

        typing.remove();

    }
}


/* =====================================================
   CHAT SUBMIT
===================================================== */

chatForm.addEventListener(
    'submit',
    async function(e) {

        e.preventDefault();


        const text =
            userInput.value.trim();


        if (!text) return;


        appendMessage(
            'user',
            text
        );


        userInput.value = '';


        showTyping();


        try {

            const response =
                await fetch(
                    '/api/chat',
                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body:
                            JSON.stringify({
                                message: text,
                                session_id:
                                    sessionId
                            })
                    }
                );


            if (!response.ok) {

                throw new Error(
                    'Server error'
                );

            }


            const data =
                await response.json();


            removeTyping();


            appendMessage(
                'bot',
                data.reply ||
                'দুঃখিত, কোনো উত্তর পাওয়া যায়নি।'
            );


        } catch (error) {

            console.error(
                error
            );


            removeTyping();


            appendMessage(
                'bot',
                'সার্ভার কানেকশন ত্রুটি হয়েছে। দয়া করে কয়েক সেকেন্ড পরে আবার চেষ্টা করুন।'
            );

        }

    }
);

</script>

</body>

</html>
"""


# =========================================================
# PREVIEW PAGE
# =========================================================

PREVIEW_TEMPLATE = r"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>EZKROY AI — Preview</title>

<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>

<link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
>


<style>

body {

    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(14,165,233,.18),
            transparent 45%
        ),
        #020617;

}


.card {

    background:
        rgba(15,23,42,.70);

    backdrop-filter:
        blur(20px);

}


.float {

    animation:
        float 4s ease-in-out infinite;

}


@keyframes float {

    0%,100% {

        transform:
            translateY(0);

    }

    50% {

        transform:
            translateY(-10px);

    }

}

</style>

</head>


<body
    class="text-white min-h-screen
    flex items-center
    justify-center p-6"
>


<div
    class="max-w-5xl
    w-full
    text-center"
>


    <!-- LOGO -->

    <div
        class="float
        mx-auto mb-8
        w-20 h-20
        rounded-3xl
        bg-sky-500
        flex items-center
        justify-center
        text-3xl
        shadow-2xl
        shadow-sky-500/20"
    >

        <i
            class="fa-solid fa-bolt"
        ></i>

    </div>


    <p
        class="text-sky-400
        uppercase
        tracking-[.35em]
        text-xs
        font-bold mb-3"
    >
        AI SALES AGENT
    </p>


    <h1
        class="text-4xl
        md:text-6xl
        font-black
        mb-5"
    >

        Meet

        <span
            class="text-sky-400"
        >
            EZKROY
        </span>

    </h1>


    <p
        class="text-slate-400
        max-w-2xl
        mx-auto
        text-base
        md:text-lg
        leading-relaxed
        mb-10"
    >

        An AI-powered sales assistant
        that talks to customers,
        answers questions,
        collects orders and helps
        businesses sell 24/7.

    </p>


    <!-- STORY CARDS -->

    <div
        class="grid
        md:grid-cols-3
        gap-5
        mb-10"
    >


        <div
            class="card
            border border-slate-800
            rounded-3xl
            p-7"
        >

            <div
                class="w-12 h-12
                mx-auto mb-4
                rounded-2xl
                bg-sky-500/10
                text-sky-400
                flex items-center
                justify-center"
            >

                <i
                    class="fa-solid fa-comments"
                ></i>

            </div>

            <h3
                class="font-bold text-lg mb-2"
            >
                Customer Message
            </h3>

            <p
                class="text-slate-400
                text-sm"
            >
                A customer asks about
                a product, price or availability.
            </p>

        </div>


        <div
            class="card
            border border-slate-800
            rounded-3xl
            p-7"
        >

            <div
                class="w-12 h-12
                mx-auto mb-4
                rounded-2xl
                bg-sky-500/10
                text-sky-400
                flex items-center
                justify-center"
            >

                <i
                    class="fa-solid fa-robot"
                ></i>

            </div>

            <h3
                class="font-bold text-lg mb-2"
            >
                EZKROY Responds
            </h3>

            <p
                class="text-slate-400
                text-sm"
            >
                EZKROY understands the
                customer and responds naturally.
            </p>

        </div>


        <div
            class="card
            border border-slate-800
            rounded-3xl
            p-7"
        >

            <div
                class="w-12 h-12
                mx-auto mb-4
                rounded-2xl
                bg-sky-500/10
                text-sky-400
                flex items-center
                justify-center"
            >

                <i
                    class="fa-solid fa-cart-shopping"
                ></i>

            </div>

            <h3
                class="font-bold text-lg mb-2"
            >
                Order Collected
            </h3>

            <p
                class="text-slate-400
                text-sm"
            >
                Product, size, quantity,
                name, phone and address
                are collected.
            </p>

        </div>


    </div>


    <!-- CTA -->

    <a
        href="/"
        class="inline-flex
        items-center
        gap-3
        bg-sky-500
        hover:bg-sky-400
        px-7 py-4
        rounded-2xl
        font-bold
        transition
        shadow-xl
        shadow-sky-500/20"
    >

        <i
            class="fa-solid fa-bolt"
        ></i>

        Try EZKROY AI

    </a>


    <p
        class="text-xs
        text-slate-600
        mt-8"
    >

        EZKROY AI Sales Agent

    </p>


</div>

</body>

</html>
"""


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():

    return render_template_string(
        HTML_TEMPLATE
    )


@app.route("/preview")
def preview():

    return render_template_string(
        PREVIEW_TEMPLATE
    )


@app.route("/health")
def health():

    knowledge_rows = len(
        get_knowledge_data()
    )

    return jsonify({

        "status":
            "ok",

        "service":
            "EZKROY AI",

        "knowledge_rows":
            knowledge_rows,

        "gemini_configured":
            bool(
                GEMINI_API_KEY
            ),

        "order_webhook_configured":
            bool(
                ORDERS_WEBHOOK_URL
            ),

        "time":
            datetime.now().isoformat()

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

    session_id = str(
        data.get(
            "session_id"
        )
        or request.remote_addr
        or "default"
    )

    if not message:

        return jsonify({

            "reply":
                "অনুগ্রহ করে আপনার "
                "বার্তা লিখুন।"

        })


    # =====================================================
    # ORDER MODE
    # =====================================================

    draft = order_sessions.get(
        session_id,
        {}
    )

    if (
        is_order_intent(message)
        or draft
    ):

        draft.update(
            parse_order_from_message(
                message
            )
        )

        # Simple natural-language size detection

        normalized_message = normalize(
            message
        )

        if not draft.get(
            "size"
        ):

            if (
                "30ml"
                in normalized_message
            ):

                draft["size"] = "30ml"

            elif (
                "15ml"
                in normalized_message
            ):

                draft["size"] = "15ml"


        # Simple quantity detection

        if not draft.get(
            "quantity"
        ):

            quantity_match = re.search(
                r"(?:x\s*)?(\d+)\s*(?:টা|pcs?|piece|pieces)?",
                message,
                flags=re.I
            )

            if quantity_match:

                try:

                    draft["quantity"] = int(
                        quantity_match.group(1)
                    )

                except Exception:

                    pass


        order_sessions[
            session_id
        ] = draft


        question = (
            next_order_question(
                draft
            )
        )


        if question:

            return jsonify({

                "reply":
                    question,

                "order_mode":
                    True

            })


        order, sync_result = (
            complete_order(
                draft
            )
        )


        order_sessions.pop(
            session_id,
            None
        )


        if not order:

            return jsonify({

                "reply":
                    str(
                        sync_result
                    )

            })


        if sync_result is True:

            sync_text = (
                "আপনার অর্ডারটি "
                "Google Sheet-এ "
                "সফলভাবে সংরক্ষণ করা হয়েছে।"
            )

        elif (
            sync_result
            == "webhook_missing"
        ):

            sync_text = (
                "অর্ডারটি সিস্টেমে নেওয়া হয়েছে। "
                "তবে Google Sheet webhook "
                "এখনো সেট করা হয়নি।"
            )

        else:

            sync_text = (
                "অর্ডারটি সিস্টেমে নেওয়া হয়েছে; "
                "তবে Google Sheet sync-এ "
                "সাময়িক সমস্যা হয়েছে।"
            )


        return jsonify({

            "reply":
                f"অর্ডার কনফার্ম হয়েছে! 🎉\n\n"
                f"Order ID: {order['Order ID']}\n"
                f"Product: {order['Product']}\n"
                f"Size: {order['Size']}\n"
                f"Quantity: {order['Quantity']}\n"
                f"Total: ৳{order['Total Price']}\n\n"
                f"{sync_text}",

            "order_mode":
                False,

            "order":
                order

        })


    # =====================================================
    # KNOWLEDGE SHEET FIRST
    # =====================================================

    sheet_ans = (
        search_sheet_knowledge(
            message
        )
    )


    if sheet_ans:

        return jsonify({

            "reply":
                sheet_ans,

            "source":
                "knowledge_sheet"

        })


    # =====================================================
    # GEMINI CONTEXT
    # =====================================================

    rows = get_knowledge_data()

    context_rows = []


    for row in rows[:80]:

        q = row.get(
            "question",
            ""
        )

        a = row.get(
            "answer",
            ""
        )


        if q or a:

            context_rows.append(
                f"Q: {q}\nA: {a}"
            )


    context = "\n\n".join(
        context_rows
    )


    gemini_ans = ask_gemini(
        message,
        context
    )


    if gemini_ans:

        return jsonify({

            "reply":
                gemini_ans,

            "source":
                "gemini"

        })


    # =====================================================
    # FALLBACK
    # =====================================================

    return jsonify({

        "reply":
            "দুঃখিত, এই প্রশ্নের "
            "নির্ভরযোগ্য উত্তর আমার কাছে "
            "এখন নেই। আপনি অন্যভাবে "
            "প্রশ্নটি লিখে চেষ্টা করতে পারেন।",

        "source":
            "fallback"

    })


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
