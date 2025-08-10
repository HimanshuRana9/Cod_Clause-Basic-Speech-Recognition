Speech Recognition - WebM + Live WebSocket Transcription

How to run with Docker (recommended):
1. Ensure Docker is installed.
2. From repo root:
   docker-compose up --build
3. Visit frontend at http://localhost:3000 and backend via SocketIO at ws://localhost:5000

Notes:
- Dockerfile for backend installs ffmpeg so conversion works inside container.
- The frontend sends small WebM/Opus chunks via Socket.IO for live partial transcripts.
- This is a demo; for production, secure Socket.IO, scale workers, and use a robust STT service.
