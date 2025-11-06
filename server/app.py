from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3, bcrypt, os, datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=api_key)

MODEL = "models/gemini-2.0-pro"

@app.route('/')
def home():
    return "✅ FitAI backend running", 200


# ---------- WORKOUT ----------
@app.route('/api/generate_workout', methods=['POST'])
def generate_workout():
    try:
        data = request.get_json()
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
        return jsonify({"plan": {"details": response.text.strip()}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- DIET ----------
@app.route('/api/generate_diet', methods=['POST'])
def generate_diet():
    try:
        data = request.get_json()
        user_prompt = f"""
You are a certified nutritionist AI.
Create a detailed, personalized vegetarian diet plan only (no meat or eggs).
Strictly follow:
- Provide exactly {data.get('meals')} meals per day.
- Do NOT include restricted items or allergies.
- Include calories, protein, carbs, and fats per meal.
- Adapt to cuisine and food preference.

User details:
Weight: {data.get('weight')} kg
Height: {data.get('height')} cm
Gender: {data.get('gender')}
Goal: {data.get('goal')}
Cuisine Preference: {data.get('cuisine')}
Food Preference: {data.get('food_preference')}
Restrictions: {data.get('restrictions')}
Meals: {data.get('meals')}
"""
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(user_prompt)
        return jsonify({"plan": {"details": response.text.strip()}})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- DATABASE ----------
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


init_db()


# ---------- AUTH ----------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not all([username, email, password]):
        return jsonify({"error": "All fields required"}), 400
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    joined = datetime.date.today().isoformat()
    try:
        with sqlite3.connect("users.db") as conn:
            conn.execute("INSERT INTO users (username, email, password, member_since) VALUES (?, ?, ?, ?)",
                         (username, email, hashed, joined))
        return jsonify({"message": "Signup successful"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "User already exists"}), 400


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    with sqlite3.connect("users.db") as conn:
        row = conn.execute("SELECT username, password FROM users WHERE email=?", (email,)).fetchone()
    if row and bcrypt.checkpw(password.encode(), row[1]):
        return jsonify({"message": "Login successful", "username": row[0]}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# ---------- MAIN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
