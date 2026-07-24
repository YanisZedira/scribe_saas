# Commit 4 — `6104ac5` — coquille React et CSS

[Voir le commit](https://github.com/AshDv/ScribeProject/commit/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250)

## `web/src/App.jsx` — 7 lignes

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/App.jsx#L1-L7)

| Ligne | Code | Explication |
|---|---|---|
| 1 | `export default function App() {` | Déclare un composant fonctionnel PascalCase et l’exporte par défaut. `{` ouvre le corps. |
| 2 | `return <main ...><section ...>` | `return` donne l’arbre JSX. `main` est le contenu principal, `section` une zone thématique. Deux classes sont appliquées à la section. |
| 3 | bloc `.brand` | `div` groupe marque et nom. Deux `span` sont en ligne via CSS. |
| 4 | `<h1>...` | Titre principal unique de la page. |
| 5 | `<p>...` | Paragraphe signalant l’état temporaire. |
| 6 | fermetures | Ferme `section`, `main` puis termine l’instruction avec `;`. |
| 7 | `}` | Ferme la fonction. |

Le JSX est très compact. Moins de lignes ne signifie pas plus lisible ; un formateur le répartirait.

## `web/src/index.css` — 90 lignes physiques

[Voir le fichier](https://github.com/AshDv/ScribeProject/blob/6104ac55c5dad4fe4b6d7382a7ea5d17c9862250/web/src/index.css#L1-L90)

Chaque ligne contient une ou plusieurs règles entières.

| Ligne | Sélecteur | Explication de toutes les propriétés importantes |
|---|---|---|
| 1 | `@import` | Charge DM Sans et Manrope depuis Google avec plusieurs graisses. `display=swap` montre une police de secours pendant le téléchargement. Limite RGPD : appel tiers et IP. |
| 2 | vide | Séparation. |
| 3 | `:root` | Définit police globale, couleur, fond, désactive synthèse de fausses graisses et crée les variables `--ink`, `--muted`, `--line`, `--panel`, `--green`, `--green-dark`, `--mint`, `--cream`, `--danger`. |
| 4 | `*` | `box-sizing:border-box` fait inclure padding/border dans largeur et hauteur. |
| 5 | `body` | Retire la marge, impose largeur/hauteur minimales et un fond radial. `100vh` vaut toute la hauteur visible. |
| 6 | `button,input` | `font:inherit` fait hériter la typographie au lieu du style navigateur. |
| 7 | `button,a` | Retire le flash tactile WebKit. Peut réduire un feedback natif ; les états visuels doivent rester clairs. |
| 8 | `.icon` | `flex:0 0 auto` empêche l’icône de grandir ou rétrécir. |
| 9 | `.app-shell` | Hauteur minimale et grille de 260 px + reste disponible `1fr`. |
| 10 | `.sidebar` | Pleine hauteur, padding, fond sombre, flex colonne, `sticky`, hauteur viewport. |
| 11 | `.brand` | Flex horizontal centré, espacement, raccourci `font`, tracking négatif. |
| 12 | `.brand-mark` | Carré 38 px, Grid centré, coins, couleurs et ombre interne. |
| 13 | `.nav-list` | Flex colonne, espacement et marge supérieure. |
| 14 | `.nav-button` | Retire bord/fond, définit couleurs, flex, padding, curseur, graisse et transition. |
| 15 | hover/active navigation | Texte blanc et fond blanc transparent lors du survol ou état actif. |
| 16 | `.nav-button.active` | Ombre interne gauche verte simulant un indicateur. |
| 17 | `.profile-card` | `margin-top:auto` pousse le profil en bas ; flex et bord supérieur. |
| 18 | `.avatar` | Cercle 36 px centré avec initiales. |
| 19 | `.profile-copy` | Colonne flexible, largeur minimale zéro pour autoriser l’ellipse. |
| 20 | `.profile-copy strong` | Petit texte, cache débordement, ellipse, une ligne. |
| 21 | `.profile-copy span` | Même mécanisme pour l’e-mail avec couleur atténuée. |
| 22 | `.icon-button` | Bouton carré Grid sans bord et fond transparent. |
| 23 | hover icon | Ajoute un léger fond. |
| 24 | `.main-content` | Largeur maximale 1180 px, centrage horizontal, padding. |
| 25 | `.page` | Animation d’entrée 0,35 s, courbe ease, conserve l’état final avec `both`. |
| 26 | `@keyframes enter` | Départ transparent et décalé de 7 px ; l’état final revient aux valeurs normales. |
| 27 | `.page-header` | Flex, alignement haut, séparation entre titre/actions et marge basse. |
| 28 | enfant direct div | `min-width:0` autorise le rétrécissement dans flex. |
| 29 | titres | Police Manrope 800, taille `clamp`, tracking et marges. |
| 30 | paragraphes d’en-tête | Retire marge, couleur atténuée, taille 16 px. |
| 31 | eyebrow/card-label | Vert, gras, petit, lettres espacées, uppercase visuel. |
| 32 | `.secure-badge` | Badge flex arrondi avec bord, fond et taille petite. |
| 33 | `.recorder-grid` | Deux colonnes flexibles : zone principale 1,6 et panneau minimum 280 px. |
| 34 | famille de cartes | Fond blanc, bord, rayon 24 px et ombre commune : DRY CSS. |
| 35 | `.recorder-card` | Hauteur minimale, padding, flex colonne centré. |
| 36 | `.title-label` | Label pleine largeur, colonne, gap et typographie. |
| 37 | entrées | Bord, coins, fond, couleur, suppression outline natif et transition. Il faut conserver un focus visible ensuite. |
| 38 | entrée titre | Padding et taille 16 px. |
| 39 | focus entrées | Bord vert et anneau `box-shadow` accessible visuellement. |
| 40 | `.orb` | Cercle 142 px, marges, Grid centré, fond radial et transition. |
| 41 | `.orb.live` | Applique l’animation pulse uniquement lorsque les deux classes existent. |
| 42 | `@keyframes pulse` | À 50 %, ajoute un anneau de 22 px semi-transparent. |
| 43 | `.orb-inner` | Cercle interne, gradient, blanc et ombre. |
| 44 | `.timer` | Police très grasse 34 px et espacement. |
| 45 | `.recorder-status` | Marges et texte atténué. |
| 46 | famille boutons | Base commune : bord, rayon, hauteur, padding, flex centré, curseur, texte et transition. |
| 47 | boutons principaux | Fond vert, texte blanc, ombre. |
| 48 | hover principaux | Vert foncé et translation verticale de -1 px. |
| 49 | point du bouton record | Petit cercle blanc. |
| 50 | bouton disabled | Opacité et curseur d’attente. `disabled` bloque aussi l’action native. |
| 51 | `.compact` | Largeur automatique et hauteur 42 px. |
| 52 | secondaire | Texte sombre et fond gris-vert. |
| 53 | stop | Blanc sur rouge. |
| 54 | `.control-row` | Flex, retour à la ligne, centrage et espacement. |
| 55 | `.audio-player` | Largeur maximum 420 px et marge basse. |
| 56 | processing/loading | Flex centré avec gap et couleur muted. |
| 57 | spinners | Cercle bordé, segment supérieur vert, animation infinie. |
| 58 | tailles spinners | Petit 20 px et grand 42 px sur la même ligne. |
| 59 | `@keyframes spin` | Rotation complète à l’état final. |
| 60 | `.steps-card` | Padding et fond crème très clair. |
| 61 | titre steps | Manrope, graisse, taille, marges. |
| 62 | `.step` | Flex, gap et marge basse. |
| 63 | numéro d’étape | Brun, graisse, taille et petit padding haut. |
| 64 | texte étape | `strong` en bloc ; paragraphe atténué avec line-height et marge zéro. |
| 65 | `.consent` | Encadré cliquable, flex, bord/fond crème et rayon. |
| 66 | checkbox consent | 18 px et accent vert. |
| 67 | textes consent | Colonne ; tailles différentes pour titre et aide. |
| 68 | alertes | Base padding/rayon/taille ; variante erreur rouge clair avec bord. |
| 69 | `.auth-layout` | Grille deux colonnes légèrement asymétriques et pleine hauteur. |
| 70 | story/panel | `min-width:0` évite le débordement des enfants Grid. |
| 71 | `.auth-story` | Conteneur relatif, débordement masqué, gradient, flex colonne. |
| 72 | pseudo-élément story | Cercle décoratif absolu créé par `content:""`. |
| 73 | `.story-copy` | Marge automatique verticale, largeur max, au-dessus du décor via `z-index`. |
| 74 | typographie story | Couleurs, grand titre responsive, paragraphe et espacements. Plusieurs règles sont compactées sur la ligne. |
| 75 | feature row | Flex avec wrap ; enfants flex et petite typographie. |
| 76 | footer/panel/card | Couleur du small, centrage Grid du panneau et largeur maximale de la carte. |
| 77 | titre auth | Marges, Manrope 32 px et tracking. `.muted` définit la couleur atténuée. |
| 78 | bouton Google | Pleine largeur, marge, fond blanc et bord ; hover soulève. |
| 79 | séparateur | Flex avec deux pseudo-lignes `:before/:after` prenant l’espace restant. |
| 80 | formulaire/champs | Formulaire colonne ; labels colonnes ; entrées paddées ; aide petite. |
| 81 | text/back buttons | Boutons transparents verts ; variantes de largeur/marges. |
| 82 | liste/ligne recording | Colonne de lignes ; chaque ligne est bouton flex avec hover, bord et ombre. |
| 83 | icône/copie/flèche | Icône carrée, texte flexible en colonne et flèche atténuée. |
| 84 | statuts | Base badge et variantes completed/processing/uploaded/failed par couleur. |
| 85 | cartes vides/processing | Padding, centrage, styles de titres et paragraphes. |
| 86 | résultat | En-tête flex, bouton danger, grille 2 colonnes, cartes pleines lignes, listes, topics, erreurs. Ligne très chargée. |
| 87 | confidentialité | Grille deux colonnes, titres et paragraphes lisibles. |
| 88 | réunion/consentement | Largeur, formulaires participants, rows, hints, checkboxes, page publique et actions. Ligne excessivement longue. |
| 89 | media `max-width:900px` | Sur tablette : sidebar horizontale, navigation icônes, padding réduit, grilles 1 colonne, auth 1 colonne. |
| 90 | media `max-width:560px` | Sur mobile : padding réduit, en-têtes colonne, cartes plus petites, liste simplifiée et formulaire participant réorganisé. |

## Revue critique du CSS

Points positifs :

- variables de couleur ;
- composants visuels cohérents ;
- états focus ;
- responsive ;
- classes métier nommées ;
- styles partagés regroupés.

Points attaquables :

- une ligne peut contenir plus de dix règles : difficile à relire ;
- beaucoup de styles de fonctionnalités futures sont ajoutés avant leur JSX ;
- Google Fonts appelle un tiers ;
- absence de `prefers-reduced-motion` ;
- contrastes non prouvés par test ;
- pas de méthodologie CSS explicite ;
- moins de lignes physiques ne respecte pas mieux KISS.

Réponse :

> J’ai centralisé très tôt un design system cohérent, mais le fichier est trop compact. Je
> conserverais les mêmes sélecteurs tout en passant un formateur, en séparant tokens, composants et
> pages, et en auto-hébergeant les polices.

