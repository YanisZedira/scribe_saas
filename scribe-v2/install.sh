#!/usr/bin/env bash
# ===========================================================================
# Scribe — installation TOUT-EN-UN (Linux / Ubuntu avec GPU NVIDIA)
# Installe Docker + NVIDIA Container Toolkit, construit la stack, télécharge le
# modèle IA et lance la SaaS. À lancer depuis scribe-v2/ :  sudo bash install.sh
# ===========================================================================
set -euo pipefail
cd "$(dirname "$0")"
echo "================  Installation de Scribe  ================"

# 1) Docker -----------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installation de Docker..."
  curl -fsSL https://get.docker.com | sh
fi

# 2) NVIDIA Container Toolkit (si GPU présent) ------------------------------
if command -v nvidia-smi >/dev/null 2>&1; then
  if ! docker info 2>/dev/null | grep -qi 'Runtimes:.*nvidia'; then
    echo "==> Installation du NVIDIA Container Toolkit..."
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
      | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
      | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
      > /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update && apt-get install -y nvidia-container-toolkit
    nvidia-ctk runtime configure --runtime=docker
    systemctl restart docker
  fi
else
  echo "⚠️  Aucun GPU NVIDIA détecté. La stack tournera (lentement) en CPU."
fi

# 3) Configuration ----------------------------------------------------------
[ -f .env ] || cp .env.example .env

# 4) Build + démarrage ------------------------------------------------------
echo "==> Construction et démarrage des conteneurs (peut prendre plusieurs minutes)..."
docker compose up -d --build

# 5) Attente d'Ollama puis téléchargement du modèle Qwen --------------------
echo "==> Attente du service Ollama..."
for _ in $(seq 1 30); do
  if docker compose exec -T ollama ollama list >/dev/null 2>&1; then break; fi
  sleep 3
done
echo "==> Téléchargement du modèle Qwen 2.5 (~5 Go, une seule fois)..."
docker compose exec -T ollama ollama pull qwen2.5:7b-instruct

cat <<'EOF'

==========================================================
  ✅  Scribe est lancé !
     • Application : http://localhost:3000
     • API / docs  : http://localhost:8000/docs
     • Santé       : http://localhost:8000/api/health

  Commandes utiles :
     docker compose logs -f      # voir les logs
     docker compose down         # arrêter
==========================================================
EOF
