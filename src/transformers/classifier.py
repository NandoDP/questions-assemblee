import pickle
import os
from typing import Dict, List, Tuple
from transformers import CamembertForSequenceClassification, CamembertTokenizer
import re
from src.utils.logger import get_logger
from src.utils.rules import rules, departements
from rapidfuzz import fuzz

logger = get_logger(__name__)

class QuestionClassifier:
    def __init__(self):
        # self.thematic_classifier = None
        
        self.model_classifier = None
        self.tokenizer = None
        self.label_encoder_classifier = None

        self.sentiment_analyzer = None
        self.urgency_classifier = None
        # self._load_models()

        # Chemin vers le dossier où le modèle et le tokenizer ont été sauvegardés
        
    
    def _load_models(self):
        """Charge les modèles pré-entraînés"""
        try:
            # # Classificateur thématique
            # self.thematic_classifier = joblib.load('models/thematic_classifier.pkl')
            
            # # Analyseur de sentiment
            # self.sentiment_analyzer = pipeline(
            #     "sentiment-analysis",
            #     model="camembert-base",
            #     tokenizer="camembert-base"
            # )
            
            # # Classificateur d'urgence
            # self.urgency_classifier = joblib.load('models/urgency_classifier.pkl')

            # Chemins relatifs pour l'environnement Docker
            model_dir = "/opt/airflow/models/camembert_model"
            label_encoder_file = "/opt/airflow/models/label_encoder.pkl"
            
            # Vérifier si les fichiers existent
            if not os.path.exists(model_dir):
                logger.warning(f"Modèle Camembert non trouvé dans {model_dir}")
                self._create_default_models()
                return
                
            if not os.path.exists(label_encoder_file):
                logger.warning(f"Label encoder non trouvé dans {label_encoder_file}")
                self._create_default_models()
                return
            
            self.model_classifier = CamembertForSequenceClassification.from_pretrained(model_dir)
            self.tokenizer = CamembertTokenizer.from_pretrained(model_dir)

            # Charger le label encoder
            with open(label_encoder_file, "rb") as f:
                self.label_encoder_classifier = pickle.load(f)
            
            logger.info("Modèles chargés avec succès")
            
        except Exception as e:
            logger.warning(f"Erreur lors du chargement des modèles: {str(e)}")
            self._create_default_models()
    
    def _create_default_models(self):
        """Crée des modèles par défaut en cas d'échec du chargement"""
        logger.info("Utilisation des modèles par défaut")
        self.model_classifier = None
        self.tokenizer = None
        self.label_encoder_classifier = None
    
    def classify_question(self, texte: str, objet: str) -> Dict:
        """Classifie une question selon plusieurs dimensions"""
        
        # Thématique
        thematique = self._classify_thematic(texte, objet)
        
        # Sentiment
        sentiment = self._analyze_sentiment(texte)
        
        # Urgence
        urgence = self._classify_urgency(texte, objet)
        
        # Complexité
        complexite = self._assess_complexity(texte)

        # Département
        departements = self._concerned_departement(texte, objet)
        
        return {
            'thematique_principale': thematique,
            'thematique_secondaire': None,
            'score_sentiment': sentiment['score'],
            'score_urgence': urgence,
            'score_complexite': complexite,
            'departements_concernes': departements,
            'confiance_classification': min(
                sentiment['confiance'],
                urgence
            )
        }
    
    def _classify_thematic(self, texte: str, objet: str) -> str:
        """Classifie par thématique"""
        
        # Combinaison objet + texte pour plus de précision
        combined_text = f"{objet} {texte}"
        
        if self.label_encoder_classifier and self.model_classifier and self.tokenizer:
            try:
                inputs = self.tokenizer(combined_text, return_tensors="pt", truncation=True, padding=True)
                outputs = self.model_classifier(**inputs)
                predicted = outputs.logits.argmax().item()
                return self.label_encoder_classifier.inverse_transform([predicted])[0]
            except Exception as e:
                logger.warning(f"Erreur lors de la classification avec le modèle: {str(e)}")
                return self._classify_thematic_rules(combined_text)
        
        return self._classify_thematic_rules(combined_text)
    
    def _classify_thematic_rules(self, texte: str) -> str:
        """Classification thématique par règles (fallback)"""
        
        texte_lower = texte.lower()
        scores = {}
        
        for theme, keywords in rules.items():
            score = sum(1 for keyword in keywords if keyword in texte_lower)
            scores[theme] = score
        
        principale = max(scores, key=scores.get) if scores else 'autre'
        
        return principale
    
    def _analyze_sentiment(self, texte: str) -> Dict:
        """Analyse le sentiment du texte"""
        
        if self.sentiment_analyzer:
            result = self.sentiment_analyzer(texte[:512])  # Limite de tokens
            
            # Conversion en score -1 à 1
            if result[0]['label'] == 'NEGATIVE':
                score = -result[0]['score']
            else:
                score = result[0]['score']
            
            return {
                'score': score,
                'confiance': result[0]['score']
            }
        
        return {'score': 0.0, 'confiance': 0.5}
    
    def _classify_urgency(self, texte: str, objet: str) -> float:
        """Évalue l'urgence d'une question"""
        
        urgency_keywords = [
            'urgent', 'immédiat', 'rapidement', 'dès que possible',
            'crise', 'catastrophe', 'danger', 'risque grave'
        ]
        
        combined_text = f"{objet} {texte}".lower()
        
        score = 0.0
        for keyword in urgency_keywords:
            if keyword in combined_text:
                score += 0.2
        
        return min(score, 1.0)
    
    def _assess_complexity(self, texte: str) -> float:
        """Évalue la complexité d'une question"""
        
        # Facteurs de complexité
        factors = {
            'longueur': min(len(texte) / 1000, 1.0),
            'phrases': min(texte.count('.') / 10, 1.0),
            'mots_techniques': 0.0,
            'références_légales': 0.0
        }
        
        # Mots techniques
        technical_words = ['article', 'décret', 'loi', 'réglementation', 'jurisprudence']
        factors['mots_techniques'] = min(
            sum(1 for word in technical_words if word in texte.lower()) / 10,
            1.0
        )
        
        # Références légales
        legal_refs = len(re.findall(r'article\s+\d+|loi\s+n°|décret\s+n°', texte.lower()))
        factors['références_légales'] = min(legal_refs / 5, 1.0)
        
        return sum(factors.values()) / len(factors)
    
    def _concerned_departement(self, texte: str, object: str) -> List[str]:
        """
        Retourne la liste de tous les départements mentionnés (même de façon approchée) dans le texte.
        """
        texte_lower = f"{object} {texte}".lower()
        departement_trouves = set()

        for dep in departements:
            for mot in texte_lower.split():
                # On utilise un seuil de similarité de 80%
                if fuzz.ratio(dep.lower(), mot) > 80:
                    departement_trouves.add(dep)
                    break  # On passe au département suivant dès qu'il est trouvé

        return list(departement_trouves)