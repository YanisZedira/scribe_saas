"""Maquette interactive Scribe — livrable de pré-production.

Objectif (cf. dossier §6.3) : FIGER LE PARCOURS et sécuriser les choix UX. La
maquette ne fait PAS tourner la chaîne réelle ; les traitements sont mockés.

Couvre :
- les deux parcours : mode visio (wireframe + flow) et mode dictaphone
  (capture réelle via st.audio_input + transcription mockée) ;
- écran de consentement RGPD ;
- compte-rendu en placeholder ;
- sélecteur de ton/thème simulé + icône ;
- gestion d'erreurs et indicateurs de chargement.

Lancement :  streamlit run app.py
"""

from __future__ import annotations

import time
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Scribe — Maquette", page_icon="🎙️", layout="wide")

# --------------------------------------------------------------------------- #
# Données mockées (transcription d'exemple, identique au pipeline réel)
# --------------------------------------------------------------------------- #
MOCK_TRANSCRIPT = [
    ("Alice", "00:00", "Bonjour à tous, merci d'être présents pour ce point hebdomadaire."),
    ("Bob", "00:05", "De rien. On commence par le retard sur la livraison ?"),
    ("Alice", "00:11", "Oui. Le module de paiement a pris deux jours de retard à cause d'un bug d'intégration."),
    ("Bob", "00:19", "Je peux prendre le correctif. Je vise une livraison pour vendredi."),
    ("Alice", "00:27", "Parfait. Décision : on repousse la mise en production à lundi prochain."),
    ("Bob", "00:34", "D'accord. Il faut aussi prévenir le client de ce décalage."),
    ("Alice", "00:40", "Je m'en occupe. Action : envoyer un e-mail au client avant ce soir."),
]

MOCK_ACTIONS = pd.DataFrame([
    {"Responsable": "Bob", "Action": "Livrer le correctif du module paiement",
     "Échéance": (date.today() + timedelta(days=3)).isoformat(), "Statut": "À faire"},
    {"Responsable": "Alice", "Action": "Envoyer un e-mail d'information au client",
     "Échéance": date.today().isoformat(), "Statut": "À faire"},
])

TONES = {"positif": "😊", "neutre": "😐", "négatif": "😟", "urgent": "🔥"}
THEMES = ["Livraison / planning", "Technique / bug", "Relation client", "Budget / coûts"]


# --------------------------------------------------------------------------- #
# Composants réutilisables
# --------------------------------------------------------------------------- #
def consent_gate(mode_key: str) -> bool:
    """Écran de consentement RGPD (matérialise l'analyse RGPD du dossier)."""
    st.markdown("#### 🔒 Consentement des participants (RGPD)")
    st.info(
        "Un enregistrement de réunion contient des **voix** (donnée biométrique) et "
        "des propos identifiables. Le traitement est **bloqué** tant que le "
        "consentement n'est pas recueilli."
    )
    c1, c2 = st.columns(2)
    p1 = c1.checkbox("Participant 1 (Alice) consent à l'enregistrement", key=f"c1_{mode_key}")
    p2 = c2.checkbox("Participant 2 (Bob) consent à l'enregistrement", key=f"c2_{mode_key}")
    st.caption("Conservation : 90 jours (configurable) · Droit à l'effacement disponible à tout moment.")
    return p1 and p2


def show_results():
    """Affiche le compte-rendu placeholder, le ton/thèmes et les actions."""
    st.success("✅ Traitement terminé (simulé).")

    # Sélecteur de ton / thème simulé
    col_t, col_th = st.columns(2)
    tone = col_t.selectbox("Ton détecté (simulé)", list(TONES), index=0)
    col_t.markdown(f"### {TONES[tone]} {tone.capitalize()}")
    selected = col_th.multiselect("Thèmes détectés (simulés)", THEMES,
                                  default=THEMES[:3])

    st.divider()
    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### 📝 Compte-rendu (placeholder)")
        st.markdown(
            "> **Résumé.** Point hebdomadaire. Le module de paiement a pris du retard "
            "(bug d'intégration). Décision de repousser la mise en production à lundi. "
            "Deux actions assignées.\n\n"
            "**Décisions**\n- Mise en production repoussée à lundi prochain.\n\n"
            "**Actions** — voir tableau ci-contre."
        )
        st.markdown("#### 📜 Transcription (mockée)")
        for speaker, ts, text in MOCK_TRANSCRIPT:
            st.markdown(f"**:blue[{speaker}]** · `{ts}`  \n{text}")

    with right:
        st.markdown("#### ✅ Actions extraites")
        st.dataframe(MOCK_ACTIONS, hide_index=True, use_container_width=True)
        st.markdown("#### 🏷️ Thèmes")
        st.write(" · ".join(f"`{t}`" for t in selected) or "—")
        st.markdown("#### 🗣️ Temps de parole (simulé)")
        st.bar_chart(pd.DataFrame({"min": [2.1, 1.6]}, index=["Alice", "Bob"]))


