import os
import time
import json
import warnings
import urllib3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response, send_file
from scraper_engine import ScraperController
from excel_exporter import export_to_excel

# Suppress insecure SSL warnings for rapid website contact checks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

app = Flask(__name__)
controller = ScraperController()

EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/start", methods=["POST"])
def api_start():
    data = request.get_json() or {}
    services = data.get("services", [])
    locations = data.get("locations", [])
    max_results = data.get("max_results", 25)
    remove_duplicates = data.get("remove_duplicates", True)
    
    # Allow string input if user sent raw text
    if isinstance(services, str):
        services = [s.strip() for s in services.replace("\r", "").split("\n") if s.strip()]
    if isinstance(locations, str):
        locations = [l.strip() for l in locations.replace("\r", "").split("\n") if l.strip()]

    ok, message = controller.start_job(
        services=services,
        locations=locations,
        max_results=max_results,
        remove_duplicates=remove_duplicates
    )
    return jsonify({"success": ok, "message": message, "snapshot": controller.get_snapshot()})

@app.route("/api/pause", methods=["POST"])
def api_pause():
    ok, message = controller.pause()
    return jsonify({"success": ok, "message": message, "snapshot": controller.get_snapshot()})

@app.route("/api/resume", methods=["POST"])
def api_resume():
    ok, message = controller.resume()
    return jsonify({"success": ok, "message": message, "snapshot": controller.get_snapshot()})

@app.route("/api/stop", methods=["POST"])
def api_stop():
    ok, message = controller.stop()
    return jsonify({"success": ok, "message": message, "snapshot": controller.get_snapshot()})

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify(controller.get_snapshot())

@app.route("/api/events")
def api_events():
    """Server-Sent Events (SSE) stream for live real-time dashboard updates"""
    def event_stream():
        last_hash = ""
        while True:
            snap = controller.get_snapshot()
            # Simple change signature check
            sig = f"{snap['state']}-{snap['businesses_processed']}-{snap['status_message']}-{snap['current_business_name']}-{snap['total_collected']}"
            if sig != last_hash:
                last_hash = sig
                yield f"data: {json.dumps(snap)}\n\n"
            time.sleep(0.5)

    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/export", methods=["GET", "POST"])
def api_export():
    """Generates and downloads the styled Excel spreadsheet"""
    snap = controller.get_snapshot()
    businesses = snap.get("businesses", [])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Google_Maps_Leads_{timestamp}.xlsx"
    filepath = os.path.join(EXPORT_DIR, filename)
    
    export_to_excel(businesses, filepath)
    
    return send_file(
        filepath,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    print("Starting Google Maps Automation Tool on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
