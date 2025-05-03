from flask import Flask, request, jsonify, send_from_directory
import uuid
import threading
import time
import requests
import os

app = Flask(__name__)
node_id = str(uuid.uuid4())
peers = set()

bootstrap_url = os.environ.get("BOOTSTRAP_URL", "http://localhost:5000")
my_address = os.environ.get("MY_ADDRESS", "http://localhost:5000")

os.makedirs("storage", exist_ok=True)

kv_store = {}

@app.route("/")
def index():
    return jsonify({"message": f"Node {node_id} is running!"})

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

@app.route("/message", methods=["POST"])
def message():
    data = request.get_json()
    sender = data.get("sender")
    msg = data.get("msg")
    print(f"Received message from {sender}: {msg}", flush=True)
    return jsonify({"status": "received"})

# Project 3:
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filepath = f"./storage/{file.filename}"
    file.save(filepath)
    return jsonify({"status": "uploaded", "filename": file.filename})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('./storage', filename)

@app.route("/kv", methods=["POST"])
def insert_kv():
    data = request.get_json()
    key = data.get("key")
    value = data.get("value")
    if key and value:
        kv_store[key] = value
        return jsonify({"status": "stored", "key": key, "value": value})
    return jsonify({"error": "Missing key or value"}), 400

@app.route("/kv/<key>", methods=["GET"])
def get_kv(key):
    value = kv_store.get(key)
    if value is not None:
        return jsonify({"key": key, "value": value})
    return jsonify({"error": "Key not found"}), 404


def register_with_bootstrap():
    try:
        res = requests.post(f"{bootstrap_url}/register", json={"peer": my_address})
        if res.status_code == 200:
            peer_list = res.json().get("peers", [])
            peers.update(peer_list)
            peers.discard(my_address)
            print(f"Registered with bootstrap. Peers: {peers}")
    except Exception as e:
        print(f"Failed to register with bootstrap: {e}")

def update_peers():
    while True:
        for peer in list(peers):
            try:
                res = requests.get(f"{peer}/peers")
                if res.status_code == 200:
                    new_peers = res.json().get("peers", [])
                    peers.update(new_peers)
                    peers.discard(my_address)
            except:
                continue
        time.sleep(10)

if __name__ == "__main__":

    threading.Thread(target=register_with_bootstrap).start()
    threading.Thread(target=update_peers, daemon=True).start()

    app.run(host="0.0.0.0", port=5000)
