import { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useAuth } from '../../hooks/useAuth'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  // Pages without top padding (map pages)
  const isMapPage = location.pathname === '/' || location.pathname === '/map'

  return (
    <div className="min-h-screen bg-dark-bg">
      <Sidebar />
      <Header />

      {/* Main content area - добавляем отступ слева только если пользователь авторизован */}
      <main className={`${isAuthenticated ? 'md:ml-sidebar' : ''} ${isMapPage ? 'min-h-screen overflow-hidden' : 'min-h-0 pb-8'} ${isMapPage ? '' : 'pt-20'}`}>
        {children}
      </main>
    </div>
  )
}
