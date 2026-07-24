# Yanis — React, Vite, HTML et CSS expliqués depuis zéro

Ce chapitre explique les deux commits qui créent l’interface de départ :

- [`ed08945 — chore(web): configure React and Vite`](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb)
- [`6104ac5 — chore(web): add application shell`](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250)

Le navigateur ne comprend pas Python. Il reçoit principalement du HTML pour la structure, du CSS pour l’apparence et du JavaScript pour le comportement. React est une bibliothèque JavaScript qui aide à construire l’interface à partir de composants. Vite est l’outil qui lance cette interface pendant le développement et prépare les fichiers destinés à l’hébergement.

## 1. JavaScript, JSX, React et Vite ne sont pas la même chose

JavaScript est le langage exécuté par le navigateur.

JSX est une écriture qui permet d’insérer une structure ressemblant à du HTML dans un fichier JavaScript. Le navigateur ne comprend pas directement tout le JSX : Vite et le plugin React le transforment.

React est une bibliothèque. Une bibliothèque est du code déjà écrit que notre programme appelle. React compare l’interface souhaitée à l’interface présente et met à jour le navigateur.

Vite est un outil de développement et de construction. Il sert les fichiers localement, transforme le JSX, recharge la page après une modification et fabrique une version optimisée avec `vite build`.

Node.js exécute Vite sur l’ordinateur du développeur. Node n’est pas le langage : le langage reste JavaScript. Node est le programme capable d’exécuter JavaScript en dehors du navigateur.

## 2. Le nom du commit `chore(web): configure React and Vite`

`chore` indique une préparation technique plutôt qu’une fonctionnalité métier complète.

`web` précise la zone concernée : l’interface envoyée au navigateur.

`configure React and Vite` signifie que le commit installe la structure minimale permettant d’afficher un composant React et de faire passer les demandes `/api` au backend local.

## 3. `web/index.html`, ligne par ligne

### `<!doctype html>`

Cette déclaration dit au navigateur d’interpréter le document selon la version moderne de HTML, appelée HTML5.

Les caractères `<! ... >` signalent une déclaration spéciale, pas une balise visible. Sans cette ligne, certains navigateurs peuvent utiliser un ancien mode de compatibilité qui calcule les tailles et la mise en page différemment.

### `<html lang="fr">`

`<html>` ouvre l’élément qui contient toute la page.

`lang="fr"` est un attribut. Un attribut apporte une information à un élément. Ici, il indique que la langue principale est le français.

Cette information aide les lecteurs d’écran, les moteurs de recherche et les outils de correction. Elle ne traduit rien automatiquement.

La balise sera fermée par `</html>` à la fin. Le `/` indique une fermeture.

### `<head>`

`head` contient les renseignements sur la page qui ne constituent pas son contenu principal visible : encodage, description, titre d’onglet et couleurs.

### `<meta charset="UTF-8" />`

`meta` fournit une information sur le document. `charset` signifie « jeu de caractères ».

`UTF-8` est une manière standard de représenter les lettres, accents, symboles et caractères de nombreuses langues sous forme d’octets.

Sans cette indication, des caractères comme `é` peuvent être affichés incorrectement selon le contexte.

La terminaison `/>` ferme immédiatement l’élément, car `meta` n’entoure aucun contenu.

### Ligne `viewport`

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
```

Le viewport est la zone de page visible dans le navigateur.

`width=device-width` demande d’utiliser la largeur réelle de l’écran de l’appareil. `initial-scale=1.0` demande un niveau de zoom initial normal.

Cette ligne est essentielle pour que les règles adaptées aux téléphones s’appliquent correctement. Sans elle, un téléphone pourrait simuler une page beaucoup plus large, puis la réduire.

### Ligne `theme-color`

```html
<meta name="theme-color" content="#132622" />
```

Elle propose au navigateur une couleur associée au site, notamment pour certaines barres d’interface sur mobile.

`#132622` est une couleur écrite en hexadécimal. Les deux premiers chiffres décrivent le rouge, les deux suivants le vert et les deux derniers le bleu, sur une échelle allant de `00` à `ff`.

Cette couleur n’impose pas le fond de la page; le CSS le fait séparément.

