-- Q1 : Quantité de communes par département
SELECT d.codedepart, d.nomdepart, COUNT(c.idcom) AS nb_communes
FROM departement d
JOIN commune c ON c.codedepat = d.codedepart
GROUP BY d.codedepart, d.nomdepart
ORDER BY d.codedepart;
/**
-- Q2 : Quantité d'actes à LUÇON
SELECT COUNT(*) AS nb_actes_lucon
FROM acte a
JOIN commune c ON c.idcom = a.idcom
WHERE UPPER(c.nom) = 'LUÇON';

-- Q3 : Contrats de mariage avant 1855
SELECT COUNT(*) AS nb_contrats_avant_1855
FROM acte a
JOIN type_acte t ON t.idtype = a.idtype
WHERE t.libelle = 'Contrat de mariage' AND EXTRACT(YEAR FROM a.date_act) < 1855;

-- Q4 : Commune avec le plus de publications de mariage
SELECT c.nom, d.codedepart, COUNT(*) AS nb_publications
FROM acte a
JOIN type_acte t ON t.idtype = a.idtype
JOIN commune c ON c.idcom = a.idcom
JOIN departement d ON d.codedepart = c.codedepat
WHERE t.libelle = 'Publication de mariage'
GROUP BY c.nom, d.codedepart
ORDER BY nb_publications DESC
LIMIT 1;

-- Q5 : Premier et dernier acte
SELECT MIN(date_act) AS premier_acte, MAX(date_act) AS dernier_acte
FROM acte;

-- BONUS : Retrouverles participants d'un acte avec leurs rôles
SELECT p.nom, p.prenom, pa.role
FROM participation pa
JOIN personne p ON p.idpers = pa.idpers
WHERE pa.idact = 2
ORDER BY pa.role;

-- BONUS PERSO : Rechercher tous les actes d'une personne par nom
SELECT a.idact, t.libelle, a.date_act, c.nom AS commune, pa.role
FROM participation pa
JOIN acte a ON a.idact  = pa.idact
JOIN type_acte t ON t.idtype = a.idtype
JOIN commune c ON c.idcom  = a.idcom
JOIN personne p ON p.idpers = pa.idpers
WHERE UPPER(p.nom) = 'ABADIE'
ORDER BY a.date_act;  **/