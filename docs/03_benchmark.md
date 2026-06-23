# Scribe — Benchmark des API (état de l'art)

> Tarifs relevés en **juin 2026** sur documentation publique. Conversion indicative **1 $ ≈ 0,92 €**. Le détail chiffré et les formules de coût figurent dans `benchmark/benchmark.xlsx`. Les chiffres marqués « ~ » sont des estimations à revérifier avant tout engagement contractuel (cf. sources en fin de document).

---

## 1. Méthodologie

- **Scénario de référence** : réunion de **30 minutes**, **2 à 4 participants**, en français.
- **Sortie attendue** : transcription diarisée + classification (ton/thèmes) + CR structuré + actions.
- **Familles évaluées** : (1) visioconférence intégrable, (2) transcription+diarisation, (3) LLM résumé/actions, (4) classification.
- **Critères** : coût ($/€), temps de réponse/latence, quota, langues, conformité RGPD, **capacité à récupérer l'audio**.
- **Protocole de mesure (palier avancé)** : scripts `pytest` dans `benchmark/scripts/` mesurant la latence p50/p95 sur des échantillons courts, budget plafonné à 15 €.

---

## 2. Famille 1 — Visioconférence intégrable

| Critère | **LiveKit** | **Daily** | **Jitsi** | Whereby | Twilio Video |
|---|---|---|---|---|---|
| Modèle | Open-source + Cloud | SaaS | Open-source | SaaS | SaaS |
| Coût | ~0,0005 $/part-min (Cloud) · **gratuit** self-host | gratuit < ~10k min puis usage | **gratuit** (infra only) | abo + usage | **❌ EOL** |
| Récup. audio | ★★★ Egress **multipiste** | ★★★ raw-tracks | ★★ via Jibri | ★★ | — |
| Plans | Build (gratuit), Ship 50 $/mo, Scale 500 $/mo | tiers usage | — | ~9,99 $/mo+ | — |
| Langues | N/A (transport) | N/A | N/A | N/A | N/A |
| RGPD/UE | ★★★ self-host UE | ★★ US | ★★★ self-host | ★★ | — |
| **Verdict** | ✅ **Plateforme propre** | Alternative rapide | Repli low-cost | Écarté | ❌ Écarté (fin de vie) |

**Bot pour plateformes externes — Recall.ai** : couvre **Teams, Google Meet, Zoom**, Webex, GoTo. **0,50 $/h** d'enregistrement (Pay-As-You-Go 2026) + **0,15 $/h** transcription intégrée + stockage 0,05 $/30 j au-delà de 7 j gratuits. **Aucun frais de plateforme mensuel.** → 1 intégration = 3 plateformes, évite de maintenir 3 SDK.

---

## 3. Famille 2 — Transcription + diarisation

| Critère | **OpenAI** | **AssemblyAI** | **Deepgram** | **Whisper self-host** | Google STT v2 |
|---|---|---|---|---|---|
| Modèle | gpt-4o-transcribe / whisper | Universal | Nova-3 | whisper + pyannote | Chirp |
| Coût/h audio | **~0,34 €** ($0,006/min) | **~0,25 €** ($0,27/h, diar. incluse) | **~0,27 €** (batch+diar.) | **coût GPU** only | ~0,9 € (estim.) |
| Diarisation | via pyannote/API tierce | ✅ native (95 langues) | ✅ native (add-on) | ✅ pyannote | ✅ |
| Streaming | ✅ (gpt-realtime ~$0,017/min) | ✅ | ✅ ($0,0048–0,0058/min) | selon impl. | ✅ |
| Langues | 90+ | **99** | 30+ | 90+ | **125+** |
| Quota | élevé (limites compte) | élevé | $200 crédit offert | illimité (votre infra) | quotas GCP |
| RGPD/UE | ⚠️ US (DPA, zero-retention option) | ⚠️ US | ⚠️ US (on-prem possible) | ★★★ **UE/on-prem** | ⚠️ US (régions UE) |
| **Verdict** | ✅ **Socle (simplicité)** | Bon si diar. clé | ✅ **Cible (diar. pas chère)** | ✅ **Avancé (souveraineté)** | Écarté (coût) |

