import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Toaster } from 'sonner'
import MainLayout from './components/layout/MainLayout'
import HomePage from './pages/HomePage'
import MapPage from './pages/MapPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import ProblemsPage from './pages/ProblemsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import UserProfilePage from './pages/UserProfilePage'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Profile } from './pages/Profile'
import { About } from './pages/About'
import { HowItWorks } from './pages/HowItWorks'
import { Contacts } from './pages/Contacts'
import { MyReports } from './pages/MyReports'
import NotificationsPage from './pages/NotificationsPage'
import { UserSettings } from './pages/UserSettings'
import { Gamification } from './pages/Gamification'
import { Subscriptions } from './pages/Subscriptions'
import { SocialFeed } from './pages/SocialFeed'
import AdminDashboard from './pages/AdminDashboard'
import { ProtectedRoute } from './components/ProtectedRoute'
import { useAuth } from './hooks/useAuth'
import './api/client'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => {
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        return failureCount < 2
      },
      staleTime: 5 * 60 * 1000,
    },
    mutations: {
      retry: false,
    },
  },
})

function AppContent() {
  const { checkAuth } = useAuth()
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    checkAuth().finally(() => setIsReady(true))
  }, [checkAuth])

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0B1220]">
        <div className="text-[#E5E7EB]">Загрузка...</div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/about" element={<MainLayout><About /></MainLayout>} />
      <Route path="/how-it-works" element={<MainLayout><HowItWorks /></MainLayout>} />
      <Route path="/contacts" element={<MainLayout><Contacts /></MainLayout>} />

      <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
      <Route path="/map" element={<MainLayout><MapPage /></MainLayout>} />
      <Route path="/problems/:id" element={<MainLayout><ProblemDetailPage /></MainLayout>} />
      <Route path="/users/:userId" element={<MainLayout><UserProfilePage /></MainLayout>} />
      <Route path="/problems" element={<ProtectedRoute><MainLayout><ProblemsPage /></MainLayout></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><MainLayout><AnalyticsPage /></MainLayout></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><MainLayout><NotificationsPage /></MainLayout></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><MainLayout><Profile /></MainLayout></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><MainLayout><MyReports /></MainLayout></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><MainLayout><UserSettings /></MainLayout></ProtectedRoute>} />
      <Route path="/achievements" element={<ProtectedRoute><MainLayout><Gamification /></MainLayout></ProtectedRoute>} />
      <Route path="/subscriptions" element={<ProtectedRoute><MainLayout><Subscriptions /></MainLayout></ProtectedRoute>} />
      <Route path="/feed" element={<ProtectedRoute><MainLayout><SocialFeed /></MainLayout></ProtectedRoute>} />
      <Route path="/admin" element={<ProtectedRoute><MainLayout><AdminDashboard /></MainLayout></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
        <Toaster
          position="top-right"
          theme="dark"
          richColors
          closeButton
          duration={4000}
        />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App