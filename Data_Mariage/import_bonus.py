# Script d'import BONUS - mariages.csv (fichier bruité 564k lignes)
# Corrections : encodage latin-1, valeurs manquantes, données corrompues
 
import csv
import psycopg2
from datetime import datetime
import re
 
DB_CONFIG = {
    'host': 'localhost',
    'port': 5434,
    'dbname': 'mariagesBonus',
    'user': '',
    'password': ''
}
 
# Change ce chemin vers ton fichier mariages.csv
CSV_FILE = r"C:\Users\ASUS\Documents\Licence informatique\licence3\Semestre2\ModelisationBaseEtDonnees\mariages\mariages_L3.csv"
 
# Departements valides
DEPTS_VALIDES = {'44', '49', '79', '85'}
 
# Types d'actes valides
TYPES_VALIDES = {
    'Certificat de mariage', 'Contrat de mariage', 'Divorce',
    'Mariage', 'Promesse de mariage - fiançailles',
    'Publication de mariage', 'Rectification de mariage'
}
 
def fix_encoding(val):
    """Corrige les problèmes d'encodage latin-1 lu comme UTF-8."""
    try:
        return val.encode('latin-1').decode('utf-8')
    except Exception:
        return val
 
def clean(val):
    """Nettoie une valeur : None si n/a, vide, null ou +."""
    val = val.strip()
    # Supprimer les + en fin de valeur (bruit dans le fichier)
    val = re.sub(r'\s*\+\s*$', '', val).strip()
    return None if val.lower() in ('n/a', '', 'null', '+', 'n/') else val
 
def parse_date(s):
    """Parse DD/MM/YYYY, retourne None si invalide."""
    if not s:
        return None
    s = s.strip()
    # Corriger les formats de date bruités
    s = re.sub(r'[^0-9/]', '', s)
    try:
        return datetime.strptime(s, '%d/%m/%Y').date()
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
 
def import_bonus():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
 
    # Lire avec encodage latin-1 pour corriger le bruit
    rows = []
    with open(CSV_FILE,'r', encoding='latin-1') as f:
        reader = csv.reader(f)
        for row in reader:
            # Corriger l'encodage de chaque cellule
            rows.append([fix_encoding(cell) for cell in row])
 
    print(f"Lignes lues : {len(rows)}")
 
    cur.execute("SELECT libelle, idtype FROM type_acte")
    type_map = {row[0]: row[1] for row in cur.fetchall()}
 
    cur.execute("SELECT codedepart FROM departement")
    depts_db = {str(row[0]) for row in cur.fetchall()}
 
    # Communes dedupliquees
    communes_seen = {}
    ignores = 0
 
    for row in rows:
        # Verifier que la ligne a bien 16 colonnes
        if len(row) < 16:
            ignores += 1
            continue
 
        # Verifier departement valide
        dept = clean(row[13])
        if dept not in depts_db:
            ignores += 1
            continue
 
        # Verifier type d'acte valide
        type_lib = clean(row[1])
        if type_lib not in type_map:
            ignores += 1
            continue
 
        nom_commune = clean(row[12])
        if nom_commune is None:
            ignores += 1
            continue
 
        key = (nom_commune, int(dept))
        if key not in communes_seen:
            cur.execute(
                "INSERT INTO commune (nom, codedepat) VALUES (%s, %s) RETURNING idcom",
                (nom_commune, int(dept))
            )
            communes_seen[key] = cur.fetchone()[0]
 
    print(f"Communes inserees : {len(communes_seen)}")
    print(f"Lignes ignorees (invalides) : {ignores}")
 
    nb_actes = 0
    nb_erreurs = 0
 
    for row in rows:
        if len(row) < 16:
            continue
 
        dept = clean(row[13])
        type_lib = clean(row[1])
 
        if dept not in depts_db or type_lib not in type_map:
            continue
 
        nom_commune = clean(row[12])
        if nom_commune is None:
            continue
 
        try:
            idact = int(row[0])
        except Exception:
            nb_erreurs += 1
            continue
 
        date_acte = parse_date(row[14])
        num_vue   = clean(row[15])
 
        # Personnes
        idpers_epoux = insert_personne(cur, clean(row[2]), clean(row[3]))
        idpers_epouse = insert_personne(cur, clean(row[7]), clean(row[8]))
        idpers_pere_epoux = insert_personne(cur, None, clean(row[4]))
        idpers_mere_epoux = insert_personne(cur, clean(row[5]), clean(row[6]))
        idpers_pere_epouse = insert_personne(cur, None, clean(row[9]))
        idpers_mere_epouse = insert_personne(cur, clean(row[10]), clean(row[11]))
 
        # Acte
        idcom = communes_seen[(nom_commune, int(dept))]
        idtype = type_map[type_lib]
 
        try:
            cur.execute(
                "INSERT INTO acte (idact, date_act, idtype, idcom, num_vue) VALUES (%s,%s,%s,%s,%s)",
                (idact, date_acte, idtype, idcom, num_vue)
            )
        except Exception:
            # idact deja present (doublon) : on ignore
            conn.rollback()
            nb_erreurs += 1
            continue
 
        insert_participation(cur, idpers_epoux, idact, 'epoux')
        insert_participation(cur, idpers_epouse, idact, 'epouse')
        insert_participation(cur, idpers_pere_epoux, idact, 'pere_epoux')
        insert_participation(cur, idpers_mere_epoux, idact, 'mere_epoux')
        insert_participation(cur, idpers_pere_epouse, idact, 'pere_epouse')
        insert_participation(cur, idpers_mere_epouse, idact, 'mere_epouse')
 
        nb_actes += 1
 
        # Commit par batch de 1000 pour éviter les timeouts
        if nb_actes % 1000 == 0:
            conn.commit()
            print(f"{nb_actes} actes importes...")
 
    conn.commit()
    print(f"\nImport terminé !")
    print(f"Actes importes: {nb_actes}")
    print(f"Erreurs/doublons: {nb_erreurs}")
    cur.close()
    conn.close()
 
if __name__ == '__main__':
    import_bonus()