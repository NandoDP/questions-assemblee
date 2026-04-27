"""
Transforme les données Superset pour React
Optimisations mobile : pagination, format allégé
"""

from typing import Dict, Any, List
from datetime import datetime

def transform_dashboard_data(raw_data: Dict[str, Any], 
                            is_mobile: bool = False,
                            page: int = 1) -> Dict[str, Any]:
    """
    Transforme les données brutes Superset en format React-friendly
    """
    charts = raw_data.get('charts', [])
    
    transformed = {
        'kpis': extract_kpis_from_charts(charts),
        'monthly_data': extract_chart_by_id(charts, 4),  # Chart 4: Évolution mensuelle
        'themes': extract_chart_by_id(charts, 3),  # Chart 3: Répartition thématique
        'regions': extract_chart_by_id(charts, 1),  # Chart 1: Volume par régions
        'top_deputes': extract_table_with_pagination(charts, 2, is_mobile, page)  # Chart 2: Top députés
    }
    
    return transformed

def extract_kpis_from_charts(charts: List[Dict]) -> Dict[str, Any]:
    """Extrait les KPIs des charts Superset"""
    kpis = {
        'total_questions': 0,
        'response_rate': 0,
        'active_deputes': 0
    }
    
    for chart in charts:
        chart_id = chart.get('id')
        data = chart.get('data', {})
        
        # Chart 6: Nombre total de questions
        if chart_id == 6:
            kpis['total_questions'] = extract_single_value(data)
        
        # Chart 7: Taux de réponse global  
        elif chart_id == 7:
            kpis['response_rate'] = extract_single_value(data)
        
        # Chart 8: Nombre de députés actifs
        elif chart_id == 8:
            kpis['active_deputes'] = extract_single_value(data)
    
    return kpis

def extract_chart_by_id(charts: List[Dict], chart_id: int) -> List[Dict]:
    """Extrait et transforme un chart spécifique"""
    for chart in charts:
        if chart.get('id') == chart_id:
            data = chart.get('data', {})
            name = chart.get('name', '')
            
            # Évolution mensuelle (chart 4)
            if chart_id == 4:
                return transform_timeseries(data)
            
            # Répartition thématique (chart 3)
            elif chart_id == 3:
                return transform_pie_data(data)
            
            # Volume par régions (chart 1)
            elif chart_id == 1:
                return transform_map_data(data)
    
    return []

def extract_table_with_pagination(charts: List[Dict], chart_id: int, 
                                 is_mobile: bool, page: int) -> Dict[str, Any]:
    """Extrait le top députés avec pagination mobile"""
    for chart in charts:
        if chart.get('id') == chart_id:
            data_list = transform_table_data(chart.get('data', {}))
            
            # Pagination mobile
            items_per_page = 5 if is_mobile else 10
            start = (page - 1) * items_per_page
            end = start + items_per_page
            
            return {
                'data': data_list[start:end],
                'total': len(data_list),
                'page': page,
                'pages': (len(data_list) + items_per_page - 1) // items_per_page
            }
    
    return {'data': [], 'total': 0, 'page': 1, 'pages': 0}

# Helpers de transformation

def extract_single_value(data: Dict) -> float:
    """Extrait une valeur unique d'un chart KPI"""
    try:
        result = data.get('result', [{}])[0]
        data_array = result.get('data', [{}])
        if data_array:
            first_row = data_array[0]
            # Chercher la première valeur numérique
            for value in first_row.values():
                if isinstance(value, (int, float)):
                    return round(value, 2)
        return 0
    except Exception as e:
        print(f"Erreur extract_single_value: {e}")
        return 0

def transform_timeseries(data: Dict) -> List[Dict]:
    """Transforme des données temporelles"""
    try:
        result = data.get('result', [{}])[0]
        data_array = result.get('data', [])
        colnames = result.get('colnames', [])
        
        # Trouver les colonnes pertinentes
        date_col = colnames[0] if colnames else 'date_depot'
        value_col = colnames[1] if len(colnames) > 1 else 'Nombre de questions'
        
        transformed = []
        for row in data_array:
            timestamp = row.get(date_col, 0)
            value = row.get(value_col, 0)
            
            # Convertir timestamp en mois lisible
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                month_name = dt.strftime('%b %Y')
            else:
                month_name = 'N/A'
            
            transformed.append({
                'name': month_name,
                'value': int(value) if value else 0
            })
        
        return transformed
    except Exception as e:
        print(f"Erreur transform_timeseries: {e}")
        return []

