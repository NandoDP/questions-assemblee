from datetime import datetime
import asyncio
import aiohttp
from typing import List, Dict, Optional
from dataclasses import dataclass
from src.models.question import QuestionIn
from src.models.depute import DeputeIn
from src.utils.logger import get_logger
from src.utils.settings import settings

logger = get_logger(__name__)

@dataclass
class APIResponse:
    data: Dict
    status_code: int
    headers: Dict
    timestamp: str

class ParliamentaryAPIClient:
    def __init__(self):
        self.base_url = settings.API_URL
        self.api_token = settings.API_TOKEN
        self.session = None
        self.rate_limit = settings.API_RATE_LIMIT
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Parliamentary-ETL/1.0'}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_questions(self,
                        statut: str = None,
                        # depute_id: str = None,
                        sort: str = None,
                        fields: list = None,
                        date_debut: str = None,
                        date_fin: str = None,
                        limit: int = 100) -> List[QuestionIn]:
        """Récupère les questions depuis l'API"""

        if self.api_token is None:
            logger.error("Il n'y a pas de token API")
            return []
        
        params = {
            "limit": limit,
            # "offset": offset
        }
        # Filtres dynamiques
        if date_debut:
            params["filter[question_date][_gte]"] = date_debut
        if date_fin:
            params["filter[question_date][_lte]"] = date_fin
        if statut:
            params["filter[status]"] = statut
        if sort:
            params["sort"] = sort
        if fields:
            params["fields"] = ",".join(fields)

        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
            
        questions = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = await self._make_request(
                    'GET', 
                    self.base_url, 
                    params=params,
                    headers=headers
                )
                
                if not response.data.get('data'):
                    break
                    
                questions.extend(response.data['data'])
                
                # Pagination
                if len(response.data['data']) < limit:
                    break
                    
                page += 1
                
                # Rate limiting
                await asyncio.sleep(1 / self.rate_limit)
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération page {page}: {e}")
                break
                
        logger.info(f"Récupérées {len(questions)} questions")
        return [QuestionIn(
            id=int(q.get('id')),
            numero_question=int(q.get('id')),
            date_depot=q.get('question_date'),
            statut=("repondue" if q.get("is_answered", False) else "en_attente"),
            type_question='ecrite',
            objet=str(q.get('subject')),
            texte_question=str(q.get('question_text')),
            depute_id=int(q.get('deputy'))
        ) for q in questions]
    
    async def get_deputes(self,
                        url: str,
                        statut: str = None,
                        sort: str = None,
                        fields: list = None,
                        limit: int = 70) -> List[DeputeIn]:
        """Récupère les questions depuis l'API"""

        if self.api_token is None:
            logger.error("Il n'y a pas de token API")
            return []
        
        params = {
            "limit": limit,
            # "offset": offset
        }
        # Filtres dynamiques
        if statut:
            params["filter[status]"] = statut
        if sort:
            params["sort"] = sort
        if fields:
            params["fields"] = ",".join(fields)

        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
            
        deputes = []
        page = 1
        
        while True:
            params['page'] = page
            
            try:
                response = await self._make_request(
                    'GET', 
                    url, 
                    params=params,
                    headers=headers
                )
                
                if not response.data.get('data'):
                    break
                    
                deputes.extend(response.data['data'])
                
                # Pagination
                if len(response.data['data']) < limit:
                    break
                    
                page += 1
                
                # Rate limiting
                await asyncio.sleep(1 / self.rate_limit)
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération page {page}: {e}")
                break
                
        logger.info(f"Récupérées {len(deputes)} députes")
        return [DeputeIn(
            id=int(d.get('id')),
            nom=d.get('first_name'),
            prenom=d.get('last_name'),
            nom_complet=f"{d.get('first_name')} {d.get('last_name')}",
            groupe_parlementaire=("PASTEF" if int(d.get('group'))==1 else ("TAKKU WALLU" if int(d.get('group'))==2 else "Non inscrits")),
        ) for d in deputes]
    
    async def get_ministeres(self) -> List[Dict]:
        """Récupère la liste des ministères"""
        response = await self._make_request('GET', f'{self.base_url}/ministeres')
        return response.data.get('ministeres', [])
    
    async def _make_request(self, method: str, url: str, **kwargs) -> APIResponse:
        """Effectue une requête HTTP avec gestion d'erreurs"""
        
        for attempt in range(3):  # 3 tentatives
            try:
                async with self.session.request(method, url, **kwargs) as response:
                    data = await response.json()
                    
                    if response.status == 429:  # Rate limit
                        wait_time = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limit atteint, attente {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    response.raise_for_status()
                    
                    return APIResponse(
                        data=data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        timestamp=datetime.now().isoformat()
                    )
                    
            except aiohttp.ClientError as e:
                logger.error(f"Erreur client (tentative {attempt + 1}): {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)