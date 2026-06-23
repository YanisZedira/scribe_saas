# Scribe — Business model & pricing (produit SaaS)

> Comment Scribe devient une SaaS commercialement viable. Les coûts variables (API) sont issus de `03_benchmark.md`.

---

## 1. Positionnement & marché

- **Catégorie** : Meeting intelligence / AI note-taker.
- **Concurrents** : Otter.ai, Fireflies.ai, Fathom, Microsoft Teams Premium (intelligent recap), tl;dv.
- **Différenciateurs Scribe** :
  1. **Présentiel ET distanciel** (dictaphone + visio) — la plupart des concurrents ne couvrent que la visio.
  2. **Multi-plateformes** (Teams, Meet, Zoom) **+ plateforme propre** (LiveKit).
  3. **RGPD/souveraineté** : option self-host UE, consentement natif — argument fort en Europe.
  4. **Suivi d'actions dans le temps** (pas seulement un CR ponctuel).

---

## 2. Segments cibles

| Segment | Besoin | Disposition à payer |
|---|---|---|
| Indépendants / freelances | CR clients, dictaphone présentiel | Faible (freemium) |
| PME / équipes | Suivi décisions & actions | Moyenne (par siège) |
| ETI / grands comptes (UE) | Conformité, self-host, SSO | Élevée (entreprise) |
| Secteurs régulés (santé, juridique, public) | Souveraineté, on-prem | Très élevée |

---

## 3. Structure de coûts (par utilisateur actif / mois)

Hypothèse : **20 réunions/mois × 30 min** = 10 h d'audio.

| Poste | Mode économique (self-host) | Mode managé (API) |
|---|---|---|
| Transcription | ~0 € (GPU mutualisé) | 10 h × 0,34 € = **3,40 €** |
| LLM (CR + classif.) | 20 × 0,003 € = **0,06 €** | 0,06 € |
| Visio | ~0 € (LiveKit self-host) | bot Recall 10 h × 0,65 $ ≈ **6,0 €** (si externe) |
| Infra (hébergement, BDD) | ~1–2 € | ~1–2 € |
| **Coût marginal / user / mois** | **~1,5–2,5 €** | **~5–10 €** |

➡️ **Marge brute saine** dès un prix de vente ≥ 12 €/mois.

---

## 4. Grille tarifaire proposée

| Plan | Prix | Cible | Inclus |
|---|---|---|---|
| **Free** | 0 € | Découverte | 5 réunions/mois, dictaphone, CR basique, rétention 7 j |
| **Pro** | **12 €/mois** (ou 120 €/an) | Indépendants, power users | Réunions illimitées*, visio (Meet/Teams/Zoom), CR structuré + actions, dashboard, rétention 90 j |
| **Team** | **18 €/siège/mois** | Équipes (min. 3) | Tout Pro + partage, espace équipe, tendances, intégrations (agenda, Slack), exports |
| **Enterprise** | sur devis | ETI/grands comptes, secteurs régulés | Tout Team + **self-host UE**, SSO/SAML, DPA signé, SLA 99,9 %, support dédié, on-prem STT |

\* « illimité » avec garde-fou anti-abus (fair use, ex. 60 h audio/mois).

**Logique de prix** : aligné sur le marché (Otter ~17 $, Fireflies ~18 $/mois) avec un **plan Pro plus accessible** et un **différenciateur Enterprise souveraineté** où la concurrence est faible.

---

## 5. Modèle de revenus & projections (illustratif)

| Hypothèse | Valeur |
|---|---|
| Conversion Free → payant | 4 % |
| Mix Pro/Team | 60 % / 40 % |
| Churn mensuel | 4 % |
| ARPU | ~14 €/mois |

| Scénario à 12 mois | Users payants | MRR | Coûts API (managé) | Marge brute |
|---|---|---|---|---|
| Prudent | 300 | ~4 200 € | ~2 100 € | ~50 % |
| Médian | 1 200 | ~16 800 € | ~7 200 € | ~57 % |
| Optimiste | 4 000 | ~56 000 € | ~22 000 € | ~60 % |

> La bascule **self-host** sur les comptes à fort volume fait grimper la marge brute vers **75–85 %**.

---

## 6. Go-to-market

- **PLG (Product-Led Growth)** : freemium + onboarding fluide + partage de CR (boucle virale : un participant non-utilisateur reçoit un CR Scribe).
- **Bottom-up entreprise** : adoption individuelle → upsell Team → Enterprise.
- **Angle conformité** : contenu et SEO sur « note-taker RGPD », « alternative souveraine à Otter », ciblage UE/secteur public.
- **Intégrations** comme canal : marketplace Teams/Zoom, Slack, Google Workspace.

---

## 7. Risques business

| Risque | Mitigation |
|---|---|
| Commoditisation (LLM/STT moins chers et intégrés partout) | Se différencier par **présentiel + souveraineté + suivi d'actions**, pas par la transcription brute |
| Teams Premium / Google « recap » natifs | Cibler le **multi-plateformes** et le **présentiel** que les natifs ne couvrent pas |
| Coût API qui explose au volume | Chemin **self-host** déjà implémenté (providers interchangeables) |
| Confiance/RGPD | Faire de la conformité un **argument de vente**, pas une contrainte |
