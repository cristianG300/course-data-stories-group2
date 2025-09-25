import os
import requests
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

# --------------------------------------------------------------------------
# --- NEUER SPARQL-PROXY-ENDPUNKT (WIRD HINZUGEFÜGT) ---
# --------------------------------------------------------------------------
REAL_SPARQL_ENDPOINT = "https://datastoriesnfdi4c.ise.fiz-karlsruhe.de/sparql"

@app.route('/sparql', methods=['GET', 'POST'])
def sparql_proxy():
    """
    This endpoint takes SPARQL requests, forwards them to the real 
    endpoint, and returns the response. This solves the CORS problem.
    """
    try:
        if request.method == 'POST':
            query = request.data
            headers = {
                'Content-Type': request.headers.get('Content-Type'),
                'Accept': request.headers.get('Accept')
            }
        else: # GET
            query = None # GET requests use params, not data
            headers = {'Accept': 'application/sparql-results+json'}
        
        # Make the request to the real SPARQL endpoint
        response = requests.request(
            method=request.method,
            url=REAL_SPARQL_ENDPOINT,
            params=request.args,
            data=query,
            headers=headers,
            timeout=30 # 30-second timeout
        )
        # Return the response from the SPARQL endpoint directly to the browser
        return response.content, response.status_code, response.headers.items()

    except requests.exceptions.RequestException as e:
        print(f"Error forwarding SPARQL request: {e}")
        return "Error connecting to the SPARQL endpoint.", 502

# --------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)