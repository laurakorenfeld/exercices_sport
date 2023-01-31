from urllib.parse import unquote
from app import app
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

# Rendu : 31/01
# API pour une base de données d'exercices utilisant Flask pour gérer les routes et SQLite pour stocker les données. 
# Les routes permettent d'afficher tous les exercices, d'ajouter un exercice, de rechercher un exercice par nom, de mettre à jour ou supprimer un exercice. 
# Il utilise également des requêtes HTTP pour gérer les différentes actions (GET, POST, PUT, DELETE). 
# Sécurité non gérée et code à encore améliorer.

# Cette API contient une interface utilateur qui permet de tester différentes requêtes. La page swagger ne fonctionne pas correctement, il vaut mieux tester via l'IHM.


# Les données sont par heure et pour un individu de 70kg : à adapter
# Imaginons la recherche d'objectif suivante : Je veux perdre quotidiennement 2000 kcal par jour en faisant du sport. Quel sport d'intensité moyenne je pourrais faire pour atteindre mon objectif ?



@app.route('/exercices', methods=['GET', 'POST'])

def exercices():
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    if request.method == 'GET': # permet de voir tous les exercices de la base de données
        cursor = conn.execute("SELECT * FROM exercices")
        exo = [
            dict(nom=row[1],calh=row[2],met=row[3],type=row[4],materiel=row[5])
            for row in cursor.fetchall()
        ]
        if exo is not None:
            return jsonify(exo)
    if request.method == 'POST': # perment de modifier les informations d'un exercice existant
        new_nom = request.form['nom']
        new_calh = request.form['calh']
        new_met = request.form['met']
        new_type = request.form['type']
        new_mat = request.form['materiel']
        sql = """INSERT INTO exercices (nom, calh, met, type, materiel)
                VALUES (?, ?, ?, ?, ?)"""
        cursor = cursor.execute(sql, (new_nom, new_calh, new_met, new_type, new_mat))
        conn.commit()
        return f"L'exercice avec id est {cursor.lastrowid} a été ajoutée", 201

# recupere_nom permet d'effectuer la recherche d'un exercice par son nom en récupérant la requête et en redirigeant vers la page de les informations de l'exercice souhaité

@app.route('/exercices/recupere_nom', methods=['POST'])
def recupere_nom():
    recherche=request.form['recherche']
    return(redirect(f'/exercices/{recherche}'))

# recupere_nom permet d'effectuer la recherche d'un exercice via la barre déroulante en redirigeant vers la page de les informations de l'exercice souhaité


@app.route('/exercices/recupere_selection', methods=['POST'])
def recupere_selection():
    exos = request.form.get('exercise-select')
    print(exos)
    if exos:
        return redirect(f'/exercices/{exos}')

# exo_rech permet de rechercher un exercice par son nom mais aussi d'en ajouter ou d'en effacer un grâce aux méthodes PUT et DELETE

@app.route('/exercices/<string:recherche>', methods=['GET', 'POST', 'PUT', 'DELETE'])

def exo_rech(recherche):
    # afficher un exercice
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    sql = """SELECT * FROM exercices WHERE nom='{}'""".format(recherche)
    cursor = cursor.execute(sql)
    exercice = [
        dict(nom=row[0],kcalh=row[1],met=row[2],type=row[3],materiel=row[4], id=row[5]) for row in cursor.fetchall()
                ]
    if exercice is not None and exercice!=[]: 
        return jsonify(exercice), 200

    if request.method == 'PUT':   # ajouter un exercice
        sql = """UPDATE exercices
            SET nom=?,
                calh=?,
                met=?
                type=?
                materiel=? 
            WHERE nom=?"""
        calh = request.form['calh']
        met = request.form['met']
        type = request.form['type']
        materiel = request.form['materiel']
        updated_exo = {
            "id": cursor.lastrowid,
            "nom": nom,
            "calh": calh,
            "met": met,
            "type": type,
            "materiel": materiel
        }
        conn.execute(sql, (id, nom, calh, met, type, materiel))
        conn.commit()
        return jsonify(updated_exo)
    if request.method == 'DELETE': # effacer un exercice
        sql = """DELETE FROM exercices WHERE nom=?"""
        conn.execute(sql, (nom,))
        conn.commit()
        return "L'exercice avec '{}' a été effacée".format(nom), 200
    else :
        return render_template('output.html', name = "Rien en stock pour le moment, vous pouvez ajouter votre propre exercice ! Méthode POST sur /exercices")  

