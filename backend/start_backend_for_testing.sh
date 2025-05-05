#!/bin/bash
echo "Starting backend server for testing..."
cd /home/ubuntu/repos/Cortana/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
