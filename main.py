from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Flask
app = Flask(__name__)

# Fetch values from environment variables
type_ = os.getenv("type")
project_id = os.getenv("project_id")
private_key_id = os.getenv("private_key_id")
private_key = os.getenv("private_key")
client_email = os.getenv("client_email")
client_id = os.getenv("client_id")
auth_uri = os.getenv("auth_uri")
token_uri = os.getenv("token_uri")
auth_provider_x509_cert_url = os.getenv("auth_provider_x509_cert_url")
client_x509_cert_url = os.getenv("client_x509_cert_url")
universe_domain = os.getenv("universe_domain")

# Save them back into dictionary (same format as service account JSON)
firebase_vars = {
    "type": type_,
    "project_id": project_id,
    "private_key_id": private_key_id,
    "private_key": private_key,
    "client_email": client_email,
    "client_id": client_id,
    "auth_uri": auth_uri,
    "token_uri": token_uri,
    "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    "client_x509_cert_url": client_x509_cert_url,
    "universe_domain": universe_domain,
}

# Initialize Firebase
cred = credentials.Certificate(firebase_vars)
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
    app.run(host="0.0.0.0", port=5000, debug=True)
