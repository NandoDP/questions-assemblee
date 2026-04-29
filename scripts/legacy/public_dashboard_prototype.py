import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# URL du dashboard Superset (à configurer via variable d'environnement)
SUPERSET_URL = os.getenv('SUPERSET_URL', 'http://localhost:8088')
DASHBOARD_ID = os.getenv('DASHBOARD_ID', '1')

@app.route("/")
def home():
    """Page d'accueil avec le dashboard intégré"""
    dashboard_url = f"{SUPERSET_URL}/superset/dashboard/{DASHBOARD_ID}/?standalone=true"
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Questions Parlementaires - Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem 2rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .header h1 {
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            .header p {
                font-size: 0.95rem;
                opacity: 0.9;
            }
            .dashboard-container {
                width: 100%;
                height: calc(100vh - 100px);
                padding: 0;
            }
            iframe {
                width: 100%;
                height: 100%;
                border: none;
                background: white;
            }
            .footer {
                background: #2d3748;
                color: white;
                text-align: center;
                padding: 1rem;
                font-size: 0.85rem;
            }
            .footer a {
                color: #667eea;
                text-decoration: none;
            }
            .footer a:hover {
                text-decoration: underline;
            }
            .loading {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                font-size: 1.2rem;
                color: #667eea;
            }
            @media (max-width: 768px) {
                .header h1 {
                    font-size: 1.4rem;
                }
                .header p {
                    font-size: 0.85rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Questions Parlementaires - Analyse & Insights</h1>
            <p>Analyse automatisée des questions parlementaires avec classification ML</p>
        </div>
        
        <div class="dashboard-container" id="dashboard">
            <div class="loading">⏳ Chargement du dashboard...</div>
            <iframe 
                src="{{ dashboard_url }}" 
                onload="document.querySelector('.loading').style.display='none'"
                allow="fullscreen"
                loading="lazy">
            </iframe>
        </div>
        
        <div class="footer">
            Dashboard en lecture seule • Données mises à jour quotidiennement via GitHub Actions •
            <a href="https://github.com/NandoDP/questions-assemblee" target="_blank">Code source</a>
        </div>
    </body>
    </html>
    """, dashboard_url=dashboard_url)

@app.route("/health")
def health():
    """Health check endpoint pour Render"""
    return jsonify({"status": "healthy", "service": "questions-assemblee-dashboard"}), 200

@app.route("/api/info")
def info():
    """Informations sur l'API"""
    return jsonify({
        "project": "Questions Parlementaires",
        "description": "Analyse automatisée des questions parlementaires françaises",
        "version": "1.0.0",
        "superset_url": SUPERSET_URL,
        "dashboard_id": DASHBOARD_ID,
        "github": "https://github.com/NandoDP/questions-assemblee"
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