# index est la fonction qui permet d'afficher la page d'accueil mais aussi d'effectuer la recherche d'un exercice en fonction de son intensité, du matériel souhaité et de l'accompagnement

@app.route('/',methods=['POST','GET'])

def index():
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    if request.method == 'POST': 
        intensite = request.form["intensite"]
        matoupas = request.form["materiel"]
        compagnie = request.form["groupe"]   
        if matoupas == "nomat":
            mat="non"
        else :
            mat="oui"   
        # MET < 3 : intensité faible, 3 < MET < 6 : modérée, MET <6 : intense
        if intensite =="moderee":
            a=3
            b=6
        elif intensite =="faible":
            a=0
            b=3.1
        elif intensite =="intense":
            a=6.1
            b=20
        sql = """SELECT * FROM exercices WHERE met>{} AND met<{} AND materiel ='{}' AND type ='{}'""".format(a,b,mat,compagnie)
        cursor = cursor.execute(sql)
        exo = [
            dict(nom=row[0],calh=row[1],met=row[2],avecqui=row[3]) for row in cursor.fetchall()
                ]
        if exo is not None:
            return  jsonify(exo)
    
        else :
            return render_template('exercices.html') 
    exos = get_exercise_names()    
    return render_template('index.html',exos=exos)

# inscription permet à un utilisateur non renseigné dans la base de données d'être ajouté. S'il est déjà inscrit, il sera redirigé vers sa page d'objectif

@app.route('/inscrits', methods=['GET', 'POST'])
def inscription():
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        objectif = request.form.get('objectif')
        objectif_sport = request.form.get('objectif_sport')
        if nom !='' and prenom!='' :
            if objectif_sport !='' and objectif != '' :              
                objectifs(nom, prenom, objectif, objectif_sport)
                return(redirect(f'/affiche_objectifs/{nom}/{prenom}'))
            else : 
                cursor.execute("SELECT id_user FROM inscrits WHERE nom='{}' AND prenom='{}'".format(nom,prenom))
                id = cursor.fetchone()
                if id is  None :
                    sql = """INSERT INTO inscrits (nom, prenom)
                    VALUES (?, ?)"""
                    cursor.execute(sql, (nom, prenom))
                    conn.commit()
                    id = cursor.lastrowid
                    return f"La personne avec id est {id} a été ajoutée", 201
                else :
                    return(redirect(f'/affiche_objectifs/{nom}/{prenom}'))
        elif objectif_sport !='' and objectif != '' :
            return heures(objectif, objectif_sport)
        else : 
            return render_template('output.html', name = "Veuillez renseigner les champs")  
            
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM inscrits")
        inscrit = [
            dict(id=row[0],nom=row[1],prenom=row[2],objectif=row[3])
            for row in cursor.fetchall()
        ]
        if inscrit is not None:
            jsonify(inscrit)
    

# personne(id) permet d'ajouter un inscrit, de modifier ses informations ou d'effacer ses données 

@app.route('/inscrits/<int:id>', methods=['GET','PUT', 'DELETE'])
def personne(id):
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM inscrits WHERE id_user={}".format(id))
        rows = cursor.fetchall()
        for r in rows : 
            personne = r
        if personne is not None : 
            return jsonify(personne), 200
        else :
            return "Something wrong", 404
    if request.method == 'PUT':   
        sql = """UPDATE inscrits
            SET nom=?,
                prenom=?,
                objectif=?, 
            WHERE id=?"""
        nom = request.form['nom']
        prenom = request.form['prenom']
        objectif = request.form['objectif']

        updated_inscrit = {
            "id": id,
            "nom": nom,
            "prenom": prenom,
            "objectif": objectif,
        }
        conn.execute(sql, (nom, prenom, objectif, id))
        conn.commit()
        return jsonify(updated_inscrit)

    if request.method == 'DELETE':
        sql = """DELETE FROM inscrits WHERE id_user=?"""
        conn.execute(sql, (id,))
        conn.commit()
        return render_template('output.html', name =  "La personne avec id est {} a été effacée".format(id))

