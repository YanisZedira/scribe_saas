# Scribe STT — micro-service Faster-Whisper large-v3 (souverain)

Conteneur autonome qui transcrit l'audio avec **Whisper large-v3** sur GPU.
À déployer **chez toi** (GPU) ou sur un **hébergeur européen** (Scaleway, OVHcloud)
pour garder les données en UE. L'app Scribe pointe `STT_ENDPOINT_URL` dessus.

API (compatible OpenAI) :
- `POST /v1/audio/transcriptions` (multipart `file`) → `{ "text": "..." }`
- `GET /health`

---

## Déploiement sur un GPU européen (Scaleway — exemple)

> Coût indicatif : un GPU L4 ~ **1 €/h**. **Pense à supprimer l'instance après la démo.**

1. Crée un compte sur **https://console.scaleway.com** (société française, données UE).
2. **Compute → GPU → Create instance** : choisis un type **L4** (ou H100 si dispo),
   région **Paris (fr-par)**, image **Ubuntu + Docker** (ou Ubuntu standard).
3. Connecte-toi en SSH (la console donne la commande), puis :

```bash
# (si Docker absent)
curl -fsSL https://get.docker.com | sh
# (support GPU dans Docker)
sudo apt-get install -y nvidia-container-toolkit && sudo systemctl restart docker

# Récupère ce dossier (git clone de ton repo) puis :
cd scribe-v2/whisper-service
sudo docker build -t scribe-stt .
sudo docker run -d --gpus all -p 9000:9000 \
  -e STT_API_KEY=choisis-un-secret-ici \
  --name scribe-stt scribe-stt
```

4. Ouvre le **port 9000** (Security Group Scaleway) et note l'**IP publique**.
5. Teste : `http://<IP_PUBLIQUE>:9000/health` → `{"status":"ok",...}`.
6. Sur ton poste, dans `scribe-v2/backend/.env` :

```
STT_ENDPOINT_URL=http://<IP_PUBLIQUE>:9000
STT_ENDPOINT_KEY=choisis-un-secret-ici
```

7. Relance le back-end → la transcription passe par le GPU EU, en large-v3. 🎯

> **OVHcloud** : démarche identique (Public Cloud → instance GPU, région UE,
> mêmes commandes Docker).

---

## Alternative : tourne chez toi si tu as un GPU NVIDIA

```bash
docker build -t scribe-stt .
docker run -d --gpus all -p 9000:9000 -e STT_API_KEY=secret scribe-stt
# .env : STT_ENDPOINT_URL=http://localhost:9000
```

## Production Suez

Le **même conteneur** se déploie sur les serveurs GPU on-premise de Suez :
zéro donnée ne sort, `STT_ENDPOINT_URL` pointe vers l'IP interne. C'est l'argument
de souveraineté de bout en bout.

## Sécurité (exposition Internet)

- Toujours définir `STT_API_KEY` (sinon l'endpoint est ouvert).
- Idéalement, mettre un reverse-proxy HTTPS (Caddy/Traefik) devant, ou restreindre
  l'IP source dans le Security Group. Pour la prod : VPN / réseau privé.