### Ligne `description`

Le texte décrit brièvement le service. Un moteur de recherche peut l’utiliser dans son résultat, sans obligation.

Cette description n’est pas visible dans le corps de la page. Elle aide le référencement et le partage.

### `<title>Scribe — Vos échanges, enfin clairs</title>`

Le contenu de `title` apparaît notamment dans l’onglet du navigateur.

Le tiret long `—` est un caractère typographique dans le texte. Il n’a aucun rôle de programmation.

### `</head>` puis `<body>`

`</head>` termine les informations invisibles. `<body>` ouvre le contenu de la page affiché à l’utilisateur.

### `<div id="root"></div>`

`div` est un conteneur générique. Ici il est vide au départ.

`id="root"` lui attribue un identifiant unique. `root` signifie « racine ». Le JavaScript retrouvera ce conteneur et demandera à React d’y insérer toute l’application.

Si l’identifiant était renommé sans modifier `main.jsx`, `document.getElementById("root")` ne trouverait rien et React ne pourrait pas afficher l’application.

### `<script type="module" src="/src/main.jsx"></script>`

`script` charge du JavaScript.

`type="module"` active le système moderne d’imports et d’exports. Chaque fichier peut importer précisément ce dont il a besoin.

`src="/src/main.jsx"` désigne le fichier de départ. Le `/` initial part de la racine servie par Vite.

Le navigateur demande ce fichier à Vite. Vite transforme le JSX et renvoie du JavaScript compréhensible.

### Fermetures `</body>` et `</html>`

Elles terminent respectivement le contenu visible et le document entier.

Une bonne structure imbrique les balises comme des boîtes : la dernière boîte ouverte est la première fermée.

## 4. `web/package.json`, ligne par ligne

JSON est un format texte pour représenter des objets. Un objet JSON est entouré d’accolades `{}`. Chaque propriété associe un nom entre guillemets à une valeur grâce à `:`.

Les virgules séparent les propriétés. La dernière propriété d’un groupe ne prend pas de virgule.

### `"name": "scribe-web"`

Cette propriété donne un nom technique au projet frontend.

Le tiret est autorisé dans ce nom de paquet. Ce nom n’est pas affiché automatiquement comme titre de la page; le titre HTML est indépendant.

### `"private": true`

Cette valeur empêche normalement la publication accidentelle du projet comme paquet public sur le registre npm.

`true` est un booléen JSON, donc une valeur « vraie ». Il n’est pas placé entre guillemets parce que ce n’est pas du texte.

### `"version": "1.0.0"`

La version suit la forme majeure.mineure.corrective.

En théorie, une modification incompatible augmente le premier nombre, une fonctionnalité compatible augmente le deuxième, et une correction augmente le troisième. Ici, la valeur sert surtout de métadonnée du projet.

Elle n’est pas synchronisée automatiquement avec `__version__` du backend.

### `"type": "module"`

Cette ligne indique à Node que les fichiers `.js` du projet utilisent la syntaxe moderne `import` et `export`.

Sans elle, Node pourrait attendre l’ancien système `require` et mal interpréter `vite.config.js`.

### Objet `"scripts"`

Un script npm associe un nom court à une commande.

`"dev": "vite"` signifie que `npm run dev` lance le serveur de développement Vite.

`"build": "vite build"` signifie que `npm run build` fabrique la version destinée au déploiement dans le dossier `dist`.

`"preview": "vite preview"` lance localement un serveur qui montre le résultat déjà construit. Ce n’est pas un serveur de production recommandé.

### Objet `"dependencies"`

Une dépendance est une bibliothèque dont l’application a besoin pour fonctionner.

`react` contient la logique des composants, des états et des effets.

`react-dom` relie React au modèle de document du navigateur, appelé DOM. Le DOM est la représentation en mémoire des éléments HTML.

Le symbole `^` devant `18.3.1` autorise npm à choisir certaines versions plus récentes restant dans la même grande version. Le fichier `package-lock.json` fixe ensuite la version réellement installée.

### Objet `"devDependencies"`

Une dépendance de développement est surtout nécessaire pour construire ou travailler sur le projet, pas pour exécuter directement le JavaScript final dans le navigateur.

