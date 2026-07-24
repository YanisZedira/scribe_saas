# Commit 8 — `1ae2765` — dictaphone navigateur

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

[Voir `MeetingWorkflow.jsx`](https://github.com/AshDv/ScribeProject/blob/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428/web/src/MeetingWorkflow.jsx#L1-L217)

## Lignes 1 à 5 — imports et chronomètre

| Ligne | Explication |
|---|---|
| 1 | Importe trois hooks React. |
| 2 | Importe le client API. |
| 3 | Vide. |
| 4-5 | Fonction fléchée `formatTime`. `Math.floor(seconds/60)` calcule minutes ; `%60` calcule reste ; `String` convertit ; `padStart` ajoute zéro ; template literal assemble `MM:SS`. |

## `MeetingWorkflow`, lignes 7 à 15

| Ligne | Explication |
|---|---|
| 7 | Composant exporté, callback `onCreated` déstructuré. |
| 8 | État `meeting`, initialement `null`. |
| 10 | Sans réunion, retourne `MeetingSetup`; `setMeeting` devient callback. |
| 11-13 | Si statut non recording, retourne suivi des accords. |
| 14 | Sinon retourne Recorder avec réunion et callback parent. |
| 15 | Ferme fonction. |

Ces retours anticipés forment une machine à trois écrans.

## `MeetingSetup`, lignes 17 à 59

### États

| Ligne | Explication |
|---|---|
| 17 | Composant interne. |
| 18 | Titre par défaut. |
| 19 | Tableau initial avec un objet participant vide. |
| 20 | Erreur vide. |
| 21 | `busy=false`, aucune requête active. |

### `update`, lignes 23 à 30

```javascript
setParticipants((items) =>
  items.map((item, position) =>
    position === index ? { ...item, [field]: value } : item
  )
);
```

- utilise l’état courant reçu par callback ;
- `map` crée un nouveau tableau ;
- compare chaque position ;
- spread copie l’objet ciblé ;
- `[field]` crée une propriété dynamique `name` ou `email` ;
- les autres objets gardent la même référence.

Pourquoi ne pas muter `participants[index].name` : React s’appuie sur de nouvelles références pour
comprendre les changements.

### `create`, lignes 32 à 44

| Ligne | Explication |
|---|---|
| 32 | Fonction async recevant événement de formulaire. |
| 33 | Empêche rechargement HTML. |
| 34 | Passe en occupé ; bouton sera disabled. |
| 35 | Efface ancienne erreur. |
| 36 | Ouvre try. |
| 37 | Attend création API puis passe la réunion au parent. |
| 38-39 | Capture erreur réseau/métier et affiche son message. |
| 40-41 | `finally` s’exécute succès/échec ; remet busy false. |
| 42-44 | Fermetures. |

### JSX, lignes 46 à 59

- `section.page` ouvre l’écran ;
- header contient eyebrow, h1 et explication ;
- formulaire appelle `create` ;
- champ titre contrôlé par `value` et `onChange` ;
- bouton Ajouter a `type="button"` pour ne pas soumettre ;
- spread ajoute un objet participant ;
- `participants.map` produit chaque ligne ;
- `key={index}` est simple mais instable après suppression ;
- `aria-label` dynamique rend le champ identifiable ;
- bouton retirer apparaît seulement si plus d’un participant ;
- `filter` crée un tableau sans la position ;
- texte RGPD rappelle finalité ;
- erreur conditionnelle ;
- bouton disabled pendant l’envoi et libellé ternaire.

## `ConsentStatus`, lignes 61 à 95

### États

- `notice=false` : annonce dans la salle non confirmée ;
- `error=""`.

### Polling, lignes 65 à 70

| Ligne | Explication |
|---|---|
| 65 | Ouvre effet. |
| 66 | Fonction async locale : GET réunion puis callback parent. |
| 67 | `setInterval` appelle toutes les 3 000 ms. `.catch(() => {})` avale les erreurs. |
| 68 | Cleanup annule l’intervalle. |
| 69 | Dépend de l’ID et du callback. |

Limite critique : en panne réseau, aucune erreur n’est montrée et le système continue.

### `start`, lignes 72 à 84

- si case d’annonce fausse : message puis retour ;
- sinon appelle route start ;
- remplace réunion avec réponse ;
- catch affiche l’erreur.

### JSX

- liste des participants par `meeting.participants.map` ;
- `key={participant.id}` stable ;
- statut CSS dynamique ;
- ternaires : Retiré, Accepté ou En attente ;
- checkbox contrôlée `notice` ;
- bouton disabled si `all_consented` faux ;
- le backend revalide malgré le disabled.

## `Recorder`, lignes 97 à 217

### États React, lignes 98 à 102

| État | Type / rôle |
|---|---|
| `state` | chaîne de machine à états, initiale `idle` |
| `seconds` | nombre pour l’affichage |
| `audioBlob` | Blob ou null |
| `audioUrl` | chaîne URL locale |
| `error` | chaîne affichée |

### Refs, lignes 103 à 106

| Ref | Valeur |
|---|---|
| `recorder` | instance MediaRecorder |
| `stream` | MediaStream du micro |
| `chunks` | tableau de Blob audio |
| `consentRevoked` | booléen lu par callbacks |

Une ref survit au rendu et sa modification ne déclenche pas un nouveau rendu.

### Effet chronomètre, lignes 108 à 112

- ne fait rien hors `recording` ;
- intervalle chaque seconde ;
- mise à jour fonctionnelle `value + 1` ;
- cleanup ;
- recréé quand `state` change.

Le timer peut dériver en arrière-plan ; ce n’est pas la durée audio certifiée.

### Effet consentement, lignes 114 à 132

| Instruction | Explication |
|---|---|
| vérifie state recording/paused | Ne poll pas en idle/ready. |
| `verify` async | Charge réunion actuelle. |
| statut non recording ou accord manquant | Détecte interdiction. |
| `consentRevoked.current = true` | Informe `onstop` de ne pas créer le Blob. |
| optional stop | Arrête si MediaRecorder actif. |
| `setAudioBlob(null)` | Efface données prêtes. |
| setter fonctionnel URL | Révoque URL actuelle puis vide. |
| `setError(...)` | Message utilisateur. |
| intervalle 3 s | Répète vérification. |
| catch vide | Panne ignorée, comportement fail-open. |
| cleanup | Annule intervalle. |

### Effet de nettoyage, lignes 134 à 138

- retourne directement une fonction cleanup ;
- arrête chaque track du stream ;
- révoque l’URL si présente ;
- dépend d’`audioUrl`, donc cleanup aussi lors de changement.

### `start`, lignes 140 à 175

| Ligne/bloc | Explication |
|---|---|
| efface erreur | Nouveau départ propre. |
| try | Encadre permission/constructeur. |
| revoke flag false | Nouvelle session autorisée. |
| `getUserMedia({audio:true})` | Demande permission et flux microphone. HTTPS/localhost requis. |
| `chunks.current=[]` | Nouveau buffer. |
| `new MediaRecorder(stream)` | Appelle le constructeur navigateur. |
| `ondataavailable` | Callback déclenché avec morceaux. |
| `if event.data.size` | Ignore morceau vide. |
| `push` | Ajoute dans l’ordre. |
| `onstop` | Callback lorsque stop terminé. |
| branche consentRevoked | Vide, null, idle, coupe tracks, return. |
| `new Blob(chunks, {type})` | Assemble les morceaux ; MIME réel ou fallback. |
| `setAudioBlob` | Stocke octets pour upload. |
| `URL.createObjectURL` | Crée URL locale de préécoute. |
| `setState("ready")` | Affiche lecteur/actions. |
| stop tracks | Libère microphone. |
| `recorder.current.start()` | Lance réellement MediaRecorder. |
| reset secondes | Nouveau chrono. |
| state recording | Lance UI et effet timer. |
| catch sans variable | Toute erreur devient message micro générique. |

Limites :

- pas de `MediaRecorder.isTypeSupported`;
- pas de gestion différente selon erreur ;
- audio entier en mémoire ;
- pas de `timeslice`;
- pas de niveau sonore.

### `pause`, lignes 177 à 185

- inspecte l’état natif réel ;
- si recording, appelle pause et état React paused ;
- sinon appelle resume optionnel et état recording.

Le `else` suppose que tout autre état autorisé signifie paused. Le bouton n’est affiché que dans ces
deux états, ce qui maintient l’invariant UI.

### `stop`, lignes 187 à 189

Vérifie objet et état non inactive puis appelle stop. `onstop` fera le reste.

### `reset`, lignes 191 à 198

Révoque URL, efface Blob/URL/temps/état/erreur. Chaque setter déclenche une mise à jour React,
généralement regroupée.

### `send`, lignes 200 à 210

- état uploading ;
- API avec titre, Blob, confirmation vraie et ID ;
- réponse `item`, puis callback avec `item.id`;
- en erreur : message et retour ready pour retry.

### JSX, lignes 212 à 217

Une grande partie est compactée sur six lignes :

- header explique l’auto-identification et les modèles ;
- badge consentements ;
- classe `live` uniquement pendant recording ;
- chronomètre ;
- libellé par ternaires imbriqués ;
- boutons selon machine à états ;
- `<audio controls src={audioUrl}>` pour préécoute ;
- fragment groupe lecteur et boutons ;
- spinner pendant upload ;
- alerte.

Les ternaires imbriqués sont fonctionnels mais une table de libellés serait plus lisible.

## Ajouts `api.js`

| Ligne logique | Explication |
|---|---|
| `listRecordings` | GET liste. |
| `getRecording(id)` | URL dynamique détail. |
| `const form = new FormData()` | Conteneur multipart navigateur. |
| `form.set("title", title)` | Champ texte. |
| `form.set("consent", String(consent))` | Conversion booléen vers texte multipart. |
| `form.set("consent_session_id", ...)` | Identifiant exact attendu. |
| `form.set("audio", audio, nom)` | Ajoute Blob et nom client horodaté. |
| `request(... POST body form)` | Le helper ne force pas JSON pour FormData. |
| `deleteRecording` | DELETE. |

Ne jamais fixer manuellement l’en-tête multipart : le navigateur doit ajouter la boundary.

