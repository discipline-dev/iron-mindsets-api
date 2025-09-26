from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import json
from datetime import datetime
import csv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Categories and vibes
categories = ["Discipline", "Resilience", "Money Mindset", "Growth", "Kindness", "Focus", "Courage"]
vibes = ["classic", "poetic", "snarky", "encouraging", "short and punchy", "metaphorical"]

# Filters
banned_phrases = [
    "strength doesn’t come from what you can do",
    "strength doesn't come from what you can do",
    "overcoming the things you once thought you couldn’t",
    "overcoming the things you once thought you couldn't"
]

banned_words = [
    "sea", "ocean", "wave", "tide", "sailing", "anchor", "nautical",
    "buoy", "marine", "ship", "resilienceatsea", "seawarrior", "seaspirit"
]

def normalize(text):
    return text.lower().strip().replace("’", "'").replace("“", '"').replace("”", '"')

def generate_quote(category=None, vibe=None):
    category_choice = category if category in categories else random.choice(categories)
    vibe_choice = vibe if vibe in vibes else random.choice(vibes)

    system_prompt = (
        "You are a motivational quote generator inspired by David Goggins' intensity, "
        "but accessible to a broad audience. Focus on discipline, resilience, focus, and growth. "
        "Encourage people to embrace discomfort, persistence, and self-mastery, but without extreme shock value. "
        "Avoid clichés, avoid tired self-help tropes, and never use ocean metaphors. "
        "Your goal: create quotes that are tough, raw, and inspiring — but still clear and relatable "
        "for everyday people. End with 3-5 strong, modern hashtags."
    )

    user_prompt = (
        f"Write a {vibe_choice} motivational quote about {category_choice}. "
        "Make it intense and practical, with the energy of discipline and resilience. "
        "Do not include clichés or tired phrases like 'what doesn’t kill you makes you stronger.' "
        "Avoid all ocean-related language. Keep it sharp, original, and something someone could live by. "
        "Add 3-5 powerful hashtags."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=100,
        temperature=1.0
    )

    message = response.choices[0].message.content.strip()
    parts = message.rsplit("#", 1)
    quote = parts[0].strip().strip('"')
    hashtags = "#" + parts[1].strip() if len(parts) > 1 else ""

    if any(phrase in normalize(quote) for phrase in banned_phrases):
        return None

    if any(word in hashtags.lower() for word in banned_words):
        return None

    return {
        "quote": quote,
        "hashtags": hashtags,
        "category": category_choice,
        "vibe": vibe_choice,
        "timestamp": datetime.utcnow().isoformat()
    }

def log_request(data):
    """Append each API request to requests_log.csv"""
    file_exists = os.path.isfile("requests_log.csv")
    with open("requests_log.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

@app.route("/quote", methods=["GET"])
def get_quote():
    category = request.args.get("category")
    vibe = request.args.get("vibe")

    quote_data = generate_quote(category, vibe)
    if quote_data is None:
        return jsonify({"error": "Filtered content. Try again."}), 400

    # Log the request
    log_request(quote_data)

    return jsonify(quote_data)

@app.route("/")
def home():
    return jsonify({"message": "Iron Mindsets API. Use /quote to get motivated."})

if __name__ == "__main__":
    app.run(debug=True)
