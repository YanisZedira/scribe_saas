# Scribe — Dossier de cadrage

> Projet fil rouge · RNCP 36146 (Concepteur développeur de solutions digitales) · Bloc BC01 / amorce BC02
> Version 1.0 — pré-production

---

## 1. Vision produit

### Elevator pitch

> **Scribe transforme chaque réunion — à distance ou en présentiel — en un compte-rendu structuré et une liste d'actions, automatiquement.** L'utilisateur lance Scribe, parle, et récupère en quelques minutes un résumé fidèle, l'attribution de qui a dit quoi, le ton et les thèmes de la réunion, et des actions assignées avec responsables et échéances — le tout consultable dans un espace personnel qui suit les décisions dans le temps.

### Le problème (la douleur)

Les réunions sont le premier outil de coordination des équipes, et le plus mal exploité :

- **40 à 60 % du contenu d'une réunion est oublié** dans les 24 h. Les décisions se perdent, les actions ne sont pas suivies.
- Prendre des notes **empêche de participer** : celui qui écrit ne contribue pas pleinement.
- Les comptes-rendus manuels coûtent **20 à 30 minutes par réunion** et sont rédigés de façon hétérogène.
- Les outils existants (Otter, Fireflies, Teams Premium…) sont **soit cantonnés à une plateforme**, soit **inutilisables en présentiel**, soit **opaques sur le RGPD** (données envoyées hors UE, voix biométrique non traitée).

### La proposition de valeur unique

Scribe est le **seul** assistant qui couvre **les deux situations d'usage opposées avec la même qualité** :

1. **Réunion à distance** → Scribe rejoint / héberge la visio (Teams, Google Meet, Zoom, ou sa propre plateforme LiveKit) et récupère l'audio à la source.
2. **Réunion en présentiel** → Scribe devient un **dictaphone intelligent** sur le navigateur.

…et qui place le **RGPD et l'éthique au cœur du produit** (consentement explicite, hébergement UE possible, droit à l'effacement natif), un argument décisif pour les organisations européennes.

### Critères de succès

