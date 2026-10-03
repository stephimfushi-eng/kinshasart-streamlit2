# KINSHAS'Art — WENZE

Application Streamlit pour le concours photo KINSHAS'Art.

## Fonctions
- page publique du concours ;
- inscription 18–25 ans ;
- upload de la pièce d'identité et de la photo ;
- ID candidat permanent `MSN-xxxx` écrit comme valeur ;
- stockage Google Sheets + Google Drive ;
- espace Jury anonymisé, grille /100 ;
- espace Administration séparé.

## Installation locale
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Connexion Google
1. Créer un projet Google Cloud et un Service Account.
2. Activer Google Sheets API et Google Drive API.
3. Partager le Google Sheets KINSHAS'Art et les deux dossiers Drive (photos + pièces d'identité) avec l'adresse e-mail du Service Account en rôle Éditeur.
4. Dans Streamlit Cloud, ouvrir **Settings > Secrets** et recopier les valeurs du fichier `.streamlit_secrets.example.toml` avec les vraies informations du Service Account.
5. Ne jamais publier le fichier de secrets sur GitHub.

## Déploiement
Pousser `app.py`, `requirements.txt` et `README.md` sur GitHub, puis créer une application dans Streamlit Community Cloud et sélectionner `app.py`.

## Sécurité
Le jury ne doit pas recevoir l'accès au Google Sheets administratif ni au dossier des pièces d'identité. Utiliser un mot de passe Jury différent du mot de passe Administration.

## Important sur les ID
L'application écrit l'ID dans la feuille Administration comme une valeur, pas une formule. Il reste donc inchangé après tri ou déplacement des lignes. Pour une très forte simultanéité de candidatures, une version suivante pourra utiliser un compteur transactionnel côté serveur.
