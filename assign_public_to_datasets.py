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
            # Ajouter les permissions datasource pour le rôle Public
            perm = security_manager.find_permission_view_menu(
                'datasource_access',
                f'[{dataset.database.database_name}].[{dataset.table_name}](id:{dataset.id})'
            )
            
            if perm and perm not in public_role.permissions:
                public_role.permissions.append(perm)
                updated += 1
                print(f"  ✓ {dataset.table_name} - Permission datasource_access ajoutée")
            elif perm:
                print(f"  → {dataset.table_name} - Permission déjà présente")
            else:
                # Créer la permission si elle n'existe pas
                security_manager.add_permission_view_menu(
                    'datasource_access',
                    f'[{dataset.database.database_name}].[{dataset.table_name}](id:{dataset.id})'
                )
                perm = security_manager.find_permission_view_menu(
                    'datasource_access',
                    f'[{dataset.database.database_name}].[{dataset.table_name}](id:{dataset.id})'
                )
                if perm:
                    public_role.permissions.append(perm)
                    updated += 1
                    print(f"  ✓ {dataset.table_name} - Permission créée et ajoutée")
        
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