# permet d'ajouter l'objectif à un profil
def objectifs(nom, prenom, objectif, objectif_sport):
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()    
    cursor.execute("SELECT id_user FROM inscrits WHERE nom=? AND prenom=?", (nom, prenom))
    id_user = cursor.fetchone()

    if id_user is not None:
            # Ajouter l'objectif à l'utilisateur existant
            sql="SELECT calh FROM exercices WHERE nom='{}'".format(objectif_sport)
            cursor.execute(sql)
            calh=cursor.fetchone()
            print(calh[0])
            heure = int(objectif)/int(calh[0])
            cursor.execute("INSERT INTO objectifs (id_user, objectif, sport, heures) VALUES (?, ?, ?, ?)", (id_user[0], objectif, objectif_sport, heure))
            conn.commit()
            return render_template('output.html', name = "L'objectif {} kcal a été ajouté à l'utilisateur {} {}".format(objectif,nom, prenom))
    else:
            # Ajouter l'utilisateur et son objectif
            
            cursor.execute("INSERT INTO inscrits (nom, prenom, objectif) VALUES (?, ?, ?)", (nom, prenom, objectif))
            id_user=cursor.lastrowid
            cursor.execute("INSERT INTO objectifs (id_user, objectif) VALUES (?, ?)", (id_user, objectif))
            conn.commit()
            return render_template('output.html', name = "L'utilisateur {} {} avec l'objectif {} a été ajouté".format(nom, prenom, objectif))
   

@app.route('/recupere_id', methods=['POST'])
def recupere_id():
    nom=request.form['nom']
    prenom=request.form['prenom']
    return(redirect(f'/affiche_objectifs/{nom}/{prenom}'))

@app.route('/affiche_objectifs/<string:nom>/<string:prenom>', methods=['GET'])
def affiche_objectifs(nom, prenom):
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT id_user FROM inscrits WHERE nom=? AND prenom=?", (nom, prenom))
    id_user = cursor.fetchone()
    if id_user is not None : 
        id_user = id_user[0]
        cursor.execute("SELECT objectif, sport, heures FROM objectifs WHERE id_user={}".format(id_user))
        objectif = cursor.fetchall()
        if objectif is not None:
            return render_template('objectifs.html', objectif=objectif, prenom=prenom)
        else : 
            return render_template('output.html', name = "Veuillez renseigner votre premier objectif")
    else:
        return redirect((f'/inscrits'))


@app.route('/heures/<string:objectif>/<string:objectif_sport>', methods=['GET'])
def heures(objectif, objectif_sport):
    objectif_sport=unquote(objectif_sport)
    obj=int(objectif)
    conn = sqlite3.connect('data.sqlite')
    cursor = conn.cursor()
    sql="SELECT calh FROM exercices WHERE nom='{}'".format(objectif_sport)
    cursor.execute(sql)
    calh=cursor.fetchone()
    print(calh[0])
    heure = obj/int(calh[0])
    if obj is not None:
        return render_template('output.html', name ="Il faudra effectuer {} heures de l'exercice '{}' pour atteindre votre objectif".format(heure,objectif_sport))
    else:
        return render_template('output.html', name = "L'exercice renseigné n'est pas dans la base de données, veuillez l'ajouter via /exercices avec la méthode PUT")

def get_exercise_names():
    conn = sqlite3.connect('data.sqlite')
    cursor  = conn.cursor()
    query = "SELECT nom FROM exercices"
    cursor.execute(query)
    exos = [row[0] for row in cursor.fetchall()]
    return exos


@app.route('/<name>')
def nom(name):

    return 'Salut! Je pense que tu as fait une erreur dans ta requête : {}'.format(name)

if __name__=='__main':
    app.run(debug=True)