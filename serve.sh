#!/bin/bash
# Serve SemAtlas Learn. Idempotent: if the server is already up, just opens it.
cd "$(dirname "$0")"
if ! curl -s -o /dev/null --max-time 1 http://localhost:8899/; then
    nohup python3 -m http.server 8899 >/dev/null 2>&1 &
    sleep 1
fi
echo "SemAtlas Learn at:  http://localhost:8899"
open "http://localhost:8899/"
