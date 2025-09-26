from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os
import random
import json
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Load config
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Reuse your logic
categories = ["Discipline", "Resilience", "Money Mindset", "Growth", "Kindness", "Focus", "Courage"]
vibes = ["classic", "poetic", "snarky", "encouraging", "short and punchy", "metaphorical"]

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
        "You are a highly creative motivational quote generator. "
        "Avoid clichés, ocean metaphors, and overused inspirational tropes. "
        "Your goal is to surprise and inspire with original language. "
        "No sea themes, no nautical language, no Poseidon cosplay. Ever."
    )

    user_prompt = (
        f"Write a {vibe_choice} motivational quote about {category_choice}. "
        "Avoid any version of the quote 'strength comes from overcoming what you thought you couldn’t.' "
        "Avoid all ocean-related language or metaphors. "
        "Do not reference sailing, waves, tides, sea creatures, or anything nautical. "
        "Make it feel fresh, original, and not from a self-help fish. Add 3-5 unique hashtags."
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

@app.route("/quote", methods=["GET"])
def get_quote():
    category = request.args.get("category")
    vibe = request.args.get("vibe")

    quote_data = generate_quote(category, vibe)
    if quote_data is None:
        return jsonify({"error": "Filtered content. Try again."}), 400

    return jsonify(quote_data)

@app.route("/")
def home():
    return jsonify({"message": "Existential Quote Bot API. Use /quote to get motivated."})

if __name__ == "__main__":
    app.run(debug=True)