# --------------------------------------------------------------------------- #
# Parcours dictaphone
# --------------------------------------------------------------------------- #
def parcours_dictaphone():
    st.subheader("🎤 Mode dictaphone — réunion en présentiel")
    st.caption("L'application capte le micro de l'appareil. Diarisation à inférer.")

    if not consent_gate("dicta"):
        st.warning("⛔ Cochez les deux consentements pour activer la captation.")
        return

    st.markdown("#### 1. Captation audio (réelle)")
    audio = st.audio_input("Enregistrez un court extrait ou importez un fichier")

    if audio is not None:
        st.audio(audio)
        if st.button("🚀 Lancer la transcription (mockée)", type="primary"):
            with st.status("Traitement en cours…", expanded=True) as status:
                st.write("⬆️ Normalisation de l'audio (WAV 16 kHz)…"); time.sleep(0.6)
                st.write("📝 Transcription (Whisper — mockée)…"); time.sleep(0.8)
                st.write("🗣️ Diarisation (pyannote — mockée)…"); time.sleep(0.6)
                st.write("🏷️ Classification ton/thèmes…"); time.sleep(0.5)
                st.write("📄 Génération du compte-rendu…"); time.sleep(0.5)
                status.update(label="Terminé", state="complete")
            show_results()
    else:
        st.info("🎙️ En attente d'un enregistrement…")


# --------------------------------------------------------------------------- #
# Parcours visio (wireframe uniquement — pas de SDK dans Streamlit)
# --------------------------------------------------------------------------- #
def parcours_visio():
    st.subheader("📹 Mode visio — réunion à distance")
    st.caption("Wireframe & flow. Streamlit gère mal la visio en direct : on montre "
               "le PARCOURS, pas le SDK.")

    plateforme = st.radio(
        "Plateforme de captation",
        ["Plateforme Scribe (LiveKit)", "Microsoft Teams (bot)",
         "Google Meet (bot)", "Zoom (bot)"],
        horizontal=False,
    )

    if "Scribe" in plateforme:
        st.markdown(
            "```\n"
            "┌──────────────────────────────────────────┐\n"
            "│  Salle Scribe (LiveKit)            ● REC  │\n"
            "│  ┌────────────┐   ┌────────────┐          │\n"
            "│  │   Alice    │   │    Bob     │          │\n"
            "│  │  🎥 caméra │   │  🎥 caméra │          │\n"
            "│  └────────────┘   └────────────┘          │\n"
            "│  [🎤] [🎥] [🖥️ Partager]   [Quitter]      │\n"
            "└──────────────────────────────────────────┘\n"
            "```"
        )
        st.success("Pistes audio séparées par participant → « qui parle » connu nativement.")
    else:
        st.markdown(f"**Flux bot — {plateforme.split(' (')[0]}**")
        st.markdown(
            "```\n"
            "1. Utilisateur colle l'URL de la réunion\n"
            "2. Scribe envoie un bot (Recall.ai) qui rejoint la réunion\n"
            "3. Le bot enregistre l'audio (+ transcription diarisée)\n"
            "4. Webhook 'recording.done' → Scribe lance le pipeline\n"
            "5. Compte-rendu disponible dans le tableau de bord\n"
            "```"
        )
        st.text_input("URL de la réunion", placeholder="https://teams.microsoft.com/l/meetup-join/…")

    if not consent_gate("visio"):
        st.warning("⛔ Cochez les deux consentements pour simuler le lancement.")
        return

    if st.button("🚀 Rejoindre & traiter (simulé)", type="primary"):
        with st.status("Connexion à la visio…", expanded=True) as status:
            st.write("🤖 Le bot rejoint la réunion…"); time.sleep(0.7)
            st.write("🎙️ Enregistrement multipiste…"); time.sleep(0.7)
            st.write("📝 Transcription + diarisation native…"); time.sleep(0.7)
            st.write("📄 Compte-rendu…"); time.sleep(0.5)
            status.update(label="Terminé", state="complete")
        show_results()


# --------------------------------------------------------------------------- #
# Tableau de bord (aperçu)
# --------------------------------------------------------------------------- #
def parcours_dashboard():
    st.subheader("📊 Tableau de bord (aperçu maquette)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Réunions", "12")
    c2.metric("Minutes traitées", "284")
    c3.metric("Actions ouvertes", "7")
    c4.metric("Coût API", "1,84 €")
    st.markdown("#### Thèmes dominants")
    st.bar_chart(pd.DataFrame({"Occurrences": [8, 6, 5, 3]}, index=THEMES))
    st.markdown("#### Réunions récentes")
    st.dataframe(pd.DataFrame([
        {"Titre": "Point hebdo produit", "Mode": "📹 Teams", "Durée": "32 m", "Statut": "✅"},
        {"Titre": "Atelier client X", "Mode": "🎤 Dictaphone", "Durée": "47 m", "Statut": "✅"},
        {"Titre": "Rétro sprint 14", "Mode": "📹 Scribe", "Durée": "28 m", "Statut": "⏳"},
    ]), hide_index=True, use_container_width=True)


# --------------------------------------------------------------------------- #
# Mise en page
# --------------------------------------------------------------------------- #
st.title("🎙️ Scribe — Maquette interactive")
st.caption("Pré-production · les traitements sont **simulés**. Voir le dossier de cadrage pour le détail.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Parcours", ["Tableau de bord", "Mode dictaphone", "Mode visio"])
    st.divider()
    st.markdown("**Gestion d'erreurs (démo)**")
    if st.checkbox("Simuler une erreur API"):
        st.error("❌ Erreur 503 : le service de transcription est indisponible. "
                 "Réessayez dans quelques instants. (Le pipeline réel relance "
                 "automatiquement avec back-off.)")
    st.divider()
    st.caption("RNCP 36146 · Projet fil rouge Scribe")

if page == "Tableau de bord":
    parcours_dashboard()
elif page == "Mode dictaphone":
    parcours_dictaphone()
else:
    parcours_visio()
