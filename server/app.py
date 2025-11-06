from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
from dotenv import load_dotenv
import sqlite3, bcrypt, os, datetime

# Load env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file.")
genai.configure(api_key=api_key)
MODEL = "models/gemini-2.5-pro"

@app.route('/')
def home():
    return "✅ FitAI backend running", 200

# ---------- WORKOUT ----------
@app.route('/api/generate_workout', methods=['POST'])
def generate_workout():
    try:
        data = request.get_json()
        print("🔥 /api/generate_workout hit:", data)

        user_prompt = (
            f"Generate a personalized AI-powered workout plan based on these details:\n"
            f"Weight: {data.get('weight')} kg\n"
            f"Height: {data.get('height')} cm\n"
            f"Gender: {data.get('gender')}\n"
            f"Goal: {data.get('goal')}\n"
            f"Preferred Split: {data.get('split')}\n"
            f"Experience Level: {data.get('level')}\n\n"
            f"Format the response clearly with workout days, exercises, and reps."
        )
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(user_prompt)
        if not getattr(response, "text", "").strip():
            return jsonify({"error": "Empty response from Gemini model."}), 500
        return jsonify({"plan": {"split": data.get("split", "Custom"), "details": response.text.strip()}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- DIET ----------
@app.route('/api/generate_diet', methods=['POST'])
def generate_diet():
    try:
        data = request.get_json()
        print("🥗 /api/generate_diet hit:", data)

        meals = data.get("meals", 4)
        pref = (data.get("food_preference") or "").lower().strip()
        restrictions = (data.get("restrictions") or "").lower()

        # 🔥 Forbidden items based on user preference
        forbidden = []
        if pref == "vegetarian":
            forbidden = ["chicken", "fish", "egg", "mutton", "beef", "pork", "seafood", "prawn", "bacon", "meat", "turkey"]
        elif pref == "vegan":
            forbidden = ["chicken", "fish", "egg", "mutton", "beef", "pork", "seafood", "prawn", "bacon", "meat", "turkey",
                         "milk", "cheese", "curd", "paneer", "yogurt", "butter", "honey"]

        prompt = f"""
You are a certified nutritionist AI.
Generate a personalized diet plan as per the following details.
⚠️ STRICT RULES:
- ABSOLUTELY NEVER include these foods: {', '.join(forbidden)} or any other animal-derived ingredient.
- If vegetarian or vegan, protein sources must come only from plant-based or dairy (for vegetarians) items.
- Respect allergies and restrictions: {restrictions}
- Provide exactly {meals} meals per day.
- Include name, meal contents, and macros for each meal.
- End with a short tip.

User details:
Weight: {data.get('weight')} kg
Height: {data.get('height')} cm
Gender: {data.get('gender')}
Goal: {data.get('goal')}
Cuisine Preference: {data.get('cuisine')}
Food Preference: {data.get('food_preference')}
Meals per day: {data.get('meals')}
"""

        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        text = response.text.strip()

        # 🧹 Basic cleanup (in case model slips in banned foods)
        clean_text = text
        for bad in forbidden:
            if bad.lower() in clean_text.lower():
                print(f"⚠️ Found banned item: {bad}")
                clean_text = clean_text.replace(bad, "tofu / lentils / soya chunks")

        # 🔧 Optional: ensure case-insensitive cleaning
        import re
        for bad in forbidden:
            clean_text = re.sub(bad, "tofu / lentils / soya chunks", clean_text, flags=re.IGNORECASE)

        formatted = clean_text.replace("\n", "<br>").replace("**", "")

        return jsonify({
            "plan": {
                "goal": data.get("goal", "Custom"),
                "details": formatted
            }
        })

    except Exception as e:
        print("❌ Error in /api/generate_diet:", str(e))
        return jsonify({"error": str(e)}), 500



# ---------- DB ----------
def init_db():
    with sqlite3.connect("users.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password BLOB,
                member_since TEXT
            )
        """)
        # add member_since if missing
        try:
            conn.execute("SELECT member_since FROM users LIMIT 1;")
        except sqlite3.OperationalError:
            conn.execute("ALTER TABLE users ADD COLUMN member_since TEXT;")
init_db()

# ---------- SIGNUP ----------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not (username and email and password):
        return jsonify({"error": "All fields required"}), 400
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    joined = datetime.date.today().isoformat()
    try:
        with sqlite3.connect("users.db") as conn:
            conn.execute("INSERT INTO users (username, email, password, member_since) VALUES (?, ?, ?, ?)",
                         (username, email, hashed, joined))
        return jsonify({"message": "Signup successful", "member_since": joined}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400

# ---------- LOGIN ----------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    with sqlite3.connect("users.db") as conn:
        row = conn.execute("SELECT username, password, member_since FROM users WHERE email=?", (email,)).fetchone()
    if row and bcrypt.checkpw(password.encode("utf-8"), row[1]):
        return jsonify({"message": "Login successful", "username": row[0], "email": email, "member_since": row[2]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# ---------- UPDATE PROFILE ----------
@app.route("/api/update_profile", methods=["POST"])
def update_profile():
    data = request.get_json()
    email = data.get("email")  # trusted from client localStorage for this simple app
    new_username = data.get("username")
    new_password = data.get("password", "")

    if not email or not new_username:
        return jsonify({"error": "Email and username required"}), 400

    with sqlite3.connect("users.db") as conn:
        # ensure user exists
        row = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            return jsonify({"error": "User not found"}), 404

        if new_password:
            hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
            conn.execute("UPDATE users SET username=?, password=? WHERE email=?", (new_username, hashed, email))
        else:
            conn.execute("UPDATE users SET username=? WHERE email=?", (new_username, email))

    return jsonify({"message": "Profile updated", "username": new_username}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
