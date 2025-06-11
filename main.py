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
        data = request.get_json(force=True, silent=True)
        if not data:
            logging.error("Invalid or missing JSON payload: %s", request.data.decode())
            return jsonify({"status": "error", "message": "Missing or invalid JSON body"}), 400

        # Required fields (all .get() for safety)
        client_name         = data.get("clientName")
        contact_name        = data.get("primaryContactName")
        contact_email       = data.get("primaryContactEmail")
        contact_phone       = data.get("primaryContactPhone")
        subdomain           = data.get("portalSubdomain")
        logo_url            = data.get("logoUrl")
        primary_color       = data.get("primaryColorHex")
        secondary_color     = data.get("secondaryColorHex")
        primetracers_key    = data.get("primeTracersApiKey")
        calendly_key        = data.get("calendlyApiKey")
        twilio_sid          = data.get("twilioAccountSid")
        twilio_key          = data.get("twilioApiKey")
        sendgrid_key        = data.get("sendgridApiKey")

        if not client_name:
            return jsonify({"status": "error", "message": "Missing required field: clientName"}), 400

        # Create Airtable record
        new_record = clients_table.create({
            "Client Name": client_name,
            "Primary Contact Name": contact_name,
            "Primary Contact Email": contact_email,
            "Primary Contact Phone": contact_phone,
            "Portal Subdomain": subdomain,
            "Logo URL": logo_url,
            "Primary Color": primary_color,
            "Secondary Color": secondary_color,
            "PrimeTracers API Key": primetracers_key,
            "Calendly API Key": calendly_key,
            "Twilio Account SID": twilio_sid,
            "Twilio API Key": twilio_key,
            "Sendgrid API Key": sendgrid_key,
            "Provisioning Status": "In Progress"
        })

        client_id = new_record["id"]

        # Final update to mark provision complete
        clients_table.update(client_id, {"Provisioning Status": "Complete"})

        return jsonify({"status": "provisioned", "clientId": client_id}), 200

    except Exception as e:
        logging.exception("Provisioning failed")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
