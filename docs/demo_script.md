# Script vidéo démo (≤ 3 min)

| Temps | Écran | Narration |
|---|---|---|
| 0:00–0:20 | Slide titre + problème | « Les réunions se perdent : 40 à 60 % du contenu oublié en 24 h. Scribe les transforme en compte-rendu et actions, à distance comme en présentiel. » |
| 0:20–0:35 | Maquette — tableau de bord | Présentation des indicateurs et thèmes dominants. |
| 0:35–1:15 | Maquette — **mode dictaphone** | Écran de consentement RGPD → capture audio réelle (`st.audio_input`) → indicateurs de chargement → CR placeholder + actions + temps de parole. |
| 1:15–1:55 | Maquette — **mode visio** | Wireframe salle LiveKit + flow bot Teams/Meet/Zoom. Insister sur l'abstraction « source audio » commune. |
| 1:55–2:20 | App réelle (`/app`) | Connexion, création d'une réunion, traitement de bout en bout (mode mock), CR généré. |
| 2:20–2:40 | Code — `audio_source/` | Montrer l'abstraction et les 3 sources ; « changer de fournisseur = une variable d'env ». |
| 2:40–3:00 | Slide RGPD + clôture | Consentement bloquant, droit à l'effacement, option self-host UE. « Scribe : utile, fluide, conforme. » |

**Conseils** : montrer la gestion d'erreur (case « simuler une erreur API »), garder un rythme soutenu, sous-titrer les étapes du pipeline.