`@vitejs/plugin-react` apprend à Vite comment transformer correctement React et JSX.

`vite` est l’outil de serveur local et de construction.

La version `7.3.6` de Vite exige une version récente de Node. L’équipe a rencontré concrètement une erreur avec Node 20.11.1 parce que Vite demandait au minimum une version plus récente. Cela montre qu’un numéro fixé dans le projet a des conséquences sur l’environnement nécessaire.

## 5. Pourquoi `package-lock.json` contient environ 1 800 lignes

Ce fichier est fabriqué par npm. Il décrit exactement l’arbre des bibliothèques installées.

Un « arbre de dépendances » signifie que React dépend de certains paquets, que Vite dépend d’autres paquets, et que ces paquets peuvent eux-mêmes dépendre d’autres éléments. Le lockfile enregistre leurs versions, leurs adresses de téléchargement et des empreintes d’intégrité.

Les lignes typiques ont les rôles suivants :

- `lockfileVersion` indique la version du format du fichier ;
- `packages` ouvre la liste des paquets ;
- `node_modules/...` indique l’emplacement logique d’une bibliothèque ;
- `version` fixe sa version exacte ;
- `resolved` indique d’où npm la télécharge ;
- `integrity` contient une empreinte permettant de détecter un contenu différent de celui attendu ;
- `dependencies` liste les autres paquets nécessaires ;
- `engines` indique les versions de Node acceptées ;
- `optional` signifie que l’installation peut continuer sans ce paquet dans certains environnements ;
- `dev` signale un paquet utilisé pour le développement.

Il serait faux de prétendre que Yanis a écrit manuellement les 1 800 lignes. Il a choisi les dépendances directes dans `package.json`, puis npm a résolu et verrouillé tout le reste.

Si le professeur pointe une ligne d’un paquet inconnu, la bonne réponse est :

« Cette entrée a été générée par npm pour une dépendance directe ou indirecte. Je peux expliquer sa structure : voici la version exacte, la source, l’empreinte et ses propres dépendances. Nous conservons ce fichier afin que l’installation soit reproductible. Je ne prétends pas avoir développé cette bibliothèque. »

Le fichier doit être commité parce que deux ordinateurs utilisant le même `package.json` pourraient autrement sélectionner des versions secondaires différentes.

## 6. `web/src/main.jsx`, ligne par ligne

### `import React from "react";`

`import` rend une valeur d’un autre module disponible.

`React` est le nom local donné à l’export principal du paquet `react`.

Dans ce fichier, ce nom est aussi nécessaire pour écrire `React.StrictMode`. Les guillemets autour de `"react"` indiquent le nom du paquet installé, pas un chemin de fichier local.

### `import ReactDOM from "react-dom/client";`

Cette ligne importe l’interface moderne de React pour créer une racine dans le navigateur.

`ReactDOM` est le nom local. Le chemin `react-dom/client` choisit précisément les fonctions côté navigateur.

### `import App from "./App.jsx";`

Le point `.` signifie « depuis le dossier actuel ». Cette ligne récupère l’export par défaut du fichier `App.jsx` et le nomme `App`.

Une majuscule est utilisée parce qu’en JSX un nom commençant par une majuscule représente un composant React. Un nom minuscule comme `<main>` représente un élément HTML.

### `import "./index.css";`

Cette importation ne place pas une valeur dans une variable. Elle demande à Vite d’inclure les styles du fichier.

Lorsque l’application est chargée, ces règles CSS sont appliquées au document.

### `ReactDOM.createRoot(document.getElementById("root")).render(`

Cette ligne enchaîne plusieurs actions :

1. `document` représente la page dans le navigateur ;
2. `.getElementById("root")` cherche l’élément dont l’identifiant est `root` ;
3. `ReactDOM.createRoot(...)` confie cet élément à React ;
4. `.render(...)` demande d’y afficher le contenu donné entre les parenthèses.

Les points permettent d’appeler une capacité appartenant à l’objet placé à gauche.

### `<React.StrictMode>`

`StrictMode` est un outil de développement. Il aide React à révéler certains comportements risqués. En développement, React peut volontairement répéter certains appels pour faire apparaître un effet mal nettoyé.

