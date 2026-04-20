import { Shield, ShieldCheck, Crown, Heart } from 'lucide-react'
import { UserRole } from '../api/generated/models/UserRole'

interface RoleBadgeProps {
  role: UserRole
  size?: 'sm' | 'md'
}

const roleConfig = {
  [UserRole.ADMIN]: {
    label: 'Админ',
    icon: Crown,
    className: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  },
  [UserRole.MODERATOR]: {
    label: 'Модератор',
    icon: ShieldCheck,
    className: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  },
  [UserRole.OFFICIAL]: {
    label: 'Официальное лицо',
    icon: Shield,
    className: 'bg-green-500/20 text-green-400 border-green-500/30',
  },
  [UserRole.VOLUNTEER]: {
    label: 'Волонтёр',
    icon: Heart,
    className: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  },
  [UserRole.USER]: {
    label: '',
    icon: null,
    className: '',
  },
}

export function RoleBadge({ role, size = 'sm' }: RoleBadgeProps) {
  const config = roleConfig[role]

  // Don't show badge for regular users
  if (role === UserRole.USER || !config.label) {
    return null
  }

  const Icon = config.icon
  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'
  const textSize = size === 'sm' ? 'text-xs' : 'text-sm'
  const padding = size === 'sm' ? 'px-2 py-0.5' : 'px-3 py-1'

  return (
    <span
      className={`inline-flex items-center gap-1 ${padding} rounded-full border font-medium ${textSize} ${config.className}`}
    >
      {Icon && <Icon className={iconSize} />}
      {config.label}
    </span>
  )
}
