import re
import spacy
import html
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ProcessedText:
    texte_nettoye: str
    mots_cles: List[str]
    entites_nommees: Dict[str, List[str]]
    nombre_mots: int
    langue: str
    reponse: Optional[str] = None  # Nouvelle propriété pour la réponse

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")
        self.stop_words = set(self.nlp.Defaults.stop_words)

    # def a_supprimer(self, texte: str) -> List[str]:
    #     doc = self.nlp(texte)
        
    #     # Extraction des mots-clés
    #     return self._extract_keywords(doc)
        
    def process_question(self, texte: str, repondu: bool = False) -> ProcessedText:
        """Traite le texte d'une question au format HTML"""
        
        # Nettoyage HTML
        texte_nettoye = self._clean_html_text(texte)
        
        # Extraction de la réponse si demandée
        reponse = None
        if repondu:
            reponse = self._extract_response(texte)
            if reponse:
                logger.info("Réponse extraite avec succès")
        
        # Analyse NLP sur le texte principal (sans la réponse)
        texte_principal = self._extract_main_question(texte_nettoye)
        doc = self.nlp(texte_principal)
        
        # Extraction des mots-clés
        mots_cles = self._extract_keywords(doc)
        
        # Extraction des entités nommées
        entites = self._extract_entities(doc)
        
        # Métriques
        nombre_mots = len([token for token in doc if not token.is_space])
        
        # Détection de langue
        langue = self._detect_language(texte_principal)
        
        return ProcessedText(
            texte_nettoye=texte_principal,
            mots_cles=mots_cles,
            entites_nommees=entites,
            nombre_mots=nombre_mots,
            langue=langue,
            reponse=reponse
        )
    
    def _clean_html_text(self, texte: str) -> str:
        """Nettoie le texte HTML"""
        
        # Décodage des entités HTML
        texte = html.unescape(texte)
        
        # Utilisation de BeautifulSoup pour extraire le texte
        soup = BeautifulSoup(texte, 'html.parser')
        
        # Suppression des images
        for img in soup.find_all('img'):
            img.decompose()
        
        # Extraction du texte en préservant les paragraphes
        texte_brut = soup.get_text(separator=' ', strip=True)
        
        # Nettoyage supplémentaire
        texte_brut = self._clean_text(texte_brut)
        
        return texte_brut
    
    def _extract_response(self, texte_html: str) -> Optional[str]:
        """Extrait la réponse du gouvernement si elle existe"""
        
        # Décodage des entités HTML
        texte_html = html.unescape(texte_html)
        
        soup = BeautifulSoup(texte_html, 'html.parser')
        
        # Recherche des marqueurs de réponse
        response_markers = [
            'Réponse du gouvernement',
            'Réponse du ministre',
            'Réponse de l\'administration',
            'Réponse officielle'
        ]
        
        # Recherche par balise h3 ou h2 contenant "Réponse"
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            if heading.get_text() and any(marker.lower() in heading.get_text().lower() for marker in response_markers):
                # Récupération de tous les éléments suivants jusqu'à la fin
                response_elements = []
                for sibling in heading.find_next_siblings():
                    if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break  # Arrêt si on trouve un autre titre
                    if sibling.name == 'p' and sibling.get_text(strip=True):
                        response_elements.append(sibling.get_text(strip=True))
                
                if response_elements:
                    return ' '.join(response_elements)
        
        # Recherche par contenu de paragraphe
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if any(marker.lower() in text.lower() for marker in response_markers):
                # Si le paragraphe contient le marqueur, prendre les paragraphes suivants
                response_elements = []
                for sibling in p.find_next_siblings('p'):
                    if sibling.get_text(strip=True):
                        response_elements.append(sibling.get_text(strip=True))
                
                if response_elements:
                    return ' '.join(response_elements)
        
        # Recherche par pattern regex dans le texte brut
        texte_brut = soup.get_text()
        pattern = r'(?i)r[eé]ponse\s+du\s+gouvernement\s*:?\s*(.*?)(?=\n\s*\n|\Z)'
        match = re.search(pattern, texte_brut, re.DOTALL)
        
        if match:
            response_text = match.group(1).strip()
            # Nettoyage de la réponse
            response_text = re.sub(r'\s+', ' ', response_text)
            return response_text
        
        return None
    
    def _extract_main_question(self, texte: str) -> str:
        """Extrait la question principale en excluant la réponse"""
        
        # Recherche des marqueurs de réponse pour les exclure
        response_markers = [
            'Réponse du gouvernement',
            'Réponse du ministre',
            'Réponse de l\'administration'
        ]
        
        for marker in response_markers:
            if marker.lower() in texte.lower():
                # Couper le texte avant le marqueur de réponse
                index = texte.lower().find(marker.lower())
                if index > 0:
                    texte = texte[:index]
                break
        
        return texte.strip()
    
    def _clean_text(self, texte: str) -> str:
        """Nettoie le texte"""
        
        # Suppression des caractères spéciaux
        texte = re.sub(r'[^\w\s\-\.,;:!?()àâäéèêëîïôöùûüÿçÀÂÄÉÈÊËÎÏÔÖÙÛÜŸÇ]', ' ', texte)
        
        # Normalisation des espaces
        texte = re.sub(r'\s+', ' ', texte)
        
        # Suppression des numéros de page, références JO, etc.
        texte = re.sub(r'(J\.O\.|Journal Officiel).*?\d+', '', texte)
        texte = re.sub(r'Question n°\s*\d+', '', texte)
        
        # # Suppression des formules de politesse courantes
        # texte = re.sub(r'Monsieur\s+le\s+ministre,?\s*', '', texte, flags=re.IGNORECASE)
        # texte = re.sub(r'Madame\s+la\s+ministre,?\s*', '', texte, flags=re.IGNORECASE)
        
        return texte.strip()
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extrait les mots-clés pertinents"""
        
        keywords = []
        
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Extraction des phrases nominales
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:
                keywords.append(chunk.text.lower())
        
        return list(set(keywords))
    
    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extrait les entités nommées"""
        
        entities = {
            'personnes': [],
            'lieux': [],
            'organisations': [],
            'dates': [],
            'montants': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PER':
                entities['personnes'].append(ent.text)
            elif ent.label_ in ['LOC', 'GPE']:
                entities['lieux'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organisations'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['montants'].append(ent.text)
        
        return entities
    
    def _detect_language(self, texte: str) -> str:
        """Détecte la langue du texte"""
        # Implémentation simple basée sur des mots courants français
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'pour', 'dans', 'sur', 'avec', 'par']
        
        words = texte.lower().split()
        french_score = sum(1 for word in words if word in french_indicators)
        
        return 'fr' if french_score > len(words) * 0.1 else 'autre'