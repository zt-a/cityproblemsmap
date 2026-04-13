import { useState, useEffect } from 'react'
import { Search, Bell, MapPin, Menu, X, ChevronDown, LogIn, ExternalLink } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { useWebSocketNotifications } from '../../hooks/useWebSocketNotifications'
import { NotificationsService } from '../../api/generated/services/NotificationsService'
import type { NotificationPublic } from '../../api/generated/models/NotificationPublic'
import type { NotificationStats } from '../../api/generated/models/NotificationStats'

const navItems = [
  { label: 'Главная', path: '/' },
  { label: 'Карта', path: '/map' },
  { label: 'О проекте', path: '/about' },
  { label: 'Как это работает', path: '/how-it-works' },
  { label: 'Контакты', path: '/contacts' },
]

export default function Header() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const [notifications, setNotifications] = useState<NotificationPublic[]>([])
  const [stats, setStats] = useState<NotificationStats | null>(null)

  // Reset header state on route change
  useEffect(() => {
    setIsMobileMenuOpen(false)
    setIsUserMenuOpen(false)
    setIsNotificationsOpen(false)
  }, [location.pathname])

  // Load notifications when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications()
    }
  }, [isAuthenticated])

  // WebSocket for real-time notifications
  useWebSocketNotifications({
    onMessage: (data) => {
      console.log('New notification received:', data)
      // Reload notifications when new one arrives
      loadNotifications()

      // Show browser notification if supported
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('CityProblemMap', {
          body: data.message,
          icon: '/favicon.ico',
        })
      }
    },
    onConnect: () => {
      console.log('WebSocket connected')
    },
    onDisconnect: () => {
      console.log('WebSocket disconnected')
    },
  })

  const loadNotifications = async () => {
    try {
      const [notifData, statsData] = await Promise.all([
        NotificationsService.getNotificationsApiV1NotificationsGet(undefined, 5, true),
        NotificationsService.getNotificationStatsApiV1NotificationsStatsGet(),
      ])
      setNotifications(notifData.items || [])
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load notifications:', error)
    }
  }

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await NotificationsService.markNotificationsAsReadApiV1NotificationsMarkReadPost({
        notification_ids: [notificationId],
      })
      loadNotifications()
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)

    if (diffMins < 1) return 'только что'
    if (diffMins < 60) return `${diffMins} мин`
    if (diffHours < 24) return `${diffHours} ч`
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  }

  const handleLogout = async () => {
    await logout()
    setIsUserMenuOpen(false)
    navigate('/login')
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-[10000] h-20 glass border-b transition-transform duration-300" style={{ borderWidth: '1px' }}>
      <div className="h-full px-4 md:px-6 flex items-center justify-between">
        {/* Left: Logo + Mobile Menu Button */}
        <div className="flex items-center gap-3">
          {/* Mobile menu button */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="md:hidden w-9 h-9 flex items-center justify-center rounded-lg hover:bg-dark-hover"
          >
            {isMobileMenuOpen ? (
              <X className="w-5 h-5 text-text-primary" />
            ) : (
              <Menu className="w-5 h-5 text-text-primary" />
            )}
          </button>

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-xl flex items-center justify-center">
              <MapPin className="w-5 h-5 text-white" />
            </div>
            <span className="text-text-primary font-semibold text-lg hidden sm:block">CityMap</span>
          </Link>
        </div>

        {/* Center: Navigation - Desktop only */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  px-4 py-2 rounded-lg text-sm font-normal
                  ${
                    isActive
                      ? 'bg-dark-hover text-text-primary'
                      : 'text-text-secondary hover:text-text-primary hover:bg-dark-hover/50'
                  }
                `}
              >
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* Search - Hidden on small mobile */}
          <button
            className="hidden sm:flex w-9 h-9 items-center justify-center rounded-lg hover:bg-dark-hover"
            aria-label="Поиск"
          >
            <Search className="w-5 h-5 text-text-secondary hover:text-text-primary" />
          </button>

          {isAuthenticated ? (
            <>
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                  className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-dark-hover relative"
                  aria-label="Уведомления"
                >
                  <Bell className="w-5 h-5 text-text-secondary hover:text-text-primary" />
                  {stats && stats.unread_count > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full"></span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {isNotificationsOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-[9998]"
                      onClick={() => setIsNotificationsOpen(false)}
                    />
                    <div className="absolute right-0 top-full mt-2 w-96 glass border border-border rounded-xl shadow-xl z-[9999] overflow-hidden">
                      {/* Header */}
                      <div className="p-4 border-b border-border flex items-center justify-between">
                        <div>
                          <h3 className="text-sm font-semibold text-text-primary">Уведомления</h3>
                          {stats && stats.unread_count > 0 && (
                            <p className="text-xs text-text-secondary">{stats.unread_count} непрочитанных</p>
                          )}
                        </div>
                        <Link
                          to="/notifications"
                          className="text-xs text-primary hover:text-primary-hover flex items-center gap-1"
                          onClick={() => setIsNotificationsOpen(false)}
                        >
                          Все
                          <ExternalLink className="w-3 h-3" />
                        </Link>
                      </div>

                      {/* Notifications List */}
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length > 0 ? (
                          <div className="divide-y divide-border">
                            {notifications.map((notification) => (
                              <div
                                key={notification.id}
                                className="p-3 hover:bg-dark-hover transition-colors cursor-pointer"
                                onClick={() => {
                                  handleMarkAsRead(notification.id)
                                  setIsNotificationsOpen(false)
                                  // Navigate to related content if available
                                  if (notification.metadata?.problem_id) {
                                    navigate(`/problems/${notification.metadata.problem_id}`)
                                  }
                                }}
                              >
                                <div className="flex gap-3">
                                  <div className="flex-shrink-0 w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                                    <Bell className="w-4 h-4 text-primary" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm text-text-primary line-clamp-2">
                                      {notification.message}
                                    </p>
                                    <p className="text-xs text-text-muted mt-1">
                                      {formatDate(notification.created_at)}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-8 text-center">
                            <Bell className="w-12 h-12 text-text-muted mx-auto mb-2" />
                            <p className="text-sm text-text-secondary">Нет новых уведомлений</p>
                          </div>
                        )}
                      </div>

                      {/* Footer */}
                      {notifications.length > 0 && (
                        <div className="p-3 border-t border-border">
                          <Link
                            to="/notifications"
                            className="block text-center text-sm text-primary hover:text-primary-hover"
                            onClick={() => setIsNotificationsOpen(false)}
                          >
                            Посмотреть все уведомления
                          </Link>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>

              {/* User Avatar with Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center gap-2 hover:bg-dark-hover rounded-lg p-1 pr-2"
                  aria-label="Профиль"
                >
                  <img
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'user'}`}
                    alt="User Avatar"
                    className="w-8 h-8 rounded-full"
                  />
                  <ChevronDown className="w-4 h-4 text-text-secondary hidden sm:block" />
                </button>

                {/* Dropdown Menu */}
                {isUserMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-[9998]"
                      onClick={() => setIsUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 top-full mt-2 w-48 glass border border-border rounded-xl shadow-xl z-[9999] overflow-hidden">
                      <div className="p-3 border-b border-border">
                        <p className="text-sm font-semibold text-text-primary">{user?.username}</p>
                        <p className="text-xs text-text-secondary">{user?.email}</p>
                      </div>
                      <div className="py-2">
                        <Link
                          to="/profile"
                          className="block px-4 py-2 text-sm text-text-primary hover:bg-dark-hover"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          Профиль
                        </Link>
                        <Link
                          to="/settings"
                          className="block px-4 py-2 text-sm text-text-primary hover:bg-dark-hover"
                          onClick={() => setIsUserMenuOpen(false)}
                        >
                          Настройки
                        </Link>
                        <button
                          className="w-full text-left px-4 py-2 text-sm text-danger hover:bg-dark-hover"
                          onClick={handleLogout}
                        >
                          Выйти
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors"
            >
              <LogIn className="w-4 h-4" />
              <span className="hidden sm:inline">Войти</span>
            </Link>
          )}
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <>
          {/* Top spacer with logo */}
          <div className="md:hidden absolute top-full left-0 right-0 h-16 glass border-b border-border z-[9998] flex items-center px-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-xl flex items-center justify-center">
                <MapPin className="w-5 h-5 text-white" />
              </div>
              <span className="text-text-primary font-semibold text-lg">CityMap</span>
            </div>
          </div>

          {/* Menu content */}
          <div className="md:hidden absolute left-0 right-0 glass border-b border-border z-[9999]" style={{ top: 'calc(100% + 4rem)' }}>
            <nav className="p-4 space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    block px-4 py-3 rounded-lg text-sm font-normal
                    ${
                      isActive
                        ? 'bg-dark-hover text-text-primary'
                        : 'text-text-secondary hover:text-text-primary hover:bg-dark-hover/50'
                    }
                  `}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
        </>
      )}
    </header>
  )
}