# Maquette Streamlit — Scribe

Maquette interactive de pré-production. **Les traitements sont simulés (mockés)** :
la maquette fige le parcours et sécurise les choix UX, elle ne fait pas tourner la
chaîne IA réelle (voir dossier §6.3).

## Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Contenu

| Écran | Détail |
|---|---|
| **Tableau de bord** | Indicateurs, thèmes dominants, réunions récentes |
| **Mode dictaphone** | Capture audio **réelle** via `st.audio_input` → transcription **mockée**, CR placeholder |
| **Mode visio** | Wireframe + flow diagram (Scribe/LiveKit, Teams, Meet, Zoom). Pas de SDK (Streamlit gère mal la visio live) |
| **Consentement RGPD** | Écran de consentement bloquant avant tout traitement |
| **Ton / thèmes** | Sélecteur simulé + icône |
| **Erreurs & chargement** | `st.status` (indicateurs) + simulation d'erreur API (sidebar) |

## Vidéo démo

Voir `docs/demo_script.md` pour le script de la vidéo de démonstration (≤ 3 min).
