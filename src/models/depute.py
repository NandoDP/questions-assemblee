from sqlalchemy import Column, String, Integer, Float, Date, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

Base = declarative_base()

class Depute(Base):
    __tablename__ = "deputes"

    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    nom_complet = Column(String(200), nullable=False)
    parti_politique = Column(String(100))
    groupe_parlementaire = Column(String(100))
    circonscription = Column(String(10))
    departement = Column(String(3))
    region = Column(String(100))
    debut_mandat = Column(Date)
    fin_mandat = Column(Date)
    legislature = Column(Integer)
    nombre_questions_total = Column(Integer, default=0)
    nombre_questions_repondues = Column(Integer, default=0)
    delai_moyen_reponse = Column(Float)
    date_creation = Column(TIMESTAMP)
    date_modification = Column(TIMESTAMP)

class DeputeIn(BaseModel):
    id: Optional[int] = None
    nom: str
    prenom: str
    nom_complet: str
    parti_politique: Optional[str] = None
    groupe_parlementaire: Optional[str] = None
    circonscription: Optional[str] = None
    departement: Optional[str] = None
    region: Optional[str] = None
    debut_mandat: Optional[date] = None
    fin_mandat: Optional[date] = None
    legislature: Optional[int] = None
    nombre_questions_total: Optional[int] = None
    nombre_questions_repondues: Optional[int] = None
    delai_moyen_reponse: Optional[float] = None
    date_creation: Optional[datetime] = None
    date_modification: Optional[datetime] = None