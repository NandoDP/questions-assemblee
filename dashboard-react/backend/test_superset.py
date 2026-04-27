"""
Script de test pour vérifier la connexion Superset et le format des données
"""
import sys
import json
sys.path.insert(0, 'c:/Users/maodo/Documents/Dev/perso/question-assemblee/dashboard-react/backend')

from api.superset_client import SupersetClient

# Initialiser le client
superset = SupersetClient('https://questions-assemblee-superset.onrender.com')

# Test 1: Login
print("🔐 Test login...")
success = superset.login('guest', 'guest')
if success:
    print("✅ Login réussi!")
else:
    print("❌ Login échoué")
    sys.exit(1)

# Test 2: Récupérer le dashboard
print("\n📊 Test récupération dashboard 1...")
try:
    data = superset.get_dashboard_data(1, 'guest', 'guest')
    print("✅ Dashboard récupéré!")
    print(f"\n📋 Nombre de charts: {len(data.get('charts', []))}")
    
    # Afficher les noms des charts
    print("\n📈 Charts disponibles:")
    for chart in data.get('charts', []):
        print(f"  - {chart.get('name')} (ID: {chart.get('id')})")
    
    # Sauvegarder pour inspection
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("\n💾 Données sauvegardées dans dashboard_data.json")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