Il ne s’agit pas d’un mode de sécurité réseau. Il ne protège ni les mots de passe ni l’API.

### `<App />`

Cette ligne demande à React d’utiliser le composant `App`.

La barre avant `>` ferme immédiatement la balise parce qu’aucun contenu enfant n’est écrit entre une ouverture et une fermeture séparées.

React appelle la fonction `App` et utilise le JSX qu’elle renvoie.

### Fermeture de `StrictMode`, `);`

`</React.StrictMode>` ferme le composant conteneur.

La parenthèse `)` ferme l’appel à `render`. Le point-virgule termine l’instruction JavaScript. JavaScript peut parfois l’ajouter implicitement, mais l’écrire rend la fin explicite.

## 7. `web/vite.config.js`, ligne par ligne

### Imports

`defineConfig` est une fonction d’aide de Vite. Elle ne change pas fondamentalement l’objet, mais améliore la compréhension des réglages par l’éditeur.

`react` est une fonction fournie par le plugin React.

### Commentaire du proxy

Le commentaire explique que les appels dont l’adresse commence par `/api` seront transmis au backend sur le port 8000.

Un proxy est un intermédiaire. Le navigateur croit appeler le même serveur que le frontend, puis Vite transfère la demande à FastAPI.

### `export default defineConfig({`

`export default` rend cette configuration disponible comme export principal du fichier.

`defineConfig({` appelle la fonction avec un objet JavaScript. L’accolade ouvre l’objet.

### `plugins: [react()],`

`plugins` est une propriété contenant une liste. `react()` crée la configuration du plugin React.

Sans ce plugin, la transformation du JSX et certaines fonctions de rechargement React ne seraient pas correctement configurées.

### Objet `server`

`port: 5174` demande à Vite d’écouter sur la porte 5174.

`strictPort: true` lui interdit de choisir silencieusement un autre port si 5174 est occupé. Cette décision est utile parce que le backend autorise précisément `http://localhost:5174`.

Sans `strictPort`, Vite pourrait démarrer sur 5175 tandis que CORS et les liens continueraient d’attendre 5174.

### `proxy: { "/api": "http://localhost:8000" },`

La clé `"/api"` correspond au début des chemins à transférer. La valeur est l’adresse du backend.

Ainsi, le frontend peut demander `/api/health` sans écrire l’adresse complète. En développement, Vite transmet à `http://localhost:8000/api/health`.

Ce proxy existe uniquement pendant le développement Vite. Après un déploiement, l’hébergeur doit prévoir une règle équivalente ou le frontend doit connaître l’URL publique de l’API.

### Accolades finales

La première ferme l’objet `server`. La suivante ferme l’objet général. `);` ferme l’appel et termine l’instruction.

## 8. Le composant `App.jsx` du commit suivant

```jsx
export default function App() {
```

`function` définit une fonction nommée `App`. Elle ne reçoit aucun paramètre dans cette version.

`export default` permet à `main.jsx` de l’importer sans accolades.

L’accolade ouvre le corps de la fonction.

```jsx
return <main className="public-page"><section className="content-card public-card">
```

`return` donne à React la structure à afficher.

`main` est un élément HTML sémantique représentant le contenu principal de la page. `section` regroupe un contenu cohérent.

En JSX, on écrit `className` au lieu de `class`, car `class` est déjà un mot du langage JavaScript. La valeur `"content-card public-card"` applique deux classes CSS au même élément.

Le code est compressé sur peu de lignes. Il fonctionne, mais il est moins facile à relire ou à commenter ligne par ligne qu’une balise par ligne. « Moins de lignes » n’est pas toujours synonyme de KISS : KISS demande surtout la simplicité de compréhension.

```jsx
<div className="brand"><span className="brand-mark">S</span><span>Scribe</span></div>
```

`div` regroupe le logo textuel.

Le premier `span` est un petit conteneur en ligne affichant la lettre `S` avec la classe visuelle `brand-mark`. Le second affiche le nom.

Les balises sont imbriquées et refermées dans l’ordre inverse de leur ouverture.

```jsx
<h1>Votre réunion devient claire.</h1>
```

`h1` est le titre principal. Une page devrait normalement avoir un titre principal clair, utile pour la structure et l’accessibilité.

