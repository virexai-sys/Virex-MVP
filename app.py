```python
# =========================================================
# CHAT API — SMART PRODUCT + SHEET + AI
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
            "reply": "আপনার প্রশ্নটি লিখুন।",
            "order_created": False
        })


    print("\nCUSTOMER:", message)


    # =====================================================
    # PRODUCT DETECTION
    # =====================================================

    product = find_product(message)

    size = detect_size(message)


    # =====================================================
    # PRICE QUESTION
    # =====================================================

    if product and is_price_query(message):

        reply = build_product_answer(
            product,
            size
        )

        return jsonify({

            "reply": reply,

            "order_created": False,

            "product": product.get("name"),

            "size": size
        })


    # =====================================================
    # SIMPLE GREETING
    # =====================================================

    normalized = normalize_text(message)

    greetings = [
        "hi",
        "hello",
        "hey",
        "হাই",
        "হ্যালো",
        "আসসালামু আলাইকুম",
        "salam",
        "assalamualaikum"
    ]

    if normalized in greetings:

        return jsonify({

            "reply":
                "হ্যালো! 👋 আমি EZKROY AI Assistant। "
                "আপনি কোনো perfume-এর price, details বা order সম্পর্কে জানতে পারেন।",

            "order_created": False
        })


    # =====================================================
    # ORDER REQUEST
    # =====================================================

    if is_order_request(message):

        if product:

            product_name = product.get(
                "name",
                "এই product"
            )

            if size:

                reply = (
                    f"অবশ্যই! 😊 "
                    f"{product_name} {size} order করতে পারবেন। "
                    f"Order complete করতে আপনার নাম, ফোন নম্বর "
                    f"এবং delivery address দিন।"
                )

            else:

                reply = (
                    f"অবশ্যই! 😊 "
                    f"{product_name} order করতে পারবেন। "
                    f"আপনি কোন size চান — 15ml নাকি 30ml? "
                    f"তারপর আপনার নাম, ফোন নম্বর এবং delivery address দিন।"
                )

        else:

            reply = (
                "অবশ্যই! 😊 কোন perfumeটি order করতে চান "
                "তার নাম বলুন। তারপর size, নাম, ফোন নম্বর "
                "ও delivery address নেব।"
            )


        return jsonify({

            "reply": reply,

            "order_created": False
        })


    # =====================================================
    # PRODUCT INFORMATION QUESTION
    # =====================================================

    if product:

        catalog_info = json.dumps(
            product,
            ensure_ascii=False,
            indent=2
        )

        reply = ask_ai(
            message,
            f"""
The customer is asking about this exact product.

IMPORTANT:
Use ONLY this product information.

{catalog_info}

Do NOT use an unrelated Google Sheet answer.
"""
        )

        return jsonify({

            "reply": reply,

            "order_created": False,

            "product": product.get("name")
        })


    # =====================================================
    # GOOGLE SHEET ANSWER
    # =====================================================

    verified_answer = (
        find_matching_sheet_answer(
            message
        )
    )


    # =====================================================
    # AI RESPONSE
    # =====================================================

    if verified_answer:

        context = f"""
A verified Google Sheet answer was found.

Use it ONLY if it directly answers the customer's question.

Verified answer:
{verified_answer}

Do not add unrelated information.
"""

    else:

        context = """
No verified Google Sheet answer was found.

Answer naturally using EZKROY's available knowledge.
Do not invent product prices or business policies.
"""


    reply = ask_ai(
        message,
        context
    )


    return jsonify({

        "reply":
            reply,

        "order_created":
            False
    })
```
