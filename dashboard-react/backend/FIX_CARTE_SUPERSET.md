# Correction du chart "Volume de questions par régions"

## Problème
Le chart actuel retourne une seule valeur agrégée (148) au lieu des données par département nécessaires pour la carte.

## Solution : Modifier la requête SQL dans Superset

### Étapes
1. Connexion : https://questions-assemblee-superset.onrender.com
2. Login : guest / guest
3. Aller dans Charts → "Volume de questions par régions" (ID: 1)
4. Cliquer sur "Edit chart"
5. Remplacer la requête SQL par celle ci-dessous

### Nouvelle requête SQL

```sql
SELECT 
  d.nom AS departement,
  d.latitude,
  d.longitude,
  d.code_region,
  COUNT(DISTINCT q.id) AS count
FROM questions AS q
JOIN LATERAL UNNEST(q.departements_concernes) AS departement_nom ON TRUE
LEFT JOIN departements AS d ON d.nom = departement_nom
WHERE q.departements_concernes IS NOT NULL
  AND d.latitude IS NOT NULL 
  AND d.longitude IS NOT NULL
GROUP BY d.nom, d.latitude, d.longitude, d.code_region
ORDER BY count DESC
```

### Ou version simplifiée (sans JOIN)

```sql
SELECT 
  d.nom AS nom,
  d.latitude AS latitude,
  d.longitude AS longitude,
  COUNT(*) AS count
FROM departements AS d
LEFT JOIN questions AS q ON d.nom = ANY(q.departements_concernes)
WHERE d.latitude IS NOT NULL
GROUP BY d.nom, d.latitude, d.longitude
ORDER BY count DESC
```

### Configuration du chart
- **Chart type** : Deck.gl Scatterplot ou Deck.gl Hexagon
- **Longitude** : longitude
- **Latitude** : latitude
- **Metric** : count
- **Label** : nom

### Après modification
1. Sauvegarder le chart
2. Redémarrer l'API backend (ou attendre le redémarrage automatique)
3. Les vraies données s'afficheront sur la carte

## Alternative : Créer un nouveau chart
Si vous ne voulez pas modifier l'existant, créez un nouveau chart avec l'ID 9 et modifiez `data_transformer.py` :
```python
# Chart 9: Volume par régions (nouveau)
elif chart_id == 9:
    return transform_map_data(data)
```

Et dans `app.py` :
```python
'regions': extract_chart_by_id(charts, 9),  # Chart 9 au lieu de 1
```
