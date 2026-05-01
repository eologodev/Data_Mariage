# Modélisation BDD - Archives de Mariages (PostgreSQL / Python)

> Projet universitaire - Modélisation des Bases de Données  


---

## Description

Modélisation, normalisation et exploitation d'un jeu de données réel issu des **archives départementales françaises** : actes de mariage de 4 départements (Loire-Atlantique, Maine-et-Loire, Deux-Sèvres, Vendée).

**564 000 enregistrements** nettoyés, modélisés et importés dans PostgreSQL sous Linux, avec production de KPI statistiques via des requêtes SQL avancées.

---

## Pipeline

```
CSV brut (564 000 lignes)
      
      
Nettoyage Python (psycopg2 + pandas)
   Gestion des valeurs nulles / N/A
   Normalisation des dates (dd/mm/yyyy → DATE)
   Déduplication des entités (personnes, communes)
      
      
Modèle relationnel PostgreSQL
   6 tables normalisées (3NF)
   Clés étrangères + contraintes d'intégrité
   Index sur les colonnes de jointure
      
      
Requêtes SQL avancées  KPI
```

---

## Modèle de données

```
departement -> commune -> acte -> participation -> personne
                               |-> type_acte
```

 Table | Description 

 `departement` | 4 départements (44, 49, 79, 85) 
 `commune` | Communes par département 
 `type_acte` | Mariage, contrat, divorce, fiançailles... 
 `acte` | Acte civil avec date, commune, type 
 `personne` | Individus impliqués dans les actes 
 `participation` | Rôle de chaque personne dans chaque acte 

---

## KPI produits

 Question | Requête 

 Nombre de communes par département | `GROUP BY` + `COUNT` 
 Nombre d'actes à Luçon | `JOIN` commune + filtre 
 Contrats de mariage avant 1855 | `EXTRACT(YEAR)` 
 Commune avec le plus de publications | `ORDER BY` + `LIMIT 1` 
 Premier et dernier acte enregistré | `MIN / MAX` sur date 
 Tous les actes d'une personne par nom | Jointure multi-tables 

---

## Technologies

 Outil | Rôle 

 Python / psycopg2 | Import et nettoyage des données 
 PostgreSQL | Base de données relationnelle 
 SQL | Modélisation + requêtes analytiques 
 Linux | Environnement d'exécution 

---

## Lancer le projet

```bash
# 1. Créer la base de données
psql -U postgres -c "CREATE DATABASE mariages_db;"

# 2. Créer le schéma
psql -U postgres -d mariages_db -f mariages_db.sql

# 3. Importer les données (adapter le chemin CSV dans import_data.py)
python3 import_data.py

# 4. Lancer les requêtes
psql -U postgres -d mariages_db -f requete.sql
```

---

## Structure

```
.
 mariages_db.sql           — schéma complet (tables, index, contraintes)
 mariages_db_bonus.sql     — schéma étendu (version bonus)
 requete.sql               — requêtes KPI principales
 mariages_bonus_requete.sql — requêtes bonus avancées
 import_data.py            — import CSV → PostgreSQL
 import_bonus.py           — import version bonus
 compteRendu_FALL-OLOGOUDOU.pdf — rapport complet
```

---

## Ce que ce projet m'a appris

- Concevoir un modèle relationnel normalisé (3NF) à partir de données brutes réelles
- Gérer le nettoyage et l'import de données massives (564 000 lignes) en Python
- Optimiser les requêtes SQL avec des index ciblés
- Produire des indicateurs statistiques exploitables à partir d'archives historiques
