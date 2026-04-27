import { useQuery } from '@tanstack/react-query'
import { fetchDashboardData } from '../utils/api'

export const useDashboardData = (dashboardId) => {
  const isMobile = window.innerWidth < 768
  
  return useQuery({
    queryKey: ['dashboard', dashboardId, isMobile],
    queryFn: () => fetchDashboardData(dashboardId, isMobile),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
