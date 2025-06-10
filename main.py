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
        data = request.get_json(force=True)
        if not data:
            logging.error("No JSON payload received")
            abort(400)

        logging.info(f"Received provision payload: {data}")
        client_name = data["clientName"]
        client_email = data.get("email", "")
        client_phone = data.get("phone", "")
        workspace_id = data.get("workspaceId", "")

        # Step 1: Simulate base clone — add to Clients table
        new_record = clients_table.create({
            "Client Name": client_name,
            "Email": client_email,
            "Phone": client_phone,
            "Provisioning Status": "In Progress"
        })
        client_id = new_record["id"]

        # Step 2: Write to Config table
        config_table.create({
            "Client ID": client_id,
            "Client Name": client_name,
            "Workspace ID": workspace_id,
            "Email": client_email,
            "Phone": client_phone
        })

        # Step 3: (Skip Zapier for now)

        # Step 4: Update provisioning status
        clients_table.update(client_id, {"Provisioning Status": "Complete"})

        return jsonify({"status": "provisioned", "clientId": client_id}), 200

    except Exception as e:
        logging.exception("Provisioning failed")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
