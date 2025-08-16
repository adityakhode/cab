from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import json, os

# Initialize Flask
app = Flask(__name__)

# Load Firebase credentials from environment variable
firebase_key = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(firebase_key)

# Initialize Firebase app (only once)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# =========================
# 🔹 API Endpoints
# =========================

@app.route("/add_stop", methods=["POST"])
def add_stop():
    data = request.json
    company_name = data.get("company_name")

    stop_data = {
        "driver": data.get("driver", ""),
        "Time": data.get("time_str", "00:00 AM"),
        "Count": data.get("count", 0),
        "seq": data.get("seq", 0),
        "status": data.get("status", True),
        "Company Name": company_name
    }

    try:
        db.collection("stop").document(company_name).set(stop_data)
        return jsonify({"success": True, "message": "Stop added"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/update_stop", methods=["PUT"])
def update_stop():
    data = request.json
    company_name = data.get("company_name")

    try:
        db.collection("stop").document(company_name).update(data)
        return jsonify({"success": True, "message": "Stop updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/delete_stop/<company_name>", methods=["DELETE"])
def delete_stop(company_name):
    try:
        db.collection("stop").document(company_name).delete()
        return jsonify({"success": True, "message": "Stop deleted"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/get_stops", methods=["GET"])
def get_stops():
    try:
        stops_ref = db.collection("stop").order_by("seq")
        docs = stops_ref.stream()
        stops = []
        for doc in docs:
            stop = doc.to_dict()
            stop["id"] = doc.id
            stops.append(stop)
        return jsonify(stops), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/update_sequence", methods=["PUT"])
def update_sequence():
    """Update sequence after drag & drop reordering"""
    data = request.json  # [{ "company_name": "X", "seq": 1 }, ...]
    try:
        for stop in data:
            company_name = stop["company_name"]
            db.collection("stop").document(company_name).update({"seq": stop["seq"]})
        return jsonify({"success": True, "message": "Sequence updated"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