```jsx
<p>Le MVP est en cours de construction.</p>
```

`p` représente un paragraphe. MVP signifie « produit minimum viable », une version contenant le minimum nécessaire pour vérifier que l’idée fonctionne.

```jsx
</section></main>;
}
```

Les deux balises ferment les conteneurs. Le point-virgule termine le `return`. L’accolade ferme la fonction.

## 9. Comment lire chaque règle CSS

Une règle CSS suit cette forme :

```css
sélecteur { propriété: valeur; propriété: valeur; }
```

Le sélecteur choisit les éléments concernés. Les accolades entourent les instructions. Une propriété indique ce qui est modifié. Les deux-points séparent la propriété de sa valeur. Le point-virgule sépare les déclarations.

Dans ce fichier, plusieurs propriétés sont placées sur la même ligne. Cela réduit le nombre de lignes physiques, mais pas la quantité de règles à comprendre.

## 10. Import des polices

```css
@import url('https://fonts.googleapis.com/...');
```

`@import` demande au navigateur de télécharger une autre feuille de styles. L’adresse Google fournit DM Sans et Manrope avec plusieurs épaisseurs.

Conséquence visuelle : le texte utilise ces polices si le téléchargement réussit.

Conséquence réseau et RGPD : le navigateur du visiteur contacte un domaine Google et lui transmet au minimum des informations techniques comme l’adresse IP. Pour une maîtrise plus stricte, les fichiers de police devraient être hébergés par Scribe ou remplacés par des polices déjà présentes sur l’appareil.

Si le téléchargement échoue, les valeurs de secours `sans-serif` permettent quand même d’afficher le texte.

## 11. Variables globales `:root`

`:root` sélectionne la racine du document.

`font-family:"DM Sans",sans-serif` choisit DM Sans puis une police générique sans empattement en secours.

`color:#172022` fixe la couleur de texte par défaut. `background:#f4f6f2` fixe le fond.

`font-synthesis:none` demande au navigateur de ne pas inventer artificiellement une graisse ou un style absent.

Les propriétés commençant par `--`, comme `--green`, sont des variables CSS. Une autre règle peut écrire `var(--green)` au lieu de répéter la couleur.

Cela applique DRY : changer une couleur centrale peut modifier plusieurs composants. DRY signifie éviter de répéter une même information qui devrait n’avoir qu’une seule source.

`--ink` représente le texte foncé; `--muted` un texte secondaire; `--line` les bordures; `--panel` un fond de carte; `--green` et `--green-dark` les couleurs d’action; `--mint` et `--cream` des fonds doux; `--danger` les actions risquées.

## 12. Règles de base

`* { box-sizing:border-box; }` sélectionne tous les éléments. `border-box` demande que la largeur annoncée inclue le contenu, le remplissage et la bordure. Cela rend les tailles plus prévisibles.

`body` retire la marge automatique, garantit au moins 320 pixels de largeur et la hauteur de l’écran. `100vh` signifie 100 % de la hauteur visible. Le fond combine un dégradé radial et une couleur.

`button,input { font:inherit; }` demande aux boutons et champs de reprendre la police de leur parent au lieu d’une police automatique du navigateur.

`button,a` retire la coloration de toucher propre à certains navigateurs WebKit. Cela change l’apparence, mais il faut conserver un autre retour visuel clair lors du clic et du focus.

`.icon { flex:0 0 auto; }` empêche une icône de grandir ou rétrécir dans une disposition flexible.

## 13. Structure générale

`.app-shell` crée une grille de deux colonnes : une barre latérale de 260 pixels et le reste de l’espace pour le contenu.

`.sidebar` prend toute la hauteur, utilise un fond sombre et organise ses enfants verticalement. `position:sticky`, `top:0` et `height:100vh` la maintiennent visible pendant le défilement.

`.brand` aligne le symbole et le nom horizontalement. `gap` crée l’espace entre eux. La notation raccourcie `font:800 21px "Manrope"` choisit la graisse 800, la taille 21 pixels et la police.

`.brand-mark` construit le carré arrondi du S. `display:grid` et `place-items:center` centrent la lettre dans les deux directions. `box-shadow:inset` dessine une ombre à l’intérieur.

