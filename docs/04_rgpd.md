# Scribe — Analyse RGPD & éthique IA

> Un enregistrement de réunion contient des **voix** (donnée biométrique, art. 9 RGPD), des **propos identifiables** et potentiellement **confidentiels**. C'est un traitement à risque qui exige des mesures spécifiques.

---

## 1. Données traitées & qualification

| Donnée | Catégorie RGPD | Sensibilité |
|---|---|---|
| Voix (empreinte vocale) | **Donnée biométrique** (art. 9) si utilisée pour identifier | ⚠️ Élevée |
| Transcription (propos) | Donnée personnelle (art. 4) | Élevée (confidentialité métier) |
| Nom des intervenants | Donnée personnelle | Moyenne |
| Adresse e-mail (compte) | Donnée personnelle | Moyenne |
| Métadonnées (date, durée, thèmes) | Donnée personnelle | Faible |

> **Important** : la diarisation « anonyme » (SPEAKER_00/01) ne crée pas de biométrie ; l'**identification nominative** (rattacher une voix à une personne nommée) peut relever de l'art. 9 → consentement explicite renforcé requis.

---

## 2. Base légale & consentement

- **Base légale retenue** : **consentement** (art. 6.1.a) de **tous les participants**, recueilli **avant** la captation. Le consentement est **explicite, éclairé et traçable**.
- Mise en œuvre dans Scribe :
  - Écran/case de consentement **bloquant** (HTTP 428 si absent — voir `routers/meetings.py::_guard_consent`).
  - Trace horodatée par participant (entité `Consent`).
  - Information préalable : finalité (CR + suivi), durée de conservation, droits.
  - En visio externe, le bot **annonce** sa présence (message + nom « Scribe »).

---

## 3. Durée de conservation & minimisation

| Élément | Durée | Mécanisme |
|---|---|---|
| Enregistrement audio brut | **supprimé après transcription** (option) | minimisation |
| Transcription + CR | **90 j par défaut**, configurable par utilisateur (`retention_days`) | `expires_at` + purge |
| Compte utilisateur | tant que le compte est actif | — |

**Minimisation** : on ne conserve pas l'audio brut une fois la transcription produite (sauf option explicite), réduisant le risque biométrique.

---

## 4. Droits des personnes

| Droit | Implémentation Scribe |
|---|---|
| **Accès** | `GET /api/meetings/{id}` (propriétaire) |
| **Effacement** | `DELETE /api/meetings/{id}` → suppression **en cascade** (segments, actions, locuteurs, consentements) |
| **Rectification** | édition des noms d'intervenants / actions |
| **Portabilité** | export JSON/PDF (palier avancé) |
| **Opposition** | refus de consentement = pas de traitement |

---

## 5. Sous-traitants (API tierces) & transferts

Chaque API externe est un **sous-traitant** au sens RGPD → un **DPA** (Data Processing Agreement) est nécessaire, et les **transferts hors UE** doivent être encadrés (CCT / clauses contractuelles types).

| Sous-traitant | Rôle | Localisation | Mesure |
|---|---|---|---|
| OpenAI | STT + LLM | US | DPA + option zero-retention + CCT |
| Deepgram / AssemblyAI | STT alternatif | US | DPA + CCT (ou on-prem Deepgram) |
| Recall.ai | Bot visio | US | DPA + CCT |
| LiveKit (self-host) | Visio propre | **UE (votre infra)** | ✅ pas de transfert |
| Whisper+pyannote (self-host) | STT souverain | **UE (votre infra)** | ✅ pas de transfert |

> **Chemin de souveraineté** : pour les clients RGPD-sensibles, Scribe bascule sur la stack **100 % self-host UE** (LiveKit + Whisper/pyannote) → aucun transfert hors UE, aucun DPA tiers requis.

---

## 6. Éthique IA

- **Transparence** : l'utilisateur sait que le CR est généré par IA et peut contenir des erreurs (mention affichée).
- **Lutte contre l'hallucination** : sortie structurée contrainte, ancrage sur la transcription, température basse, **revue humaine encouragée** avant diffusion.
- **Biais** : la qualité STT/diarisation varie selon accents/langues → afficher un **score de confiance** et permettre la correction.
- **Non-surveillance** : Scribe est un outil de productivité, pas de surveillance des employés ; le temps de parole est informatif, pas un outil de notation individuelle.

---

## 7. Mesures par palier (rappel grille)

| Sujet | 🟢 Socle | 🔵 Cible | 🟣 Avancé |
|---|---|---|---|
| Consentement | identifié, base légale | écran maquetté + registre simplifié | **effectif bloquant** + traçabilité |
| Conservation | durée définie | configurable | purge auto + politique |
| Effacement | annoncé | endpoint | **cascade + anonymisation** |
| Sous-traitants | listés | DPA identifiés | **DPA signés + hébergement UE** |

---

## 8. Registre de traitement (simplifié)

| Champ | Valeur |
|---|---|
| Traitement | Transcription et analyse de réunions |
| Finalité | Production de comptes-rendus et suivi d'actions |
| Base légale | Consentement (art. 6.1.a) |
| Catégories de données | Voix, transcription, identité, e-mail |
| Personnes concernées | Participants aux réunions, utilisateurs |
| Destinataires | Utilisateur propriétaire ; sous-traitants API |
| Transferts hors UE | Oui si providers US (encadrés CCT) ; non en mode self-host |
| Durée de conservation | 90 j (configurable) |
| Mesures de sécurité | Chiffrement transit/repos, auth JWT, isolation par user, purge |
