from flask import Flask, request, jsonify

app = Flask(__name__)
peers = set()

@app.route("/")
def index():
    return jsonify({"message": "Bootstrap node is running!"})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    peer = data.get("peer")
    if peer:
        peers.add(peer)
        return jsonify({"status": "registered", "peers": list(peers)})
    return jsonify({"error": "No peer provided"}), 400

@app.route("/peers", methods=["GET"])
def get_peers():
    return jsonify({"peers": list(peers)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
