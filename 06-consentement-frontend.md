# Commit 6 — `ecd894c` — consentement frontend

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/ecd894ce955b396193fcc1300278517fbd4c3d35)

## `PrivacyFlows.jsx`, lignes 1 à 94

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/ecd894ce955b396193fcc1300278517fbd4c3d35/web/src/PrivacyFlows.jsx#L1-L94)

## Imports et états, lignes 1 à 8

| Ligne | Explication |
|---|---|
| 1 | Import nommé de `useEffect` et `useState`. |
| 2 | Import nommé de l’objet `api` local. |
| 3 | Ligne vide. |
| 4 | Composant exporté `PublicConsent`, props déstructurées pour obtenir `token`. |
| 5 | `notice` commence à `null` : données pas encore reçues. |
| 6 | `message` commence vide : confirmation métier. |
| 7 | `error` commence vide : erreur séparée. |
| 8 | Ligne vide avant effet. |

## Chargement, lignes 9 à 11

```javascript
useEffect(() => {
  api.getPublicConsent(token).then(setNotice).catch(...);
}, [token]);
```

- l’effet synchronise avec l’API ;
- `then(setNotice)` passe la réponse à React ;
- `catch` récupère le message ;
- `[token]` relance si la prop change ;
- aucun `AbortController` : une réponse tardive peut tenter une mise à jour après démontage.

## Fonction `act`, lignes 13 à 24

| Ligne | Explication |
|---|---|
| 13 | Fonction async recevant une autre fonction `action`. |
| 14 | Efface l’erreur précédente. |
| 15 | Ouvre `try`. |
| 16 | Attend `action(token)` ; réponse stockée dans `response`. |
| 17 | Ternaire : message accepté si statut exact, sinon message de retrait. |
| 18 | Recharge la notice officielle après modification. |
| 19 | Ouvre `catch`; `requestError` est l’objet Error. |
| 20 | Affiche `requestError.message`. |
| 21-24 | Ferme catch et fonction, puis ligne vide. |

Le nom `act` est court mais vague. `performConsentAction` serait plus explicite.

## Retours de chargement, lignes 26 à 28

- si erreur et aucune notice : shell + erreur ;
- si aucune notice sans erreur : chargement ;
- `active` est vrai si une date d’accord existe et aucun retrait.

`active` peut contenir une chaîne de date plutôt qu’un booléen strict. `Boolean(...)` serait plus
précis.

## JSX principal, lignes 29 à 52

| Lignes | Explication |
|---|---|
| 29 | Retourne `PublicShell`, composant wrapper. |
| 30 | Petit label sémantique. |
| 31 | Titre dynamique de réunion, échappé par React. |
| 32 | Salutation avec nom dynamique. |
| 33 | Ouvre la liste de transparence. |
| 34 | Informe de la captation voix/propos. |
| 35 | Affiche le sous-traitant dynamique. |
| 36 | Explique analyse de transcription. |
| 37 | Promet suppression audio après traitement ; doit correspondre au backend. |
| 38 | Affiche durée dynamique. |
| 39 | Explique droits. |
| 40 | Ferme liste. |
| 41 | Affiche contact. |
| 42 | Affichage conditionnel du succès. |
| 43 | Ouvre groupe de contrôles. |
| 44 | Si inactif, bouton accepter ; fonction fléchée appelle `act(api.acceptConsent)`. |
| 45 | Si inactif et jamais retiré, bouton refuser. |
| 46 | Si actif, bouton retirer. |
| 47 | Ouvre bouton effacement avec callback async inline. |
| 48 | `confirm` natif ; retour anticipé si annulation. |
| 49 | Attend DELETE public. Pas de `try/catch` autour de ce bloc. |
| 50 | Affiche un message local, sans recharger la notice. |
| 51 | Ferme callback, bouton et groupe. |
| 52 | Ferme `PublicShell` et retourne. |

Limite : après effacement, le token devient invalide mais l’écran garde les anciennes données en
mémoire jusqu’au rechargement.

## `PublicShell`, lignes 54 à 56

| Ligne | Explication |
|---|---|
| 54 | Fonction interne recevant `children`. |
| 55 | Renvoie le main, la carte, la marque puis insère `{children}`. |
| 56 | Ferme fonction. |

`children` est le contenu placé entre `<PublicShell>...</PublicShell>`.

## `LegalGate`, lignes 58 à 94

| Lignes | Explication |
|---|---|
| 58 | Composant exporté recevant callback `onAccepted`. |
| 59 | Notice légale, initialement absente. |
| 60 | État contrôlé de case CGU. |
| 61 | État contrôlé de case RGPD. |
| 62 | Erreur. |
| 64-66 | Effet exécuté une fois : charge notices ou message d’erreur. |
| 68 | Fonction async `accept`. |
| 69 | Ouvre try. |
| 70 | Appelle endpoint légal. L’API envoie deux booléens vrais. |
| 71 | Informe le parent que le passage est terminé. |
| 72-74 | Capture/affiche l’erreur. |
| 77 | Retourne shell public. |
| 78 | Libellé obligatoire. |
| 79 | Titre. |
| 80 | Fragment affiché seulement si `notice` existe. |
| 81 | Responsable et adresse. |
| 82 | Liste `processing`; `map` transforme les textes en `<li>`. `key={item}` suppose unicité. |
| 83 | Liste des finalités. |
| 84 | Liste des bases légales. |
| 85 | Liste des droits. |
| 86 | `join(", ")` transforme la liste des sous-traitants en texte. |
| 87 | Statut DPA. |
| 88 | Checkbox contrôlée CGU ; `checked` vient de l’état ; `onChange` lit `event.target.checked`. |
| 89 | Checkbox contrôlée RGPD. |
| 90 | Ferme fragment conditionnel. |
| 91 | Affiche erreur. |
| 92 | Bouton désactivé si une case manque ; `onClick={accept}` passe la fonction sans l’appeler immédiatement. |
| 93 | Ferme shell. |
| 94 | Ferme fonction. |

## Ajouts `api.js`

| Méthode | Requête | Explication |
|---|---|---|
| `startConsentSession(id)` | POST `/start` + JSON notice true | Demande le démarrage. Le backend revalide. |
| `stopConsentSession(id)` | POST `/stop` | Arrête l’état de réunion. |
| `getPublicConsent(token)` | GET public | Charge notice. |
| `acceptConsent(token)` | POST public | Pose l’accord. |
| `withdrawConsent(token)` | POST public | Pose le retrait. |
| `eraseConsentData(token)` | DELETE public | Déclenche l’effacement. |

Les backticks construisent des template literals et `${token}` insère le token dans le chemin.

## Questions pièges

**Pourquoi les cases frontend ne suffisent-elles pas ?**  
Le navigateur est contrôlé par l’utilisateur. Le backend doit refuser aussi.

**Pourquoi une fonction passée à `act` ?**  
Pour mutualiser try/catch, message et rafraîchissement.

**Pourquoi `onClick={accept}` sans parenthèses ?**  
On donne la fonction à React. `accept()` l’exécuterait pendant le rendu.

