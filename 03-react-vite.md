# Commit 3 — `ed08945` — outillage React et Vite

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/ed08945d27613f7d2942baf3e482465483e338bb)

Message : `chore(web): add frontend tooling`.

## `web/index.html` — 14 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/index.html#L1-L14)

| Ligne | Code | Explication exacte |
|---|---|---|
| 1 | `<!doctype html>` | Déclare HTML5 et évite le mode de compatibilité historique. |
| 2 | `<html lang="fr">` | Élément racine ; `lang` aide lecteurs d’écran et correcteurs. |
| 3 | `<head>` | Ouvre la zone de métadonnées. |
| 4 | `<meta charset="UTF-8" />` | Définit Unicode ; permet les accents. Balise autofermée en style JSX/XML, acceptée ici. |
| 5 | meta viewport | Demande une largeur égale à l’écran et un zoom initial 1. |
| 6 | meta theme-color | Suggère une couleur à l’interface du navigateur mobile. |
| 7 | meta description | Texte descriptif de l’application. |
| 8 | `<title>` | Titre de l’onglet et des favoris. |
| 9 | `</head>` | Ferme les métadonnées. |
| 10 | `<body>` | Ouvre le contenu visible. |
| 11 | `<div id="root"></div>` | Conteneur vide ciblé par ReactDOM. `id` doit être unique. |
| 12 | script module | Charge `/src/main.jsx`. `type="module"` autorise imports et différé implicite. |
| 13 | `</body>` | Ferme le corps. |
| 14 | `</html>` | Ferme le document. |

## `web/package.json` — 19 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/package.json#L1-L19)

| Lignes | Code | Explication |
|---|---|---|
| 1 | `{` | Ouvre un objet JSON. JSON exige guillemets doubles et interdit commentaires. |
| 2 | `"name": "scribe-web"` | Nom npm interne. |
| 3 | `"private": true` | Empêche une publication npm accidentelle. |
| 4 | `"version": "1.0.0"` | Version sémantique déclarée. |
| 5 | `"type": "module"` | Les `.js` utilisent ESM `import/export`. |
| 6 | `"scripts": {` | Ouvre le dictionnaire des commandes npm. |
| 7 | `"dev": "vite"` | `npm run dev` exécute le binaire Vite local. |
| 8 | `"build": "vite build"` | Produit les assets optimisés dans `dist`. |
| 9 | `"preview": "vite preview"` | Sert localement le build pour vérification, pas production. |
| 10 | `},` | Ferme scripts ; virgule car une propriété suit. |
| 11 | `"dependencies": {` | Paquets nécessaires au code applicatif. |
| 12 | React avec caret | `^18.3.1` accepte des versions compatibles avant la prochaine majeure. |
| 13 | ReactDOM | Pont React vers le DOM navigateur. |
| 14 | `},` | Ferme les dépendances runtime. |
| 15 | `"devDependencies": {` | Outils utilisés pour développer/construire. |
| 16 | plugin React | Transformation JSX et Fast Refresh. |
| 17 | Vite | serveur et bundler. |
| 18 | `}` | Ferme devDependencies. |
| 19 | `}` | Ferme l’objet racine. |

## `web/package-lock.json` — fichier généré

Le fichier est produit par npm. Les premières lignes :

| Champ | Explication |
|---|---|
| `{` | objet JSON racine |
| `name` | recopie le paquet |
| `version` | recopie la version |
| `lockfileVersion: 3` | format moderne du lockfile npm |
| `requires: true` | indique la présence de dépendances |
| `packages` | dictionnaire de tous les paquets résolus |
| clé `""` | paquet racine du projet |
| `node_modules/...` | chemin logique d’un paquet installé |
| `version` | version exacte sélectionnée |
| `resolved` | URL de l’archive npm |
| `integrity` | empreinte cryptographique vérifiant le téléchargement |
| `dev: true` | paquet de développement |
| `license` | licence déclarée |
| `dependencies` | dépendances indirectes de ce paquet |
| `peerDependencies` | paquets attendus chez le consommateur |
| `engines.node` | versions Node supportées |
| `optional` | dépendance non indispensable selon plateforme |
| `funding` | information de financement |