## 14. Navigation et profil

`.nav-list` aligne les boutons verticalement avec un espace et une marge supérieure.

`.nav-button` retire la bordure et le fond natifs, définit les couleurs, l’alignement, le remplissage et le pointeur de souris. `transition:.2s` anime les changements de propriétés compatibles pendant deux dixièmes de seconde.

`.nav-button:hover` s’applique lorsque la souris survole le bouton. `.nav-button.active` s’applique lorsque JavaScript ajoute la classe `active`. La virgule signifie que les deux sélecteurs partagent les mêmes règles.

La règle active ajoute aussi une petite barre verte intérieure avec `box-shadow`.

`.profile-card` utilise `margin-top:auto` pour pousser la carte vers le bas de la colonne.

`.avatar` crée un cercle de 36 pixels. `border-radius:50%` transforme le carré en cercle.

`.profile-copy` organise le nom et le mail verticalement. `min-width:0` est important dans un conteneur flexible : il permet au contenu de rétrécir.

Les règles `overflow:hidden`, `text-overflow:ellipsis` et `white-space:nowrap` coupent un texte trop long et affichent des points de suspension.

`.icon-button` crée un bouton carré sans fond. Le survol ajoute un fond légèrement blanc grâce à une couleur hexadécimale avec transparence.

## 15. Contenu, titres et animation

`.main-content` limite la largeur à 1180 pixels, centre le bloc et ajoute de l’espace intérieur.

`.page { animation:enter .35s ease both; }` lance l’animation `enter` pendant 0,35 seconde. `ease` rend le mouvement progressif. `both` conserve les états utiles avant et après.

`@keyframes enter` définit l’état de départ : invisible et décalé de 7 pixels vers le bas. L’état final non écrit reprend les valeurs normales.

`.page-header` place le titre et l’élément de droite sur la même ligne, séparés au maximum. `align-items:flex-start` les aligne par leur haut.

Le symbole `>` dans `.page-header>div` choisit uniquement un `div` enfant direct.

Les règles des `h1` utilisent `clamp(30px,4vw,45px)`. `clamp` choisit une taille qui varie avec l’écran, sans descendre sous 30 ni dépasser 45 pixels.

`var(--ink)` lit la variable définie dans `:root`.

`.eyebrow,.card-label` met les petits labels en vert, majuscules et espacés. `text-transform:uppercase` modifie seulement l’affichage, pas le texte d’origine dans le HTML.

`.secure-badge` crée une pastille. `border-radius:999px` garantit des extrémités très arrondies.

## 16. Zone dictaphone

`.recorder-grid` crée deux colonnes dont la première est environ deux fois plus large. `minmax` autorise une largeur minimale et une croissance.

La règle partagée des cartes leur donne fond blanc, bordure, arrondis et ombre. Cela évite de répéter ces propriétés.

`.recorder-card` organise son contenu verticalement et le centre. `min-height:530px` garantit une présence visuelle même avec peu de contenu.

`.title-label` organise le libellé et son champ. Les règles du champ définissent bordure, fond, couleur et transition.

`:focus` s’applique lorsque le champ reçoit le clavier. La bordure verte et l’anneau d’ombre indiquent visuellement où l’utilisateur écrit.

`.orb` dessine le grand cercle du microphone avec un dégradé radial. `.orb.live` ajoute l’animation `pulse` lorsque React place la classe `live`.

`@keyframes pulse` agrandit une ombre au milieu de l’animation, créant une impression de pulsation.

`.orb-inner` dessine le cercle vert intérieur. `.timer` donne au compteur une police forte. `.recorder-status` colore le texte d’état.

Les classes de boutons partagent leurs dimensions, centrage, graisse et animation. Les boutons principaux sont verts; le bouton d’arrêt est rouge; le bouton secondaire est gris.

`:hover` change le fond et déplace le bouton d’un pixel. `:disabled` réduit l’opacité et affiche un curseur d’attente.

`.control-row` autorise le retour à la ligne des boutons si l’écran est étroit.

`.audio-player` limite la largeur du lecteur audio natif.

