from flask import Flask, request, jsonify, send_from_directory
import uuid
import threading
import time
import requests
import os
import hashlib

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

    if not key or not value:
        return jsonify({"error": "Missing key or value"}), 400

    all_peers = list(peers) + [my_address]
    responsible_node = hash_key_to_node(key, all_peers)
    print(f"[{my_address}] Responsible for key '{key}' → {responsible_node}", flush=True)

    if responsible_node != my_address:
        # Forward to the correct node
        try:
            res = requests.post(f"{responsible_node}/kv", json=data)
            return res.json(), res.status_code
        except Exception as e:
            return jsonify({"error": f"Failed to forward: {str(e)}"}), 500

    # Store locally
    kv_store[key] = value
    return jsonify({"status": "stored", "key": key, "value": value})

@app.route("/kv/<key>", methods=["GET"])
def get_kv(key):
    all_peers = list(peers) + [my_address]
    responsible_node = hash_key_to_node(key, all_peers)
    print(f"[{my_address}] Responsible for key '{key}' → {responsible_node}", flush=True)

    if responsible_node != my_address:
        try:
            res = requests.get(f"{responsible_node}/kv/{key}")
            return res.json(), res.status_code
        except Exception as e:
            return jsonify({"error": f"Failed to forward: {str(e)}"}), 500

    value = kv_store.get(key)
    if value is not None:
        return jsonify({"key": key, "value": value})
    return jsonify({"error": "Key not found"}), 404

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "alive"})

def register_with_bootstrap():
    try:
        res = requests.post(f"{bootstrap_url}/register", json={"peer": my_address})
        if res.status_code == 200:
            peer_list = res.json().get("peers", [])
            peer_list.append(bootstrap_url)  # ensure bootstrap is in list
            peer_list.append(my_address)     # ensure self is in list
            peers.update(peer_list)
            peers.discard(my_address)
            print(f"Registered with bootstrap. Peers: {peers}")
    except Exception as e:
        print(f"Failed to register with bootstrap: {e}")

def update_peers():
    while True:
        try:
            # Get peers from bootstrap first
            res = requests.get(f"{bootstrap_url}/peers")
            if res.status_code == 200:
                new_bootstrap_peers = res.json().get("peers", [])
                peers.update(new_bootstrap_peers)
        except Exception as e:
            print(f"Failed to update from bootstrap: {e}")

        # Ping and collect valid peers
        alive_peers = set()
        
        for peer in list(peers):
            try:
                # First, try to get their peer list
                res = requests.get(f"{peer}/peers", timeout=3)
                if res.status_code == 200:
                    new_peers = res.json().get("peers", [])
                    peers.update(new_peers)
                
                # Then, ping to check liveness
                ping_res = requests.get(f"{peer}/ping", timeout=3)
                if ping_res.status_code == 200:
                    alive_peers.add(peer)
            except Exception as e:
                print(f"Peer unreachable: {peer} - {e}")

        # Refresh peers with only alive ones
        peers.clear()
        peers.update(alive_peers)
        peers.discard(my_address)

        print(f"[{my_address}] Known alive peers: {peers}", flush=True)
        time.sleep(10)

def hash_key_to_node(key, peers_list):
    hashed = hashlib.sha1(key.encode()).hexdigest()
    index = int(hashed, 16) % len(peers_list)
    return sorted(peers_list)[index]

if __name__ == "__main__":

    threading.Thread(target=register_with_bootstrap).start()
    threading.Thread(target=update_peers, daemon=True).start()

    app.run(host="0.0.0.0", port=5000)
