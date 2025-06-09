import os
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
PROVISION_TOKEN = os.environ.get("PROVISION_TOKEN")

@app.before_request
def require_token():
    # only enforce on /api/provision
    if request.path == "/api/provision":
        auth = request.headers.get("Authorization", "")
        # expecting header: Authorization: Bearer <token>
        if not auth.startswith("Bearer ") or auth.split(" ",1)[1] != PROVISION_TOKEN:
            abort(401, description="Unauthorized")


@app.route('/api/provision', methods=['POST'])
def provision():
    data = request.get_json()
    client = data.get('clientName', 'unknown')
    # Echo back for now
    return jsonify({'status': 'ok', 'client': client}), 200

@app.route('/', methods=['GET'])
def home():
    return "✅ Provisioning API is live. POST to /api/provision to create a client.", 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
