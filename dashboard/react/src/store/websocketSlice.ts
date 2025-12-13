import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface WebSocketState {
  connected: boolean
  connecting: boolean
  error: string | null
  lastMessage: any
  subscriptions: string[]
  reconnectAttempts: number
  maxReconnectAttempts: number
}

const initialState: WebSocketState = {
  connected: false,
  connecting: false,
  error: null,
  lastMessage: null,
  subscriptions: [],
  reconnectAttempts: 0,
  maxReconnectAttempts: 5
}

const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    connectStart: (state) => {
      state.connecting = true
      state.error = null
    },
    connectSuccess: (state) => {
      state.connected = true
      state.connecting = false
      state.error = null
      state.reconnectAttempts = 0
    },
    connectFailure: (state, action: PayloadAction<string>) => {
      state.connected = false
      state.connecting = false
      state.error = action.payload
      state.reconnectAttempts += 1
    },
    disconnect: (state) => {
      state.connected = false
      state.connecting = false
      state.subscriptions = []
    },
    messageReceived: (state, action: PayloadAction<any>) => {
      state.lastMessage = action.payload
    },
    subscribe: (state, action: PayloadAction<string>) => {
      if (!state.subscriptions.includes(action.payload)) {
        state.subscriptions.push(action.payload)
      }
    },
    unsubscribe: (state, action: PayloadAction<string>) => {
      state.subscriptions = state.subscriptions.filter(sub => sub !== action.payload)
    },
    clearError: (state) => {
      state.error = null
    }
  }
})

export const {
  connectStart,
  connectSuccess,
  connectFailure,
  disconnect,
  messageReceived,
  subscribe,
  unsubscribe,
  clearError
} = websocketSlice.actions

export default websocketSlice.reducer