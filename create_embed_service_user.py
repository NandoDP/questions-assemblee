#!/usr/bin/env python3
"""
Crée un compte de service dédié à l'Embedded SDK Superset.
Usage: python create_embed_service_user.py
"""

import os
import sys

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

EMBED_USERNAME = os.getenv('SUPERSET_EMBED_USERNAME', 'embed_service')
EMBED_PASSWORD = os.getenv('SUPERSET_EMBED_PASSWORD', 'change-me-embed-password')
EMBED_EMAIL = os.getenv('SUPERSET_EMBED_EMAIL', 'embed-service@example.com')
EMBED_ROLE_NAME = os.getenv('SUPERSET_EMBED_ROLE_NAME', 'EmbeddedService')


def ensure_permission(security_manager, role, action, resource):
    perm = security_manager.find_permission_view_menu(action, resource)
    if perm and perm not in role.permissions:
        role.permissions.append(perm)
        return True
    return False


try:
    from superset.app import create_app

    print('🔐 Configuration du compte de service Embedded SDK...')

    app = create_app()
    with app.app_context():
        from superset import security_manager
        from superset.extensions import db

        role = security_manager.find_role(EMBED_ROLE_NAME)
        if not role:
            print(f'➕ Création du rôle {EMBED_ROLE_NAME}...')
            role = security_manager.add_role(EMBED_ROLE_NAME)
        else:
            print(f'✓ Rôle {EMBED_ROLE_NAME} déjà présent')

        gamma_role = security_manager.find_role('Gamma')
        copied_permissions = 0
        if gamma_role:
            for perm in gamma_role.permissions:
                if perm not in role.permissions:
                    role.permissions.append(perm)
                    copied_permissions += 1

        api_permissions = [
            ('can_read', 'Dashboard'),
            ('can_list', 'Dashboard'),
            ('can_get_embedded', 'Dashboard'),
            ('can_read', 'Chart'),
            ('can_read', 'Dataset'),
            ('can_read', 'Database'),
            ('can_read', 'SecurityRestApi'),
            ('can_csrf_token', 'SecurityRestApi'),
            ('can_guest_token', 'SecurityRestApi'),
            ('can_grant_guest_token', 'SecurityRestApi'),
        ]

        added_permissions = 0
        for action, resource in api_permissions:
            if ensure_permission(security_manager, role, action, resource):
                added_permissions += 1

        user = security_manager.find_user(username=EMBED_USERNAME)
        if user:
            print(f'✓ Utilisateur {EMBED_USERNAME} déjà présent')
            existing_roles = {existing_role.name for existing_role in user.roles}
            required_roles = [role]
            if gamma_role and 'Gamma' not in existing_roles:
                required_roles.append(gamma_role)
            if role.name not in existing_roles or (gamma_role and 'Gamma' not in existing_roles):
                user.roles = list({current_role.name: current_role for current_role in [*user.roles, *required_roles]}.values())
        else:
            print(f'➕ Création de l\'utilisateur {EMBED_USERNAME}...')
            assigned_role = gamma_role if gamma_role else role
            user = security_manager.add_user(
                username=EMBED_USERNAME,
                first_name='Embedded',
                last_name='Service',
                email=EMBED_EMAIL,
                role=assigned_role,
                password=EMBED_PASSWORD,
            )
            if not user:
                print('❌ Échec de création du compte de service')
                sys.exit(1)
            if role not in user.roles:
                user.roles.append(role)

        db.session.commit()

        print(f'✅ Rôle {EMBED_ROLE_NAME} prêt ({copied_permissions} permissions Gamma copiées, {added_permissions} permissions API ajoutées)')
        print(f'✅ Compte de service prêt : {EMBED_USERNAME}')
        print('ℹ️  Vérifier dans Superset > Security > List Roles que SecurityRestApi expose bien les permissions guest/csrf attendues.')

except Exception as exc:
    print(f'❌ Erreur: {exc}')
    import traceback
    traceback.print_exc()
    sys.exit(1)