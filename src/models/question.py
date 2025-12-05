from sqlalchemy import Column, String, Integer, Float, Date, Text, JSON, ARRAY, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import date, datetime

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    numero_question = Column(Integer, unique=True, nullable=False)
    numero_jo = Column(String(50))
    date_depot = Column(Date, nullable=False)
    date_publication_jo = Column(Date)
    date_reponse = Column(Date)
    date_derniere_relance = Column(Date)
    type_question = Column(String(50), nullable=False)
    statut = Column(String(30), nullable=False)
    thematique_principale = Column(String(100))
    thematique_secondaire = Column(String(100))
    sous_thematique = Column(String(100))
    objet = Column(Text, nullable=False)
    texte_question = Column(Text, nullable=False)
    texte_reponse = Column(Text)
    depute_id = Column(Integer, ForeignKey("deputes.id"))
    ministere_destinataire_id = Column(Integer, ForeignKey("ministeres.id"))
    ministere_repondant_id = Column(Integer, ForeignKey("ministeres.id"))
    mots_cles = Column(ARRAY(Text))
    entites_nommees = Column(JSON)
    score_sentiment = Column(Float)
    score_urgence = Column(Float)
    score_complexite = Column(Float)
    nombre_mots_question = Column(Integer)
    nombre_mots_reponse = Column(Integer)
    delai_reponse_jours = Column(Integer)
    nombre_relances = Column(Integer, default=0)
    niveau_territorial = Column(String(30))
    regions_concernees = Column(ARRAY(Text))
    departements_concernes = Column(ARRAY(Text))
    source_fichier = Column(String(255))
    version_traitement = Column(String(20))
    confiance_classification = Column(Float)
    date_creation = Column(TIMESTAMP)
    date_modification = Column(TIMESTAMP)

class QuestionIn(BaseModel):
    id: Optional[int] = None
    numero_question: int
    numero_jo: Optional[str] = None
    date_depot: date
    date_publication_jo: Optional[date] = None
    date_reponse: Optional[date] = None
    date_derniere_relance: Optional[date] = None
    type_question: str
    statut: str
    thematique_principale: Optional[str] = None
    thematique_secondaire: Optional[str] = None
    sous_thematique: Optional[str] = None
    objet: str
    texte_question: str
    texte_reponse: Optional[str] = None
    depute_id: Optional[int] = None
    ministere_destinataire_id: Optional[int] = None
    ministere_repondant_id: Optional[int] = None
    mots_cles: Optional[List[str]] = None
    entites_nommees: Optional[Any] = None
    score_sentiment: Optional[float] = None
    score_urgence: Optional[float] = None
    score_complexite: Optional[float] = None
    nombre_mots_question: Optional[int] = None
    nombre_mots_reponse: Optional[int] = None
    delai_reponse_jours: Optional[int] = None
    nombre_relances: Optional[int] = None
    niveau_territorial: Optional[str] = None
    regions_concernees: Optional[List[str]] = None
    departements_concernes: Optional[List[str]] = None
    source_fichier: Optional[str] = None
    version_traitement: Optional[str] = None
    confiance_classification: Optional[float] = None
    date_creation: Optional[datetime] = None
    date_modification: Optional[datetime] = None