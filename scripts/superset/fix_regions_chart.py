#!/usr/bin/env python3
"""
Répare le chart "Volume de questions par régions" au démarrage de Superset.

Le problème venait d'un query_context figé sans groupement par code_region,
ce qui forçait Superset à calculer une agrégation globale unique.
"""

import json
import os
import sys

os.environ.setdefault("SUPERSET_CONFIG_PATH", "/app/pythonpath/superset_config.py")

CHART_ID = int(os.getenv("SUPERSET_REGIONS_CHART_ID", "1"))
DATASET_ID = int(os.getenv("SUPERSET_REGIONS_DATASET_ID", "2"))
PUBLIC_DASHBOARD_IDS = [
    int(value.strip())
    for value in os.getenv("SUPERSET_PUBLIC_DASHBOARD_IDS", "1,3").split(",")
    if value.strip()
]

DATASET_SQL = """
SELECT
  d.nom AS departement,
  d.code_region,
  d.code_dep,
  d.latitude,
  d.longitude,
  COUNT(DISTINCT q.id) AS count
FROM questions AS q
JOIN LATERAL UNNEST(q.departements_concernes) AS departement_nom ON TRUE
LEFT JOIN departements AS d ON d.nom = departement_nom
WHERE q.departements_concernes IS NOT NULL
  AND d.code_region IS NOT NULL
GROUP BY d.nom, d.code_region, d.code_dep, d.latitude, d.longitude
""".strip()


def default_metric() -> dict:
    return {
        "expressionType": "SIMPLE",
        "column": {
            "column_name": "count",
            "type": "LONGINTEGER",
            "type_generic": 0,
        },
        "aggregate": "SUM",
        "sqlExpression": None,
        "datasourceWarning": False,
        "hasCustomLabel": False,
        "label": "SUM(count)",
    }


try:
    from superset.app import create_app

    print("🗺️ Réparation du chart régions...")

    app = create_app()
    with app.app_context():
        from superset.connectors.sqla.models import SqlaTable
        from superset.extensions import db
        from superset.models.slice import Slice

        dataset = db.session.query(SqlaTable).filter_by(id=DATASET_ID).one_or_none()
        chart = db.session.query(Slice).filter_by(id=CHART_ID).one_or_none()

        if not dataset:
            print(f"⚠️ Dataset {DATASET_ID} introuvable")
            sys.exit(0)

        if not chart:
            print(f"⚠️ Chart {CHART_ID} introuvable")
            sys.exit(0)

        changed = False

        if (dataset.sql or "").strip() != DATASET_SQL:
            dataset.sql = DATASET_SQL
            changed = True
            print(f"  ✓ Dataset {dataset.table_name} SQL mis à jour")

        params = json.loads(chart.params or "{}")
        metric = params.get("metric") or default_metric()
        dashboard_ids = params.get("dashboards") or PUBLIC_DASHBOARD_IDS
        dashboard_ids = [int(dashboard_id) for dashboard_id in dashboard_ids]

        params.update(
            {
                "datasource": f"{dataset.id}__table",
                "slice_id": chart.id,
                "viz_type": "country_map",
                "select_country": "senegal",
                "entity": "code_region",
                "metric": metric,
                "row_limit": 50000,
                "adhoc_filters": params.get("adhoc_filters", []),
                "extra_form_data": params.get("extra_form_data", {}),
                "dashboards": dashboard_ids,
            }
        )

        desired_query_context = {
            "datasource": {"id": dataset.id, "type": "table"},
            "force": False,
            "queries": [
                {
                    "filters": [],
                    "extras": {"having": "", "where": ""},
                    "applied_time_extras": {},
                    "columns": ["code_region"],
                    "metrics": [metric],
                    "annotation_layers": [],
                    "series_limit": 0,
                    "row_limit": params["row_limit"],
                    "url_params": {},
                    "custom_params": {},
                    "custom_form_data": {},
                }
            ],
            "form_data": {
                **params,
                "slice_id": chart.id,
                "dashboards": dashboard_ids,
                "force": False,
                "result_format": "json",
                "result_type": "full",
            },
            "result_format": "json",
            "result_type": "full",
        }

        serialized_params = json.dumps(params, sort_keys=True)
        serialized_query_context = json.dumps(desired_query_context, sort_keys=True)

        if chart.params != serialized_params:
            chart.params = serialized_params
            changed = True
            print(f"  ✓ Chart {chart.id} params mis à jour")

        if chart.query_context != serialized_query_context:
            chart.query_context = serialized_query_context
            changed = True
            print(f"  ✓ Chart {chart.id} query_context régénéré")

        if chart.datasource_id != dataset.id:
            chart.datasource_id = dataset.id
            changed = True

        if chart.datasource_type != "table":
            chart.datasource_type = "table"
            changed = True

        if changed:
            db.session.commit()
            print("✅ Chart régions réparé")
        else:
            print("✓ Chart régions déjà à jour")

except Exception as exc:
    print(f"❌ Erreur réparation chart régions: {exc}")
    import traceback

    traceback.print_exc()
    sys.exit(1)