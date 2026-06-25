#!/usr/bin/env python3
"""Banc de test Scribe — Vexa + Voxtral + Mistral.

Usage :
  python run.py check                  # vérifie les clés + ping chaque service
  python run.py voxtral [audio.mp3]    # transcription (fichier, ou échantillon démo)
  python run.py mistral [transcript.txt]  # analyse d'une transcription
  python run.py pipeline <audio.mp3>   # Voxtral -> Mistral (transcription + analyse)
  python run.py vexa <lien_teams>      # bot rejoint la réunion -> transcript -> Mistral

Configuration : copie .env.example en .env et renseigne MISTRAL_API_KEY / VEXA_API_KEY.
"""

from __future__ import annotations

import json
import os
import sys

from dotenv import load_dotenv

import mistral
import voxtral
from vexa import Vexa, parse_url

load_dotenv()
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
VEXA_KEY = os.getenv("VEXA_API_KEY")
VEXA_URL = os.getenv("VEXA_API_URL", "https://api.cloud.vexa.ai")
VOXTRAL_MODEL = os.getenv("VOXTRAL_MODEL", "voxtral-mini-latest")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

SAMPLE_AUDIO_URL = "https://docs.mistral.ai/audio/obama.mp3"
SAMPLE_TRANSCRIPT = (
    "Camille: Bonjour à tous, on démarre le point produit hebdomadaire.\n"
    "Aymen: Premier sujet, le retard sur l'intégration du module de paiement.\n"
    "Camille: Oui, deux jours de retard à cause d'un bug d'intégration.\n"
    "Aymen: Je prends le correctif, je vise une livraison pour vendredi.\n"
    "Camille: Décision : on repousse la mise en production à lundi prochain.\n"
    "Aymen: Il faut prévenir le client du décalage.\n"
    "Camille: Action : j'envoie un e-mail au client avant ce soir."
)

# Couleurs terminal
G, R, Y, B, X = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"
def ok(m): print(f"{G}✅ {m}{X}")
def ko(m): print(f"{R}❌ {m}{X}")
def info(m): print(f"{B}→ {m}{X}")
def title(m): print(f"\n{Y}=== {m} ==={X}")
def show(obj): print(json.dumps(obj, ensure_ascii=False, indent=2))


def need(key, name):
    if not key:
        ko(f"{name} manquant dans .env"); sys.exit(1)


# --------------------------------------------------------------------------- #
def cmd_check():
    title("Vérification des clés et services")
    print(f"MISTRAL_API_KEY : {'présent' if MISTRAL_KEY else 'ABSENT'}")
    print(f"VEXA_API_KEY    : {'présent' if VEXA_KEY else 'ABSENT'}")

    if MISTRAL_KEY:
        try:
            r = voxtral.transcribe(api_key=MISTRAL_KEY, model=VOXTRAL_MODEL,
                                   file_url=SAMPLE_AUDIO_URL, language=None)
            ok(f"Voxtral OK — {len(r.get('text',''))} caractères transcrits")
        except Exception as e:  # noqa: BLE001
            ko(f"Voxtral : {e}")
        try:
            a = mistral.analyze(api_key=MISTRAL_KEY, transcript=SAMPLE_TRANSCRIPT,
                                model=MISTRAL_MODEL)
            ok(f"Mistral OK — titre: « {a.get('titre')} »")
        except Exception as e:  # noqa: BLE001
            ko(f"Mistral : {e}")

    if VEXA_KEY:
        import httpx
        try:
            r = httpx.get(f"{VEXA_URL.rstrip('/')}/bots/status",
                          headers={"X-API-Key": VEXA_KEY}, timeout=20)
            ok(f"Vexa OK — statut {r.status_code}") if r.status_code < 400 else ko(f"Vexa {r.status_code}: {r.text[:120]}")
        except Exception as e:  # noqa: BLE001
            ko(f"Vexa : {e}")


def cmd_voxtral(args):
    need(MISTRAL_KEY, "MISTRAL_API_KEY")
    title("Transcription Voxtral")
    if args:
        info(f"Fichier : {args[0]}")
        r = voxtral.transcribe(api_key=MISTRAL_KEY, model=VOXTRAL_MODEL,
                               file_path=args[0], language="fr")
    else:
        info("Aucun fichier fourni → échantillon de démo (anglais).")
        r = voxtral.transcribe(api_key=MISTRAL_KEY, model=VOXTRAL_MODEL,
                               file_url=SAMPLE_AUDIO_URL, language=None)
    ok(f"Langue détectée : {r.get('language')}")
    print(f"\n{B}Texte :{X}\n{r.get('text','')[:1500]}")
    segs = r.get("segments") or []
    if segs:
        print(f"\n{B}{len(segs)} segments (3 premiers) :{X}")
        show(segs[:3])
    return r.get("text", "")


def cmd_mistral(args):
    need(MISTRAL_KEY, "MISTRAL_API_KEY")
    title("Analyse Mistral")
    transcript = open(args[0], encoding="utf-8").read() if args else SAMPLE_TRANSCRIPT
    if not args:
        info("Aucun fichier fourni → transcription d'exemple.")
    a = mistral.analyze(api_key=MISTRAL_KEY, transcript=transcript, model=MISTRAL_MODEL)
    ok("Analyse produite :")
    show(a)
    return a


def cmd_pipeline(args):
    need(MISTRAL_KEY, "MISTRAL_API_KEY")
    if not args:
        ko("Usage : python run.py pipeline <audio.mp3>"); sys.exit(1)
    title("Pipeline : Voxtral → Mistral")
    info("1/2 Transcription (Voxtral)…")
    text = voxtral.transcribe(api_key=MISTRAL_KEY, model=VOXTRAL_MODEL,
                              file_path=args[0], language="fr").get("text", "")
    ok(f"Transcrit ({len(text)} caractères)")
    print(text[:800] + ("…" if len(text) > 800 else ""))
    info("2/2 Analyse (Mistral)…")
    show(mistral.analyze(api_key=MISTRAL_KEY, transcript=text, model=MISTRAL_MODEL))


def cmd_vexa(args):
    need(VEXA_KEY, "VEXA_API_KEY")
    if not args:
        ko("Usage : python run.py vexa <lien_reunion_teams>"); sys.exit(1)
    url = args[0]
    title("Vexa : envoi du bot")
    platform, native_id, _ = parse_url(url)
    info(f"Plateforme={platform}  id={native_id}")
    v = Vexa(VEXA_KEY, VEXA_URL)
    v.send_bot(url)
    ok("Bot envoyé. Il rejoint la réunion (admets-le si une salle d'attente apparaît).")
    info("Attente de la fin de la réunion… (Ctrl+C pour arrêter)")
    data = v.wait_transcript(platform, native_id,
                             on_tick=lambda st, n: print(f"   statut={st}  segments={n}"))
    v.stop_bot(platform, native_id)
    text = v.transcript_text(data)
    print(f"\n{B}Transcription :{X}\n{text[:1500]}")
    if MISTRAL_KEY and text.strip():
        title("Analyse Mistral de la réunion")
        show(mistral.analyze(api_key=MISTRAL_KEY, transcript=text, model=MISTRAL_MODEL))


COMMANDS = {"check": lambda a: cmd_check(), "voxtral": cmd_voxtral,
            "mistral": cmd_mistral, "pipeline": cmd_pipeline, "vexa": cmd_vexa}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__); sys.exit(0)
    try:
        COMMANDS[sys.argv[1]](sys.argv[2:])
    except KeyboardInterrupt:
        print("\nInterrompu.")
    except Exception as e:  # noqa: BLE001
        ko(str(e)); sys.exit(1)
