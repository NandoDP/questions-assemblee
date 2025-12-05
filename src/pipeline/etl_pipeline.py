from datetime import datetime, timedelta
from typing import List, Dict
from src.extractors.api_client import ParliamentaryAPIClient
from src.transformers.text_processor import TextProcessor
from src.transformers.classifier import QuestionClassifier
from src.loaders.database import DatabaseLoader
from src.models.question import QuestionIn, Question
from src.utils.logger import get_logger
from src.models.depute import DeputeIn

logger = get_logger(__name__)

class ETLPipeline:
    def __init__(self):
        self.api_client = ParliamentaryAPIClient()
        self.text_processor = TextProcessor()
        self.classifier = QuestionClassifier()
        self.db_loader = DatabaseLoader()

    async def load_deputes_pipeline(self):
        """Exécute le pipeline de chargement des députes"""
        
        start_time = datetime.now()
        logger.info(f"Démarrage du pipeline de chargement des députes - {start_time}")
        
        try:
            # Initialisation
            await self.db_loader.initialize()
            
            # Extraction
            deputes_data = await self._extract_deputes()
            if not deputes_data:
                logger.info("Aucun député à ajouter")
                return                        
            # Chargement
            await self._load_deputes(deputes_data)
            logger.info(f"Pipeline terminé - {len(deputes_data)} députés ajoutés")

        except Exception as e:
            logger.error(f"Erreur dans le pipeline de chargement des députes: {e}")
            raise
        finally:
            await self.db_loader.close()
        
    async def run_full_pipeline(self, 
                              date_debut: str = None,
                              date_fin: str = None,
                              incremental: bool = True):
        """Exécute le pipeline complet"""
        
        start_time = datetime.now()
        logger.info(f"Démarrage du pipeline ETL - {start_time}")
        
        try:
            # Initialisation
            await self.db_loader.initialize()
            
            # # Extraction
            # deputes_data = await self._extract_deputes()
            # if not deputes_data:
            #     logger.info("Aucun député à ajouter")
            #     return                        
            # # Chargement
            # await self._load_deputes(deputes_data)
            # logger.info(f"Pipeline terminé - {len(deputes_data)} députés ajoutés")

            
            # Extraction
            questions_data = await self._extract_data(date_debut, date_fin, incremental)
            
            if not questions_data:
                logger.info("Aucune nouvelle question à traiter")
                return
            
            # Transformation
            processed_questions = await self._transform_data(questions_data)
            
            # Chargement
            await self._load_data(processed_questions)
            
            # # Maintenance
            # await self.db_loader.execute_maintenance()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"Pipeline terminé en {duration} - {len(processed_questions)} questions traitées")
            
        except Exception as e:
            logger.error(f"Erreur dans le pipeline: {e}")
            raise
        finally:
            await self.db_loader.close()
    
    async def _extract_data(self, 
                          date_debut: str,
                          date_fin: str,
                          incremental: bool) -> List[QuestionIn]:
        """Phase d'extraction"""
        
        logger.info("Début de l'extraction")

        status = "published"
        
        # # Détermination des dates
        # if not date_debut and incremental:
        #     date_debut = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        # if not date_fin:
        #     date_fin = datetime.now().strftime('%Y-%m-%d')
        
        async with self.api_client as client:
            # Récupération des questions
            questions = await client.get_questions(statut=status, date_debut=date_debut, date_fin=date_fin)
            
            # Filtrage des questions déjà traitées si incrémental
            if incremental:
                # existing_questions = await self.db_loader.get_existing_questions(date_debut)
                existing_questions = await self.db_loader.get_existing_questions()
                questions = [
                    q for q in questions 
                    if q.numero_question not in existing_questions
                ]
            
            logger.info(f"Extraites {len(questions)} questions")
            return questions
    
    async def _transform_data(self, questions_data: List[QuestionIn]) -> List[Question]:
        """Phase de transformation"""
        
        logger.info("Début de la transformation")
        
        processed_questions = []
        
        for question_data in questions_data:
            try:
                # Traitement du texte
                processed_question = self.text_processor.process_question(
                    question_data.texte_question, repondu=(question_data.statut=='repondue')
                )
                
                # Classification
                classification = self.classifier.classify_question(
                    processed_question.texte_nettoye,
                    question_data.objet
                )                
                
                # Création de l'enregistrement
                question_data.texte_question = processed_question.texte_nettoye
                question_data.texte_reponse = processed_question.reponse
                question_data.thematique_principale = classification['thematique_principale']
                question_data.mots_cles = processed_question.mots_cles
                question_data.entites_nommees = processed_question.entites_nommees
                question_data.departements_concernes = classification['departements_concernes']
                question_data.score_sentiment=classification['score_sentiment']
                question_data.score_urgence=classification['score_urgence']
                # question_data.score_complexite=classification['score_complexite']
                
                # Conversion en Question (SQLAlchemy)
                question_db = Question(**question_data.dict())
                # print(f"Question: {question_db}")
                processed_questions.append(question_db)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de la question {question_data.numero_question}: {e}")
                continue
        
        logger.info(f"Transformées {len(processed_questions)} questions")
        return processed_questions
    
    async def _load_data(self, questions: List[Question]):
        """Phase de chargement"""
        
        logger.info("Début du chargement")
        
        # Chargement par batch pour éviter les timeouts
        batch_size = 100
        
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            await self.db_loader.bulk_insert_questions(batch)
            
            logger.info(f"Chargé batch {i//batch_size + 1}/{(len(questions) + batch_size - 1)//batch_size}")
        
        logger.info("Chargement terminé")

    def extraire_phrase_ministre_avancee(self, texte: str) -> str:
        """
        Version avancée qui gère mieux les cas complexes et nettoie le résultat.
        
        Args:
            texte (str): Le texte à analyser
            
        Returns:
            Optional[str]: La première phrase trouvée et nettoyée, ou "Non trouvé" si aucune phrase ne correspond
        """
        if not texte:
            return "Non trouvé"
        
        import re
        
        # Nettoyage du texte (suppression des retours à la ligne excessifs)
        texte_nettoye = re.sub(r'\s+', ' ', texte.strip())
        
        # Pattern plus robuste qui gère les majuscules/minuscules et les espaces
        # Recherche une phrase complète commençant par un mot avec 'minist'
        pattern = r'(?i)\b(minist[a-zA-ZàâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ]*[^.]*?)\.'
        
        match = re.search(pattern, texte_nettoye)
        
        if match:
            phrase = match.group(1).strip()
            
            # Nettoyage supplémentaire
            phrase = re.sub(r'\s+', ' ', phrase)  # Normalisation des espaces
            phrase = phrase.capitalize()  # Première lettre en majuscule
            
            return phrase + '.'
        
        return "Non trouvé"

    async def _extract_deputes(self) -> List[DeputeIn]:
        """Phase d'extraction"""
        
        logger.info("Début de l'extraction")

        status = "active"
        
        async with self.api_client as client:
            # Récupération des deputes
            deputes = await client.get_deputes(
                url="https://cms.vie-publique.sn/items/assembly_deputy",
                statut=status, 
                limit=200
            )
            
            logger.info(f"Récuperations des {len(deputes)} députes")
            return deputes
        
    async def _load_deputes(self, deputes: List[DeputeIn]):
        """Phase de chargement"""
        
        logger.info("Début du chargement")
        
        # Chargement par batch pour éviter les timeouts
        batch_size = 100
        
        for i in range(0, len(deputes), batch_size):
            batch = deputes[i:i + batch_size]
            await self.db_loader.bulk_insert_deputes(batch)
            
            logger.info(f"Chargé batch {i//batch_size + 1}/{(len(deputes) + batch_size - 1)//batch_size}")
        
        logger.info("Chargement terminé")
        
        

import asyncio

if __name__ == "__main__":
    pipeline = ETLPipeline()
    asyncio.run(pipeline.run_full_pipeline())