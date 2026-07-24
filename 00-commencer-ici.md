# Yanis — comprendre le projet en partant réellement de zéro

Ce guide part du principe que tu n’as jamais programmé. Il ne te demande pas de mémoriser des mots
techniques avant de comprendre ce qu’ils représentent.

## La règle utilisée dans les autres documents

Pour chaque ligne importante, tu trouveras six explications :

1. **La ligne exacte** : le texte présent dans Git.
2. **La traduction en français normal** : ce que la ligne demande à l’ordinateur.
3. **Chaque morceau expliqué** : mots, parenthèses, signes et noms.
4. **Ce qui se passe réellement** : en mémoire, dans le navigateur, sur le réseau ou dans la base.
5. **Pourquoi la ligne est ici** : son rôle dans le fichier et dans la fonctionnalité.
6. **Si on l’enlève ou si elle échoue** : conséquence observable.

## Avant le code : qu’est-ce qu’un programme ?

Un ordinateur ne comprend pas « crée une réunion » comme un humain. Il exécute une suite
d’instructions très précises.

Un **programme** est cet ensemble d’instructions.

Un **fichier source** est un fichier texte contenant des instructions écrites dans un langage de
programmation. Par exemple :

```text
config.py
MeetingWorkflow.jsx
index.css
```

L’extension indique généralement la nature du fichier :

- `.py` : Python, exécuté sur le serveur ;
- `.js` : JavaScript ;
- `.jsx` : JavaScript pouvant contenir une écriture ressemblant à du HTML ;
- `.css` : règles visuelles ;
- `.html` : structure d’une page ;
- `.json` : données structurées ou configuration ;
- `.toml` : configuration lisible ;
- `.ps1` : commandes PowerShell pour Windows.

## Qu’est-ce qu’une ligne de code ?

Une ligne est une partie d’une instruction. Une seule instruction peut prendre plusieurs lignes pour
rester lisible.

Exemple :

```python
recording = session.get(Recording, recording_id)
```

Cette ligne signifie :

> Demande à la base de données de chercher un enregistrement dont l’identifiant vaut
> `recording_id`, puis garde le résultat sous le nom `recording`.

L’ordinateur ne comprend pas les noms comme un humain. Les développeurs choisissent des noms qui
rendent le code explicable.

## Qu’est-ce qu’une valeur ?

Une valeur est une information manipulée par le programme.

Exemples :

```text
"Nouvelle réunion"       un texte
50                       un nombre entier
true                     vrai
false                    faux
null / None              absence de valeur
["Yanis", "Aymen"]       une liste
```

Le **type** décrit la famille d’une valeur.

Pourquoi les types sont importants :

- on peut additionner des nombres ;
- on peut découper un texte ;
- on peut parcourir une liste ;
- on ne peut pas raisonnablement additionner un microphone et un utilisateur.

## Qu’est-ce qu’une variable ?

Une variable est un nom donné à une valeur pour pouvoir la réutiliser.

```python
path = Path(recording.audio_path).resolve()
```

Traduction :

> Calcule le chemin complet du fichier audio et appelle ce résultat `path`.

Après cette ligne, le programme peut écrire `path` au lieu de refaire tout le calcul.

Le signe `=` signifie ici **affecter** :

```text
nom à gauche = valeur calculée à droite
```

Ce n’est pas exactement le « égal » d’une équation mathématique.

## Qu’est-ce qu’une constante ?

Une constante est une valeur qui ne devrait pas changer pendant l’exécution.

Python utilise une convention en majuscules :

```python
SYSTEM_PROMPT = """..."""
```

Cela dit aux développeurs :

> Cette valeur représente une règle globale. Ne la modifiez pas comme une variable locale.

Python ne bloque pas techniquement la modification. C’est une convention humaine.

## Qu’est-ce qu’une fonction ?

Une fonction est un petit programme nommé à l’intérieur du programme principal.

```python
def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
```

Traduction :

> Je crée une opération appelée `token_hash`. On lui donne un texte appelé `token`. Elle rend un
> nouveau texte représentant son empreinte.

Pourquoi créer une fonction :

- éviter de recopier la même logique ;
- donner un nom à une opération ;
- pouvoir la tester ;
- cacher les détails à l’endroit où elle est utilisée.

## Paramètre et argument

Dans la définition :

```python
def token_hash(token: str)
```

`token` est un **paramètre** : la place prévue pour recevoir une valeur.

Dans l’appel :

```python
token_hash(token_recu)
```

`token_recu` est l’**argument** réellement donné.

