#!/usr/bin/env python3
"""Crée la configuration embedded pour les dashboards Superset publies."""

import os
import sys

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

RAW_DASHBOARD_IDS = os.getenv('SUPERSET_PUBLIC_DASHBOARD_IDS', os.getenv('SUPERSET_DASHBOARD_ID', '1'))
ALLOWED_DOMAINS = [
    domain.strip()
    for domain in os.getenv('SUPERSET_EMBED_ALLOWED_DOMAINS', '').split(',')
    if domain.strip()
]


def parse_dashboard_ids() -> list[int]:
    dashboard_ids = []
    for raw_value in RAW_DASHBOARD_IDS.split(','):
        value = raw_value.strip()
        if not value:
            continue
        dashboard_ids.append(int(value))
    return dashboard_ids


try:
    from superset.app import create_app

    print('🧩 Configuration embedded dashboard...')

    app = create_app()
    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard
        from superset.daos.dashboard import EmbeddedDashboardDAO

        dashboard_ids = parse_dashboard_ids()
        if not dashboard_ids:
            print('⚠️ Aucun dashboard configure pour l\'embed')
            sys.exit(0)

        for dashboard_id in dashboard_ids:
            dashboard = db.session.query(Dashboard).filter(Dashboard.id == dashboard_id).one_or_none()
            if dashboard is None:
                print(f'⚠️ Dashboard introuvable: {dashboard_id}')
                continue

            embedded = EmbeddedDashboardDAO.upsert(dashboard, ALLOWED_DOMAINS)
            db.session.commit()

            print(f'✅ Embedded dashboard prêt pour {dashboard.id}: {embedded.uuid}')
            print(f'✅ Domaines autorisés: {embedded.allowed_domains}')

except Exception as exc:
    print(f'❌ Erreur: {exc}')
    import traceback
    traceback.print_exc()
    sys.exit(1)