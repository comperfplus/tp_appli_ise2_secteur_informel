import os
from datetime import date
from decimal import Decimal, InvalidOperation
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

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
        if price < 0: raise InvalidOperation
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
        if qty <= 0 or price < 0: raise ValueError
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