| Axe | Indicateur | Cible |
|---|---|---|
| Adoption | Réunions traitées / utilisateur actif / semaine | ≥ 3 |
| Qualité perçue | % de CR jugés « utilisables sans retouche » | ≥ 80 % |
| Qualité technique | WER (taux d'erreur mot) FR sur audio propre | ≤ 12 % |
| Fiabilité | Disponibilité du service (SLO) | ≥ 99,5 % |
| Performance | Délai de traitement / minute d'audio | ≤ 0,5× temps réel |
| Économie | Coût API moyen par réunion de 30 min | ≤ 0,30 € |
| Conformité | % de réunions avec consentement tracé | 100 % |

---

## 2. Personae & parcours

### Persona 1 — Camille, manager en télétravail

- **Rôle** : manager d'une équipe produit de 8 personnes, 100 % distanciel.
- **Contexte** : 15–20 réunions Teams/Meet par semaine. Jongle entre animation et prise de notes.
- **Douleurs** : oublie les décisions, perd du temps à rédiger les CR, relances d'actions chronophages.
- **Objectif** : déléguer entièrement la prise de notes et le suivi d'actions, sans changer ses outils (Teams/Meet).
- **Citation** : *« Je veux animer mes réunions, pas les retranscrire. »*

**Journey map — mode visio**

| Étape | Action utilisateur | Émotion | Réponse de Scribe |
|---|---|---|---|
| Avant | Planifie une réunion Teams | Neutre | Colle l'URL dans Scribe (ou connecte son agenda) |
| Démarrage | Lance la réunion | Légère charge | Le bot Scribe rejoint, signale l'enregistrement aux participants |
| Consentement | — | Vigilance RGPD | Écran/message de consentement, traçabilité |
| Pendant | Anime, participe | Soulagée (ne note plus) | Capte l'audio multipiste en arrière-plan |
| Fin | Quitte la réunion | Curieuse | Pipeline async, notification « CR prêt » |
| Après | Ouvre le CR | Satisfaite | CR structuré + actions assignées + relances |

### Persona 2 — Karim, chef de projet en présentiel

- **Rôle** : chef de projet BTP / conseil, réunions de chantier et ateliers clients **sur site**.
- **Contexte** : réunions en salle, autour d'une table, sans visio. Souvent plusieurs interlocuteurs.
- **Douleurs** : impossible d'utiliser les outils de visio ; notes manuscrites illisibles ; pas de trace des engagements clients.
- **Objectif** : un dictaphone qui transcrit, identifie les intervenants et sort un CR exploitable face au client.
- **Citation** : *« En réunion de chantier, je n'ai que mon téléphone et trois personnes qui parlent en même temps. »*

**Journey map — mode dictaphone**

| Étape | Action utilisateur | Émotion | Réponse de Scribe |
|---|---|---|---|
| Avant | Ouvre Scribe sur mobile/laptop | Neutre | Sélectionne « Dictaphone » |
| Consentement | Informe les participants | Vigilance | Écran de consentement, case à cocher |
| Captation | Pose l'appareil, lance | Confiance | Capte le micro, gère coupures, découpe les longs fichiers |
| Fin | Arrête l'enregistrement | Attente | Transcription + diarisation (séparation des voix) |
| Après | Consulte le CR | Soulagé | CR + actions + temps de parole par intervenant |

---

## 3. Carte des user-stories (User Story Map) & MoSCoW

Chaque story est **rattachée à un palier** (🟢 socle / 🔵 cible / 🟣 avancé) et priorisée **MoSCoW** (M=Must, S=Should, C=Could, W=Won't-now).

### Épopée A — Captation audio

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| A1 | En tant qu'utilisateur, je capte une réunion **présentiel** via le micro du navigateur. | 🟢 | **M** |
| A2 | En tant qu'utilisateur, je capte une réunion **visio** via un SDK intégré (audio global). | 🟢 | **M** |
| A3 | En visio, je récupère **une piste audio par participant**. | 🔵 | **S** |
| A4 | En dictaphone, la captation est **robuste** (coupures gérées, longs fichiers découpés). | 🔵 | **S** |
| A5 | Je rejoins une visio **externe** (Teams/Meet/Zoom) via un **bot de réunion**. | 🟣 | **C** |
| A6 | J'héberge la visio en **auto-hébergé** (LiveKit/Jitsi) avec reprise sur incident. | 🟣 | **C** |

### Épopée B — Transcription & diarisation

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| B1 | J'obtiens la **transcription texte** de la réunion. | 🟢 | **M** |
| B2 | En visio, « qui parle » découle du **découpage par piste**. | 🟢 | **M** |
| B3 | En dictaphone, j'obtiens une **diarisation réelle** (séparation des voix). | 🔵 | **S** |
| B4 | Les intervenants sont **nommés** (identification nominative), multilingue, timestamps fins. | 🟣 | **C** |

### Épopée C — Classification

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| C1 | J'obtiens un **ton global** ou une **liste de thèmes**. | 🟢 | **M** |
| C2 | J'obtiens une classification **par segment** (ton, thèmes, urgence). | 🔵 | **S** |
| C3 | J'utilise un **modèle dédié/affiné** avec métriques de qualité. | 🟣 | **W** |

### Épopée D — Compte-rendu & actions

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| D1 | J'obtiens un **résumé en texte libre**. | 🟢 | **M** |
| D2 | J'obtiens un **CR structuré** (décisions, actions + responsable + échéance) en JSON rendu proprement. | 🔵 | **S** |
| D3 | Les actions sont **reliées aux responsables**, avec statuts, relances, export PDF/e-mail/agenda. | 🟣 | **C** |

### Épopée E — Persistance & historique

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| E1 | Je m'**authentifie** et retrouve **mes** réunions. | 🟢 | **M** |
| E2 | Les données suivent un **modèle relationnel propre** avec filtres. | 🔵 | **S** |
| E3 | Je **partage** une réunion, je configure la **rétention**, j'**anonymise**. | 🟣 | **C** |

### Épopée F — Tableau de bord

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| F1 | Je vois la **liste** de mes réunions et j'accède au CR + 1-2 indicateurs. | 🟢 | **M** |
| F2 | Je **filtre** (date, thème, statut) et je vois des **graphes**. | 🔵 | **S** |
| F3 | Je suis des **tendances dans le temps** + alertes d'actions en retard. | 🟣 | **C** |

### Épopée G — RGPD & transverse

| ID | User story | Palier | MoSCoW |
|---|---|---|---|
| G1 | Le **consentement** est recueilli avant tout traitement. | 🟢 | **M** |
| G2 | J'exerce mon **droit à l'effacement**. | 🔵 | **S** |
| G3 | **Anonymisation** des transcriptions + DPA sous-traitants. | 🟣 | **C** |

> **Règle de découpage** : aucune story de palier supérieur (🔵/🟣) n'est planifiée avant que le **socle 🟢 de la même épopée** ne soit livré, testé et documenté.

---

## 4. État de l'art / benchmark (synthèse)

Le benchmark détaillé (coût, latence, quotas, langues, RGPD, capacité à récupérer l'audio) figure dans **[`03_benchmark.md`](03_benchmark.md)** et **`benchmark/benchmark.xlsx`**. Synthèse :

### 4.1 Visioconférence intégrable (≥ 3)

| Plateforme | Modèle | Coût indicatif | Récup. audio | RGPD / UE | Verdict |
|---|---|---|---|---|---|
| **LiveKit** (Cloud ou self-host) | WebRTC open-source | ~0,0005 $/participant-min (Cloud) ; **gratuit** self-host | ★★★ Egress multipiste | ★★★ self-host UE | **Plateforme propre** |
| **Daily** | API SaaS | gratuit < ~10k min, puis à l'usage | ★★★ raw-tracks | ★★ US | Alternative rapide |
| **Jitsi** | Open-source | gratuit (infra) | ★★ via Jibri | ★★★ self-host | Repli low-cost |
| Whereby Embedded | SaaS | abo + à l'usage | ★★ | ★★ | Écarté (coût/UE) |
| Twilio Video | SaaS | — | — | — | ❌ **En fin de vie** (EOL) |

### 4.2 Transcription + diarisation (≥ 3)

| API | Modèle | Coût (€/h audio) | Diarisation | Langues | RGPD |
|---|---|---|---|---|---|
| **OpenAI** | gpt-4o-transcribe / whisper | ~0,34 €/h ($0,006/min) | via API tierce ou whisper+pyannote | 90+ | ⚠️ US (DPA dispo) |
| **AssemblyAI** | Universal | ~0,25 €/h ($0,27/h) **diar. incluse** | ✅ native (95 langues) | 99 | ⚠️ US |
| **Deepgram** | Nova-3 | ~0,27 €/h (batch + diar.) | ✅ native | 30+ | ⚠️ US (option on-prem) |
| Whisper **self-host** + pyannote | open-source | coût GPU only | ✅ pyannote | 90+ | ★★★ **UE/on-prem** |
| Google Speech-to-Text v2 | Chirp | ~0,9 €/h (estim.) | ✅ | 125+ | ⚠️ US |

### 4.3 LLM pour résumé + extraction d'actions (≥ 2)

| Modèle | Coût (in/out, $/1M tokens) | Qualité FR | Sortie JSON | Verdict |
|---|---|---|---|---|
| **GPT-4o-mini** | 0,15 / 0,60 | ★★★ | ✅ json_object | **Défaut (rapport qualité/prix)** |
| **Claude Haiku** | 1,00 / 5,00 | ★★★ | ✅ | Repli qualité |
| **Gemini 2.5 Flash** | 0,30 / 2,50 | ★★ | ✅ | Alternative |

### 4.4 Classification (≥ 1 approche)

- **Approche retenue (socle/cible)** : appel **LLM** (le même que pour le CR) → ton, thèmes, urgence en JSON. Zéro infra supplémentaire, multilingue, flexible.
- **Approche alternative (avancé)** : modèle NLP dédié (CamemBERT fine-tuné pour le FR) → comparaison LLM vs modèle dédié (qualité, coût, latence) documentée.

> **Choix de tête** : OpenAI gpt-4o-transcribe + gpt-4o-mini pour démarrer (simple, peu cher, JSON natif) ; **chemin de souveraineté** Whisper+pyannote self-host pour les clients RGPD-sensibles ; LiveKit comme plateforme propre + Recall.ai pour Teams/Meet/Zoom.

---

## 5. Analyse RGPD & éthique IA (synthèse)

Détail complet dans **[`04_rgpd.md`](04_rgpd.md)**. Un enregistrement de réunion contient des **voix (donnée biométrique, art. 9 RGPD)** et des propos identifiables / confidentiels. Mesures par palier :

| Sujet | 🟢 Socle | 🔵 Cible | 🟣 Avancé |
|---|---|---|---|
| **Consentement** | Mentionné, base légale identifiée | Écran de consentement maquetté, registre simplifié | Consentement **effectif** bloquant + traçabilité |
| **Conservation** | Durée définie (90 j) | Configurable par utilisateur | Purge automatique + politique documentée |
| **Droit à l'effacement** | Annoncé | Endpoint de suppression | Effacement **en cascade** + anonymisation |
| **Sous-traitants** | Listés | DPA identifiés | **DPA signés** + hébergement UE option |

---

## 6. Roadmap & backlog

### 6.1 Release plan (haut niveau)

| Release | Contenu | Paliers visés |
|---|---|---|
| **R1 — MVP socle** | Auth, dictaphone (audio global), visio (audio global), transcription brute, résumé LLM, liste réunions | 🟢 tous |
| **R2 — Cible** | Diarisation réelle dictaphone, visio multipiste, CR structuré JSON, modèle relationnel + filtres, dashboard graphes, API+front séparés, async | 🔵 |
| **R3 — Avancé** | Bot Teams/Meet/Zoom, identification nominative, actions reliées + relances + export, partage/anonymisation, tendances, CD complet + monitoring | 🟣 |

### 6.2 Backlog Sprint #1 (détaillé & estimé)

> **Objectif Sprint #1** : livrer un **socle de bout en bout** (dictaphone → transcription → résumé → liste) avant toute story de palier supérieur. Estimation en *story points* (Fibonacci).

| # | Story | Tâches | SP | Critères d'acceptation |
|---|---|---|---|---|
| S1-1 | E1 Auth | Modèle User, register/login JWT, garde-fou | 3 | Un user s'inscrit, se connecte, voit ses réunions uniquement |
| S1-2 | A1 Dictaphone | `st.audio_input`/upload, `DictaphoneSource`, normalisation | 5 | Un audio uploadé est accepté, borné en taille |
| S1-3 | B1 Transcription | Abstraction STT + provider OpenAI + fallback mock | 5 | Un audio produit des segments texte |
| S1-4 | D1 Résumé | Client LLM + résumé texte libre | 3 | Un CR texte est généré et affiché |
| S1-5 | F1 Liste | Endpoint liste + écran tableau de bord minimal | 2 | La liste affiche les réunions + accès CR |
| S1-6 | G1 Consentement | Écran/flag de consentement bloquant | 2 | Sans consentement, traitement refusé (428) |
| S1-7 | Qualité | Tests unitaires pipeline + CI lint/test | 3 | CI verte, couverture ≥ 70 % sur logique non-IA |
| | | **Total** | **23 SP** | |

---

## 7. Plan de risques

Matrice **Probabilité (1-5) × Impact (1-5)** → criticité = P×I. Risques propres au sujet inclus.

| # | Risque | P | I | Crit. | Mesures de mitigation |
|---|---|---|---|---|---|
| R1 | **Dépassement du budget API** sur audios longs | 4 | 4 | 16 | Garde-fou durée (90 min), découpage, estimation de coût a priori, choix gpt-4o-mini, quotas par user, mode mock en dev |
| R2 | **Latence de transcription** trop élevée | 3 | 4 | 12 | Traitement **asynchrone** (worker+queue), STT batch, feedback de progression, SLO ≤ 0,5× temps réel |
| R3 | **Échec d'intégration visio** (SDK/bot) | 4 | 4 | 16 | Abstraction `AudioSource` isolant la visio, Recall.ai (1 intégration = 3 plateformes), repli LiveKit/Jitsi, tests de webhook |
| R4 | **Qualité de diarisation insuffisante** (dictaphone) | 4 | 3 | 12 | Privilégier visio multipiste, pyannote + post-traitement, identification nominative optionnelle, afficher un score de confiance |
| R5 | **Non-conformité RGPD** (voix biométrique) | 3 | 5 | 15 | Consentement bloquant tracé, hébergement UE (self-host), DPA, droit à l'effacement, minimisation |
| R6 | **Fuite / accès non autorisé** aux enregistrements | 2 | 5 | 10 | Chiffrement au repos et en transit, isolation par utilisateur, rétention courte, logs d'accès |
| R7 | **Dépendance fournisseur** (lock-in / changement de prix) | 3 | 3 | 9 | Abstractions multi-providers (STT/LLM/visio), chemin self-host, veille tarifaire (cf. EOL Twilio Video) |
| R8 | **Qualité audio dégradée** (bruit, micro lointain) | 4 | 3 | 12 | Réduction de bruit, consignes UX (placer l'appareil), VAD, fallback « audio insuffisant » |
| R9 | **Hallucination du LLM** dans le CR (fausses décisions) | 3 | 4 | 12 | Sortie structurée contrainte, citations/ancrage sur la transcription, température basse, revue humaine encouragée |
| R10 | **Indisponibilité d'une API tierce** | 2 | 4 | 8 | Retry back-off, dégradation gracieuse (fallback provider), monitoring/alerting |

---

## 8. Plan qualité

| Domaine | Métrique cible | Outil |
|---|---|---|
| **Style de code** | PEP 8 + type-hinting + docstrings Google | `ruff`, `mypy` |
| **Couverture de tests** | ≥ 70 % des fonctions critiques (socle) ; tests d'intégration (avancé) | `pytest`, `pytest-cov` |
| **Revue de code** | 1 reviewer min. par PR, CI verte obligatoire | GitHub PR + CI |
| **Qualité STT** | WER ≤ 12 % (FR, audio propre) mesuré sur échantillons | scripts benchmark |
| **Qualité diarisation** | DER (Diarization Error Rate) suivi | scripts benchmark |
| **Performance** | Traitement ≤ 0,5× temps réel ; p95 latence API mesurée | scripts `benchmark/scripts` |
| **Sécurité** | Pas de secret en clair, dépendances scannées | `.env`, audit deps |
| **Définition of Done** | Story = code + tests + doc + CI verte + critères d'acceptation validés | — |

---

*Fin du dossier de cadrage. Voir `02_specs_architecture.md` pour les spécifications techniques détaillées.*
