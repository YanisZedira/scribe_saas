# Yanis — le dictaphone du navigateur expliqué ligne par ligne

Ce chapitre explique :

- [`1ae2765 — feat(recorder): add browser dictaphone`](https://github.com/AshDv/ScribeProject/commit/1ae2765b1bb0b9d585757c781a44ff2f4fc5b428)

Le commit ajoute le parcours complet dans le navigateur : préparer la réunion, attendre les accords, ouvrir le microphone, mettre en pause, arrêter, écouter, recommencer et envoyer l’audio.

## 1. Ce que le navigateur fait réellement

Le navigateur demande l’autorisation d’utiliser le microphone grâce à `getUserMedia`.

Il reçoit un flux audio. Un flux est une suite de données produites au fil du temps.

`MediaRecorder` transforme ce flux en fragments compressés. Le code place ces fragments dans une liste.

À l’arrêt, `Blob` rassemble les fragments en un objet fichier conservé en mémoire.

`URL.createObjectURL` fabrique une adresse temporaire permettant au lecteur `<audio>` de lire ce Blob.

Lors de l’envoi, `FormData` place ce Blob dans une demande HTTP transmise au backend.

À aucun moment ce commit ne fait lui-même la transcription. Le navigateur capture; le backend appelle ensuite Voxtral et Mistral.

## 2. Les imports

```jsx
import { useEffect, useRef, useState } from "react";
```

Les accolades demandent trois exports précis de React.

`useState` mémorise une valeur qui influence l’affichage.

`useRef` mémorise une valeur mutable entre deux affichages sans demander un nouvel affichage lorsqu’elle change.

`useEffect` lance une action après l’affichage et permet de la nettoyer.

```jsx
import { api } from "./api";
```

Cette ligne importe l’objet qui regroupe les appels au backend.

## 3. Fonction `formatTime`

```jsx
const formatTime = (seconds) =>
```

`const` crée une variable qui ne sera pas réaffectée. La valeur de cette variable est une fonction fléchée.

La fonction reçoit un nombre de secondes.

```jsx
`${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
```

Décomposition de la partie minutes :

1. `seconds / 60` calcule le nombre de minutes avec éventuellement une partie décimale ;
2. `Math.floor(...)` enlève la partie décimale en arrondissant vers le bas ;
3. `String(...)` transforme le nombre en texte ;
4. `.padStart(2, "0")` ajoute un zéro à gauche si le texte a moins de deux caractères.

Décomposition de la partie secondes :

1. `seconds % 60` calcule le reste après division par 60 ;
2. ce reste va de 0 à 59 ;
3. il est transformé en texte ;
4. un zéro est ajouté si nécessaire.

Les accents graves créent une chaîne modèle. `${...}` insère un calcul. Le deux-points entre les deux expressions est un caractère affiché.

Exemples :

- 5 devient `00:05`;
- 65 devient `01:05`;
- 3 600 devient `60:00`.

La fonction ne gère pas un format avec des heures séparées. Après une heure, elle continue à afficher le total des minutes.

## 4. Composant `MeetingWorkflow`

```jsx
export function MeetingWorkflow({ onCreated }) {
```

Le composant reçoit une fonction `onCreated`. Elle sera appelée après l’envoi réussi afin que le parent puisse ouvrir le résultat.

```jsx
const [meeting, setMeeting] = useState(null);
```

Au départ, aucune réunion n’existe dans ce parcours. `null` représente cette absence.

Lorsque `setMeeting` reçoit un objet, React réexécute le composant et choisit un autre écran.

### Premier choix

```jsx
if (!meeting) return <MeetingSetup onCreated={setMeeting} />;
```

Si `meeting` est absent, afficher le formulaire. La fonction `setMeeting` est donnée au composant enfant sous le nom `onCreated`.

Quand l’enfant appelle cette fonction avec la réponse du backend, le parent mémorise la réunion.

### Deuxième choix

```jsx
if (meeting.status !== "recording") {
  return <ConsentStatus meeting={meeting} onChange={setMeeting} />;
}
```

Si la réunion n’est pas encore autorisée à enregistrer, afficher l’état des consentements.

`!==` compare en exigeant une différence de valeur et de type.

Le composant enfant reçoit l’objet et une fonction permettant de le remplacer après actualisation.

### Dernier choix

Si l’état vaut `recording`, afficher `Recorder`.

Cette structure forme une petite machine à états : la valeur de `meeting` et son statut déterminent l’écran.

Une machine à états est une manière de décrire un processus par des états autorisés et des passages entre eux.

## 5. Composant `MeetingSetup`

### État du titre

```jsx
const [title, setTitle] = useState("Nouvelle réunion");
```

Le titre commence avec une valeur utilisable. Un champ React dont la valeur vient de l’état est appelé « champ contrôlé » : React possède la valeur affichée.

### État des participants

```jsx
const [participants, setParticipants] = useState([{ name: "", email: "" }]);
```

La valeur initiale est une liste contenant un objet.

Cet objet a deux propriétés vides : `name` et `email`.

La page affiche donc immédiatement une ligne de participant.

### États `error` et `busy`

`error` contient un message en cas d’échec.

`busy` vaut faux au départ et vrai pendant l’envoi. Il sert à désactiver le bouton et afficher « Envoi… ».

Cette protection visuelle réduit les doubles clics, mais le backend doit aussi gérer les demandes répétées si elles arrivent.

## 6. Fonction `update`

```jsx
const update = (index, field, value) => {
```

La fonction reçoit :

- `index` : position du participant dans la liste ;
- `field` : nom de la propriété à modifier, `name` ou `email`;
- `value` : nouveau texte.

```jsx
setParticipants((items) =>
```

Au lieu d’utiliser directement la variable extérieure, on donne à React une fonction qui reçoit la valeur la plus récente sous le nom `items`.

Cette forme évite d’utiliser une ancienne liste lorsque plusieurs mises à jour sont regroupées.

```jsx
items.map((item, position) =>
```

`map` parcourt chaque participant et construit une nouvelle liste de même longueur.

`item` est le participant actuel. `position` est son numéro commençant à zéro.

```jsx
position === index ? { ...item, [field]: value } : item,
```

L’opérateur conditionnel se lit :

- si la position correspond, créer un nouvel objet ;
- sinon, conserver l’objet existant.

`...item` copie toutes les propriétés de l’ancien objet.

`[field]: value` utilise la valeur de `field` comme nom de propriété. Si `field` vaut `"email"`, seule la propriété email est remplacée.

Pourquoi créer une nouvelle liste et un nouvel objet ? React détecte plus facilement le changement grâce à une nouvelle référence. Modifier directement `participants[index].name` serait plus difficile à suivre et pourrait ne pas provoquer l’affichage attendu.

Les virgules finales sont acceptées en JavaScript et facilitent les ajouts futurs.

## 7. Fonction `create`

```jsx
async function create(event) {
```

La fonction est appelée lors de l’envoi du formulaire. `event` décrit l’événement du navigateur.

```jsx
event.preventDefault();
```

Par défaut, un formulaire HTML recharge la page. Cette ligne annule ce comportement afin que React envoie la demande sans perdre son état.

```jsx
setBusy(true);
setError("");
```

L’interface passe en mode occupé et efface une ancienne erreur.

Le bloc `try` tente la demande :

```jsx
onCreated(await api.createConsentSession({ title, participants }));
```

L’objet `{ title, participants }` utilise une écriture raccourcie : quand le nom de propriété et la variable ont le même nom, JavaScript évite `title: title`.

`await` attend la réponse. `onCreated` reçoit ensuite l’objet réunion.

Le bloc `catch` reçoit l’erreur sous le nom `requestError` et affiche son message.

Le bloc `finally` s’exécute après succès ou échec et remet `busy` à faux.

Cette structure garantit que le bouton redevient disponible même si la demande échoue.

## 8. JSX de préparation

`<section className="page">` ouvre la page.

L’en-tête explique que chaque participant doit accepter par mail.

```jsx
<form ... onSubmit={create}>
```

Le formulaire appelle la fonction `create` lors d’un clic sur son bouton de soumission ou d’une validation au clavier.

### Champ titre

`value={title}` affiche la valeur d’état.

`onChange={(event) => setTitle(event.target.value)}` récupère chaque nouvelle valeur saisie.

`event.target` est l’élément qui a produit l’événement. `.value` est son texte actuel.

`required` demande au navigateur de refuser un champ vide. Le backend vérifie aussi la longueur; la validation du navigateur peut être contournée.

### Bouton Ajouter

`type="button"` est essentiel. Dans un formulaire, un bouton sans type peut agir comme soumission. Ici, il doit seulement ajouter une ligne.

```jsx
setParticipants([...participants, { name: "", email: "" }])
```

Les crochets créent une nouvelle liste. `...participants` copie les éléments existants. Le nouvel objet vide est ajouté à la fin.

Cette écriture utilise la valeur capturée au moment de l’affichage. Une forme fonctionnelle serait encore plus sûre si de nombreux ajouts pouvaient se produire très rapidement.

### Boucle visuelle

`participants.map(...)` crée un bloc pour chaque personne.

`key={index}` fournit la position comme identité React. Cette solution fonctionne souvent pour une petite liste, mais retirer un élément peut faire réutiliser des éléments à une autre position. Un identifiant stable généré pour chaque ligne serait plus robuste.

### Attributs `aria-label`

ARIA est un ensemble d’attributs aidant les technologies d’assistance.

Comme les champs n’ont pas de balise `<label>` visible distincte, `aria-label` leur donne un nom compréhensible par un lecteur d’écran.

La chaîne modèle ajoute le numéro humain `index + 1`, car l’index JavaScript commence à zéro.

### Retrait d’un participant

Le bouton apparaît seulement si la liste contient plus d’une personne.

```jsx
participants.filter((_, position) => position !== index)
```

`filter` construit une nouvelle liste contenant seulement les éléments dont la condition est vraie.

Le premier paramètre `_` représente le participant mais n’est pas utilisé. La condition garde toutes les positions sauf celle à supprimer.

Le symbole `×` est seulement le caractère affiché sur le bouton.

### Message et bouton final

Le paragraphe demande d’ajouter toutes les voix captées.

L’erreur est affichée seulement si le texte n’est pas vide.

Le bouton est désactivé pendant `busy`. L’opérateur conditionnel choisit « Envoi… » ou le libellé normal.

## 9. Composant `ConsentStatus`

### État `notice`

Ce booléen représente la case dans laquelle l’organisateur confirme l’annonce dans la salle.

### Actualisation toutes les trois secondes

```jsx
useEffect(() => {
```

L’effet est installé après l’affichage.

```jsx
const refresh = async () => onChange(await api.getConsentSession(meeting.id));
```

La fonction demande la version actuelle de la réunion et la remet dans le parent.

```jsx
const timer = setInterval(() => refresh().catch(() => {}), 3000);
```

`setInterval` répète une fonction toutes les 3 000 millisecondes, donc trois secondes.

Cette technique s’appelle polling : le navigateur demande régulièrement « est-ce que l’état a changé ? ».

`.catch(() => {})` capture l’échec mais ne fait rien. Les accolades vides représentent une fonction vide.

Conséquence : une panne réseau n’affiche aucune erreur à l’utilisateur. Le dernier état connu reste visible comme s’il était actuel. Ce choix rend la démonstration moins bruyante, mais il masque une information importante.

```jsx
return () => clearInterval(timer);
```

La fonction renvoyée par l’effet est son nettoyage. React l’appelle lorsque le composant disparaît ou avant de recréer l’intervalle.

`clearInterval` empêche les demandes de continuer en arrière-plan et évite d’accumuler plusieurs minuteurs.

La liste `[meeting.id, onChange]` demande de reconstruire l’effet si l’identifiant ou la fonction change.

## 10. Fonction `start` de l’écran de consentement

Si `notice` est faux, la fonction place un message et s’arrête avec `return`.

Sinon elle appelle le backend. Le backend vérifie à nouveau tous les accords et ne fait pas confiance à la seule case React.

En cas de succès, `onChange` remplace la réunion par celle dont le statut vaut `recording`. Le composant parent affiche alors automatiquement `Recorder`.

## 11. Liste des participants

Pour chaque participant, l’interface affiche le nom, le mail et une pastille.

La classe dynamique :

```jsx
`status ${condition ? "completed" : "uploaded"}`
```

ajoute `completed` si l’accord est actif, sinon `uploaded`.

Le texte utilise deux conditions imbriquées :

- si `withdrawn_at` existe : « Retiré » ;
- sinon si `consented_at` existe : « Accepté » ;
- sinon : « En attente ».

Le texte réel est plus important que la couleur pour les personnes qui ne distinguent pas certaines couleurs.

Le bouton dictaphone est désactivé tant que `meeting.all_consented` est faux.

## 12. Les états du composant `Recorder`

### `state`

Le texte peut valoir :

- `idle` : rien n’est en cours ;
- `recording` : capture active ;
- `paused` : capture suspendue ;
- `ready` : fichier prêt à écouter et envoyer ;
- `uploading` : transfert en cours.

Utiliser un seul état textuel évite plusieurs booléens contradictoires comme `isRecording=true` et `isPaused=true` par accident.

### `seconds`

Nombre de secondes affichées.

Il mesure le temps durant lequel l’état vaut `recording`. Il ne vient pas de l’horloge du fichier audio; des retards du navigateur peuvent rendre ce compteur légèrement imprécis.

### `audioBlob`

Objet binaire final en mémoire. Il sera envoyé.

### `audioUrl`

Adresse temporaire locale permettant de lire le Blob.

### `error`

Message visible.

## 13. Pourquoi utiliser `useRef`

```jsx
const recorder = useRef(null);
const stream = useRef(null);
const chunks = useRef([]);
const consentRevoked = useRef(false);
```

Chaque référence est un objet dont la valeur modifiable se trouve dans `.current`.

`recorder.current` contient le `MediaRecorder`.

`stream.current` contient le flux du microphone.

`chunks.current` contient les fragments audio.

`consentRevoked.current` mémorise si l’arrêt vient d’un retrait.

Ces valeurs doivent survivre aux nouveaux affichages, mais les modifier ne doit pas forcément réafficher la page. C’est le rôle de `useRef`.

Si `chunks` était une variable locale simple, elle serait recréée lors de chaque réexécution du composant et les fragments pourraient être perdus.

## 14. Effet de minuterie

Si l’état n’est pas `recording`, l’effet renvoie `undefined`. Cela signifie qu’il n’installe rien.

Sinon, un intervalle ajoute 1 à la valeur toutes les secondes :

```jsx
setSeconds((value) => value + 1)
```

La forme fonctionnelle reçoit la valeur la plus récente. Elle évite qu’un intervalle conserve une ancienne valeur.

Le nettoyage supprime l’intervalle.

La liste `[state]` relance la logique lorsque l’état change. Pendant une pause, l’intervalle est supprimé et le compteur cesse d’avancer.

## 15. Effet de surveillance du consentement

Il fonctionne seulement pendant `recording` ou `paused`.

```jsx
['recording', 'paused'].includes(state)
```

Une liste de deux textes est créée, puis `.includes` vérifie si elle contient l’état actuel.

La fonction `verify` recharge la réunion.

Si l’état serveur n’est plus `recording` ou si tous les consentements ne sont plus actifs :

1. `consentRevoked.current = true` mémorise la cause ;
2. le MediaRecorder est arrêté s’il n’est pas déjà inactif ;
3. le Blob actuel est effacé ;
4. l’ancienne URL locale est libérée ;
5. un message est affiché.

### Le symbole `?.`

`recorder.current?.state` utilise le chaînage optionnel. Si `recorder.current` vaut `null`, JavaScript n’essaie pas de lire `.state`.

Cela évite une erreur pendant les instants où le recorder n’existe pas encore.

### Libération de l’URL

`URL.revokeObjectURL(currentUrl)` informe le navigateur que l’adresse temporaire ne sera plus utilisée. Sans cette libération, la mémoire associée peut rester réservée.

### Limite critique du `.catch(() => {})`

Comme l’échec réseau est ignoré, le navigateur continue localement si le serveur devient inaccessible.

Il ne peut donc pas savoir qu’un participant a retiré son accord pendant cette panne.

Pour une protection plus forte, une erreur répétée devrait provoquer un arrêt par précaution et afficher « impossible de vérifier les consentements ».

Le délai normal peut aussi atteindre presque trois secondes entre le retrait et la prochaine vérification.

## 16. Effet de nettoyage général

```jsx
useEffect(() => () => {
```

Cette écriture compacte signifie : l’effet ne fait rien à l’installation, mais renvoie immédiatement une fonction de nettoyage.

```jsx
stream.current?.getTracks().forEach((track) => track.stop());
```

`getTracks()` renvoie les pistes du flux. `forEach` appelle `stop` sur chacune.

Arrêter les pistes libère réellement le microphone et fait disparaître l’indicateur d’utilisation du navigateur.

Si `audioUrl` existe, elle est également révoquée.

La dépendance `[audioUrl]` a une conséquence subtile : à chaque changement d’URL, React exécute le nettoyage de l’effet précédent. Cela peut arrêter le flux au moment où l’URL change, ce qui est souhaitable après l’arrêt, mais cette structure mélange le nettoyage du composant et le changement d’URL. Deux effets séparés seraient plus explicites.

## 17. Fonction `start`

### Préparation

Elle efface l’erreur et place `consentRevoked.current` à faux.

### Demande du microphone

```jsx
stream.current = await navigator.mediaDevices.getUserMedia({ audio: true });
```

`navigator` représente des capacités du navigateur.

`mediaDevices` regroupe les appareils audio et vidéo.

`getUserMedia({ audio: true })` demande un flux audio. Le navigateur affiche normalement une demande de permission.

Cette API fonctionne généralement uniquement dans un contexte sécurisé : HTTPS ou `localhost`.

L’utilisateur peut refuser, aucun micro peut être présent, ou le système peut bloquer l’accès. Le `catch` affiche alors un message.

### Remise à zéro des fragments

`chunks.current = []` crée une nouvelle liste vide pour ne pas mélanger un ancien enregistrement.

### Création du MediaRecorder

`new MediaRecorder(stream.current)` appelle le constructeur.

Un constructeur est une fonction spéciale utilisée avec `new` pour créer une instance. L’instance concrète est stockée dans `recorder.current`.

Le navigateur choisit ici son format par défaut. Le code ne vérifie pas avant de commencer que ce type correspond exactement à une entrée autorisée par le backend. Sur la plupart des navigateurs visés, WebM est courant, mais Safari peut produire un autre format.

## 18. Événement `ondataavailable`

Le code affecte une fonction à la propriété appelée lorsque MediaRecorder fournit un fragment.

`event.data` est le Blob du fragment.

`event.data.size` est sa taille en octets.

Si la taille est non nulle, `push` ajoute le fragment à la fin de la liste.

Le paramètre `timeslice` n’est pas donné à `start()`. Le navigateur peut donc fournir surtout un fragment final lors de l’arrêt, selon son implémentation.

## 19. Événement `onstop`

Cette fonction se déclenche après l’arrêt réel du MediaRecorder.

### Cas retrait du consentement

Si `consentRevoked.current` est vrai :

- les fragments sont effacés ;
- le Blob est effacé ;
- l’état revient à `idle`;
- chaque piste du micro est arrêtée ;
- `return` empêche de fabriquer un fichier.

Cette décision respecte le principe de ne pas conserver un audio après retrait.

Le compteur `seconds` n’est pas remis à zéro dans ce chemin. L’écran `idle` peut donc encore afficher l’ancienne durée jusqu’au prochain démarrage, qui remet le compteur à zéro.

### Cas arrêt normal

```jsx
const blob = new Blob(chunks.current, { type: recorder.current.mimeType || "audio/webm" });
```

`new Blob` rassemble les fragments.

L’option `type` utilise le type déclaré par le MediaRecorder ou `audio/webm` en secours.

Le Blob est placé dans l’état.

`URL.createObjectURL(blob)` crée une URL locale comme `blob:http://localhost/...`. Elle n’est pas une adresse publique ni un upload. Elle pointe vers la mémoire du navigateur actuel.

L’état devient `ready` et les pistes s’arrêtent.

## 20. Démarrage effectif

`recorder.current.start()` commence la capture.

`setSeconds(0)` remet le compteur à zéro.

`setState("recording")` met à jour l’interface et lance les deux intervalles.

L’ordre signifie que la capture commence juste avant que l’état visuel soit mis à jour.

Le bloc `catch` ne distingue pas les causes précises. Il affiche le même message pour un refus, une absence d’appareil ou une erreur de création MediaRecorder.

## 21. Fonction `pause`

Si l’état réel de MediaRecorder vaut `recording`, elle appelle `.pause()` puis change l’état React en `paused`.

Sinon, elle appelle `.resume()` si le recorder existe, puis met l’état à `recording`.

Limite : le `else` regroupe tous les autres états, pas seulement `paused`. L’interface n’appelle ce bouton que pendant recording ou paused, mais une vérification explicite rendrait la fonction plus sûre.

La pause ne supprime pas les fragments déjà capturés. Elle suspend l’ajout jusqu’à la reprise.

## 22. Fonction `stop`

Elle vérifie que l’objet existe et que son état réel n’est pas `inactive`.

Puis elle appelle `.stop()`.

L’arrêt n’est pas instantanément suivi de `ready` dans cette fonction. Il déclenche l’événement asynchrone `onstop`, qui construit le Blob puis met l’état à jour.

## 23. Fonction `reset`

Si une URL existe, elle est libérée.

Le Blob et l’URL sont effacés.

Le compteur revient à zéro, l’état à `idle` et l’erreur disparaît.

Cette fonction ne supprime rien du serveur, car à l’état `ready` le fichier n’a pas encore été envoyé.

## 24. Fonction `send`

L’état devient `uploading`, ce qui masque les boutons et affiche l’indicateur de traitement.

L’appel :

```jsx
api.createRecording(meeting.title, audioBlob, true, meeting.id)
```

envoie le titre, le Blob, la confirmation vraie et l’identifiant de réunion.

Après succès, `onCreated(item.id)` informe le parent de l’identifiant. Le parent peut afficher la page de résultat et interroger le statut.

En cas d’échec, le message apparaît et l’état revient à `ready`, ce qui permet de réessayer sans refaire l’enregistrement.

Limite : la fonction ne vérifie pas localement qu’`audioBlob` existe. L’interface ne montre le bouton qu’à l’état `ready`, mais le backend reste responsable.

## 25. Méthode `api.createRecording`

```jsx
const form = new FormData();
```

Le constructeur crée un formulaire capable de contenir un fichier.

`form.set("title", title)` ajoute le titre.

`String(consent)` transforme le booléen en texte `"true"` ou `"false"`, que FastAPI convertira en booléen.

L’identifiant de réunion est ajouté.

```jsx
form.set("audio", audio, `scribe-${Date.now()}.webm`);
```

Cette ligne ajoute le Blob sous le nom de champ `audio`.

Le troisième argument donne un nom au fichier transmis. `Date.now()` donne le nombre de millisecondes écoulées depuis le 1er janvier 1970.

L’extension `.webm` est utilisée même si le MediaRecorder a produit un autre type. Le backend ignore le nom et utilise le type MIME pour choisir sa propre extension, ce qui limite l’effet de cette incohérence.

La demande utilise POST.

Le code ne fixe pas lui-même l’en-tête `Content-Type`. C’est correct : le navigateur doit y ajouter automatiquement la frontière particulière du multipart. La fonction générale `request` reconnaît que le corps est un `FormData` et n’ajoute donc pas `application/json`.

## 26. Affichage du Recorder

L’en-tête annonce que chaque personne devrait dire son nom. Cette consigne aide l’association entre étiquette de locuteur et personne, mais ne garantit pas une attribution automatique parfaite.

La phrase cite Voxtral et Mistral Medium 3.5. L’interface affirme un choix de modèle; le backend et le compte fournisseur doivent réellement accepter ce nom.

La pastille « Consentements actifs » reflète le dernier état connu, actualisé toutes les trois secondes.

### Cercle animé

La chaîne de classe ajoute `live` seulement pendant l’enregistrement. Le CSS lance alors la pulsation.

Le caractère `●` est seulement un symbole visuel.

### Minuterie et texte d’état

`formatTime(seconds)` transforme le nombre.

La chaîne de conditions imbriquées choisit :

- enregistrement ;
- pause ;
- audio prêt ;
- prêt à enregistrer.

Pour `uploading`, elle tombe sur « Prêt à enregistrer », mais la ligne est accompagnée plus bas de « Traitement sécurisé… ». Un libellé spécifique `uploading` serait plus cohérent.

### Boutons conditionnels

À `idle`, seul Démarrer apparaît.

Pendant `recording` ou `paused`, Pause/Reprendre et Arrêter apparaissent.

À `ready`, le lecteur audio, Recommencer et Transcrire apparaissent. Le fragment `<>...</>` regroupe plusieurs éléments sans ajouter de balise HTML.

À `uploading`, un spinner apparaît.

L’erreur reste affichée si elle existe.

## 27. Gestion de la mémoire et du microphone

Trois ressources doivent être libérées :

1. les pistes du microphone, avec `track.stop()` ;
2. les URL de Blob, avec `URL.revokeObjectURL` ;
3. les intervalles, avec `clearInterval`.

Le code traite les trois.

Une fuite de ressources se produit lorsqu’un programme garde inutilement une ressource. Cela peut maintenir le micro actif, utiliser de la mémoire ou continuer à envoyer des demandes.

## 28. Confidentialité réelle du dictaphone

Le Blob reste dans la mémoire du navigateur jusqu’à son envoi, son remplacement ou le départ de la page.

Après l’upload, le backend écrit temporairement le fichier sur son disque local.

Le code de retrait efface les fragments et le Blob lorsqu’il détecte le retrait. Il ne peut pas effacer un enregistrement qu’un logiciel extérieur au navigateur aurait réalisé.

La page ne capture pas la vidéo.

Le navigateur affiche normalement une indication système quand le microphone est utilisé.

## 29. Nombre de lignes et simplicité

Le commit ajoute environ 223 lignes nettes, dont 217 lignes pour le parcours final dans `MeetingWorkflow.jsx` et 11 lignes d’API.

Le cœur du dictaphone est plus petit que l’ensemble du fichier : les autres lignes gèrent le consentement, les participants, les erreurs et l’interface.

Dire « le dictaphone fait 20 lignes » serait trompeur si l’on inclut la sécurité et le parcours complet. Dire « MediaRecorder est utilisé en quelques appels, mais la fonctionnalité sûre exige environ deux cents lignes de parcours » est plus honnête.

KISS signifie ici un seul composant de parcours et les API natives du navigateur, sans bibliothèque d’enregistrement supplémentaire. Il ne signifie pas supprimer les contrôles nécessaires.

## 30. Limites que Yanis doit connaître

- le polling peut prendre jusqu’à trois secondes ;
- les erreurs de vérification du consentement sont ignorées ;
- le type MediaRecorder varie selon le navigateur ;
- le timer mesure des intervalles JavaScript, pas la durée exacte du média ;
- le Blob entier reste en mémoire ;
- aucune limite locale de durée n’est appliquée ;
- le nom envoyé finit toujours par `.webm`;
- `key={index}` n’est pas l’identité la plus stable ;
- le retrait dépend du réseau pour être détecté ;
- l’état du frontend n’est pas une preuve de sécurité; le backend revérifie.

## 31. Réponse orale complète

« J’utilise l’API native `getUserMedia` pour obtenir le flux microphone, puis je crée une instance de `MediaRecorder`. Chaque événement `dataavailable` ajoute un fragment dans une référence React. À l’arrêt normal, `Blob` rassemble ces fragments et `createObjectURL` crée une adresse locale pour le lecteur. À l’arrêt causé par un retrait, les fragments sont vidés et aucun Blob n’est construit. Les valeurs qui changent l’écran utilisent `useState`; les objets techniques mutables utilisent `useRef`; les minuteurs et nettoyages utilisent `useEffect`. Toutes les trois secondes, le navigateur relit les consentements. Je sais que masquer les erreurs réseau est une faiblesse : en production, l’impossibilité de vérifier devrait arrêter l’enregistrement par précaution. »

## 32. Questions pièges

**Le son part-il directement chez Mistral pendant que l’on parle ?**  
Non. Ce code enregistre localement dans le navigateur, fabrique un Blob à l’arrêt, puis l’envoie au backend.

**Qu’est-ce qu’un Blob ?**  
Un objet du navigateur contenant des octets, ici les fragments audio rassemblés, avec un type de contenu.

**Pourquoi `useRef` au lieu de `useState` pour les fragments ?**  
Parce que chaque fragment n’a pas besoin de redessiner l’écran, mais la liste doit survivre aux affichages successifs.

**Pourquoi arrêter les pistes si MediaRecorder est déjà arrêté ?**  
MediaRecorder arrête la fabrication des données; la piste du flux peut encore garder le microphone ouvert. `track.stop()` libère l’appareil.

**Une URL `blob:` est-elle publique ?**  
Non. Elle référence une donnée en mémoire dans le contexte du navigateur actuel.

**Qu’est-ce que le polling ?**  
Une demande répétée à intervalle régulier pour vérifier si l’état du serveur a changé.

**Pourquoi le retrait n’est-il pas instantané ?**  
Le navigateur vérifie toutes les trois secondes et dépend du réseau. Le serveur ne peut pas commander directement un navigateur déconnecté.

**`MediaRecorder` fonctionne-t-il partout pareil ?**  
Non. Les formats et certaines capacités varient selon le navigateur. Il faut tester les navigateurs cibles ou choisir explicitement un type pris en charge.

**Que fait `event.preventDefault()` ?**  
Il empêche le formulaire de recharger la page afin que React garde son état et envoie la demande lui-même.

**Que veut dire `new MediaRecorder(...)` ?**  
`new` appelle le constructeur de la classe et fabrique une instance concrète contrôlant ce flux.

