import { useDashboardData } from '../hooks/useDashboardData'
import KPICard from './charts/KPICard'
import BarChart from './charts/BarChart'
import PieChart from './charts/PieChart'
import MapChart from './charts/MapChart'
import DataTable from './charts/DataTable'
import LoadingSkeleton from './LoadingSkeleton'

const Dashboard = () => {
  const { data, isLoading, error } = useDashboardData(1)
  
  if (isLoading) return <LoadingSkeleton />
  if (error) return <div className="error">Erreur: {error.message}</div>
  if (!data) return null
  
  return (
    <div className="dashboard">
      {/* KPIs - Toujours en haut */}
      <div className="kpi-grid">
        <KPICard 
          title="Questions" 
          value={data.kpis.total_questions} 
          icon="📊"
        />
        <KPICard 
          title="Taux réponse" 
          value={`${data.kpis.response_rate}%`}
          icon="✅"
        />
        <KPICard 
          title="Députés actifs" 
          value={data.kpis.active_deputes}
          icon="👥"
        />
      </div>
      
      {/* Charts Grid */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Évolution mensuelle des questions</h3>
          <BarChart data={data.monthly_data} />
        </div>
        
        <div className="chart-card">
          <h3>Répartition par thématique</h3>
          <PieChart data={data.themes} />
        </div>
        
        <div className="chart-card chart-full">
          <h3>Volume de questions par régions</h3>
          <MapChart data={data.regions} />
        </div>
        
        <div className="chart-card chart-full">
          <h3>TOP 10 des députés les plus actifs</h3>
          <DataTable data={data.top_deputes} />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
