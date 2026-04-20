import { useState, useEffect } from 'react'
import { Search, MapPin, Menu, X, ChevronDown, LogIn } from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { NotificationBell } from '../NotificationBell'

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

  // Reset header state on route change
  useEffect(() => {
    setIsMobileMenuOpen(false)
    setIsUserMenuOpen(false)
  }, [location.pathname])

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
              <NotificationBell />

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