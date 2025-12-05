import asyncpg
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from src.models.question import Question
from src.models.depute import DeputeIn
from src.utils.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseLoader:
    def __init__(self):
        self.pool = None
    
    async def initialize(self):
        """Initialise le pool de connexions"""
        self.pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=5,
            max_size=20
        )
    
    async def close(self):
        """Ferme le pool de connexions"""
        if self.pool:
            await self.pool.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager pour les connexions"""
        async with self.pool.acquire() as conn:
            yield conn
    
    async def bulk_insert_questions(self, questions: List[Question]):
        """Insertion en masse des questions"""
        
        if not questions:
            return
        
        async with self.get_connection() as conn:
            # Préparation des données
            values = []
            for q in questions:
                # print(q.score_sentiment)
                values.append((
                    q.id,
                    q.numero_question,
                    q.date_depot,
                    q.objet,
                    q.texte_question,
                    q.texte_reponse,
                    q.depute_id,
                    # q.ministere_destinataire_id,
                    q.type_question,
                    q.statut,
                    q.thematique_principale,
                    q.departements_concernes,
                    q.mots_cles,
                    q.score_sentiment,
                    q.score_urgence,
                    q.score_complexite
                ))
            
            # Insertion avec gestion des conflits
            await conn.executemany("""
                INSERT INTO questions (
                    id, numero_question, date_depot, objet, texte_question, texte_reponse,
                    depute_id, type_question,
                    statut, thematique_principale, departements_concernes, mots_cles,
                    score_sentiment, score_urgence, score_complexite
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (numero_question) DO UPDATE SET
                    date_depot = EXCLUDED.date_depot,
                    objet = EXCLUDED.objet,
                    texte_question = EXCLUDED.texte_question,
                    texte_reponse = EXCLUDED.texte_reponse,
                    thematique_principale = EXCLUDED.thematique_principale,
                    departements_concernes = EXCLUDED.departements_concernes,
                    mots_cles = EXCLUDED.mots_cles,
                    score_sentiment = EXCLUDED.score_sentiment,
                    score_urgence = EXCLUDED.score_urgence,
                    score_complexite = EXCLUDED.score_complexite,
                    date_modification = CURRENT_TIMESTAMP
            """, values)
            
        logger.info(f"Insertées {len(questions)} questions")

    async def bulk_insert_deputes(self, deputes: List[DeputeIn]):
        """Insertion en masse des députés"""
        if not deputes:
            return

        async with self.get_connection() as conn:
            valeurs = []
            for d in deputes:
                valeurs.append((
                    d.id,
                    d.nom,
                    d.prenom,
                    d.nom_complet,
                    d.groupe_parlementaire
                ))

            await conn.executemany("""
                INSERT INTO deputes (
                    id, nom, prenom, nom_complet, groupe_parlementaire
                ) VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE SET
                    nom = EXCLUDED.nom,
                    prenom = EXCLUDED.prenom,
                    nom_complet = EXCLUDED.nom_complet,
                    groupe_parlementaire = EXCLUDED.groupe_parlementaire,
                    date_modification = CURRENT_TIMESTAMP
            """, valeurs)

        logger.info(f"Insérés {len(deputes)} députés")
    
    async def update_question_response(self, 
                                     numero_question: str,
                                     texte_reponse: str,
                                     date_reponse: str,
                                     ministere_repondant_id: str):
        """Met à jour la réponse d'une question"""
        
        async with self.get_connection() as conn:
            await conn.execute("""
                UPDATE questions 
                SET texte_reponse = $1,
                    date_reponse = $2,
                    ministere_repondant_id = $3,
                    statut = 'repondue',
                    date_modification = CURRENT_TIMESTAMP
                WHERE numero_question = $4
            """, texte_reponse, date_reponse, ministere_repondant_id, numero_question)
    
    async def get_existing_questions(self, date_debut: str = None) -> List[str]:
        """Récupère les numéros de questions existantes"""
        
        async with self.get_connection() as conn:
            rows = await conn.fetch("""
                SELECT numero_question
                FROM questions 
            """)
            #     WHERE date_depot >= $1
            # """, date_debut)

            # for row in rows:
            #     id, texte = row['id'], row['objet'] + " " + row['texte_question']
            #     mots_cles = processor.a_supprimer(texte)
            #     # Mets à jour la colonne (enregistre sous forme de string ou array selon ton modèle)
            #     await conn.execute("UPDATE questions SET mots_cles = $1 WHERE id = $2", mots_cles, id)
            #     print(f"ID: {id}")

            
        # return True
        return [row['numero_question'] for row in rows]
    
    async def execute_maintenance(self):
        """Tâches de maintenance de la base"""
        
        async with self.get_connection() as conn:
            # Mise à jour des délais de réponse
            await conn.execute("""
                UPDATE questions 
                SET delai_reponse_jours = date_reponse - date_depot
                WHERE date_reponse IS NOT NULL 
                AND delai_reponse_jours IS NULL
            """)
            
            # Mise à jour des statistiques députés
            await conn.execute("""
                UPDATE deputes 
                SET nombre_questions_total = (
                    SELECT COUNT(*) FROM questions WHERE depute_id = deputes.id
                ),
                nombre_questions_repondues = (
                    SELECT COUNT(*) FROM questions 
                    WHERE depute_id = deputes.id AND statut = 'repondue'
                )
            """)
            
            # Refresh des vues matérialisées si utilisées
            await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY vue_stats_deputes")
            
        logger.info("Maintenance terminée")