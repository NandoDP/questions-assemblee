#!/usr/bin/env python3
"""Assigne le role Public aux dashboards publies embarques."""

import os
import sys

os.environ.setdefault('SUPERSET_CONFIG_PATH', '/app/pythonpath/superset_config.py')


def parse_dashboard_ids() -> list[int]:
    raw_ids = os.getenv('SUPERSET_PUBLIC_DASHBOARD_IDS', os.getenv('SUPERSET_DASHBOARD_ID', '1'))
    dashboard_ids = []
    for raw_value in raw_ids.split(','):
        value = raw_value.strip()
        if not value:
            continue
        try:
            dashboard_ids.append(int(value))
        except ValueError:
            print(f'⚠️ Dashboard ignore (id invalide): {value}')
    return dashboard_ids


try:
    from superset.app import create_app

    print('📺 Attribution du role Public aux dashboards embarques...')

    app = create_app()
    with app.app_context():
        from superset import security_manager
        from superset.extensions import db
        from superset.models.dashboard import Dashboard

        public_role = security_manager.find_role('Public')
        if not public_role:
            print('❌ Role Public introuvable')
            sys.exit(1)

        updated = 0
        for dashboard_id in parse_dashboard_ids():
            dashboard = db.session.query(Dashboard).filter(Dashboard.id == dashboard_id).one_or_none()
            if dashboard is None:
                print(f'⚠️ Dashboard introuvable: {dashboard_id}')
                continue

            if public_role not in dashboard.roles:
                dashboard.roles.append(public_role)
                updated += 1
                print(f'  ✓ Dashboard {dashboard.id} ({dashboard.dashboard_title}) partage avec Public')
            else:
                print(f'  → Dashboard {dashboard.id} ({dashboard.dashboard_title}) deja partage avec Public')

        db.session.commit()
        print(f'✅ Dashboards publics mis a jour: {updated}')

except Exception as exc:
    print(f'❌ Erreur: {exc}')
    import traceback
    traceback.print_exc()
    sys.exit(1)