Chaque bloc `node_modules/...` répète ce schéma. Yanis n’a pas inventé :

- les URLs ;
- les empreintes d’intégrité ;
- les versions indirectes ;
- les licences ;
- les contraintes des paquets.

Pourquoi le commiter :

- deux machines résolvent les mêmes versions ;
- `npm ci` peut reproduire exactement ;
- les outils de sécurité inspectent l’arbre.

Pourquoi ne pas le modifier manuellement :

- risque de contradiction avec `package.json` ;
- empreinte incorrecte ;
- npm le régénère.

Pourquoi le diff compte 1 802 lignes :

- React et Vite dépendent de Babel et de nombreux utilitaires ;
- une dépendance directe produit un arbre transitif.

Point constaté : Vite 7 exige une version Node plus récente que Node 20.11. Le lockfile contenait les
contraintes, mais `start.ps1` ne les vérifiait pas.

## `web/src/main.jsx` — 10 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/src/main.jsx#L1-L10)

| Ligne | Code | Explication exacte |
|---|---|---|
| 1 | `import React from "react";` | Import par défaut. Sert ici à `React.StrictMode`. |
| 2 | import ReactDOM client | Import par défaut du module moderne racine. |
| 3 | import `App` | Import par défaut d’un fichier local. Extension explicite. |
| 4 | import CSS | Import avec effet de bord ; Vite inclut les styles. |
| 5 | vide | Séparation imports/exécution. |
| 6 | `ReactDOM.createRoot(...).render(` | Cherche le DOM `root`, crée la racine, commence le rendu. Si l’élément manque, erreur. |
| 7 | `<React.StrictMode>` | Composant de vérification développement. |
| 8 | `<App />` | Instancie le composant racine sans props. |
| 9 | `</React.StrictMode>` | Ferme l’imbrication. |
| 10 | `);` | Ferme `render` et termine l’instruction. |

`StrictMode` peut réexécuter certains effets en développement afin de révéler un nettoyage manquant.
Il ne double pas l’interface de production.

## `web/vite.config.js` — 12 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/ed08945d27613f7d2942baf3e482465483e338bb/web/vite.config.js#L1-L12)

| Ligne | Code | Explication exacte |
|---|---|---|
| 1 | import `defineConfig` | Helper Vite pour autocomplétion/contrat. |
| 2 | import `react` | Fonction qui construit le plugin React. |
| 3 | vide | Séparation. |
| 4 | commentaire proxy | Documentation humaine. |
| 5 | `export default defineConfig({` | Exporte l’objet lu par Vite. |
| 6 | `plugins: [react()],` | Tableau contenant l’instance du plugin. |
| 7 | `server: {` | Ouvre les options du serveur de développement. |
| 8 | `port: 5174,` | Port local choisi. |
| 9 | `strictPort: true,` | Échoue si occupé au lieu de changer de port. |
| 10 | `proxy: { "/api": "http://localhost:8000" },` | Toute URL commençant `/api` est transférée à FastAPI. |
| 11 | `},` | Ferme `server`. |
| 12 | `});` | Ferme configuration et appel. |

Le proxy n’existe que pendant `vite`. Les fichiers construits ne contiennent pas un serveur proxy.

## Questions possibles

**React est-il un framework ?**  
Dans ce projet, on le présente comme une bibliothèque d’UI. Vite fournit l’outillage.

**Pourquoi JSX ?**  
Pour décrire l’arbre d’interface dans JavaScript. Vite le transforme.

**Pourquoi le frontend a-t-il besoin de Node si le navigateur exécute JavaScript ?**  
Node exécute Vite et npm pendant le développement/build. Le navigateur exécute le résultat.

