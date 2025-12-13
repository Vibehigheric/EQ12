import { configureStore } from '@reduxjs/toolkit'
import parlaySlice from './parlaySlice'
import metricsSlice from './metricsSlice'
import websocketSlice from './websocketSlice'

export const store = configureStore({
  reducer: {
    parlay: parlaySlice,
    metrics: metricsSlice,
    websocket: websocketSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['websocket/messageReceived'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch