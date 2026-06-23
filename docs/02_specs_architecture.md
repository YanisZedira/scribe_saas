# Scribe — Spécifications & architecture

> Version 1.0 — pré-production · Bloc BC01 (conception) / BC02 (choix d'outils)

Les diagrammes sont en **Mermaid** (rendus par GitHub/VS Code) ; les sources PlantUML équivalentes sont dans `docs/diagrams/`.

---

## 1. Architecture C4

### 1.1 Niveau 1 — Contexte

```mermaid
C4Context
title Scribe — Diagramme de contexte
Person(user, "Utilisateur", "Manager distanciel ou chef de projet présentiel")
System(scribe, "Scribe", "Assistant de réunion : captation, transcription, CR, suivi")
System_Ext(visio, "Plateformes visio", "Teams, Google Meet, Zoom")
System_Ext(stt, "API de transcription", "OpenAI / AssemblyAI / Deepgram")
System_Ext(llm, "API LLM", "OpenAI / Anthropic / Gemini")
System_Ext(bot, "Service de bot", "Recall.ai (rejoint Teams/Meet/Zoom)")

Rel(user, scribe, "Capte des réunions, consulte CR & actions", "HTTPS")
Rel(scribe, visio, "Rejoint / héberge la réunion", "SDK / bot")
Rel(scribe, bot, "Envoie un bot dans la réunion", "REST + webhook")
Rel(scribe, stt, "Transcrit l'audio", "REST")
Rel(scribe, llm, "Résume, classe, extrait les actions", "REST")
```

### 1.2 Niveau 2 — Conteneurs

L'**abstraction « source audio »** apparaît explicitement : elle découple totalement les deux modes de captation de la chaîne de traitement.

```mermaid
flowchart TB
  user([Utilisateur])

  subgraph client["Front-end (SPA / Streamlit maquette)"]
    spa["Web app<br/>(HTML/JS, Tailwind)"]
  end

  subgraph api["Backend FastAPI"]
    rest["API REST<br/>auth · meetings · dashboard · consent · webhooks"]
    subgraph absrc["⭐ Abstraction « Source Audio » (AudioSource)"]
      dicta["DictaphoneSource<br/>(micro navigateur)"]
      lk["LiveKitSource<br/>(plateforme propre, multipiste)"]
      botsrc["BotSource<br/>(Teams/Meet/Zoom via Recall.ai)"]
    end
    pipe["Pipeline IA<br/>transcribe → diarize → classify → summarize"]
  end

  queue[["File de tâches<br/>(Redis + RQ)"]]
  worker["Worker asynchrone"]
  db[("Base de données<br/>Postgres / SQLite")]

  stt[/"API STT"/]
  llm[/"API LLM"/]
  visio[/"Plateformes visio + Recall.ai"/]

  user --> spa --> rest
  rest --> absrc
  dicta & lk & botsrc --> pipe
  rest --> queue --> worker --> pipe
  pipe --> stt
  pipe --> llm
  botsrc & lk --> visio
  pipe --> db
  rest --> db
```

**Conteneurs** : Front-end SPA · API FastAPI · Worker · Redis · Base de données. Le **module `audio_source`** (factory + 3 implémentations) est le point de variation unique entre visio et dictaphone — tout le reste du pipeline est commun.

---

## 2. Modèle de données

### 2.1 ERD

```mermaid
erDiagram
    USER ||--o{ MEETING : possède
    MEETING ||--o{ SPEAKER : contient
    MEETING ||--o{ SEGMENT : contient
    MEETING ||--o{ ACTION : génère
    MEETING ||--o{ THEME : caractérise
    MEETING ||--o{ CONSENT : trace
    SPEAKER ||--o{ SEGMENT : prononce

    USER {
        string id PK
        string email UK
        string full_name
        string hashed_password
        int retention_days
        datetime created_at
    }
    MEETING {
        string id PK
        string owner_id FK
        string title
        enum mode "dictaphone|visio"
        enum status
        string platform "livekit|teams|meet|zoom"
        string language
        int duration_sec
        string overall_tone
        text summary_md
        text decisions_json
        float cost_eur
        bool consent_obtained
        datetime started_at
        datetime expires_at
    }
    SPEAKER {
        string id PK
        string meeting_id FK
        string label "SPEAKER_00"
        string display_name "Alice"
        float talk_time_sec
    }
    SEGMENT {
        string id PK
        string meeting_id FK
        string speaker_id FK
        float start_sec
        float end_sec
        text text
        string tone
        string urgency
    }
    ACTION {
        string id PK
        string meeting_id FK
        text description
        string assignee
        datetime due_date
        enum status "open|in_progress|done|late"
        datetime created_at
    }
    THEME {
        string id PK
        string meeting_id FK
        string label
        float weight
    }
    CONSENT {
        string id PK
        string meeting_id FK
        string participant_label
        bool consented
        datetime timestamp
    }
```

### 2.2 Dictionnaire d'attributs (extrait)

| Entité | Attribut | Type | Contraintes | Description |
|---|---|---|---|---|
| User | email | string | unique, indexé | Identifiant de connexion |
| User | retention_days | int | défaut 90 | Durée de conservation RGPD (configurable) |
| Meeting | mode | enum | `dictaphone`\|`visio` | Mode de captation |
| Meeting | status | enum | cf. cycle de vie | Étape dans le pipeline |
| Meeting | platform | string | nullable | Plateforme visio le cas échéant |
| Meeting | cost_eur | float | ≥ 0 | Coût API réel observé (suivi budget) |
| Meeting | consent_obtained | bool | défaut false | Verrou de traitement RGPD |
| Meeting | expires_at | datetime | nullable | Date d'effacement automatique |
| Speaker | label | string | — | Étiquette technique de diarisation |
| Speaker | display_name | string | nullable | Nom humain (identification nominative) |
| Segment | start_sec/end_sec | float | end ≥ start | Bornes temporelles |
| Segment | tone/urgency | string | nullable | Classification par segment (cible) |
| Action | assignee | string | nullable | Responsable (réf. Speaker.display_name) |
| Action | due_date | datetime | nullable | Échéance |
| Theme | weight | float | 0–1 | Importance relative |

### 2.3 Schéma JSON d'une réunion stockée

```json
{
  "id": "uuid",
  "title": "Point hebdo produit",
  "mode": "visio",
  "platform": "teams",
  "language": "fr",
  "duration_sec": 1920,
  "overall_tone": "neutre",
  "cost_eur": 0.11,
  "speakers": [
    {"label": "Alice", "display_name": "Alice", "talk_time_sec": 126.0}
  ],
  "segments": [
    {"speaker": "Alice", "start_sec": 0.0, "end_sec": 8.2,
     "text": "Bonjour à tous…", "tone": "positif", "urgency": "normale"}
  ],
  "themes": [{"label": "Livraison / planning", "weight": 0.8}],
  "decisions": ["Mise en production repoussée à lundi"],
  "actions": [
    {"description": "Livrer le correctif paiement", "assignee": "Bob",
     "due_date": "2026-06-26", "status": "open"}
  ]
}
```

---

## 3. Séquence clé — traitement complet d'une réunion

Distingue le **chemin visio** et le **chemin dictaphone**, convergeant vers la chaîne commune.

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant API as API FastAPI
    participant AS as AudioSource (factory)
    participant Q as File de tâches
    participant W as Worker / Pipeline
    participant STT as API STT
    participant LLM as API LLM
    participant DB as Base de données

    U->>API: POST /meetings (titre, mode, consentement)
    API->>DB: crée Meeting (status=created)

    alt Mode DICTAPHONE (présentiel)
        U->>API: POST /{id}/dictaphone (fichier audio)
        API->>API: vérifie consentement + taille
        API->>Q: enqueue(meeting_id, audio_path)
        Q->>W: job
        W->>AS: DictaphoneSource.acquire()
        AS-->>W: AudioBundle (1 piste, per_speaker=False)
    else Mode VISIO (distance)
        U->>API: POST /{id}/visio (url Teams/Meet | room LiveKit)
        API->>AS: BotSource.join() / LiveKit room
        Note over AS: Bot rejoint, enregistre
        AS-->>API: bot_id
        API->>Q: enqueue(meeting_id, bot_id)
        Q->>W: job (sur webhook recording.done)
        W->>AS: BotSource/LiveKitSource.acquire()
        AS-->>W: AudioBundle (multipiste, per_speaker=True)
    end

    Note over W: ⭐ Chaîne commune à partir d'ici
    W->>STT: transcribe(bundle)
    STT-->>W: segments (texte + timestamps)
    W->>W: diarize() → qui parle quand
    W->>LLM: classify() → ton, thèmes, urgence
    W->>LLM: summarize() → CR + actions (JSON)
    LLM-->>W: compte-rendu structuré
    W->>DB: persiste speakers, segments, themes, actions, CR
    W->>DB: status=done, coût, expires_at
    U->>API: GET /{id} → CR + actions + transcription
```

---

## 4. Choix d'API (argumenté, par famille & par palier)

| Famille | Socle 🟢 | Cible 🔵 | Avancé 🟣 | Justification |
|---|---|---|---|---|
| **Visio** | LiveKit (audio global) | LiveKit Egress **multipiste** | **Recall.ai** (Teams/Meet/Zoom) + Jitsi self-host | LiveKit = open-source, self-host UE, multipiste natif. Recall = 1 intégration pour 3 plateformes. Twilio Video **écarté (EOL)**. |
| **STT** | OpenAI gpt-4o-transcribe | + Deepgram Nova-3 (diar. native) | Whisper+pyannote **self-host** (souveraineté) | gpt-4o-transcribe : simple, 0,34 €/h, multilingue. Deepgram : diarisation native pas chère. Self-host : RGPD/coût au volume. |
| **LLM** | GPT-4o-mini | GPT-4o-mini + JSON strict | Claude Haiku en repli | Meilleur rapport qualité/prix (0,15/0,60 $/1M), JSON natif, bon en FR. |
| **Classification** | LLM (même appel) | LLM par segment | CamemBERT fine-tuné + comparaison | Démarrer sans infra ; comparer LLM vs modèle dédié au palier avancé. |

Détails chiffrés et sensibilité au volume : **[`03_benchmark.md`](03_benchmark.md)**.

---

## 5. Exigences fonctionnelles & non-fonctionnelles

| Catégorie | Exigence | Cible |
|---|---|---|
| **Performance** | Délai de traitement | ≤ 0,5× temps réel (réunion 30 min traitée < 15 min) |
| **SLO disponibilité** | Uptime API | ≥ 99,5 % |
| **SLO latence** | p95 endpoints synchrones | < 400 ms |
| **Budget API** | Coût / réunion 30 min | ≤ 0,30 € |
| **Budget pré-prod** | Plafond total essais | ≤ 15 € (audios test 5–10 min) |
| **Durée max testée** | Réunion | 90 min (garde-fou) |
| **Taille upload** | Fichier audio | ≤ 200 Mo |
| **Sécurité** | Auth | JWT, mots de passe hachés (bcrypt) |
| **Scalabilité** | Réunions simultanées | worker + queue horizontalement scalable |
| **Conformité** | Consentement | bloquant + tracé ; rétention configurable |

---

## 6. Justification technologique personnelle

### Stack & bibliothèques Python

| Choix | Alternative écartée | Raison |
|---|---|---|
| **FastAPI** | Flask, Django | Async natif, OpenAPI auto, typage Pydantic, idéal pour I/O API |
| **SQLModel** | SQLAlchemy seul | Modèles + schémas unifiés, typés, ergonomiques |
| **Pydantic v2** | dataclasses | Validation et (dé)sérialisation robustes |
| **RQ + Redis** | Celery | Plus simple, suffisant ; Celery surdimensionné au stade actuel |
| **httpx** | requests | Support async + timeouts fins |
| **passlib/bcrypt + python-jose** | — | Standards éprouvés pour auth |
| **pytest + respx** | unittest | Fixtures puissantes, mock HTTP propre |
| **ruff** | flake8 + isort + black | Tout-en-un rapide (lint PEP 8 + imports) |

### Pipeline CI/CD envisagé

```mermaid
flowchart LR
    A[Push / PR] --> B[CI: ruff lint]
    B --> C[CI: pytest + couverture ≥ 70%]
    C --> D{Branche main ?}
    D -- non --> E[Rapport PR]
    D -- oui --> F[Build image Docker]
    F --> G[Deploy Railway/Render<br/>env staging]
    G --> H[Smoke tests]
    H --> I[Promotion prod manuelle]
```

- **Socle** : déploiement manuel reproductible (Docker/README), app en ligne.
- **Cible** : CI (lint+tests sur PR), déploiement semi-auto (Railway/Render/Vercel).
- **Avancé** : CD complet, environnements séparés (dev/staging/prod), monitoring, logs, alerting.

### Monitoring envisagé

- **Logs structurés** (JSON) + corrélation par `meeting_id`.
- **Métriques** : latence pipeline par étape, coût API par réunion, taux d'échec, profondeur de queue.
- **Alerting** : actions en retard, échecs de pipeline, dépassement de budget API.
- Outils candidats : Prometheus + Grafana (self-host) ou Sentry + provider PaaS.

---

*Fin des spécifications. Annexes : `03_benchmark.md`, `04_rgpd.md`, `benchmark/benchmark.xlsx`.*
