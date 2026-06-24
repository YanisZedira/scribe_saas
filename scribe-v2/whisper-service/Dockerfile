# Image GPU (CUDA) pour Faster-Whisper large-v3.
# cuDNN 9 + CUDA 12 : compatible CTranslate2 récent (faster-whisper 1.1).
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .

# Variables conseillées au run :
#   -e WHISPER_MODEL=large-v3 -e WHISPER_DEVICE=cuda -e WHISPER_COMPUTE_TYPE=float16
#   -e STT_API_KEY=<un_secret_de_ton_choix>
ENV WHISPER_MODEL=large-v3 WHISPER_DEVICE=cuda WHISPER_COMPUTE_TYPE=float16

EXPOSE 9000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9000"]
