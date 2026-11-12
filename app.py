import os
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g
)
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("RENDER", "").lower() == "true"


def db():
    return mysql.connector.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        connection_timeout=15
    )


def rows(sql, params=()):
    cn = db()
    cur = cn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        cn.close()


def run(sql, params=()):
    cn = db()
    cur = cn.cursor()
    try:
        cur.execute(sql, params)
        cn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        cn.close()


def account_is_active(value):
    """Accepte les états actifs courants : 1, actif, active, enabled, true ou oui."""
    return str(value).strip().lower() in {
        "1", "actif", "active", "enabled", "true", "oui"
    }


@app.before_request
def require_login():
    # Seules la connexion et les ressources statiques sont accessibles sans session.
    if request.endpoint in {"login", "static"}:
        return None

    if not session.get("user_id"):
        return redirect(url_for("login", next=request.full_path))

    return None


@app.context_processor
def inject_logged_user():
    return {"logged_user": session.get("user_login")}


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        login_value = request.form.get("login", "").strip()
        password_value = request.form.get("password", "")

        if not login_value or not password_value:
            flash("Veuillez saisir votre identifiant et votre mot de passe.", "warning")
            return render_template("login.html")

        try:
            accounts = rows(
                """SELECT id, login, password, state_account
                   FROM users_accounts
                   WHERE login = %s
                   LIMIT 1""",
                (login_value,)
            )
        except mysql.connector.Error:
            app.logger.exception("Erreur lors de la vérification du compte utilisateur")
            flash("Le service de connexion est momentanément indisponible.", "danger")
            return render_template("login.html"), 500

        account = accounts[0] if accounts else None

        # Les mots de passe doivent être enregistrés avec werkzeug.security.generate_password_hash.
        password_ok = False
        if account:
            try:
                password_ok = check_password_hash(account["password"], password_value)
            except (TypeError, ValueError):
                password_ok = False

        if not account or not password_ok:
            flash("Identifiant ou mot de passe incorrect.", "danger")
            return render_template("login.html"), 401

        if not account_is_active(account["state_account"]):
            flash("Ce compte est désactivé. Veuillez contacter l'administrateur.", "danger")
            return render_template("login.html"), 403

        session.clear()
        session.permanent = True
        session["user_id"] = account["id"]
        session["user_login"] = account["login"]

        next_url = request.args.get("next") or request.form.get("next")
        # Évite les redirections vers un site externe.
        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url.split("?")[0] if next_url.endswith("?") else next_url)
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("login"))


@app.route("/")
def index():
    stats = rows("""SELECT
      (SELECT COUNT(*) FROM categorie_produit) categories,
      (SELECT COUNT(*) FROM produit) produits,
      (SELECT COUNT(*) FROM vente) ventes,
      (SELECT COALESCE(SUM(quantite * prix_unitaire),0) FROM vente) ca""")[0]
    recent = rows("""SELECT v.id_vente,v.date_vente,v.quantite,v.prix_unitaire,
      p.designation,(v.quantite*v.prix_unitaire) montant
      FROM vente v JOIN produit p ON p.id_produit=v.id_produit
      ORDER BY v.date_vente DESC,v.id_vente DESC LIMIT 8""")
    return render_template("index.html", stats=stats, recent=recent)


@app.route("/categories")
def categories():
    data = rows("""SELECT c.*,COUNT(p.id_produit) nb
      FROM categorie_produit c LEFT JOIN produit p ON p.id_categorie=c.id_categorie
      GROUP BY c.id_categorie,c.libelle ORDER BY c.libelle""")
    return render_template("categories.html", data=data)


@app.post("/categories/add")
def category_add():
    label = request.form.get("libelle", "").strip()
    if not label:
        flash("Le libellé est obligatoire.", "danger")
    else:
        try:
            run("INSERT INTO categorie_produit(libelle) VALUES(%s)", (label,))
            flash("Catégorie ajoutée.", "success")
        except mysql.connector.Error as e:
            flash(f"Erreur MySQL : {e.msg}", "danger")
    return redirect(url_for("categories"))


@app.post("/categories/<int:ident>/edit")
def category_edit(ident):
    label = request.form.get("libelle", "").strip()
    if label:
        try:
            run("UPDATE categorie_produit SET libelle=%s WHERE id_categorie=%s", (label, ident))
            flash("Catégorie modifiée.", "success")
        except mysql.connector.Error as e:
            flash(f"Erreur MySQL : {e.msg}", "danger")
    else:
        flash("Le libellé est obligatoire.", "danger")
    return redirect(url_for("categories"))


