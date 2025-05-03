# CECS327-Project3
P2P Network Project for CECS 327 – Intro to Networks and Distributed Computing  

### Phase 1: File Upload & Download

Run:
docker-compose up --build

Mount volume in Docker (optional standalone test):
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