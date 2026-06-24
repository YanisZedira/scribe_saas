# Backend FastAPI + LiveKit Agent (CPU — la transcription lourde est déléguée
# au service whisper-service sur GPU). Pas d'apt (faster-whisper utilise PyAV,
# ffmpeg embarqué) → évite les blocages réseau (proxy/403 sur dépôts Ubuntu).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
