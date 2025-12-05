from sqlalchemy import Column, String, Integer, Float, Date, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

Base = declarative_base()

class Ministere(Base):
    __tablename__ = "ministeres"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_officiel = Column(String(200), nullable=False)
    nom_court = Column(String(100))
    code_ministere = Column(String(20))
    ministere_parent_id = Column(UUID(as_uuid=True), ForeignKey("ministeres.id"))
    niveau = Column(String(30))
    date_creation = Column(Date)
    date_suppression = Column(Date)
    gouvernement = Column(String(100))
    nombre_questions_recues = Column(Integer, default=0)
    nombre_reponses_donnees = Column(Integer, default=0)
    delai_moyen_reponse = Column(Float)
    date_maj = Column(TIMESTAMP)

class MinistereIn(BaseModel):
    id: Optional[uuid.UUID]
    nom_officiel: str
    nom_court: Optional[str]
    code_ministere: Optional[str]
    ministere_parent_id: Optional[uuid.UUID]
    niveau: Optional[str]
    date_creation: Optional[date]
    date_suppression: Optional[date]
    gouvernement: Optional[str]
    nombre_questions_recues: Optional[int]
    nombre_reponses_donnees: Optional[int]
    delai_moyen_reponse: Optional[float]
    date_maj: Optional[datetime]