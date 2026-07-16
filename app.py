from flask import Flask, render_template, request, redirect, url_for, flash, session
import config
import mysql.connector

app = Flask(__name__)
app.secret_key = "ma_cle_secret_123"
def get_connexion():
    return mysql.connector.connect(
        host=config.HOST,
        user=config.USER,
        password=config.PASSWORD,
        database=config.DATABASE
    )

@app.route("/")
def accueil():
    return render_template("index.html")

@app.route("/contacts")
def afficher_contacts():
    if "username" not in session: #vérifier si l'utilisateur est connecté
        flash("❌ Vous devez vous connecter !", "erreur")
        return redirect(url_for("login"))
    connexion = get_connexion()
    curseur = connexion.cursor()
    
    recherche = request.args.get("recherche", "")
    
    if recherche:
        curseur.execute("SELECT * FROM contacts WHERE nom LIKE %s",
                        (f"%{recherche}%",)
                        )
    else:
        curseur.execute ("SELECT * FROM contacts")
    contacts = curseur.fetchall()
    curseur.close()
    connexion.close()
    return render_template("contacts.html", contacts=contacts)

@app.route("/ajouter", methods=["GET", "POST"]) #Pour ajouter un contact
def ajouter_contact():
    if "username" not in session: #vérifier si l'utilisateur est connecté
        flash("❌ Vous devez vous connecter !", "erreur")
        return redirect(url_for("login"))
    if request.method == "POST":
        nom = request.form["nom"].capitalize()
        telephone = request.form["telephone"]
        email = request.form["email"].lower()

        connexion = get_connexion()
        curseur = connexion.cursor()
        curseur.execute(
            "INSERT INTO contacts (nom, telephone, email) VALUES(%s, %s, %s)",
            (nom, telephone, email)
        )
        connexion.commit()
        curseur.close()
        connexion.close()
        flash("✅ Contact ajouté avec succès !", "succes")
        return redirect(url_for("afficher_contacts"))
    
    return render_template("ajouter.html")

@app.route("/supprimer/<int:id>") #pour supprimer
def supprimer_contact(id):
    if "username" not in session: #vérifier si l'utilisateur est connecté
        flash("❌ Vous devez vous connecter !", "erreur")
        return redirect(url_for("login"))
    connexion = get_connexion()
    curseur = connexion.cursor()
    curseur.execute("DELETE FROM contacts WHERE id = %s", (id,))
    connexion.commit()
    curseur.close()
    connexion.close()
    flash("🗑️ Contact supprimé avec succès !", "succes")
    return redirect(url_for("afficher_contacts"))

@app.route("/modifier/<int:id>", methods=["GET", "POST"]) #Pour modifier le contact
def modifier_contact(id):
    if "username" not in session: #vérifier si l'utilisateur est connecté
        flash("❌ Vous devez vous connecter !", "erreur")
        return redirect(url_for("login"))
    connexion = get_connexion()
    curseur = connexion.cursor()

    if request.method == "POST":
        nom = request.form["nom"].capitalize()
        telephone = request.form["telephone"]
        email = request.form["email"].lower()

        curseur.execute(
            "UPDATE contacts SET nom=%s, telephone=%s, email=%s WHERE id=%s",
            (nom, telephone, email, id)
        )
        connexion.commit()
        curseur.close()
        connexion.close()
        flash("✏️ Contact modifié avec succès !","succes")
        return redirect(url_for("afficher_contacts"))
    #Récupérer le contact à modifier
    curseur.execute(
        "SELECT * FROM contacts WHERE id = %s", (id,))
    contact = curseur.fetchone()
    curseur.close()
    connexion.close()
    return render_template("modifier.html", contact=contact)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connexion = get_connexion()
        curseur = connexion.cursor()
        curseur.execute(
            "SELECT * FROM utilisateurs WHERE username = %s AND password = %s",
            (username, password)
        )
        utilisateur = curseur.fetchone()
        curseur.close()
        connexion.close()

        if utilisateur:
            session["username"] = username
            flash("✅ Bienvenue " + username + " !", "succes")
            return redirect(url_for("afficher_contacts"))
        else:
            flash("❌ Login ou mot de passe incorrect !", "erreur")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("👋 Vous êtes déconnecté !", "succes")
    return redirect(url_for("login"))                

if __name__ == "__main__":
    app.run(debug=True)
