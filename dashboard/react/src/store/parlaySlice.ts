import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface BettingLeg {
  player: string
  market: string
  line: number
  odds: number
  probability: number
  expectedValue: number
  kellyStake: number
  confidence: number
  riskCategory: string
}

export interface ParlayRecommendation {
  legs: BettingLeg[]
  totalOdds: number
  expectedPayout: number
  riskScore: number
  kellyPercentage: number
  confidenceScore: number
  edgePercentage: number
  status: 'pending' | 'active' | 'won' | 'lost'
  timestamp: string
}

interface ParlayState {
  recommendations: ParlayRecommendation[]
  currentParlay: ParlayRecommendation | null
  isGenerating: boolean
  error: string | null
  filters: {
    minEV: number
    maxRisk: number
    sports: string[]
  }
}

const initialState: ParlayState = {
  recommendations: [],
  currentParlay: null,
  isGenerating: false,
  error: null,
  filters: {
    minEV: 8.0,
    maxRisk: 0.7,
    sports: ['MLB', 'NBA', 'NFL']
  }
}

const parlaySlice = createSlice({
  name: 'parlay',
  initialState,
  reducers: {
    generateParlayStart: (state) => {
      state.isGenerating = true
      state.error = null
    },
    generateParlaySuccess: (state, action: PayloadAction<ParlayRecommendation>) => {
      state.isGenerating = false
      state.currentParlay = action.payload
      state.recommendations.unshift(action.payload)
      // Keep only last 50 recommendations
      state.recommendations = state.recommendations.slice(0, 50)
    },
    generateParlayFailure: (state, action: PayloadAction<string>) => {
      state.isGenerating = false
      state.error = action.payload
    },
    setCurrentParlay: (state, action: PayloadAction<ParlayRecommendation>) => {
      state.currentParlay = action.payload
    },
    updateParlayStatus: (state, action: PayloadAction<{id: string, status: ParlayRecommendation['status']}>) => {
      const parlay = state.recommendations.find(p => p.timestamp === action.payload.id)
      if (parlay) {
        parlay.status = action.payload.status
      }
      if (state.currentParlay?.timestamp === action.payload.id) {
        state.currentParlay.status = action.payload.status
      }
    },
    updateFilters: (state, action: PayloadAction<Partial<ParlayState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload }
    },
    clearError: (state) => {
      state.error = null
    }
  }
})

export const {
  generateParlayStart,
  generateParlaySuccess,
  generateParlayFailure,
  setCurrentParlay,
  updateParlayStatus,
  updateFilters,
  clearError
} = parlaySlice.actions

export default parlaySlice.reducer