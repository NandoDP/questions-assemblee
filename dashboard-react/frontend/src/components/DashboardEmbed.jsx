import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { embedDashboard } from '@superset-ui/embedded-sdk'
import { fetchSupersetGuestToken } from '../utils/api'

const DashboardEmbed = () => {
  const mountRef = useRef(null)
  const { data, isLoading, error } = useQuery({
    queryKey: ['superset-guest-token', 1],
    queryFn: () => fetchSupersetGuestToken(1),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })

  useEffect(() => {
    if (!data || !mountRef.current) {
      return
    }

    mountRef.current.innerHTML = ''

    let embeddedDashboard = null
    let isCancelled = false

    embedDashboard({
      id: String(data.dashboardUuid),
      supersetDomain: data.supersetDomain,
      mountPoint: mountRef.current,
      fetchGuestToken: async () => data.token,
      dashboardUiConfig: {
        hideTitle: true,
        hideTab: true,
        hideChartControls: true,
        filters: {
          expanded: false,
          visible: false,
        },
      },
    })
      .then((instance) => {
        if (isCancelled) {
          instance.unmount()
          return
        }

        embeddedDashboard = instance
      })
      .catch((embedError) => {
        console.error('Erreur embed Superset', embedError)
        if (mountRef.current) {
          mountRef.current.innerHTML = '<div class="embed-error">Impossible de charger le dashboard embarqué.</div>'
        }
      })

    return () => {
      isCancelled = true
      if (embeddedDashboard) {
        embeddedDashboard.unmount()
      }
    }
  }, [data])
  
  if (isLoading) {
    return (
      <div className="loading-skeleton">
        <p>Chargement du dashboard...</p>
      </div>
    )
  }
  
  if (error) {
    return <div className="error">Erreur: {error.message}</div>
  }
  
  return (
    <div className="dashboard-embed-frame dashboard-embed-frame-fullscreen" ref={mountRef} />
  )
}

export default DashboardEmbed
