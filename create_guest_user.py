#!/usr/bin/env python3
"""
Script pour créer un utilisateur guest avec le rôle Public
Usage: python create_guest_user.py
"""

import sys
import os

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

try:
    from superset.app import create_app
    
    print("👤 Création de l'utilisateur guest...")
    
    app = create_app()
    with app.app_context():
        from superset import security_manager
        from superset.extensions import db
        
        # Vérifier si l'utilisateur guest existe déjà
        guest_user = security_manager.find_user(username='guest')
        
        if guest_user:
            print("✓ Utilisateur guest existe déjà")
            # Vérifier qu'il a bien le rôle Public
            public_role = security_manager.find_role("Public")
            if public_role not in guest_user.roles:
                guest_user.roles = [public_role]
                db.session.commit()
                print("  ✓ Rôle Public assigné à guest")
        else:
            # Créer l'utilisateur guest
            public_role = security_manager.find_role("Public")
            
            if not public_role:
                print("❌ Rôle Public non trouvé!")
                sys.exit(1)
            
            guest_user = security_manager.add_user(
                username='guest',
                first_name='Guest',
                last_name='User',
                email='guest@example.com',
                role=public_role,
                password='guest'
            )
            
            if guest_user:
                print("✅ Utilisateur guest créé avec succès")
                print("  - Username: guest")
                print("  - Password: guest")
                print("  - Rôle: Public (lecture seule)")
            else:
                print("❌ Échec de la création de l'utilisateur guest")
                sys.exit(1)

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