> **Note prix** : AssemblyAI annonce **+10 % à compter du 1ᵉʳ juillet 2026** sur le pricing in-region. Deepgram facture la diarisation en add-on : un workflow complet n'est pas au prix de base affiché. Toujours revérifier sur les pages officielles.

---

## 4. Famille 3 — LLM (résumé + extraction d'actions)

| Critère | **GPT-4o-mini** | **Claude Haiku** | **Gemini 2.5 Flash** |
|---|---|---|---|
| Coût input ($/1M tk) | **0,15** | 1,00 | 0,30 |
| Coût output ($/1M tk) | **0,60** | 5,00 | 2,50 |
| Sortie JSON stricte | ✅ `json_object` | ✅ (prompt) | ✅ |
| Qualité FR | ★★★ | ★★★ | ★★ |
| Coût / CR de réunion 30 min* | **~0,001–0,003 €** | ~0,01 € | ~0,005 € |
| RGPD/UE | ⚠️ US | ⚠️ US | ⚠️ US |
| **Verdict** | ✅ **Défaut** | Repli qualité | Alternative |

\* Estimation : ~5–8k tokens input (transcription 30 min) + ~1k output.

---

## 5. Famille 4 — Classification (≥ 1 approche)

| Approche | Coût | Latence | Qualité | Effort |
|---|---|---|---|---|
| **LLM (même appel que le CR)** | quasi nul (mutualisé) | faible | bonne, flexible, multilingue | ★ très faible |
| Modèle de sentiment pré-entraîné (HF) | gratuit (self-host) | très faible | correcte (sentiment seul) | ★★ moyen |
| **CamemBERT fine-tuné** (FR) | coût entraînement + GPU inf. | très faible | potentiellement supérieure (FR) | ★★★ élevé |

**Retenu** : LLM au socle/cible (zéro infra) ; **comparaison argumentée LLM vs modèle dédié** au palier avancé, avec métriques (accuracy, F1, latence, coût).

---

## 6. Synthèse — coût d'une réunion de 30 min (config recommandée)

| Poste | Choix | Coût |
|---|---|---|
| Captation visio (externe) | Recall.ai bot + transcription | ~0,33 € (0,5 h × 0,65 $) |
| OU Captation visio (propre) | LiveKit self-host | ~0 € (infra) |
| OU Dictaphone | navigateur | 0 € |
| Transcription (si non incluse) | gpt-4o-transcribe 0,34 €/h | ~0,17 € |
| Classification + CR + actions | GPT-4o-mini | ~0,003 € |
| **Total (visio externe)** | | **~0,33–0,35 €** |
| **Total (dictaphone / plateforme propre)** | | **~0,17 € voire 0 € (self-host)** |

✅ Sous la cible de **0,30 €/réunion** dès qu'on évite le bot externe ; le bot reste rentable pour le confort Teams/Meet/Zoom.

---

## 7. Recommandation finale (sensibilité au volume)

- **Faible volume / démarrage** : OpenAI (STT+LLM) + LiveKit + Recall.ai à l'usage. Simplicité maximale, pas d'infra.
- **Volume moyen** : bascule STT vers **Deepgram Nova-3** (diarisation native moins chère), LLM reste GPT-4o-mini.
- **Fort volume / exigence RGPD** : **Whisper+pyannote self-host** + **LiveKit/Jitsi self-host** → coût marginal proche de zéro, souveraineté des données, DPA évités.

> Le code de Scribe implémente ces choix comme **providers interchangeables** (`STT_PROVIDER`, `LLM_PROVIDER`, `VISIO_PROVIDER`) : changer de fournisseur = changer une variable d'environnement.

---

## Sources (relevé juin 2026)

- AssemblyAI — [pricing](https://www.assemblyai.com/pricing) · [99 langues](https://www.assemblyai.com/blog/99-languages)
- Deepgram — [pricing](https://deepgram.com/pricing)
- OpenAI — [API pricing](https://openai.com/api/pricing/)
- Recall.ai — [nouveau pricing 2026](https://www.recall.ai/blog/new-recall-ai-pricing-for-2026) · [pricing](https://www.recall.ai/pricing)
- LiveKit — [pricing](https://livekit.com/pricing)
- Comparatifs LLM — [BenchLM](https://benchlm.ai/llm-pricing), [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
