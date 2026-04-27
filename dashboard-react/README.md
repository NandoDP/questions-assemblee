# Dashboard React - Questions Parlementaires

Architecture moderne avec **API Flask** + **React** pour un dashboard optimisé mobile.

## 🏗️ Architecture

```
dashboard-react/
├── backend/          # API Flask
│   ├── api/          # Modules API
│   │   ├── superset_client.py    # Client Superset
│   │   └── data_transformer.py   # Transformation données
│   ├── app.py        # Point d'entrée Flask
│   └── requirements.txt
│
└── frontend/         # Application React
    ├── src/
    │   ├── components/
    │   │   ├── Dashboard.jsx
    │   │   ├── charts/
    │   │   │   ├── KPICard.jsx
    │   │   │   ├── BarChart.jsx
    │   │   │   ├── PieChart.jsx
    │   │   │   ├── MapChart.jsx
    │   │   │   └── DataTable.jsx
    │   │   └── LoadingSkeleton.jsx
    │   ├── hooks/
    │   │   └── useDashboardData.js
    │   ├── utils/
    │   │   └── api.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

## 🚀 Démarrage

### Backend (API Flask)

```bash
cd dashboard-react/backend

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt

# Copier .env
copy .env.example .env

# Lancer l'API
python app.py
# API disponible sur http://localhost:5001
```

### Frontend (React)

```bash
cd dashboard-react/frontend

# Installer dépendances
npm install

# Lancer en dev
npm run dev
# App disponible sur http://localhost:3000

# Build production
npm run build
```

## 📱 Optimisations Mobile

- **Responsive Design** : Grid adaptatif (3 colonnes → 1 colonne)
- **Lazy Loading** : Composants chargés à la demande
- **Data Pagination** : Pagination automatique sur mobile (5 items au lieu de 10)
- **Touch Optimizations** : Zones de tap 44x44px minimum
- **Performance** : 
  - Code splitting (React chunks séparés)
  - React Query caching (5min)
  - API data transformation côté serveur

## 🔌 API Endpoints

- `GET /api/health` - Health check
- `GET /api/dashboard/:id/data?mobile=true` - Données dashboard (avec pagination mobile)
- `GET /api/charts/:id/data` - Données d'un chart spécifique
- `GET /api/kpis` - KPIs seulement (chargement rapide)

## 🎨 Composants React

### Charts
- **KPICard** : Métriques clés (questions, taux réponse, députés)
- **BarChart** : Évolution mensuelle (Recharts)
- **PieChart** : Répartition thématique (Recharts)
- **MapChart** : Carte interactive Sénégal (Leaflet)
- **DataTable** : Tableau top députés (responsive)

### Hooks
- **useDashboardData** : Récupération données avec React Query
  - Gestion cache
  - Détection mobile automatique
  - Retry sur erreur

## 🌐 Intégration dans vie-publique.sn

### Option 1 : Page dédiée
```jsx
// pages/dashboard.jsx
import DashboardEmbed from '../components/DashboardEmbed'

export default function DashboardPage() {
  return <DashboardEmbed />
}
```

### Option 2 : Section homepage
```jsx
// Ajouter dans homepage
<section className="dashboard-preview">
  <h2>📊 Questions Parlementaires</h2>
  <KPIStrip />  {/* KPIs uniquement */}
  <a href="/dashboard">Voir le dashboard complet →</a>
</section>
```

## 🚢 Déploiement

### Backend (Render)
```yaml
# render.yaml
services:
  - type: web
    name: dashboard-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: SUPERSET_URL
        value: https://questions-assemblee-superset.onrender.com
```

### Frontend (Vercel/Netlify)
```bash
# Build
npm run build

# Deploy
vercel --prod
# ou
netlify deploy --prod
```

## 🔧 TODO

- [ ] Implémenter `data_transformer.py` avec formats réels Superset
- [ ] Ajouter tests (Jest + React Testing Library)
- [ ] PWA (Service Worker + manifest.json)
- [ ] Authentification optionnelle (JWT)
- [ ] Notifications push
- [ ] Mode offline (cache local)
- [ ] A11y (accessibilité)
- [ ] i18n (Français/Wolof)

## 📊 Performance Targets

- **Time to Interactive (TTI)** : < 3s (mobile 3G)
- **First Contentful Paint (FCP)** : < 1.5s
- **Cumulative Layout Shift (CLS)** : < 0.1
- **Lighthouse Score** : > 90

## 🤝 Contribution

1. Backend : Compléter les transformateurs de données
2. Frontend : Ajouter charts manquants
3. Tests : Unit + Integration tests
4. Docs : Compléter documentation API
