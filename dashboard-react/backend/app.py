"""
API Flask pour servir les données du dashboard
Proxy vers Superset avec optimisations mobile
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from api.superset_client import SupersetClient
from api.data_transformer import transform_dashboard_data

app = Flask(__name__)
CORS(app)  # Permettre les requêtes depuis React

# Configuration
SUPERSET_URL = os.getenv('SUPERSET_URL', 'https://questions-assemblee-superset.onrender.com')
DATABASE_URL = os.getenv('DATABASE_URL')
SUPERSET_EMBED_USERNAME = os.getenv('SUPERSET_EMBED_USERNAME', 'embed_service')
SUPERSET_EMBED_PASSWORD = os.getenv('SUPERSET_EMBED_PASSWORD', 'change-me-embed-password')
SUPERSET_DASHBOARD_ID = os.getenv('SUPERSET_DASHBOARD_ID', '1')

# Client Superset
superset = SupersetClient(SUPERSET_URL)

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'service': 'dashboard-api'})

@app.route('/api/superset/guest-token')
def get_superset_guest_token():
    """
    Génère un guest token pour l'Embedded SDK Superset.
    """
    try:
        dashboard_id = request.args.get('dashboardId', SUPERSET_DASHBOARD_ID)
        token = superset.get_guest_token(
            dashboard_id=dashboard_id,
            username=SUPERSET_EMBED_USERNAME,
            password=SUPERSET_EMBED_PASSWORD,
        )
        return jsonify({
            'token': token,
            'dashboardId': str(dashboard_id),
            'supersetDomain': SUPERSET_URL,
        })
        
    except Exception as e:
        app.logger.error(f"Erreur génération guest token: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<int:dashboard_id>/data')
def get_dashboard_data(dashboard_id):
    """
    Récupère les données du dashboard et les transforme pour React
    Optimisé pour mobile (données paginées, format allégé)
    """
    try:
        # Pagination mobile
        is_mobile = request.args.get('mobile', 'false').lower() == 'true'
        page = int(request.args.get('page', 1))
        
        # Récupérer les données depuis Superset
        raw_data = superset.get_dashboard_data(
            dashboard_id=dashboard_id,
            username=SUPERSET_EMBED_USERNAME,
            password=SUPERSET_EMBED_PASSWORD
        )
        
        # Transformer pour React (format optimisé)
        transformed_data = transform_dashboard_data(
            raw_data,
            is_mobile=is_mobile,
            page=page
        )
        
        return jsonify(transformed_data)
        
    except Exception as e:
        app.logger.error(f"Erreur récupération dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/<int:chart_id>/data')
def get_chart_data(chart_id):
    """
    Récupère les données d'un chart spécifique
    """
    try:
        data = superset.get_chart_data(chart_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/kpis')
def get_kpis():
    """
    KPIs optimisés pour mobile (chargement rapide)
    """
    try:
        kpis = superset.get_kpis()
        return jsonify(kpis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
