# CECS327-Project3
P2P Network Project for CECS 327 – Intro to Networks and Distributed Computing  

### Phase 1: File Upload & Download
Mount volume in Docker:
docker run -d -p 5001:5000 -v "%cd%/storage:/app/storage" --name node1 p2p-node
# Use $(pwd) instead of %cd% if on WSL or Git Bash

Make a text file to test:
echo hello world > mydoc.txt

Test file upload:
curl.exe -F "file=@mydoc.txt" http://localhost:5001/upload

Expected response:
{"status": "uploaded", "filename": "mydoc.txt"}

Verify upload:
curl.exe http://localhost:5001/download/mydoc.txt
# Or open in browser: http://localhost:5001/download/mydoc.txt


### Phase 2: Key-Value Store
Stop previous container by force
docker kill $(docker ps -q)

Prune system and clean up 
docker system prune

Start containers:
docker-compose up --build

Test storing a key-value pair:
curl.exe -X POST http://localhost:5001/kv -H "Content-Type: application/json" -d '{\"key\": \"color\", \"value\": \"blue\"}'

Expected response: {"key":"color","status":"stored","value":"blue"}

curl http://localhost:5001/kv/color
# Or open in browser: curl http://localhost:5001/kv/color

Expected response: {"key":"color","value":"blue"}

### Phase 3: Adding DHT-Based Routing for Storage

Store a key on one node:
docker exec -it node3 curl -X POST http://node3:5000/kv -H "Content-Type: application/json" --data '{\"key\":\"fruit\",\"value\":\"apple\"}'

Expected response: {"key":"fruit","status":"stored","value":"apple"}

Retrieve the key from the same node:
docker exec -it node3 curl http://node3:5000/kv/fruit

Expected response: {"key":"fruit","value":"apple"}

Retrieve the key from a different node (auto-forwarded):
docker exec -it node6 curl http://node6:5000/kv/fruit

Expected response: {"key":"fruit","value":"apple"}

Query a key that doesn't exist:
docker exec -it node4 curl http://node4:5000/kv/nonexistentkey

Expected response: {"error":"Key not found"}

### Phase 4: Peer Health Monitoring & Fault Tolerance

Check if a node is alive:
curl.exe http://localhost:5001/ping

Expected response: {"status":"alive"}

Check from another node: 
docker exec -it node2 curl http://node5:5000/ping

Expected response: {"status":"alive"}

Simulate failure by stopping a node:
docker stop node5

Ping from another node: 
docker exec -it node3 curl http://node5:5000/pin

Expected response: curl: (6) Could not resolve host: node5