from flask import Flask, request, jsonify

app = Flask(__name__)

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
