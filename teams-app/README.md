# Application Teams Scribe

Ce dossier contient le manifeste de l’onglet Scribe pour Teams. L’onglet ouvre
la même application web dans le chat, les détails, le panneau latéral ou la
scène d’une réunion.

Pour produire le paquet installable, il faut d’abord :

1. déployer le frontend sur un domaine HTTPS public ;
2. enregistrer l’application dans Microsoft Entra et récupérer son Application ID ;
3. remplacer `{{PUBLIC_DOMAIN}}` et `{{MICROSOFT_APP_ID}}` dans le manifeste ;
4. ajouter les icônes Teams `color.png` (192 × 192) et `outline.png` (32 × 32) ;
5. compresser les trois fichiers à la racine du ZIP, puis charger ce ZIP dans Teams.

La publication globale et l’accès aux calendriers exigent ensuite l’accord de
l’administrateur Microsoft 365 du tenant. Aucun secret Microsoft ne doit être
placé dans le frontend ou dans ce dossier.
