#!/usr/bin/env python3
"""Crée la configuration embedded pour le dashboard Superset principal."""

import os
import sys

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

DASHBOARD_ID = os.getenv('SUPERSET_DASHBOARD_ID', '1')
ALLOWED_DOMAINS = [
    domain.strip()
    for domain in os.getenv('SUPERSET_EMBED_ALLOWED_DOMAINS', '').split(',')
    if domain.strip()
]


try:
    from superset.app import create_app

    print('🧩 Configuration embedded dashboard...')

    app = create_app()
    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard
        from superset.daos.dashboard import EmbeddedDashboardDAO

        dashboard = db.session.query(Dashboard).filter(Dashboard.id == int(DASHBOARD_ID)).one_or_none()
        if dashboard is None:
            print(f'❌ Dashboard introuvable: {DASHBOARD_ID}')
            sys.exit(1)

        embedded = EmbeddedDashboardDAO.upsert(dashboard, ALLOWED_DOMAINS)
        db.session.commit()

        print(f'✅ Embedded dashboard prêt pour {dashboard.id}: {embedded.uuid}')
        print(f'✅ Domaines autorisés: {embedded.allowed_domains}')

except Exception as exc:
    print(f'❌ Erreur: {exc}')
    import traceback
    traceback.print_exc()
    sys.exit(1)