`.spinner` et `.large-spinner` créent un cercle dont une portion de bordure est verte. L’animation `spin` le fait tourner sans fin.

## 17. Étapes, consentement et alertes

`.steps-card` donne un fond crème à la carte d’explication.

`.step` aligne le numéro et le texte. `.step>span` choisit le numéro enfant direct. `.step strong` transforme le titre en bloc.

`.consent` construit un encadré cliquable. Le champ de 18 pixels utilise `accent-color` pour colorer la case native.

Les descendants `span`, `strong` et `small` reçoivent une organisation et des tailles adaptées.

`.alert` définit le socle d’un message. `.alert.error` ajoute les couleurs d’erreur. Plus tard, `.alert.success` apporte les couleurs de succès.

Ces couleurs ne doivent pas être le seul moyen de comprendre l’état : le texte doit également dire « erreur » ou expliquer ce qui s’est passé, notamment pour l’accessibilité.

## 18. Écran d’authentification

`.auth-layout` crée deux colonnes occupant toute la hauteur.

`.auth-story` est le panneau sombre. `position:relative` permet de placer son cercle décoratif relativement à ce panneau. `overflow:hidden` coupe ce qui dépasse.

`.auth-story:after` crée un pseudo-élément décoratif vide. Un pseudo-élément est une forme CSS qui n’exige pas d’ajouter un élément HTML. Sa position négative le fait dépasser du coin avant d’être coupé.

`.story-copy` limite la largeur et place le texte au-dessus du décor avec `z-index:1`.

Les titres utilisent une taille responsive et une hauteur de ligne réduite. Les paragraphes utilisent un gris clair et un espacement confortable.

`.feature-row` organise les avantages. `.auth-panel` centre la carte du formulaire. `.auth-card` garde au maximum 430 pixels tout en restant adaptable.

`.google-button` occupe toute la largeur et reprend un aspect clair bordé.

`.separator` place un texte entre deux lignes. `:before` et `:after` créent les lignes vides de chaque côté.

`.auth-form` organise les champs verticalement. `.field` organise le libellé, le champ et l’aide. Les boutons texte n’ont pas de fond.

## 19. Historique et compte rendu

`.recording-list` empile les enregistrements.

`.recording-row` donne à chaque ligne l’apparence d’une carte cliquable. Le survol la soulève légèrement.

`.file-icon` crée le carré de l’icône. `.recording-copy { flex:1; }` lui donne l’espace restant. `.arrow` stylise la flèche.

`.status` crée une pastille d’état. Les variantes `.completed`, `.processing`, `.uploaded` et `.failed` associent un état métier à une couleur.

`.empty-card` et `.processing-card` centrent les écrans vides ou en cours.

`.result-header` place le titre et l’action de suppression. `.danger` utilise le rouge pour signaler un acte risqué.

`.result-grid` crée deux colonnes. Les cartes résumé, transcription et thèmes utilisent `grid-column:1/-1`, donc toute la largeur de la première à la dernière ligne de grille.

`white-space:pre-wrap` conserve les retours à la ligne tout en permettant au texte de revenir à la ligne selon la largeur.

Les listes retirent les puces natives puis créent des lignes séparées par une bordure.

## 20. Confidentialité, participants et consentement public

`.privacy-grid` crée deux colonnes de cartes consacrées à la confidentialité.

`.meeting-form,.consent-dashboard` limite la largeur et ajoute du remplissage.

`.participant-heading` et `.consent-row` partagent un alignement horizontal avec espace entre les extrémités.

`.participant-fields` crée trois colonnes : nom, courriel et bouton de suppression.

`.legal-check` aligne une case et le texte juridique en haut. L’utilisateur doit pouvoir lire le texte avant de cocher; le CSS ne garantit pas à lui seul que le consentement est libre, spécifique et éclairé.

`.public-page` centre la carte de consentement public sur tout l’écran. `.public-card` limite sa largeur.

`.notice-list` rend la liste plus lisible. `.privacy-actions` aligne les actions en autorisant un retour à la ligne.

## 21. Les deux blocs `@media`

Une media query applique des règles seulement lorsque l’écran remplit une condition.

### `@media (max-width:900px)`

Lorsque la largeur ne dépasse pas 900 pixels :

