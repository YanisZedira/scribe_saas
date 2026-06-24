"""Client Qwen 2.5 — endpoint OpenAI-compatible (vLLM / Ollama / API UE).

Qwen 2.5 expose une API compatible OpenAI. On peut donc le pointer vers :
- un serveur local vLLM : http://localhost:8001/v1
- Ollama : http://localhost:11434/v1  (modèle "qwen2.5")
- une API européenne stricte (Scaleway, OVHcloud AI Endpoints, etc.)

Le client force ``response_format={"type":"json_object"}`` quand l'endpoint le
supporte, et reste tolérant sinon (le parsing robuste est fait en aval).
"""

from __future__ import annotations

import httpx

from app.config import settings


class QwenError(RuntimeError):
    pass


def chat_json(system_prompt: str, user_prompt: str, *,
              temperature: float = 0.1, max_tokens: int = 2048) -> str:
    """Appelle Qwen et retourne le contenu texte brut (censé être du JSON)."""
    if not settings.qwen_base_url:
        raise QwenError("QWEN_BASE_URL non configuré.")

    payload = {
        "model": settings.qwen_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    headers = {"Content-Type": "application/json"}
    if settings.qwen_api_key:
        headers["Authorization"] = f"Bearer {settings.qwen_api_key}"

    try:
        resp = httpx.post(f"{settings.qwen_base_url}/chat/completions",
                          json=payload, headers=headers, timeout=120)
    except httpx.HTTPError as exc:
        raise QwenError(f"Qwen injoignable : {exc}") from exc

    if resp.status_code >= 400:
        # Certains serveurs refusent response_format → on retente sans.
        payload.pop("response_format", None)
        resp = httpx.post(f"{settings.qwen_base_url}/chat/completions",
                          json=payload, headers=headers, timeout=120)
    if resp.status_code >= 400:
        raise QwenError(f"Qwen erreur {resp.status_code}: {resp.text[:300]}")

    return resp.json()["choices"][0]["message"]["content"]
