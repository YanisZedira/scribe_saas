# Scribe — Index des livrables

Récapitulatif de tout ce qui a été produit, et correspondance avec les exigences du dossier de pré-production.

## 1. La SaaS fonctionnelle (production-ready)

| Élément | Emplacement |
|---|---|
| Backend API FastAPI | `backend/app/` |
| ⭐ Abstraction « source audio » | `backend/app/audio_source/` (base, dictaphone, livekit, bot, factory) |
| Pipeline IA (STT, diarisation, classification, CR) | `backend/app/pipeline/` |
| Modèle de données relationnel | `backend/app/models.py` |
| Auth JWT | `backend/app/auth.py` |
| Workers asynchrones (RQ) + fallback | `backend/app/workers/` |
| Front-end SPA (tableau de bord, captation, CR) | `backend/app/static/index.html` |
| Tests (unitaires + intégration) | `backend/tests/` |
| Docker + compose (API+Postgres+Redis+worker) | `Dockerfile`, `docker-compose.yml` |
| CI (lint + tests) | `.github/workflows/ci.yml` |

## 2. Maquette Streamlit (livrable §6.3)

| Exigence | Statut |
|---|---|
| Deux parcours (visio + dictaphone) | ✅ `maquette/app.py` |
| Dictaphone : `st.audio_input` + transcription mockée | ✅ |
| Visio : wireframe + flow diagram (pas de SDK) | ✅ |
| CR en placeholder | ✅ |
| Sélecteur ton/thème + icône | ✅ |
| Gestion d'erreurs + indicateurs de chargement | ✅ |
| Écran de consentement RGPD | ✅ |

## 3. Documentation (dossiers §6.1 & §6.2)

| Livrable | Fichier |
|---|---|
| Dossier de cadrage (vision, personae, US map MoSCoW, benchmark, RGPD, roadmap, risques, qualité) | `docs/01_dossier_cadrage.md` |
| Spécifications & architecture (C4, ERD + dictionnaire, séquence UML, choix API, exigences, justif techno) | `docs/02_specs_architecture.md` |
| Benchmark détaillé 4 familles d'API | `docs/03_benchmark.md` |
| Analyse RGPD & éthique IA | `docs/04_rgpd.md` |
| Business model & pricing | `docs/05_business_model_pricing.md` |
| Choix des modèles & outils | `docs/06_choix_modeles_outils.md` |
| Script vidéo démo (≤ 3 min) | `docs/demo_script.md` |
| Sources PlantUML (C4 + séquence) | `docs/diagrams/*.puml` |

## 4. Annexes obligatoires (§6.4)

| Annexe | Fichier |
|---|---|
| Tableau de benchmark coût/perf | `benchmark/benchmark.xlsx` (généré par `benchmark/build_benchmark.py`) + `benchmark/benchmark_data.csv` |
| Scripts de test prototypaux (mesure de latence) | `benchmark/scripts/test_latency.py` |

## Couverture des paliers (grille du sujet)

| Brique | Socle 🟢 | Cible 🔵 | Avancé 🟣 |
|---|---|---|---|
| Captation | ✅ 2 modes | ✅ multipiste + dictaphone robuste | ✅ bot Teams/Meet/Zoom + LiveKit self-host |
| Transcription | ✅ texte | ✅ diarisation | ⚙️ identification nominative (hook prévu) |
| Classification | ✅ ton/thèmes | ✅ par segment (ton/urgence) | ⚙️ modèle dédié (comparaison documentée) |
| CR + actions | ✅ résumé | ✅ JSON structuré (décisions/actions/responsable/échéance) | ⚙️ relances/export (statuts implémentés) |
| Persistance | ✅ auth + isolation | ✅ modèle relationnel + filtres | ⚙️ partage/rétention/anonymisation |
| Tableau de bord | ✅ liste + indicateurs | ✅ graphes/thèmes/temps de parole | ⚙️ tendances/alertes |
| Architecture | ✅ propre | ✅ API+front, abstraction source audio, gestion erreurs | ✅ async worker+queue, webhooks |
| Tests & qualité | ✅ unitaires + lint | ✅ API mockées, couverture | ⚙️ tests d'intégration |
| CI/CD | ✅ Docker/README | ✅ CI lint+tests | ⚙️ CD/monitoring (documenté) |
| RGPD | ✅ identifié | ✅ consentement bloquant + registre | ✅ effacement cascade + DPA/self-host |

⚙️ = base implémentée / documentée, finalisation prévue en production.