@app.post("/categories/<int:ident>/delete")
def category_delete(ident):
    try:
        run("DELETE FROM categorie_produit WHERE id_categorie=%s", (ident,))
        flash("Catégorie supprimée.", "success")
    except mysql.connector.Error:
        flash("Suppression impossible : cette catégorie est utilisée par un produit.", "warning")
    return redirect(url_for("categories"))


@app.route("/produits")
def produits():
    cats = rows("SELECT * FROM categorie_produit ORDER BY libelle")
    products = rows("""SELECT p.*,c.libelle categorie FROM produit p
      JOIN categorie_produit c ON c.id_categorie=p.id_categorie ORDER BY p.designation""")
    return render_template("produits.html", cats=cats, products=products)


def product_values():
    designation = request.form.get("designation", "").strip()
    categorie = request.form.get("id_categorie", type=int)
    try:
        price = Decimal(request.form.get("prix_vente", ""))
        if price < 0:
            raise InvalidOperation
    except (InvalidOperation, TypeError):
        raise ValueError("Le prix de vente est invalide.")
    if not designation or not categorie:
        raise ValueError("La désignation et la catégorie sont obligatoires.")
    return designation, price, categorie


@app.post("/produits/add")
def product_add():
    try:
        vals = product_values()
        run("INSERT INTO produit(designation,prix_vente,id_categorie) VALUES(%s,%s,%s)", vals)
        flash("Produit ajouté.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except mysql.connector.Error as e:
        flash(f"Erreur MySQL : {e.msg}", "danger")
    return redirect(url_for("produits"))


@app.post("/produits/<int:ident>/edit")
def product_edit(ident):
    try:
        vals = product_values()
        run("""UPDATE produit SET designation=%s,prix_vente=%s,id_categorie=%s
             WHERE id_produit=%s""", vals + (ident,))
        flash("Produit modifié.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    except mysql.connector.Error as e:
        flash(f"Erreur MySQL : {e.msg}", "danger")
    return redirect(url_for("produits"))


@app.post("/produits/<int:ident>/delete")
def product_delete(ident):
    try:
        run("DELETE FROM produit WHERE id_produit=%s", (ident,))
        flash("Produit supprimé.", "success")
    except mysql.connector.Error:
        flash("Suppression impossible : ce produit est associé à une vente.", "warning")
    return redirect(url_for("produits"))


@app.route("/ventes")
def ventes():
    products = rows("SELECT id_produit,designation,prix_vente FROM produit ORDER BY designation")
    sales = rows("""SELECT v.*,p.designation,(v.quantite*v.prix_unitaire) montant
      FROM vente v JOIN produit p ON p.id_produit=v.id_produit
      ORDER BY v.date_vente DESC,v.id_vente DESC""")
    total = sum((Decimal(str(x["montant"])) for x in sales), Decimal("0"))
    return render_template("ventes.html", products=products, sales=sales,
                           total=total, today=date.today().isoformat())


@app.post("/ventes/add")
def vente_add():
    product = request.form.get("id_produit", type=int)
    day = request.form.get("date_vente") or date.today().isoformat()
    try:
        qty = int(request.form.get("quantite", "0"))
        price = Decimal(request.form.get("prix_unitaire", ""))
        if qty <= 0 or price < 0:
            raise ValueError
    except (ValueError, InvalidOperation, TypeError):
        flash("Saisissez une quantité positive et un prix valide.", "danger")
        return redirect(url_for("ventes"))
    if not product:
        flash("Sélectionnez un produit.", "danger")
    else:
        try:
            run("""INSERT INTO vente(date_vente,id_produit,quantite,prix_unitaire)
                   VALUES(%s,%s,%s,%s)""", (day, product, qty, price))
            flash("Vente enregistrée.", "success")
        except mysql.connector.Error as e:
            flash(f"Erreur MySQL : {e.msg}", "danger")
    return redirect(url_for("ventes"))


@app.post("/ventes/<int:ident>/delete")
def vente_delete(ident):
    run("DELETE FROM vente WHERE id_vente=%s", (ident,))
    flash("Vente supprimée.", "success")
    return redirect(url_for("ventes"))


@app.errorhandler(mysql.connector.Error)
def db_error(error):
    app.logger.exception("Erreur MySQL")
    return render_template("error.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
