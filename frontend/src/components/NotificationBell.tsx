import { useState, useRef, useEffect } from 'react'
import { Bell, Check, Trash2, Loader2, X } from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  useNotifications,
  useNotificationStats,
  useMarkAsRead,
  useDeleteNotification,
} from '../hooks/useNotifications'
import { UserName } from './UserName'
import type { NotificationPublic } from '../api/generated/models/NotificationPublic'

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const { data: stats } = useNotificationStats()
  const { data: notifications, isLoading } = useNotifications(0, 10, false)
  const markAsReadMutation = useMarkAsRead()
  const deleteNotificationMutation = useDeleteNotification()

  const unreadCount = stats?.unread || 0

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleMarkAsRead = (notificationId: number) => {
    markAsReadMutation.mutate([notificationId])
  }

  const handleDelete = (notificationId: number) => {
    deleteNotificationMutation.mutate(notificationId)
  }

  const getNotificationLink = (notification: NotificationPublic) => {
    if (notification.problem_entity_id) {
      return `/problems/${notification.problem_entity_id}`
    }
    return '#'
  }

  const handleNotificationClick = (notification: NotificationPublic) => {
    if (!notification.is_read) {
      handleMarkAsRead(notification.entity_id)
    }
    setIsOpen(false)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-dark-hover transition-colors"
      >
        <Bell className="w-5 h-5 text-text-secondary" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-danger text-white text-xs font-bold rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-dark-card border border-dark-border rounded-lg shadow-xl z-50 max-h-[600px] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-dark-border">
            <h3 className="font-semibold text-text-primary">Уведомления</h3>
            <Link
              to="/notifications"
              onClick={() => setIsOpen(false)}
              className="text-sm text-primary hover:underline"
            >
              Все
            </Link>
          </div>

          {/* Notifications List */}
          <div className="overflow-y-auto flex-1">
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 text-primary animate-spin" />
              </div>
            ) : notifications && notifications.notifications.length > 0 ? (
              <div className="divide-y divide-dark-border">
                {notifications.notifications.map((notification) => (
                  <div
                    key={notification.entity_id}
                    className={`p-4 hover:bg-dark-hover transition-colors ${
                      !notification.is_read ? 'bg-primary/5' : ''
                    }`}
                  >
                    <div className="flex gap-3">
                      <div className="flex-1">
                        <Link
                          to={getNotificationLink(notification)}
                          onClick={() => handleNotificationClick(notification)}
                          className="block"
                        >
                          <p className="text-sm font-medium text-text-primary mb-1">
                            {notification.title}
                          </p>
                          <p className="text-xs text-text-secondary mb-2">
                            {notification.message}
                          </p>
                          {notification.actor_entity_id && (
                            <div className="text-xs text-text-muted mb-1">
                              <UserName userId={notification.actor_entity_id} asText />
                            </div>
                          )}
                          <p className="text-xs text-text-muted">
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                              locale: ru,
                            })}
                          </p>
                        </Link>
                      </div>

                      <div className="flex flex-col gap-1">
                        {!notification.is_read && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleMarkAsRead(notification.entity_id)
                            }}
                            className="p-1 rounded hover:bg-dark-bg transition-colors"
                            title="Отметить прочитанным"
                          >
                            <Check className="w-4 h-4 text-primary" />
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(notification.entity_id)
                          }}
                          className="p-1 rounded hover:bg-dark-bg transition-colors"
                          title="Удалить"
                        >
                          <Trash2 className="w-4 h-4 text-danger" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-text-muted text-sm">
                Нет уведомлений
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
