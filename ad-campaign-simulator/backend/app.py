"""
=============================================================
  Ad Campaign Debugging & Analytics Simulator - Backend API
=============================================================
  This is the main file that runs our web server.
  It handles all the routes (URLs) and connects everything.

  HOW TO RUN:
  1. Install requirements: pip install flask flask-cors
  2. Run: python app.py
  3. Open browser at http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

# Import our custom modules
from database import init_db, get_db_connection
from campaigns import (
    create_campaign,
    get_all_campaigns,
    get_campaign_by_id,
    delete_campaign
)
from diagnostics import run_diagnostics
from reports import generate_pdf_report

# -------------------------------------------------------
# App Setup
# -------------------------------------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend (different port) to talk to backend

# Initialize the database when app starts
init_db()
print("✅ Database initialized")


# -------------------------------------------------------
# ROUTE: Home - just a health check
# -------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Ad Campaign Simulator API is running!",
        "version": "1.0.0",
        "endpoints": [
            "GET  /api/campaigns         - List all campaigns",
            "POST /api/campaigns         - Create new campaign",
            "GET  /api/campaigns/<id>    - Get single campaign",
            "DELETE /api/campaigns/<id> - Delete campaign",
            "GET  /api/diagnose/<id>     - Run diagnostics on campaign",
            "GET  /api/insights          - Get all campaign insights",
            "GET  /api/report/<id>       - Export campaign as PDF",
        ]
    })


# -------------------------------------------------------
# ROUTE: Get all campaigns
# -------------------------------------------------------
@app.route("/api/campaigns", methods=["GET"])
def list_campaigns():
    """Returns a list of all campaigns from the database."""
    campaigns = get_all_campaigns()
    return jsonify({"campaigns": campaigns, "count": len(campaigns)})


# -------------------------------------------------------
# ROUTE: Create a new campaign
# -------------------------------------------------------
@app.route("/api/campaigns", methods=["POST"])
def add_campaign():
    """
    Creates a new campaign.
    Expects JSON body with: name, budget, impressions, clicks, conversions
    Auto-calculates: CTR, CPC, Conversion Rate
    """
    data = request.get_json()

    # Validate required fields
    required = ["name", "budget", "impressions", "clicks", "conversions"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    campaign = create_campaign(data)
    return jsonify({"message": "Campaign created!", "campaign": campaign}), 201


# -------------------------------------------------------
# ROUTE: Get single campaign by ID
# -------------------------------------------------------
@app.route("/api/campaigns/<int:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    """Returns details of one specific campaign."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify(campaign)


# -------------------------------------------------------
# ROUTE: Delete a campaign
# -------------------------------------------------------
@app.route("/api/campaigns/<int:campaign_id>", methods=["DELETE"])
def remove_campaign(campaign_id):
    """Deletes a campaign from the database."""
    success = delete_campaign(campaign_id)
    if not success:
        return jsonify({"error": "Campaign not found"}), 404
    return jsonify({"message": "Campaign deleted successfully"})


# -------------------------------------------------------
# ROUTE: Run diagnostics on a campaign
# -------------------------------------------------------
@app.route("/api/diagnose/<int:campaign_id>", methods=["GET"])
def diagnose(campaign_id):
    """
    Runs the diagnostic engine on a campaign.
    Returns detected issues and recommendations.
    """
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    results = run_diagnostics(campaign)
    return jsonify(results)


# -------------------------------------------------------
# ROUTE: Get insights for ALL campaigns
# -------------------------------------------------------
@app.route("/api/insights", methods=["GET"])
def all_insights():
    """Runs diagnostics on every campaign and returns summary."""
    campaigns = get_all_campaigns()
    insights = []
    for c in campaigns:
        result = run_diagnostics(c)
        insights.append({
            "campaign_id": c["id"],
            "campaign_name": c["name"],
            "issues_found": len(result["issues"]),
            "health_score": result["health_score"],
            "top_issue": result["issues"][0]["type"] if result["issues"] else "None"
        })
    return jsonify({"insights": insights})


# -------------------------------------------------------
# ROUTE: Export campaign report as PDF
# -------------------------------------------------------
@app.route("/api/report/<int:campaign_id>", methods=["GET"])
def export_report(campaign_id):
    """Generates a PDF report for a campaign and returns it as download."""
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return jsonify({"error": "Campaign not found"}), 404

    diagnostics = run_diagnostics(campaign)
    pdf_path = generate_pdf_report(campaign, diagnostics)

    return send_from_directory(
        directory=os.path.dirname(pdf_path),
        path=os.path.basename(pdf_path),
        as_attachment=True
    )


# -------------------------------------------------------
# ROUTE: Seed test data (for demo purposes)
# -------------------------------------------------------
@app.route("/api/seed", methods=["POST"])
def seed_data():
    """Loads example campaigns into the database for testing."""
    from seed_data import seed_example_campaigns
    count = seed_example_campaigns()
    return jsonify({"message": f"Seeded {count} example campaigns!"})


# -------------------------------------------------------
# Start the server
# -------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 Starting Ad Campaign Simulator Backend...")
    print("📡 API running at: http://localhost:5000")
    print("🛑 Press CTRL+C to stop\n")
    app.run(debug=True, port=5000)
