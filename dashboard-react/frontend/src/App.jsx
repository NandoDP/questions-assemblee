import Dashboard from './components/Dashboard'
import DashboardEmbed from './components/DashboardEmbed'
import './App.css'

// Mode d'affichage : 'native' ou 'embed'
const DISPLAY_MODE = 'embed-sdk' // 'native' ou 'embed-sdk'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>📊 Questions Parlementaires</h1>
          <p>Analyse automatisée avec classification ML • Dashboard en lecture seule</p>
        </div>
      </header>
      
      <main className="app-main">
        {DISPLAY_MODE === 'embed-sdk' ? <DashboardEmbed /> : <Dashboard />}
      </main>
      
      <footer className="app-footer">
        <div className="container">
          <p>
            Données mises à jour quotidiennement via GitHub Actions •{' '}
            <a href="https://github.com/NandoDP/questions-assemblee" target="_blank" rel="noopener noreferrer">
              Code source
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