Analogie :

```text
fonction = machine
paramètre = ouverture de la machine
argument = objet placé dans l’ouverture
return = résultat qui ressort
```

## Qu’est-ce que `return` ?

`return` termine la fonction et rend une valeur à l’endroit qui l’a appelée.

```python
return meeting
```

signifie :

> La fonction a terminé. Voici l’objet réunion comme résultat.

Une fonction annotée `-> None` ne promet aucune valeur utile en retour.

## Qu’est-ce qu’une condition ?

Une condition choisit si un bloc doit s’exécuter.

```python
if not consent:
    raise HTTPException(400, "Consentement obligatoire")
```

Traduction :

> Si le consentement n’est pas vrai, arrête la requête et renvoie une erreur.

Le mot `if` signifie « si ».  
Le mot `not` inverse vrai et faux.  
Les deux-points `:` annoncent un bloc indenté.  
Les quatre espaces de la ligne suivante montrent qu’elle appartient au `if`.

## Qu’est-ce qu’une boucle ?

Une boucle répète une opération pour plusieurs éléments.

```python
for participant in participants:
```

Traduction :

> Prends chaque élément de la liste `participants`, appelle temporairement cet élément
> `participant`, puis exécute le bloc.

## Qu’est-ce qu’une liste ?

Une liste contient plusieurs valeurs dans un ordre.

```python
names = ["Yanis", "Aymen", "Ashwin", "Mehdi"]
```

Les positions commencent généralement à zéro :

```text
names[0] = "Yanis"
```

## Qu’est-ce qu’un dictionnaire ?

Un dictionnaire associe un nom de champ à une valeur.

```python
payload = {
    "participants": participant_names,
    "full_transcript": transcript,
}
```

Traduction :

> Crée un ensemble de données contenant un champ `participants` et un champ `full_transcript`.

Le nom avant `:` est la clé. La partie après `:` est la valeur.

Un dictionnaire Python peut ensuite devenir du JSON pour être envoyé sur Internet.

## Qu’est-ce qu’une classe ?

Une classe décrit la forme d’une famille d’objets.

```python
class ActionItem(BaseModel):
    task: str
    owner: str | None = None
```

Traduction :

> Une action doit avoir un texte de tâche. Elle peut avoir un responsable, mais ce responsable peut
> être absent.

La classe est le plan. Une **instance** est un objet réel créé à partir de ce plan.

```python
ActionItem(task="Envoyer le devis", owner="Yanis")
```

est une instance.

## Qu’est-ce qu’un constructeur ?

Le constructeur est l’opération qui crée une nouvelle instance.

```python
Recording(owner_id=user.id, title=title)
```

Traduction :

> Crée un nouvel objet de type Recording avec ce propriétaire et ce titre.

Les parenthèses contiennent les informations de départ.

## Qu’est-ce qu’un import ?

Un fichier ne contient pas tout le projet. `import` lui permet d’utiliser du code défini ailleurs.

```python
from pathlib import Path
```

Traduction :

> Dans la bibliothèque Python appelée `pathlib`, rends disponible l’outil appelé `Path`.

Si on retire cette ligne puis que le fichier utilise `Path`, Python répond que ce nom n’existe pas.

## Qu’est-ce qu’une bibliothèque ?

Une bibliothèque est du code réutilisable déjà préparé.

Exemples :

- React aide à construire l’interface ;
- FastAPI aide à créer des routes Web ;
- Pydantic valide les données ;
- HTTPX envoie des requêtes HTTP.

Utiliser une bibliothèque ne signifie pas que la fonctionnalité se fait seule. Le projet doit encore
définir ses règles.

## Qu’est-ce qu’une API ?

Une API est un contrat permettant à un programme de demander quelque chose à un autre programme.

Exemple :

```text
POST /api/recordings
```

signifie :

> Envoie au backend une demande de création d’enregistrement selon le format attendu.

L’API décrit :

- l’adresse ;
- la méthode ;
- les données à envoyer ;
- la réponse ;
- les erreurs possibles.

## Frontend et backend

Le **frontend** est ce qui s’exécute dans le navigateur et que l’utilisateur voit :

- boutons ;
- formulaires ;
- chronomètre ;
- lecteur audio.

Le **backend** est le programme serveur :

- vérifie les droits ;
- parle à la base ;
- stocke temporairement l’audio ;
- appelle Mistral ;
- renvoie les résultats.

Le frontend ne doit jamais décider seul d’une règle de sécurité, car l’utilisateur peut modifier ce
qui se passe dans son navigateur.

