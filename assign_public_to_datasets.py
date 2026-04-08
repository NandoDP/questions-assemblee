#!/usr/bin/env python3
"""
Script pour assigner le rôle Public à TOUS les datasets
Usage: python assign_public_to_datasets.py
"""

import sys
import os

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

try:
    from superset.app import create_app
    
    print("📊 Attribution du rôle Public à tous les datasets...")
    
    app = create_app()
    with app.app_context():
        # Importer APRÈS create_app() pour éviter l'erreur "App not initialized"
        from superset import security_manager
        from superset.extensions import db
        from superset.connectors.sqla.models import SqlaTable
        # Récupérer le rôle Public
        public_role = security_manager.find_role("Public")
        
        if not public_role:
            print("❌ Rôle Public non trouvé!")
            sys.exit(1)
        
        print(f"✓ Rôle Public trouvé")
        
        # Récupérer tous les datasets
        datasets = db.session.query(SqlaTable).all()
        
        print(f"📋 {len(datasets)} datasets trouvés")
        
        updated = 0
        for dataset in datasets:
            if public_role not in dataset.roles:
                dataset.roles.append(public_role)
                updated += 1
                print(f"  ✓ {dataset.table_name} - Rôle Public ajouté")
            else:
                print(f"  → {dataset.table_name} - Rôle Public déjà présent")
        
        # Commit les changements
        db.session.commit()
        
        print(f"\n✅ {updated} datasets mis à jour avec le rôle Public")
        print("\n📝 Prochaine étape:")
        print("  1. Retourner au dashboard Flask")
        print("  2. Le dashboard devrait maintenant s'afficher sans authentification !")

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
