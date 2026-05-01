DROP TABLE IF EXISTS participation CASCADE;
DROP TABLE IF EXISTS acte CASCADE;
DROP TABLE IF EXISTS personne CASCADE;
DROP TABLE IF EXISTS type_acte CASCADE;
DROP TABLE IF EXISTS commune CASCADE;
DROP TABLE IF EXISTS departement CASCADE;

CREATE TABLE departement (
    codedepart BIGINT PRIMARY KEY,
    nomdepart VARCHAR(100) NOT NULL
);

CREATE TABLE commune (
    idcom SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    codedepat BIGINT NOT NULL,
    FOREIGN KEY (codedepat) REFERENCES departement(codedepart)
);

CREATE TABLE type_acte (
    idtype SERIAL PRIMARY KEY,
    libelle VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE personne (
    idpers SERIAL PRIMARY KEY,
    nom VARCHAR(200),
    prenom VARCHAR(200)
);

CREATE TABLE acte (
    idact INTEGER PRIMARY KEY,
    date_act DATE,
    idtype INTEGER NOT NULL,
    idcom INTEGER NOT NULL,
    num_vue VARCHAR(50),
    FOREIGN KEY (idtype) REFERENCES type_acte(idtype),
    FOREIGN KEY (idcom)  REFERENCES commune(idcom)
);

CREATE TABLE participation (
    idpers INTEGER NOT NULL,
    idact INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (idpers, idact, role),
    FOREIGN KEY (idpers) REFERENCES personne(idpers),
    FOREIGN KEY (idact)  REFERENCES acte(idact)
);

INSERT INTO departement (codedepart, nomdepart) VALUES
    (44, 'Loire-Atlantique'),
    (49, 'Maine-et-Loire'),
    (79, 'Deux-Sèvres'),
    (85, 'Vendée');

INSERT INTO type_acte (libelle) VALUES
    ('Certificat de mariage'),
    ('Contrat de mariage'),
    ('Divorce'),
    ('Mariage'),
    ('Promesse de mariage - fiançailles'),
    ('Publication de mariage'),
    ('Rectification de mariage');



CREATE INDEX idx_acte_date ON acte(date_act);
CREATE INDEX idx_acte_idcom ON acte(idcom);
CREATE INDEX idx_acte_idtype ON acte(idtype);
CREATE INDEX idx_participation_idact ON participation(idact);
CREATE INDEX idx_participation_idpers ON participation(idpers);
CREATE INDEX idx_commune_codedepat ON commune(codedepat);