## Serveur, client et requête

Le navigateur est le **client** : il demande.

FastAPI est le **serveur** : il reçoit, vérifie et répond.

Une **requête** est la demande.  
Une **réponse** est le résultat renvoyé.

## Base de données, table et ligne

Une base conserve les données après la fin d’une requête.

Une **table** ressemble à un tableau :

```text
Recording
------------------------------------------------
id | owner_id | title | status | transcript
```

Une **ligne** représente un enregistrement précis.  
Une **colonne** représente un type d’information.

SQLModel permet de manipuler cette ligne comme un objet Python.

## Qu’est-ce qu’un effet de bord ?

Une opération a un effet de bord lorsqu’elle change quelque chose en dehors de sa valeur de retour.

Exemples :

- écrire un fichier ;
- supprimer un audio ;
- modifier la base ;
- envoyer un e-mail ;
- appeler Mistral ;
- démarrer le microphone.

Les effets de bord sont les parties les plus importantes à sécuriser et tester.

## Qu’est-ce qu’une exception ?

Une exception représente un problème interrompant le chemin normal.

```python
raise SummaryError("Mistral indisponible")
```

signifie :

> Le résumé ne peut pas continuer. Remonte cette erreur au code qui orchestre.

`try` désigne le code susceptible d’échouer.  
`except` explique quoi faire pour certaines erreurs.  
`finally` contient ce qui doit être tenté dans tous les cas.

## Qu’est-ce que React ?

React est une bibliothèque JavaScript pour construire une interface à partir de composants.

Un composant est une fonction qui renvoie une partie de l’écran.

```javascript
function Recorder() {
  return <button>Démarrer</button>;
}
```

Lorsque ses données changent, React recalcule la partie de l’écran concernée.

## Qu’est-ce qu’un état React ?

```javascript
const [state, setState] = useState("idle");
```

Traduction :

> Demande à React de conserver une information appelée `state`, qui vaut d’abord `idle`. React me
> donne aussi une fonction `setState` pour la modifier proprement.

Pourquoi ne pas écrire `state = "recording"` :

> React ne serait pas correctement averti qu’il doit mettre l’écran à jour.

## Qu’est-ce qu’une ref React ?

Une ref est une petite boîte conservée par React :

```javascript
const recorder = useRef(null);
```

Elle sert à garder un objet technique, par exemple le microphone, sans redessiner l’écran à chaque
changement.

La valeur se trouve dans :

```javascript
recorder.current
```

## Qu’est-ce qu’un effet React ?

Un effet connecte l’interface à quelque chose d’extérieur :

- une minuterie ;
- le réseau ;
- le micro ;
- une URL temporaire.

```javascript
useEffect(() => {
  const timer = setInterval(...);
  return () => clearInterval(timer);
}, []);
```

La fonction retournée nettoie la ressource. Sans nettoyage, la minuterie pourrait continuer après
la disparition de l’écran.

## Comment lire les signes fréquents

| Signe | Sens dans le projet |
|---|---|
| `()` | appel de fonction ou paramètres |
| `{}` en Python | dictionnaire ou ensemble |
| `{}` en JavaScript | objet ou bloc |
| `[]` | liste/tableau ou accès par position |
| `.` | accéder à une propriété ou méthode |
| `:` en Python | ouvre un bloc ou sépare clé/valeur |
| `,` | sépare des éléments |
| `=` | affecte une valeur |
| `==` | compare en Python |
| `===` | compare strictement en JavaScript |
| `!=`, `!==` | différent |
| `and`, `&&` | les deux conditions doivent être vraies |
| `or`, `||` | au moins une valeur/condition |
| `!` ou `not` | inverse |
| `?.` | continue seulement si la valeur existe |
| `=>` | fonction fléchée JavaScript |
| `...` | spread JavaScript ou valeur obligatoire Pydantic selon le contexte |
| `f"..."` | texte Python avec valeurs insérées |
| `` `...${x}` `` | texte JavaScript avec valeur insérée |

## Ordre conseillé

1. [Fondation et configuration](01-fondation-expliquee.md)
2. [Frontend et design](02-frontend-explique.md)
3. [Consentement](03-consentement-explique.md)
4. [Upload audio](04-upload-explique.md)
5. [Dictaphone](05-dictaphone-explique.md)
6. [Résumé Mistral](06-llm-explique.md)
7. [Pipeline complet](07-pipeline-explique.md)
8. [Entraînement oral](08-entrainement.md)

