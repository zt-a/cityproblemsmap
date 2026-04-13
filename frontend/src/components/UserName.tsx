import { Link } from 'react-router-dom'
import { useUser } from '../hooks/useUser'

interface UserNameProps {
  userId: number
  className?: string
  showAvatar?: boolean
}

export function UserName({ userId, className = '', showAvatar = false }: UserNameProps) {
  const { data: user, isLoading } = useUser(userId)

  if (isLoading) {
    return <span className="text-text-muted">Загрузка...</span>
  }

  return (
    <Link
      to={`/users/${userId}`}
      className={`inline-flex items-center gap-2 hover:text-primary transition-colors ${className}`}
      onClick={(e) => e.stopPropagation()}
    >
      {showAvatar && (
        <div className="w-6 h-6 rounded-full bg-dark-hover flex items-center justify-center text-xs font-bold text-primary border border-primary/20">
          {user?.username?.charAt(0).toUpperCase() || 'U'}
        </div>
      )}
      <span>{user?.username || `ID: ${userId}`}</span>
    </Link>
  )
}
