"""
Nutrition Agentic AI — Flask Application
IBM Granite LLM  ·  watsonx.ai
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
import sys

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from agents.nutrition_agent import generate_nutrition_plan, answer_nutrition_query
from agents.guardrails import check_input_safety, get_medical_disclaimer

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Nutrition Agentic AI", "model": "IBM Granite"})


@app.route("/api/generate-plan", methods=["POST"])
def generate_plan():
    """
    POST /api/generate-plan
    Body: {
        name, age, gender, city, country,
        diet_preference, activity_level,
        goals: [],
        medical_history: [],
        allergies: []
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON body"}), 400

    # Basic input validation
    required = ["name", "age"]
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "error": f"Field '{field}' is required."}), 400

    # Name / age safety
    safety = check_input_safety(str(data.get("name", "")))
    if not safety["safe"]:
        return jsonify({"success": False, "error": safety["reason"]}), 422

    logger.info("Generating nutrition plan for user: %s, age: %s", data.get("name"), data.get("age"))

    result = generate_nutrition_plan(data)

    if result["success"]:
        return jsonify(result), 200
    else:
        logger.error("Plan generation failed: %s", result.get("error"))
        return jsonify(result), 500


@app.route("/api/query", methods=["POST"])
def nutrition_query():
    """
    POST /api/query
    Body: {
        query: str,
        user_context: { name, diet_preference, medical_history, city, country }
    }
    """
    data = request.get_json(silent=True)
    if not data or not data.get("query"):
        return jsonify({"success": False, "error": "A 'query' field is required."}), 400

    query        = data["query"].strip()
    user_context = data.get("user_context", {})

    if len(query) < 3:
        return jsonify({"success": False, "error": "Query is too short."}), 400

    if len(query) > 1000:
        return jsonify({"success": False, "error": "Query exceeds 1000 characters."}), 400

    logger.info("Nutrition query: %s", query[:80])

    result = answer_nutrition_query(user_context, query)

    if result["success"]:
        return jsonify(result), 200
    else:
        logger.error("Query failed: %s", result.get("error"))
        return jsonify(result), 500


@app.route("/api/disclaimer", methods=["GET"])
def disclaimer():
    return jsonify({"disclaimer": get_medical_disclaimer()})


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    logger.info("Starting Nutrition Agentic AI on port %s", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
