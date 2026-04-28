"""
Client pour communiquer avec Superset
Gère l'authentification et les requêtes API
"""

import requests
from typing import Dict, Any
import logging
from requests import HTTPError

logger = logging.getLogger(__name__)

class SupersetClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self._access_token = None
        self._csrf_token = None
    
    def login(self, username: str, password: str) -> bool:
        """Authentification Superset"""
        try:
            response = self.session.post(
                f'{self.base_url}/api/v1/security/login',
                json={
                    'username': username, 
                    'password': password,
                    'provider': 'db',
                    'refresh': True
                }
            )
            response.raise_for_status()
            
            data = response.json()
            self._access_token = data.get('access_token')
            
            if self._access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self._access_token}'
                })
                logger.info(f"Connexion Superset réussie pour {username}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur login Superset: {e}")
            return False

    def ensure_login(self, username: str, password: str) -> None:
        """S'assure qu'une session authentifiée est disponible."""
        if self._access_token:
            return
        if not self.login(username, password):
            raise RuntimeError("Authentification Superset échouée")

    def _load_csrf_token(self) -> None:
        """Charge le token CSRF requis par certaines API Superset."""
        response = self.session.get(f'{self.base_url}/api/v1/security/csrf_token/')
        response.raise_for_status()
        self._csrf_token = response.json().get('result')
        if self._csrf_token:
            self.session.headers.update({
                'X-CSRFToken': self._csrf_token,
                'Referer': self.base_url,
            })

    def get_embedded_dashboard_uuid(self, dashboard_id: str, username: str, password: str) -> str:
        """Résout l'UUID de configuration embedded requis par l'Embedded SDK."""
        self.ensure_login(username, password)

        response = self.session.get(f'{self.base_url}/api/v1/dashboard/{dashboard_id}/embedded')
        if response.status_code == 404:
            raise RuntimeError(
                f'La configuration embedded du dashboard {dashboard_id} est absente dans Superset. '
                'Activez l\'embed dans Superset ou créez la configuration via le bootstrap.'
            )
        response.raise_for_status()

        result = response.json().get('result', {})
        embedded_uuid = result.get('uuid')
        if not embedded_uuid:
            raise RuntimeError(
                f'UUID embedded introuvable pour le dashboard {dashboard_id}'
            )

        return str(embedded_uuid)

    def get_guest_token(self, dashboard_id: str, username: str, password: str) -> str:
        """Crée un guest token pour l'Embedded SDK."""
        self.ensure_login(username, password)
        self._ensure_csrf_token()

        response = self.session.post(
            f'{self.base_url}/api/v1/security/guest_token/',
            json={
                'user': {
                    'username': 'embedded_guest',
                    'first_name': 'Embedded',
                    'last_name': 'Guest'
                },
                'resources': [
                    {
                        'type': 'dashboard',
                        'id': str(dashboard_id)
                    }
                ],
                'rls': []
            }
        )
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise RuntimeError('Guest token absent de la réponse Superset')
        return token

    def _ensure_csrf_token(self) -> None:
        if self._csrf_token:
            return
        try:
            self._load_csrf_token()
        except HTTPError as error:
            status_code = error.response.status_code if error.response is not None else 'unknown'
            raise RuntimeError(
                'Le compte Superset configuré pour l\'embed ne peut pas obtenir de CSRF token '
                f'(status {status_code}). Configurez un compte de service avec les permissions '
                'nécessaires pour guest_token/csrf_token puis renseignez SUPERSET_EMBED_USERNAME '
                'et SUPERSET_EMBED_PASSWORD.'
            ) from error
    
    def get_dashboard_data(self, dashboard_id: int, username: str = 'guest', 
                          password: str = 'guest') -> Dict[str, Any]:
        """Récupère les données complètes d'un dashboard"""
        
        # S'authentifier si nécessaire
        self.ensure_login(username, password)
        
        try:
            # Récupérer les métadonnées du dashboard
            dashboard_response = self.session.get(
                f'{self.base_url}/api/v1/dashboard/{dashboard_id}'
            )
            dashboard_response.raise_for_status()
            dashboard = dashboard_response.json()
            
            result = dashboard.get('result', {})
            
            # Parser position_json pour extraire les chart IDs
            import json
            position_json = json.loads(result.get('position_json', '{}'))
            
            chart_ids = []
            chart_names = {}
            for key, value in position_json.items():
                if key.startswith('CHART-') and isinstance(value, dict):
                    meta = value.get('meta', {})
                    chart_id = meta.get('chartId')
                    if chart_id:
                        chart_ids.append(chart_id)
                        chart_names[chart_id] = meta.get('sliceName', f'Chart {chart_id}')
            
            # Récupérer les données de chaque chart
            charts_data = []
            for chart_id in chart_ids:
                logger.info(f"Récupération du chart {chart_id}: {chart_names.get(chart_id)}")
                chart_data = self.get_chart_data(chart_id)
                charts_data.append({
                    'id': chart_id,
                    'name': chart_names.get(chart_id),
                    'data': chart_data
                })
            
            return {
                'dashboard': result,
                'charts': charts_data
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération dashboard: {e}")
            raise
    
    def get_chart_data(self, chart_id: int) -> Dict[str, Any]:
        """Récupère les données d'un chart spécifique"""
        try:
            response = self.session.get(
                f'{self.base_url}/api/v1/chart/{chart_id}/data'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur récupération chart {chart_id}: {e}")
            return {}
    
    def get_kpis(self) -> Dict[str, Any]:
        """
        Récupère les KPIs principaux
        TODO: Adapter selon les charts KPI réels
        """
        return {
            'total_questions': 257,
            'response_rate': 1.95,
            'active_deputes': 33,
            'avg_response_time': 0  # À calculer
        }
