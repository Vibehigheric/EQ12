import React, { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import ParlayBuilder from './components/ParlayBuilder'
import MetricsView from './components/MetricsView'
import SettingsView from './components/SettingsView'
import { connectStart, connectSuccess, connectFailure, messageReceived } from './store/websocketSlice'
import { updateSystemMetrics } from './store/metricsSlice'
import io from 'socket.io-client'

function App() {
  const dispatch = useDispatch()
  const [socket, setSocket] = useState<any>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    dispatch(connectStart())
    
    const newSocket = io('ws://localhost:3001', {
      transports: ['websocket']
    })

    newSocket.on('connect', () => {
      dispatch(connectSuccess())
      console.log('Connected to WebSocket server')
    })

    newSocket.on('disconnect', () => {
      dispatch(connectFailure('Connection lost'))
    })

    newSocket.on('error', (error) => {
      dispatch(connectFailure(error.message))
    })

    newSocket.on('metrics', (data) => {
      dispatch(updateSystemMetrics(data))
    })

    newSocket.on('message', (data) => {
      dispatch(messageReceived(data))
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [dispatch])

  return (
    <div className="flex h-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/parlay" element={<ParlayBuilder />} />
          <Route path="/metrics" element={<MetricsView />} />
          <Route path="/settings" element={<SettingsView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App