import os
import requests
import google.generativeai as genai
from groq import Groq
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Setup Flask App
app = Flask(__name__)
# Allow requests from your frontend (running on a different port)
CORS(app)

# Initialize Groq Client
try:
    groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"Warning: Could not initialize Groq client. Check GROQ_API_KEY. Error: {e}")
    groq_client = None

def format_special_words(text):
    # This pattern finds words with at least one underscore,
    # consisting only of uppercase letters.
    pattern = r'\b[A-Z]+(?:_[A-Z]+)+\b'

    def replace_func(match):
        # Takes a found word (e.g., "FRESCO_PAINTING_TECHNIQUE")
        # and converts it to "fresco painting technique"
        return match.group(0).replace('_', ' ').lower()

    return re.sub(pattern, replace_func, text)

@app.route('/generate-story', methods=['POST'])
def generate_story():
    """Endpoint to receive artist data and return a generated story."""
    data = request.get_json()
    if not data or 'artistName' not in data or 'artistData' not in data:
        return jsonify({"error": "Missing required data"}), 400

    artist_name = data['artistName']
    artist_data = data['artistData']

    # This is the original prompt
    user_prompt = f"""
        You are the Baroque artist {artist_name}. Using only the key information from {artist_data}, write a concise and factual first-person account of your work.
        Be direct and avoid elaborate storytelling. Make sure to include:
        - Your significant works.
        - The time periods of your creations
        - The specific locations where you created them
        - Your funders.
        - The art forms (e.g., painting) and mediums (e.g., fresco) you used.
    """
    
    story = ""
    try:
        # GROQ (meta-llama/llama-4-scout-17b-16e-instruct)
        # for true open source model use (llama-3.3-70b-versatile)
        if not groq_client:
            raise RuntimeError("Groq client is not initialized.")
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that takes on the role of a baroque artist, telling stories in the first person. Try to be concise and factual.",
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        story = chat_completion.choices[0].message.content

        story = format_special_words(story)
    
        return jsonify({"story": story})

    except Exception as e:
        error_message = f"An error occurred with the AI API: {e}"
        print(f"Error calling AI API: {e}")
        return jsonify({"error": error_message}), 500
    

# --------------------------------------------------------------------------
# --- NEW SPARQL PROXY ENDPOINT (TO BE ADDED) ---
# --------------------------------------------------------------------------
REAL_SPARQL_ENDPOINT = "https://datastoriesnfdi4c.ise.fiz-karlsruhe.de/sparql"

@app.route('/sparql', methods=['GET', 'POST'])
def sparql_proxy():
    """
    This endpoint takes SPARQL requests, forwards them to the real 
    endpoint, and returns the response.
    """
    try:
        # For GET requests, data comes from URL parameters (request.args)
        # For POST requests, data comes from the request body (request.form)
        params_to_forward = request.args if request.method == 'GET' else None
        data_to_forward = request.form if request.method == 'POST' else None

        # Forward the request to the real SPARQL endpoint
        response = requests.request(
            method=request.method,
            url=REAL_SPARQL_ENDPOINT,
            params=params_to_forward,
            data=data_to_forward,
            headers={'Accept': request.headers.get('Accept')},
            timeout=120 # 120-second timeout
        )
        
        # Return the response from the SPARQL endpoint directly to the browser
        return response.content, response.status_code, response.headers.items()

    except requests.exceptions.RequestException as e:
        print(f"Error forwarding SPARQL request: {e}")
        return "Error connecting to the SPARQL endpoint.", 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)