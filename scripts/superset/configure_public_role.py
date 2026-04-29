#!/usr/bin/env python3
"""
Script Python rapide pour configurer le rôle Public en lecture seule.
Usage: python configure_public_role.py
"""

import sys
import os


SAFE_PUBLIC_PERMISSIONS = {
    ("can_explore", "Superset"),
    ("can_explore_json", "Superset"),
    ("can_read", "Explore"),
    ("can_read", "ExplorePermalinkRestApi"),
}


def is_dangerous_permission(permission) -> bool:
    permission_name = getattr(permission.permission, "name", "")
    view_name = getattr(permission.view_menu, "name", "")
    permission_key = (permission_name, view_name)

    if permission_key in SAFE_PUBLIC_PERMISSIONS:
        return False

    dangerous_keywords = [
        'write', 'edit', 'delete', 'add', 'create',
        'sql', 'export', 'csv', 'download',
        'save', 'import', 'upload', 'samples', 'get_data'
    ]
    permission_label = str(permission).lower()
    return any(keyword in permission_label for keyword in dangerous_keywords)

# Configurer l'environnement Superset
os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

try:
    from superset.app import create_app
    from superset import security_manager
    from superset.extensions import db
    
    print("🔒 Configuration du rôle Public en lecture seule (Python)...")
    
    app = create_app()
    with app.app_context():
        # Récupérer le rôle Public
        public_role = security_manager.find_role("Public")
        
        if not public_role:
            print("❌ Rôle Public non trouvé. Création...")
            public_role = security_manager.add_role("Public")
        
        print(f"✓ Rôle Public trouvé avec {len(public_role.permissions)} permissions")
        
        # Supprimer toutes les permissions dangereuses
        removed = 0
        for perm in list(public_role.permissions):
            if is_dangerous_permission(perm):
                public_role.permissions.remove(perm)
                removed += 1
        
        print(f"✓ {removed} permissions dangereuses supprimées")
        
        # Permissions de lecture seule à ajouter
        readonly_permissions = [
            ("can_read", "Dashboard"),
            ("can_list", "Dashboard"),
            ("can_get_embedded", "Dashboard"),
            ("can_read", "EmbeddedDashboard"),
            ("can_read", "Chart"),
            ("can_list", "Chart"),
            ("can_read", "Dataset"),
            ("can_read", "Database"),
            ("can_read", "CurrentUserRestApi"),
            ("can_read", "DashboardPermalinkRestApi"),
            ("can_read", "DashboardFilterStateRestApi"),
            ("can_write", "DashboardFilterStateRestApi"),
            ("can_explore", "Superset"),
            ("can_explore_json", "Superset"),
            ("can_read", "Explore"),
            ("can_read", "ExplorePermalinkRestApi"),
            ("menu_access", "Dashboards"),
        ]
        
        added = 0
        for action, resource in readonly_permissions:
            perm = security_manager.find_permission_view_menu(action, resource)
            if perm and perm not in public_role.permissions:
                public_role.permissions.append(perm)
                added += 1
        
        print(f"✓ {added} permissions de lecture ajoutées")
        
        # Commit les changements
        db.session.commit()
        
        print(f"✅ Configuration terminée : {len(public_role.permissions)} permissions totales")
        print("\n📋 Permissions finales du rôle Public :")
        for perm in sorted(public_role.permissions, key=str):
            print(f"  - {perm}")
        
        # Vérification finale
        has_dangerous = False
        for perm in public_role.permissions:
            if is_dangerous_permission(perm):
                print(f"  ⚠️  ATTENTION: Permission dangereuse restante: {perm}")
                has_dangerous = True
        
        if not has_dangerous:
            print("\n✅ Aucune permission dangereuse détectée. Rôle Public sécurisé!")
            sys.exit(0)
        else:
            print("\n⚠️  Des permissions dangereuses subsistent. Vérifiez manuellement.")
            sys.exit(1)

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
