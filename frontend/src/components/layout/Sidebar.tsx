import { useState } from 'react'
import { Home, Map, AlertCircle, BarChart3, Bell, User, Plus, Flag, Activity } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import ProblemCreateForm from '../problem/ProblemCreateForm'

const authNavItems = [
  { icon: Home, label: 'Dashboard', path: '/' },
  { icon: AlertCircle, label: 'Problems', path: '/problems' },
  { icon: Activity, label: 'Feed', path: '/feed' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: Bell, label: 'Notifications', path: '/notifications' },
  { icon: Flag, label: 'Reports', path: '/reports' },
  { icon: User, label: 'Profile', path: '/profile' },
]

export default function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [isCreateFormOpen, setIsCreateFormOpen] = useState(false)

  // Не показываем sidebar если пользователь не авторизован
  if (!isAuthenticated) {
    return null
  }

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex fixed left-0 top-20 h-[calc(100vh-5rem)] w-sidebar bg-dark-card border-r border-border flex-col items-center py-6 z-40">
        {/* Navigation */}
        <nav className="flex-1 flex flex-col gap-2 w-full px-3">
          {authNavItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex flex-col items-center gap-1 py-3 px-2 rounded-md
                  ${
                    isActive
                      ? 'bg-primary/10 text-primary scale-105'
                      : 'text-text-secondary hover:bg-dark-hover hover:text-text-primary hover:scale-110'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* Create Button */}
        <button
          onClick={() => setIsCreateFormOpen(true)}
          className="w-14 h-14 bg-primary hover:bg-primary-hover rounded-full flex items-center justify-center shadow-lg hover:shadow-xl hover:scale-110 active:scale-95"
        >
          <Plus className="w-6 h-6 text-white" />
        </button>
      </aside>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 glass border-t z-[10000]" style={{ borderWidth: '1px' }}>
        <div className="h-full flex items-center justify-around px-2">
          {authNavItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex flex-col items-center gap-1 py-2 px-3 rounded-lg
                  ${
                    isActive
                      ? 'text-primary'
                      : 'text-text-secondary'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Mobile FAB (Floating Action Button) */}
      <button
        onClick={() => setIsCreateFormOpen(true)}
        className="md:hidden fixed bottom-20 left-4 w-14 h-14 bg-primary hover:bg-primary-hover rounded-full flex items-center justify-center shadow-xl z-[10000]"
      >
        <Plus className="w-6 h-6 text-white" />
      </button>

      {/* Problem Create Form Modal */}
      <ProblemCreateForm
        isOpen={isCreateFormOpen}
        onClose={() => setIsCreateFormOpen(false)}
        onSuccess={(problemId) => {
          navigate(`/problems/${problemId}`)
        }}
      />
    </>
  )
}
