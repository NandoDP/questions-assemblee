#!/usr/bin/env python3
"""Crée la configuration embedded pour les dashboards Superset publies."""

import os
import sys
from urllib.parse import urlparse

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')

RAW_DASHBOARD_IDS = os.getenv('SUPERSET_PUBLIC_DASHBOARD_IDS', '').strip()


def normalize_domain(domain: str) -> str:
    value = domain.strip()
    if not value:
        return ''
    if '://' not in value:
        value = f'https://{value}'
    parsed = urlparse(value)
    return parsed.scheme + '://' + parsed.netloc


ALLOWED_DOMAINS = [
    normalize_domain(domain)
    for domain in os.getenv('SUPERSET_EMBED_ALLOWED_DOMAINS', '').split(',')
    if normalize_domain(domain)
]


def parse_dashboard_ids() -> list[int]:
    if not RAW_DASHBOARD_IDS:
        return []
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
        if dashboard_ids:
            dashboards = db.session.query(Dashboard).filter(Dashboard.id.in_(dashboard_ids)).all()
        else:
            dashboards = db.session.query(Dashboard).filter(Dashboard.published.is_(True)).all()

        if not dashboards:
            print('⚠️ Aucun dashboard publie a configurer pour l\'embed')
            sys.exit(0)

        for dashboard in dashboards:
            embedded = EmbeddedDashboardDAO.upsert(dashboard, ALLOWED_DOMAINS)
            db.session.commit()

            print(f'✅ Embedded dashboard prêt pour {dashboard.id}: {embedded.uuid}')
            print(f'✅ Domaines autorisés: {embedded.allowed_domains}')

except Exception as exc:
    print(f'❌ Erreur: {exc}')
    import traceback
    traceback.print_exc()
    sys.exit(1)