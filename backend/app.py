import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup Flask App
app = Flask(__name__)
# Allow requests from your frontend (running on a different port)
CORS(app)

# Configure the Gemini API with your secret key
try:
    api_key = os.environ["GEMINI_API_KEY"]
    if not api_key:
        raise KeyError
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except KeyError:
    raise RuntimeError("GEMINI_API_KEY not found or is empty. Please check your .env file.")

@app.route('/generate-story', methods=['POST'])
def generate_story():
    """Endpoint to receive artist data and return a generated story."""
    data = request.get_json()
    if not data or 'artistName' not in data or 'artistData' not in data:
        return jsonify({"error": "Missing required data"}), 400

    artist_name = data['artistName']
    artist_data = data['artistData']

    prompt = f"""
        Du bist ein barocker Künstler namens {artist_name}. Erzähle eine kurze, fesselnde Geschichte über dein Leben und deine Arbeit in der Ich-Perspektive.
        Nutze die folgenden Daten als Grundlage: {artist_data}.
        Webe die Informationen über deine Werke, Orte und Förderer natürlich in die Geschichte ein.
        Beginne mit einer fesselnden Einleitung.
    """

    try:
        response = model.generate_content(prompt)
        return jsonify({"story": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)