import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

export const fetchDashboardData = async (dashboardId, isMobile = false) => {
  const { data } = await api.get(`/api/dashboard/${dashboardId}/data`, {
    params: { mobile: isMobile }
  })
  return data
}

export const fetchSupersetGuestToken = async (dashboardId) => {
  const { data } = await api.get('/api/superset/guest-token', {
    params: { dashboardId }
  })
  return data
}

export const fetchChartData = async (chartId) => {
  const { data } = await api.get(`/api/charts/${chartId}/data`)
  return data
}

export const fetchKPIs = async () => {
  const { data } = await api.get('/api/kpis')
  return data
}

export default api
