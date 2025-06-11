import os
from flask import Flask, request, jsonify, abort
from pyairtable import Table
import logging

app = Flask(__name__)

# Env vars
PROVISION_TOKEN = os.environ["PROVISION_TOKEN"]
AT_API_KEY = os.environ["AIRTABLE_API_KEY"]
MASTER_BASE = os.environ["AIRTABLE_BASE_ID"]

# Airtable tables
clients_table = Table(AT_API_KEY, MASTER_BASE, "Clients")
config_table = Table(AT_API_KEY, MASTER_BASE, "Config")  # Add this table in your base

@app.before_request
def require_token():
    if request.path == "/api/provision":
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        if token != PROVISION_TOKEN:
            abort(401)

@app.route("/api/provision", methods=["POST"])
def provision():
    try:
        # Try JSON payload first
        data = request.get_json(force=True, silent=True)

        # If not JSON, fallback to form data
        if not data:
            data = request.form.to_dict()
            logging.info("Using form-based data fallback: %s", data)

        if not data:
            logging.error("Missing or invalid payload")
            return jsonify({"status": "error", "message": "Missing payload"}), 400

        # Continue with existing logic
        client_name = data.get("clientName")
        if not client_name:
            return jsonify({"status": "error", "message": "Missing required field: clientName"}), 400

        # Create the new Airtable record
        new_record = clients_table.create({
            "Client Name": client_name,
            "Primary Contact Name": data.get("primaryContactName"),
            "Primary Contact Email": data.get("primaryContactEmail"),
            "Primary Contact Phone": data.get("primaryContactPhone"),
            "Portal Subdomain": data.get("portalSubdomain"),
            "Logo URL": data.get("logoUrl"),
            "Primary Color": data.get("primaryColor"),
            "Secondary Color": data.get("secondaryColor"),
            "PrimeTracers API Key": data.get("primeTracersApiKey"),
            "Calendly API Key": data.get("calendlyApiKey"),
            "Twilio Account SID": data.get("twilioAccountSid"),
            "Twilio API Key": data.get("twilioApiKey"),
            "Sendgrid API Key": data.get("sendgridApiKey"),
            "Provisioning Status": "In Progress"
        })

        client_id = new_record["id"]

        # Final update
        clients_table.update(client_id, {"Provisioning Status": "Complete"})

        return jsonify({"status": "provisioned", "clientId": client_id}), 200

    except Exception as e:
        logging.exception("Provisioning failed")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
