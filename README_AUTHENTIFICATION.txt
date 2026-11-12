# Patch d'authentification – Flask / MySQL

Ce dossier contient les fichiers à remplacer/ajouter dans le dépôt existant.

## Fichiers
- `app.py` : version avec authentification obligatoire et contrôle des sessions.
- `templates/base.html` : ajoute le nom du compte connecté et le bouton Déconnexion.
- `templates/login.html` : page de connexion.
- `hash_password.py` : outil local pour générer un hash de mot de passe.

## Table attendue
La table doit contenir les colonnes `id`, `login`, `password`, `state_account`.
Le code considère comme actif `1`, `actif`, `active`, `enabled`, `true` ou `oui`
(sans distinction majuscules/minuscules). Toute autre valeur bloque la connexion.

Exemple de structure conseillée :
```sql
CREATE TABLE IF NOT EXISTS users_accounts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  login VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  state_account TINYINT(1) NOT NULL DEFAULT 1
);
```

## Important : mots de passe
Le code attend un hash Werkzeug dans `users_accounts.password`, pas un mot de passe en clair.
Installer les dépendances (`pip install -r requirements.txt`), puis générer un hash :
```bash
python hash_password.py
```
Copier le hash affiché dans la colonne `password` du compte concerné.
Ne pas publier le mot de passe en clair dans GitHub.

## Déploiement
1. Faire une copie de sauvegarde du dépôt.
2. Remplacer `app.py` et `templates/base.html` par ceux du patch.
3. Ajouter `templates/login.html`.
4. Vérifier que `SECRET_KEY` est défini dans les variables d'environnement Render avec une longue valeur aléatoire.
5. Commit/push vers GitHub : Render redéploiera l'application.
6. Tester une URL métier directement (ex. `/produits`) en navigation privée : elle doit rediriger vers `/login`.
7. Tester un compte actif, un mot de passe incorrect et un compte désactivé.

`Werkzeug` est déjà installé avec Flask ; aucune dépendance supplémentaire n'est nécessaire.
