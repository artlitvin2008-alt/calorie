import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useTelegramWebApp, useTelegramTheme } from './lib/useTelegramWebApp'
import { apiClient } from './lib/api'
import { getTelegramTheme } from './lib/theme'
import { useThemeStore } from './store/themeStore'
import Navigation from './components/Navigation'

// Pages (will be created)
import DashboardPage from './pages/DashboardPage'
import DiaryPage from './pages/DiaryPage'
import AnalyticsPage from './pages/AnalyticsPage'
import ProfilePage from './pages/ProfilePage'

function App() {
  const { initData, colorScheme, themeParams } = useTelegramWebApp()
  const { isDark } = useTelegramTheme()
  const setTheme = useThemeStore(state => state.setTheme)

  useEffect(() => {
    // Set initData for API client
    if (initData) {
      apiClient.setInitData(initData)
    }

    // Apply Telegram theme
    const theme = getTelegramTheme(colorScheme, themeParams)
    setTheme(theme)
  }, [initData, colorScheme, themeParams, setTheme])

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background-light dark:bg-background-dark pb-20">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/diary" element={<DiaryPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
        
        <Navigation />
      </div>
    </BrowserRouter>
  )
}

export default App