- la grille principale devient un bloc ;
- la barre latérale devient une barre horizontale non collante ;
- le texte de marque et les détails du profil sont cachés ;
- la navigation passe en ligne ;
- la taille de police des boutons devient zéro pour ne garder que les icônes ;
- les grilles du dictaphone, des résultats et de la confidentialité passent à une colonne ;
- l’authentification passe à une colonne ;
- les espacements et tailles sont réduits.

`last-child` choisit le dernier enfant. Ici, il masque le nom à côté du symbole. `display:none` retire l’élément de la mise en page et des technologies d’assistance, donc il doit être utilisé avec attention.

### `@media (max-width:560px)`

Sur un téléphone plus étroit :

- les marges diminuent ;
- l’en-tête passe en colonne ;
- les cartes sont moins arrondies ;
- la pastille d’état de l’historique est cachée pour gagner de la place ;
- certains avantages visuels sont masqués ;
- les champs participant sont réorganisés ;
- le champ courriel prend toute la ligne suivante.

`input[type="email"]` sélectionne uniquement un champ dont l’attribut `type` vaut `email`.

Les propriétés `grid-column` et `grid-row` imposent sa nouvelle position dans la grille.

## 22. Ce qui est réussi et ce qui doit être reconnu honnêtement

Le frontend a une palette centralisée, une mise en page responsive, des états visuels cohérents et des classes réutilisables. React et Vite restent un choix simple pour une interface interactive.

Cependant :

- le CSS est extrêmement compact, ce qui réduit les lignes mais pas la complexité ;
- plusieurs classes ont été préparées avant l’arrivée des composants correspondants ;
- les polices chargées depuis Google produisent un appel externe du navigateur ;
- aucune règle CSS ne garantit à elle seule l’accessibilité ;
- le proxy Vite est uniquement une solution de développement ;
- le lockfile est généré, pas écrit à la main ;
- la version de Vite impose une version suffisamment récente de Node.

Reconnaître ces limites est une preuve de compréhension, pas un échec.

## 23. Réponse orale complète

« Le navigateur charge d’abord `index.html`. Le `div` nommé `root` est le point d’insertion. `main.jsx` le récupère, crée une racine React et affiche le composant `App`. Le JSX ressemble à du HTML mais reste une écriture JavaScript transformée par Vite et son plugin React. `package.json` contient nos dépendances directes et nos commandes; `package-lock.json`, généré par npm, verrouille l’arbre complet. En développement, Vite écoute sur 5174 et transmet `/api` à FastAPI sur 8000. Le CSS définit les variables de couleur, les composants visuels et deux adaptations mobiles. Sa limite principale est sa compression et le chargement de polices Google, que je remplacerais par des polices hébergées par nous pour mieux maîtriser les données réseau. »

## 24. Questions que le professeur peut poser

**React est-il un langage ?**  
Non. Le langage est JavaScript. React est une bibliothèque JavaScript.

**JSX est-il du HTML ?**  
Il ressemble au HTML mais il est écrit dans JavaScript et transformé avant d’être exécuté.

**Vite est-il le serveur backend ?**  
Non. Pendant le développement, Vite sert le frontend et transmet certaines demandes. Le backend métier reste FastAPI.

**Pourquoi `className` et pas `class` ?**  
Parce que le JSX utilise la propriété JavaScript `className`, tandis que `class` est un mot du langage.

**Pourquoi le port 5174 ?**  
C’est une porte réseau choisie pour le frontend. Elle doit correspondre aux adresses CORS et aux liens locaux.

**Une autre personne peut-elle ouvrir mon `localhost:5174` ?**  
Pas simplement avec ce lien. Chez elle, `localhost` désigne sa propre machine. Il faudrait exposer le serveur sur le réseau, autoriser le pare-feu et utiliser l’adresse de la machine, ou déployer l’application.

**Le CSS est-il du code ?**  
Oui, c’est un langage déclaratif : on décrit l’apparence souhaitée plutôt qu’une suite d’actions.

**Pourquoi ne pas retirer `package-lock.json` ?**  
Parce qu’il fixe les versions exactes et l’intégrité de l’arbre installé, ce qui rend les installations plus reproductibles.

