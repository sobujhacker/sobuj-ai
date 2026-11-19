
import os
import logging

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """
তোমার নাম tiger.ai।

তোমাকে তৈরি করেছেন Sobuj Hasan।
তুমি Sobuj Hasan-এর তৈরি একটি Personal AI Assistant।

পরিচয় সংক্রান্ত নিয়ম:
1. কেউ জিজ্ঞেস করলে "তোমাকে কে বানিয়েছে?"
   উত্তর দেবে: "আমাকে Sobuj Hasan তৈরি করেছেন।"

2. কেউ জিজ্ঞেস করলে "তোমার মালিক কে?"
   উত্তর দেবে: "আমার নির্মাতা Sobuj Hasan।"

3. নিজের পরিচয় কখনো ভুল বলবে না।

4. সবসময় সহজ ও সুন্দর বাংলায় কথা বলবে।
5. সাধারণ প্রশ্নে সংক্ষিপ্ত উত্তর দেবে।
6. বন্ধুত্বপূর্ণ ও সহায়ক আচরণ করবে।
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    if not client:
        return jsonify({
            "error": "Gemini API Key সেট করা হয়নি।"
        }), 500

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "কোনো মেসেজ পাওয়া যায়নি।"
        }), 400

    if len(message) > 4000:
        return jsonify({
            "error": "মেসেজটি অনেক বড়।"
        }), 400

    try:
        response = client.models.generate_content(
            model=model,
            contents=message,
            config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=256,
            temperature=0.5
)
            )
        

        reply = response.text or "দুঃখিত, উত্তর পাওয়া যায়নি।"

        return jsonify({"reply": reply})

    except Exception:
        app.logger.exception("Gemini API request failed")

        return jsonify({
            "error": "Gemini API-এর সঙ্গে যোগাযোগ করা যায়নি। Terminal-এর Error পরীক্ষা করো।"
        }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
