import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect } from 'react'
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
import { Notifications } from './pages/Notifications'
import { UserSettings } from './pages/UserSettings'
import { Gamification } from './pages/Gamification'
import { Subscriptions } from './pages/Subscriptions'
import { SocialFeed } from './pages/SocialFeed'
import { ProtectedRoute } from './components/ProtectedRoute'
import { useAuth } from './hooks/useAuth'
import './api/client' // Инициализация API клиента

// Create a client with better error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.status >= 400 && error?.status < 500) {
          return false
        }
        // Retry up to 2 times for other errors
        return failureCount < 2
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: false, // Don't retry mutations by default
    },
  },
})

function AppContent() {
  const { checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/about" element={<MainLayout><About /></MainLayout>} />
      <Route path="/how-it-works" element={<MainLayout><HowItWorks /></MainLayout>} />
      <Route path="/contacts" element={<MainLayout><Contacts /></MainLayout>} />

      {/* Protected routes */}
      <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
      <Route path="/map" element={<MainLayout><MapPage /></MainLayout>} />
      <Route path="/problems/:id" element={<MainLayout><ProblemDetailPage /></MainLayout>} />
      <Route path="/users/:userId" element={<MainLayout><UserProfilePage /></MainLayout>} />
      <Route path="/problems" element={<ProtectedRoute><MainLayout><ProblemsPage /></MainLayout></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><MainLayout><AnalyticsPage /></MainLayout></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><MainLayout><Notifications /></MainLayout></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><MainLayout><Profile /></MainLayout></ProtectedRoute>} />
      <Route path="/reports" element={<ProtectedRoute><MainLayout><MyReports /></MainLayout></ProtectedRoute>} />
      <Route path="/settings" element={<ProtectedRoute><MainLayout><UserSettings /></MainLayout></ProtectedRoute>} />
      <Route path="/achievements" element={<ProtectedRoute><MainLayout><Gamification /></MainLayout></ProtectedRoute>} />
      <Route path="/subscriptions" element={<ProtectedRoute><MainLayout><Subscriptions /></MainLayout></ProtectedRoute>} />
      <Route path="/feed" element={<ProtectedRoute><MainLayout><SocialFeed /></MainLayout></ProtectedRoute>} />
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