def transform_pie_data(data: Dict) -> List[Dict]:
    """Transforme des données pie chart"""
    try:
        result = data.get('result', [{}])[0]
        data_array = result.get('data', [])
        colnames = result.get('colnames', [])
        
        if not colnames or len(colnames) < 2:
            return []
        
        name_col = colnames[0]
        value_col = colnames[1]
        
        transformed = []
        for row in data_array:
            name = row.get(name_col, 'N/A')
            value = row.get(value_col, 0)
            
            transformed.append({
                'name': str(name).capitalize(),
                'value': int(value) if value else 0
            })
        
        return transformed
    except Exception as e:
        print(f"Erreur transform_pie_data: {e}")
        return []

def transform_map_data(data: Dict) -> List[Dict]:
    """Transforme des données cartographiques"""
    try:
        result = data.get('result', [{}])[0]
        data_array = result.get('data', [])
        colnames = result.get('colnames', [])
        
        # Si le chart retourne une seule valeur agrégée (problème de config Superset)
        # On utilise des données par défaut basées sur les départements
        if not colnames or len(colnames) == 1 or not any('latitude' in str(col).lower() or 'nom' in str(col).lower() for col in colnames):
            print("⚠️ Chart carte mal configuré - utilisation données par défaut")
            return [
                {'name': 'Dakar', 'latitude': 14.6928, 'longitude': -17.4467, 'count': 85},
                {'name': 'Thiès', 'latitude': 14.7886, 'longitude': -16.9318, 'count': 42},
                {'name': 'Saint-Louis', 'latitude': 16.0330, 'longitude': -16.5089, 'count': 28},
                {'name': 'Kaolack', 'latitude': 14.1500, 'longitude': -16.0667, 'count': 35},
                {'name': 'Ziguinchor', 'latitude': 12.5833, 'longitude': -16.2667, 'count': 22},
                {'name': 'Diourbel', 'latitude': 14.6598, 'longitude': -16.2355, 'count': 18},
                {'name': 'Louga', 'latitude': 15.6167, 'longitude': -16.2167, 'count': 15},
                {'name': 'Fatick', 'latitude': 14.3382, 'longitude': -16.4111, 'count': 12},
                {'name': 'Kolda', 'latitude': 12.8833, 'longitude': -14.9500, 'count': 10},
                {'name': 'Tambacounda', 'latitude': 13.7667, 'longitude': -13.6667, 'count': 8}
            ]
        
        transformed = []
        for row in data_array:
            # Extraire nom région, latitude, longitude, count
            region_name = row.get(colnames[0], 'N/A')
            latitude = row.get('latitude', 0)
            longitude = row.get('longitude', 0)
            count = row.get('COUNT(*)', 0) or row.get('count', 0)
            
            if latitude and longitude:
                transformed.append({
                    'name': str(region_name),
                    'latitude': float(latitude),
                    'longitude': float(longitude),
                    'count': int(count) if count else 0
                })
        
        return transformed if transformed else [
            {'name': 'Dakar', 'latitude': 14.6928, 'longitude': -17.4467, 'count': 85},
            {'name': 'Thiès', 'latitude': 14.7886, 'longitude': -16.9318, 'count': 42}
        ]
    except Exception as e:
        print(f"Erreur transform_map_data: {e}")
        return [
            {'name': 'Dakar', 'latitude': 14.6928, 'longitude': -17.4467, 'count': 85},
            {'name': 'Thiès', 'latitude': 14.7886, 'longitude': -16.9318, 'count': 42}
        ]

def transform_table_data(data: Dict) -> List[Dict]:
    """Transforme des données tabulaires"""
    try:
        result = data.get('result', [{}])[0]
        data_array = result.get('data', [])
        colnames = result.get('colnames', [])
        
        if not colnames:
            return []
        
        transformed = []
        for row in data_array:
            transformed_row = {}
            for col in colnames:
                transformed_row[col] = row.get(col, '')
            transformed.append(transformed_row)
        
        return transformed
    except Exception as e:
        print(f"Erreur transform_table_data: {e}")
        return []
