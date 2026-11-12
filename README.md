# Application de gestion commerciale – Flask / MySQL

Cette version couvre uniquement les tables `categorie_produit`, `produit` et `vente`.
Les tables `approvisionnement` et `depense` ne sont pas développées.

## Installation locale
1. Installer Python 3.10 ou supérieur.
2. Exécuter `pip install -r requirements.txt`.
3. Exécuter le script `schema.sql` sur la base MySQL FreeDB.
4. Définir les variables d'environnement listées dans `.env.example`.
5. Lancer `python app.py`, puis ouvrir `http://127.0.0.1:5000`.

## Paramètres FreeDB
Créer le compte et la base sur FreeDB, exécuter `schema.sql`, puis relever le hostname, port, nom de base, utilisateur et mot de passe. Vérifier que l'offre FreeDB autorise les connexions MySQL distantes depuis Render. Les offres gratuites peuvent avoir des limites de durée, capacité ou disponibilité : vérifier les conditions en vigueur.

## Déploiement Render
1. Publier les fichiers du projet sur GitHub (ne jamais publier `.env`).
2. Sur Render, créer un Web Service lié au dépôt.
3. Build Command : `pip install -r requirements.txt`
4. Start Command : `gunicorn app:app`
5. Ajouter dans Environment Variables : `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`.
6. Déployer et tester l'URL publique.

## Sécurité et limites
- Ne pas commiter les identifiants MySQL sur GitHub.
- Les identifiants doivent être définis dans les variables d'environnement Render.
- Cette version pédagogique ne comporte pas encore d'authentification ni de gestion des rôles.
- Les ventes n'actualisent pas de stock : aucun module de stock n'est inclus.
- Prévoir une protection CSRF et une authentification avant tout usage réel.
