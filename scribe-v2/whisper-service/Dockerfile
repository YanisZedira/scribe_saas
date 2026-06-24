# Image GPU pour Faster-Whisper large-v3.
# Base PyTorch officielle : Python + CUDA 12 + cuDNN 9 déjà inclus
# → AUCUN apt nécessaire (évite les blocages réseau type proxy/403 sur les
#   dépôts Ubuntu). faster-whisper décode l'audio via PyAV (ffmpeg embarqué).
FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-runtime

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV WHISPER_MODEL=large-v3 WHISPER_DEVICE=cuda WHISPER_COMPUTE_TYPE=float16
EXPOSE 9000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
