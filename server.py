from flask import Flask, request, jsonify, send_file
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from scraper import run_scraper

app = Flask(__name__)

@app.route("/")
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"))

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    company = data.get("company", "").strip()
    if not company:
        return jsonify({"error": "Company name required"}), 400
    try:
        result = run_scraper(company)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n✅ Buying Signals Server running at: http://localhost:5055\n")
    app.run(port=5055, debug=False)
