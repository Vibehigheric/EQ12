import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface SystemMetrics {
  timestamp: string
  cpuPercent: number
  memoryPercent: number
  diskUsage: number
  activeConnections: number
  cacheHitRate: number
  apiRequestsPerMinute: number
  errorRate: number
}

export interface BettingMetrics {
  totalParlays: number
  winRate: number
  avgROI: number
  totalProfit: number
  sharpeRatio: number
  maxDrawdown: number
  dailyVolume: number
}

interface MetricsState {
  systemMetrics: SystemMetrics[]
  bettingMetrics: BettingMetrics | null
  isLoading: boolean
  lastUpdated: string | null
  alerts: Alert[]
}

interface Alert {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  dismissed: boolean
}

const initialState: MetricsState = {
  systemMetrics: [],
  bettingMetrics: null,
  isLoading: false,
  lastUpdated: null,
  alerts: []
}

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    updateSystemMetrics: (state, action: PayloadAction<SystemMetrics>) => {
      state.systemMetrics.push(action.payload)
      // Keep only last 100 data points
      state.systemMetrics = state.systemMetrics.slice(-100)
      state.lastUpdated = action.payload.timestamp
    },
    updateBettingMetrics: (state, action: PayloadAction<BettingMetrics>) => {
      state.bettingMetrics = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload
    },
    addAlert: (state, action: PayloadAction<Omit<Alert, 'id' | 'dismissed'>>) => {
      const alert: Alert = {
        ...action.payload,
        id: Math.random().toString(36).substr(2, 9),
        dismissed: false
      }
      state.alerts.push(alert)
    },
    dismissAlert: (state, action: PayloadAction<string>) => {
      const alert = state.alerts.find(a => a.id === action.payload)
      if (alert) {
        alert.dismissed = true
      }
    },
    clearDismissedAlerts: (state) => {
      state.alerts = state.alerts.filter(a => !a.dismissed)
    }
  }
})

export const {
  updateSystemMetrics,
  updateBettingMetrics,
  setLoading,
  addAlert,
  dismissAlert,
  clearDismissedAlerts
} = metricsSlice.actions

export default metricsSlice.reducer