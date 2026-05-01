# Projet Modélisation BDD 2025-2026

import csv
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host':'localhost',
    'port': 5434,           
    'dbname':'mariages_db',
    'user':'',
    'password':''
}

CSV_FILE = r"C:\Users\ASUS\Documents\Licence informatique\licence3\Semestre2\ModelisationBaseEtDonnees\mariages\mariages_L3_5k.csv"

def clean(val):
    val = val.strip()
    return None if val.lower() in ('n/a', '', 'null') else val

def parse_date(s):
    try:
        return datetime.strptime(s.strip(), '%d/%m/%Y').date()
    except Exception:
        return None

def insert_personne(cur, nom, prenom):
    if nom is None and prenom is None:
        return None
    cur.execute(
        "INSERT INTO personne (nom, prenom) VALUES (%s, %s) RETURNING idpers",
        (nom, prenom)
    )
    return cur.fetchone()[0]

def insert_participation(cur, idpers, idact, role):
    if idpers is None:
        return
    cur.execute(
        "INSERT INTO participation (idpers, idact, role) VALUES (%s, %s, %s)",
        (idpers, idact, role)
    )

def import_data():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        rows = list(csv.reader(f))

    print(f"Lignes a importer : {len(rows)}")

    cur.execute("SELECT libelle, idtype FROM type_acte")
    type_map = {row[0]: row[1] for row in cur.fetchall()}

    # Communes dedupliquees
    communes_seen = {}
    for row in rows:
        nom_commune = clean(row[12])
        code_dept   = int(row[13].strip())
        key = (nom_commune, code_dept)
        if key not in communes_seen:
            cur.execute(
                "INSERT INTO commune (nom, codedepat) VALUES (%s, %s) RETURNING idcom",
                (nom_commune, code_dept)
            )
            communes_seen[key] = cur.fetchone()[0]

    print(f"Communes inserees : {len(communes_seen)}")

    nb_actes = 0
    nb_personnes = 0

    for row in rows:
        idact = int(row[0])
        type_lib = clean(row[1])

        # Epoux (personne A)
        nom_epoux = clean(row[2]); pren_epoux = clean(row[3])
        # Pere epoux : seulement prenom dans le CSV
        pren_pere_epoux = clean(row[4])
        # Mere epoux : nom + prenom
        nom_mere_epoux = clean(row[5]); pren_mere_epoux = clean(row[6])
        # Epouse (personne B)
        nom_epouse = clean(row[7]); pren_epouse = clean(row[8])
        # Pere epouse : seulement prenom dans le CSV
        pren_pere_epouse = clean(row[9])
        # Mere epouse : nom + prenom
        nom_mere_epouse = clean(row[10]); pren_mere_epouse = clean(row[11])

        nom_commune = clean(row[12])
        code_dept = int(row[13].strip())
        date_acte = parse_date(row[14])
        num_vue = clean(row[15])

        # Inserer les 6 personnes (None si donnees absentes)
        idpers_epoux = insert_personne(cur, nom_epoux, pren_epoux)
        idpers_epouse = insert_personne(cur, nom_epouse, pren_epouse)
        idpers_pere_epoux = insert_personne(cur, None, pren_pere_epoux)
        idpers_mere_epoux  = insert_personne(cur, nom_mere_epoux, pren_mere_epoux)
        idpers_pere_epouse = insert_personne(cur, None, pren_pere_epouse)
        idpers_mere_epouse = insert_personne(cur, nom_mere_epouse, pren_mere_epouse)

        nb_personnes += sum(1 for x in [
            idpers_epoux, idpers_epouse,
            idpers_pere_epoux, idpers_mere_epoux,
            idpers_pere_epouse, idpers_mere_epouse
        ] if x is not None)

        # Inserer l'acte
        idcom = communes_seen[(nom_commune, code_dept)]
        idtype = type_map[type_lib]
        cur.execute(
            "INSERT INTO acte (idact, date_act, idtype, idcom, num_vue) VALUES (%s,%s,%s,%s,%s)",
            (idact, date_acte, idtype, idcom, num_vue)
        )

        # Inserer les participations avec roles
        insert_participation(cur, idpers_epoux, idact,'epoux')
        insert_participation(cur, idpers_epouse, idact, 'epouse')
        insert_participation(cur, idpers_pere_epoux, idact, 'pere_epoux')
        insert_participation(cur, idpers_mere_epoux, idact, 'mere_epoux')
        insert_participation(cur, idpers_pere_epouse, idact, 'pere_epouse')
        insert_participation(cur, idpers_mere_epouse, idact, 'mere_epouse')

        nb_actes += 1

    conn.commit()
    print(f"Actes inseres: {nb_actes}")
    print(f"Personnes inserees: {nb_personnes}")
    print("Import termine avec succes !")
    cur.close()
    conn.close()

if __name__ == '__main__':
    import_data()
