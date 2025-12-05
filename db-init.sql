-- Script d'initialisation de la base de données pour les questions parlementaires
-- Généré à partir de questions-assemblee/data_model.md

-- 1. Table des Députés
CREATE TABLE deputes (
    id                      INTEGER PRIMARY KEY,
    nom                     VARCHAR(100) NOT NULL,
    prenom                  VARCHAR(100) NOT NULL,
    nom_complet             VARCHAR(200) NOT NULL,
    parti_politique         VARCHAR(100),
    groupe_parlementaire    VARCHAR(100),
    circonscription         VARCHAR(10),
    departement             VARCHAR(3),
    region                  VARCHAR(100),
    debut_mandat            DATE,
    fin_mandat              DATE,
    legislature             INTEGER,
    nombre_questions_total  INTEGER DEFAULT 0,
    nombre_questions_repondues INTEGER DEFAULT 0,
    delai_moyen_reponse     FLOAT,
    date_creation           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table des Ministères
CREATE TABLE ministeres (
    id                      SERIAL PRIMARY KEY,
    nom_officiel            VARCHAR(200) NOT NULL,
    nom_court               VARCHAR(100),
    code_ministere          VARCHAR(20),
    -- ministere_parent_id     INTEGER REFERENCES ministeres(id),
    niveau                  VARCHAR(30),
    date_creation           DATE,
    date_suppression        DATE,
    -- gouvernement            VARCHAR(100),
    nombre_questions_recues INTEGER DEFAULT 0,
    nombre_reponses_donnees INTEGER DEFAULT 0,
    delai_moyen_reponse     FLOAT,
    date_maj                TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE departements (
  nom TEXT PRIMARY KEY,
  latitude DOUBLE PRECISION NOT NULL,
  longitude DOUBLE PRECISION NOT NULL,
  code_region VARCHAR(5),
  code_dep VARCHAR(10)
);

-- 3. Table Principale : Questions
CREATE TABLE questions (
    id                          INTEGER PRIMARY KEY,
    numero_question             INTEGER NOT NULL,
    numero_jo                   VARCHAR(50),
    date_depot                  DATE NOT NULL,
    date_publication_jo         DATE,
    date_reponse                DATE,
    date_derniere_relance       DATE,
    type_question               VARCHAR(50) NOT NULL,
    statut                      VARCHAR(30) NOT NULL,
    thematique_principale       VARCHAR(100),
    thematique_secondaire       VARCHAR(100),
    sous_thematique             VARCHAR(100),
    objet                       TEXT NOT NULL,
    texte_question              TEXT NOT NULL,
    texte_reponse               TEXT,
    depute_id                   INTEGER REFERENCES deputes(id),
    ministere_destinataire_id   INTEGER REFERENCES ministeres(id),
    ministere_repondant_id      INTEGER REFERENCES ministeres(id),
    mots_cles                   TEXT[],
    entites_nommees             JSONB,
    score_sentiment             FLOAT,
    score_urgence               FLOAT,
    score_complexite            FLOAT,
    nombre_mots_question        INTEGER,
    nombre_mots_reponse         INTEGER,
    delai_reponse_jours         INTEGER,
    nombre_relances             INTEGER DEFAULT 0,
    niveau_territorial          VARCHAR(30),
    regions_concernees          TEXT[],
    departements_concernes      TEXT[],
    source_fichier              VARCHAR(255),
    version_traitement          VARCHAR(20),
    confiance_classification    FLOAT,
    date_creation               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contrainte unique sur numero_question
ALTER TABLE questions ADD CONSTRAINT uk_questions_numero UNIQUE (numero_question);

-- Index recommandés
CREATE INDEX idx_questions_date_depot ON questions(date_depot);
CREATE INDEX idx_questions_thematique ON questions(thematique_principale);
CREATE INDEX idx_questions_depute ON questions(depute_id);
CREATE INDEX idx_questions_ministere ON questions(ministere_destinataire_id);
CREATE INDEX idx_questions_statut ON questions(statut);
CREATE INDEX idx_questions_objet_fts ON questions USING gin(to_tsvector('french', objet));
CREATE INDEX idx_questions_texte_fts ON questions USING gin(to_tsvector('french', texte_question));
CREATE INDEX idx_questions_date_statut ON questions(date_depot, statut);
CREATE INDEX idx_questions_delai ON questions(delai_reponse_jours) WHERE delai_reponse_jours IS NOT NULL;

-- Vues utiles
CREATE VIEW vue_questions_enrichies AS
SELECT 
    q.*,
    d.nom_complet as depute_nom,
    d.parti_politique,
    d.circonscription,
    d.region,
    m.nom_officiel as ministere_nom,
    NULL as thematique_nom, -- Champ placeholder, à adapter si table thematiques
    CASE 
        WHEN q.date_reponse IS NOT NULL THEN 'Répondue'
        WHEN q.date_depot < CURRENT_DATE - INTERVAL '2 months' THEN 'En retard'
        ELSE 'En cours'
    END as statut_enrichi
FROM questions q
LEFT JOIN deputes d ON q.depute_id = d.id
LEFT JOIN ministeres m ON q.ministere_destinataire_id = m.id;

CREATE VIEW vue_stats_deputes AS
SELECT 
    d.*,
    COUNT(q.id) as nb_questions,
    COUNT(CASE WHEN q.statut = 'repondue' THEN 1 END) as nb_reponses,
    AVG(q.delai_reponse_jours) as delai_moyen,
    MAX(q.date_depot) as derniere_question
FROM deputes d
LEFT JOIN questions q ON d.id = q.depute_id
GROUP BY d.id;

-- Contraintes et règles métier
ALTER TABLE questions ADD CONSTRAINT chk_dates_coherentes 
    CHECK (date_depot <= COALESCE(date_reponse, CURRENT_DATE));
ALTER TABLE questions ADD CONSTRAINT chk_score_sentiment 
    CHECK (score_sentiment >= -1 AND score_sentiment <= 1);
ALTER TABLE questions ADD CONSTRAINT chk_delai_positif 
    CHECK (delai_reponse_jours >= 0);



-- Trigger pour mise à jour automatique des métriques
CREATE OR REPLACE FUNCTION update_question_metrics()
RETURNS TRIGGER AS $$
BEGIN
    NEW.nombre_mots_question = array_length(string_to_array(NEW.texte_question, ' '), 1);
    IF NEW.texte_reponse IS NOT NULL THEN
        NEW.nombre_mots_reponse = array_length(string_to_array(NEW.texte_reponse, ' '), 1);
    END IF;
    IF NEW.date_reponse IS NOT NULL AND NEW.date_depot IS NOT NULL THEN
        NEW.delai_reponse_jours = NEW.date_reponse - NEW.date_depot;
    END IF;
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_question_metrics
    BEFORE INSERT OR UPDATE ON questions
    FOR EACH ROW
    EXECUTE FUNCTION update_question_metrics(); 


-- Trigger pour mise à jour automatique des députes
CREATE OR REPLACE FUNCTION update_depute_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Met à jour le nombre total de questions
    UPDATE deputes
    SET 
        nombre_questions_total = (
            SELECT COUNT(*) FROM questions WHERE depute_id = NEW.depute_id
        ),
        nombre_questions_repondues = (
            SELECT COUNT(*) FROM questions WHERE depute_id = NEW.depute_id AND statut = 'repondue'
        ),
        delai_moyen_reponse = (
            SELECT AVG(delai_reponse_jours) FROM questions WHERE depute_id = NEW.depute_id AND delai_reponse_jours IS NOT NULL
        ),
        date_modification = CURRENT_TIMESTAMP
    WHERE id = NEW.depute_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_depute_metrics
AFTER INSERT OR UPDATE OR DELETE ON questions
FOR EACH ROW
EXECUTE FUNCTION update_depute_metrics();




-- Trigger pour mise à jour automatique des ministères
CREATE OR REPLACE FUNCTION update_ministere_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Met à jour les métriques pour le ministère destinataire
    IF NEW.ministere_destinataire_id IS NOT NULL THEN
        UPDATE ministeres
        SET 
            nombre_questions_recues = (
                SELECT COUNT(*) FROM questions WHERE ministere_destinataire_id = NEW.ministere_destinataire_id
            ),
            nombre_reponses_donnees = (
                SELECT COUNT(*) FROM questions WHERE ministere_destinataire_id = NEW.ministere_destinataire_id AND statut = 'repondue'
            ),
            delai_moyen_reponse = (
                SELECT AVG(delai_reponse_jours) FROM questions WHERE ministere_destinataire_id = NEW.ministere_destinataire_id AND delai_reponse_jours IS NOT NULL
            ),
            date_maj = CURRENT_TIMESTAMP
        WHERE id = NEW.ministere_destinataire_id;
    END IF;
    -- Met à jour les métriques pour le ministère répondant (si différent)
    IF NEW.ministere_repondant_id IS NOT NULL AND NEW.ministere_repondant_id <> NEW.ministere_destinataire_id THEN
        UPDATE ministeres
        SET 
            nombre_questions_recues = (
                SELECT COUNT(*) FROM questions WHERE ministere_repondant_id = NEW.ministere_repondant_id
            ),
            nombre_reponses_donnees = (
                SELECT COUNT(*) FROM questions WHERE ministere_repondant_id = NEW.ministere_repondant_id AND statut = 'repondue'
            ),
            delai_moyen_reponse = (
                SELECT AVG(delai_reponse_jours) FROM questions WHERE ministere_repondant_id = NEW.ministere_repondant_id AND delai_reponse_jours IS NOT NULL
            ),
            date_maj = CURRENT_TIMESTAMP
        WHERE id = NEW.ministere_repondant_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_ministere_metrics
AFTER INSERT OR UPDATE OR DELETE ON questions
FOR EACH ROW
EXECUTE FUNCTION update_ministere_metrics();

-- Insérer les ministères
INSERT INTO ministeres (code_ministere, nom_officiel) VALUES
('TRAVAIL', 'Ministère du Travail, de l''Emploi et des Relations avec les Institutions'),
('AFFEXT', 'Ministère de l''Intégration africaine et des Affaires étrangères'),
('ARMEE', 'Ministère des Forces armées'),
('JUSTICE', 'Ministère de la Justice, Garde des Sceaux'),
('INTERIEUR', 'Ministère de l''Intérieur et de la Sécurité publique'),
('ENERGIE', 'Ministère de l''Énergie, du Pétrole et des Mines'),
('ECO_PLAN', 'Ministère de l''Économie du Plan et de la Coopération'),
('FINANCES', 'Ministère des Finances et du Budget'),
('ENVIRON', 'Ministère de l''Environnement et de la Transition écologique'),
('FORMATION', 'Ministère de la Formation professionnelle et Porte-parole du Gouvernement'),
('HYDRAULIQUE', 'Ministère de l''Hydraulique et de l''Assainissement'),
('MCTN', 'Ministère de la Communication, des Télécommunications et du Numérique (MCTN)'),
('MESRI', 'Ministère de l''Enseignement supérieur, de la Recherche et de l''Innovation (MESRI)'),
('INDUSTRIE', 'Ministère de l''Industrie et du Commerce'),
('PECHES', 'Ministère des Pêches, des Infrastructures maritimes et portuaires'),
('FAMILLE', 'Ministère de la Famille et des Solidarités'),
('MITTA', 'Ministère des Infrastructures, des Transports terrestres et aériens'),
('URBANISME', 'Ministère de l''Urbanisme, des Collectivités territoriales et de l''Aménagement des Territoires'),
('EDUCATION', 'Ministère de l''Education nationale'),
('SANTE', 'Ministère de la Santé et de l''Action sociale'),
('FONCPUB', 'Ministère de la Fonction publique et de la Réforme du Service public'),
('JEUNESSE', 'Ministère de la Jeunesse, des Sports et de la Culture'),
('AGRICULTURE', 'Ministère de l''Agriculture, de la Souveraineté alimentaire et de l''Elevage'),
('MICROFIN', 'Ministère de la Microfinance, de l''Economie sociale et solidaire'),
('TOURISME', 'Ministère du Tourisme et de l''Artisanat');



INSERT INTO departements (nom, latitude, longitude) VALUES
  ('Dakar',     14.75,   -17.3333),  -- région / département Dakar :contentReference[oaicite:1]{index=1}
  ('Guediawaye',14.75,   -17.3333),  -- même région comme approximation
  ('Pikine',    14.75,   -17.3333),  -- idem
  ('Rufisque',  14.75,   -17.3333),
  ('Bambey',    14.75,   -16.25),    -- région Diourbel centre ~14°45′N 16°15′W :contentReference[oaicite:2]{index=2}
  ('Diourbel',  14.75,   -16.25),
  ('Mbacke',    14.75,   -16.25),
  ('Fatick',    14.3667, -16.1333),  -- région Fatick centre :contentReference[oaicite:3]{index=3}
  ('Foundiougne',14.3667,-16.1333),
  ('Gossas',    14.3667, -16.1333),
  ('Birkilane', 14.30,   -15.90),     -- région Kaffrine / Diourbel estimation autour ~14.3,‑15.9
  ('Kaffrine',  14.30,   -15.90),
  ('Koungheul', 14.30,   -15.90),
  ('Malem Hodar',14.30,  -15.90),
  ('Guinguineo',14.50,   -16.30),     -- région Kaolack centre ≈14°30′N,‑16°30′W :contentReference[oaicite:4]{index=4}
  ('Kaolack',   14.50,   -16.30),
  ('Nioro du Rip',14.50, -16.30),
  ('Kedougou',  12.0833, -12.8167),   -- région Kédougou centre ~12°05′N,‑12°49′W approximation
  ('Salemata',  12.0833, -12.8167),
  ('Saraya',    12.0833, -12.8167),
  ('Kolda',     13.0864, -14.8181),   -- région Kolda chef-lieu :contentReference[oaicite:5]{index=5}
  ('Medina Yoro Foulah',13.0864,-14.8181),
  ('Velingara', 13.0864, -14.8181),
  ('Kebemer',   15.6142, -16.2287),   -- région Louga centre ~Louga ville :contentReference[oaicite:6]{index=6}
  ('Linguere',  15.6142, -16.2287),
  ('Louga',     15.6142, -16.2287),
  ('Kanel',     15.6600, -13.2577),   -- région Matam centre ~Matam ville :contentReference[oaicite:7]{index=7}
  ('Matam',     15.6600, -13.2577),
  ('Ranerou',   15.6600, -13.2577),
  ('Dagana',    16.2200, -14.8000),   -- région Saint-Louis centre ~16°13′N,‑14°48′W :contentReference[oaicite:8]{index=8}
  ('Podor',     16.2200, -14.8000),
  ('Saint-Louis',16.2200,-14.8000),
  ('Bounkiling',12.6000, -15.6000),   -- région Sedhiou / Ziguinchor bord sud (approx)
  ('Goudomp',   12.6000, -15.6000),
  ('Sedhiou',   12.6000, -15.6000),
  ('Bakel',     13.5667, -12.8167),   -- région Tambacounda centre ~13°18′N,‑12°49′W :contentReference[oaicite:9]{index=9}
  ('Goudiry',   13.5667, -12.8167),
  ('Koumpentoum',13.5667,-12.8167),
  ('Tambacounda',13.5667,-12.8167),
  ('Mbour',     14.7167, -17.4677),   -- région Thiès centre ~14°46′N,‑16°54′W :contentReference[oaicite:10]{index=10}
  ('Thies',     14.7167, -16.9000),
  ('Tivaouane', 14.7167, -16.9000),
  ('Bignona',   12.8000, -16.2500),   -- région Ziguinchor bord sud-ouest estimation
  ('Oussouye',  12.8000, -16.2500),
  ('Ziguinchor',12.8000, -16.2500);


-- Étape 3 : mise à jour avec les codes ISO pour les régions et des codes personnalisés pour les départements
UPDATE departements
SET 
  code_region = CASE 
    WHEN nom = 'Dakar'                THEN 'SN-DK'
    WHEN nom = 'Guediawaye'           THEN 'SN-DK'
    WHEN nom = 'Pikine'               THEN 'SN-DK'
    WHEN nom = 'Rufisque'             THEN 'SN-DK'
    
    WHEN nom = 'Bambey'               THEN 'SN-DB'
    WHEN nom = 'Diourbel'             THEN 'SN-DB'
    WHEN nom = 'Mbacke'               THEN 'SN-DB'
    
    WHEN nom = 'Fatick'               THEN 'SN-FK'
    WHEN nom = 'Foundiougne'          THEN 'SN-FK'
    WHEN nom = 'Gossas'               THEN 'SN-FK'
    
    WHEN nom = 'Birkilane'            THEN 'SN-KA'
    WHEN nom = 'Kaffrine'             THEN 'SN-KA'
    WHEN nom = 'Koungheul'            THEN 'SN-KA'
    WHEN nom = 'Malem Hodar'          THEN 'SN-KA'
    
    WHEN nom = 'Guinguineo'           THEN 'SN-KL'
    WHEN nom = 'Kaolack'              THEN 'SN-KL'
    WHEN nom = 'Nioro du Rip'         THEN 'SN-KL'
    
    WHEN nom = 'Kedougou'             THEN 'SN-KE'
    WHEN nom = 'Salemata'             THEN 'SN-KE'
    WHEN nom = 'Saraya'               THEN 'SN-KE'
    
    WHEN nom = 'Kolda'                THEN 'SN-KD'
    WHEN nom = 'Medina Yoro Foulah'   THEN 'SN-KD'
    WHEN nom = 'Velingara'            THEN 'SN-KD'
    
    WHEN nom = 'Kebemer'              THEN 'SN-LG'
    WHEN nom = 'Linguere'             THEN 'SN-LG'
    WHEN nom = 'Louga'                THEN 'SN-LG'
    
    WHEN nom = 'Kanel'                THEN 'SN-MT'
    WHEN nom = 'Matam'                THEN 'SN-MT'
    WHEN nom = 'Ranerou'              THEN 'SN-MT'
    
    WHEN nom = 'Dagana'               THEN 'SN-SL'
    WHEN nom = 'Podor'                THEN 'SN-SL'
    WHEN nom = 'Saint-Louis'          THEN 'SN-SL'
    
    WHEN nom = 'Bounkiling'           THEN 'SN-SE'
    WHEN nom = 'Goudomp'              THEN 'SN-SE'
    WHEN nom = 'Sedhiou'              THEN 'SN-SE'
    
    WHEN nom = 'Bakel'                THEN 'SN-TC'
    WHEN nom = 'Goudiry'              THEN 'SN-TC'
    WHEN nom = 'Koumpentoum'          THEN 'SN-TC'
    WHEN nom = 'Tambacounda'          THEN 'SN-TC'
    
    WHEN nom = 'Mbour'                THEN 'SN-TH'
    WHEN nom = 'Thies'                THEN 'SN-TH'
    WHEN nom = 'Tivaouane'            THEN 'SN-TH'
    
    WHEN nom = 'Bignona'              THEN 'SN-ZG'
    WHEN nom = 'Oussouye'             THEN 'SN-ZG'
    WHEN nom = 'Ziguinchor'           THEN 'SN-ZG'
    ELSE NULL
  END,
  
  code_dep = CASE 
    WHEN nom = 'Dakar'                THEN 'DK-01'
    WHEN nom = 'Guediawaye'           THEN 'DK-02'
    WHEN nom = 'Pikine'               THEN 'DK-03'
    WHEN nom = 'Rufisque'             THEN 'DK-04'
    
    WHEN nom = 'Bambey'               THEN 'DB-01'
    WHEN nom = 'Diourbel'             THEN 'DB-02'
    WHEN nom = 'Mbacke'               THEN 'DB-03'
    
    WHEN nom = 'Fatick'               THEN 'FK-01'
    WHEN nom = 'Foundiougne'          THEN 'FK-02'
    WHEN nom = 'Gossas'               THEN 'FK-03'
    
    WHEN nom = 'Birkilane'            THEN 'KA-01'
    WHEN nom = 'Kaffrine'             THEN 'KA-02'
    WHEN nom = 'Koungheul'            THEN 'KA-03'
    WHEN nom = 'Malem Hodar'          THEN 'KA-04'
    
    WHEN nom = 'Guinguineo'           THEN 'KL-01'
    WHEN nom = 'Kaolack'              THEN 'KL-02'
    WHEN nom = 'Nioro du Rip'         THEN 'KL-03'
    
    WHEN nom = 'Kedougou'             THEN 'KE-01'
    WHEN nom = 'Salemata'             THEN 'KE-02'
    WHEN nom = 'Saraya'               THEN 'KE-03'
    
    WHEN nom = 'Kolda'                THEN 'KD-01'
    WHEN nom = 'Medina Yoro Foulah'   THEN 'KD-02'
    WHEN nom = 'Velingara'            THEN 'KD-03'
    
    WHEN nom = 'Kebemer'              THEN 'LG-01'
    WHEN nom = 'Linguere'             THEN 'LG-02'
    WHEN nom = 'Louga'                THEN 'LG-03'
    
    WHEN nom = 'Kanel'                THEN 'MT-01'
    WHEN nom = 'Matam'                THEN 'MT-02'
    WHEN nom = 'Ranerou'              THEN 'MT-03'
    
    WHEN nom = 'Dagana'               THEN 'SL-01'
    WHEN nom = 'Podor'                THEN 'SL-02'
    WHEN nom = 'Saint-Louis'          THEN 'SL-03'
    
    WHEN nom = 'Bounkiling'           THEN 'SE-01'
    WHEN nom = 'Goudomp'              THEN 'SE-02'
    WHEN nom = 'Sedhiou'              THEN 'SE-03'
    
    WHEN nom = 'Bakel'                THEN 'TC-01'
    WHEN nom = 'Goudiry'              THEN 'TC-02'
    WHEN nom = 'Koumpentoum'          THEN 'TC-03'
    WHEN nom = 'Tambacounda'          THEN 'TC-04'
    
    WHEN nom = 'Mbour'                THEN 'TH-01'
    WHEN nom = 'Thies'                THEN 'TH-02'
    WHEN nom = 'Tivaouane'            THEN 'TH-03'
    
    WHEN nom = 'Bignona'              THEN 'ZG-01'
    WHEN nom = 'Oussouye'             THEN 'ZG-02'
    WHEN nom = 'Ziguinchor'           THEN 'ZG-03'
    ELSE NULL
  END;