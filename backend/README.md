Backend - WebM + WebSocket Live Transcription

This backend accepts WebM/Opus audio from the frontend via POST (/api/recognize) and via WebSocket (live).

Requirements:
- ffmpeg installed (Dockerfile includes ffmpeg)
- Python 3.10+

Run locally:
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
