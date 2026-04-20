import { useState, } from 'react'
import { Bell, Check, Trash2, Loader2, Filter } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  useNotifications,
  useMarkAsRead,
  useMarkAllAsRead,
  useDeleteNotification,
  useDeleteAllNotifications,
} from '../hooks/useNotifications'
import { UserName } from '../components/UserName'
import { NotificationType } from '../api/generated/models/NotificationType'
import type { NotificationPublic } from '../api/generated/models/NotificationPublic'

const notificationTypeLabels: Record<NotificationType, string> = {
  [NotificationType.PROBLEM_STATUS_CHANGED]: 'Статус проблемы',
  [NotificationType.PROBLEM_ASSIGNED]: 'Назначение',
  [NotificationType.PROBLEM_COMMENTED]: 'Комментарий',
  [NotificationType.COMMENT_REPLIED]: 'Ответ',
  [NotificationType.PROBLEM_UPVOTED]: 'Голос',
  [NotificationType.PROBLEM_VERIFIED]: 'Верификация',
  [NotificationType.PROBLEM_REJECTED]: 'Отклонение',
  [NotificationType.COMMENT_HIDDEN]: 'Скрытие',
  [NotificationType.USER_MENTIONED]: 'Упоминание',
  [NotificationType.PROBLEM_SUBSCRIBED]: 'Подписка',
}

export default function NotificationsPage() {
  const navigate = useNavigate()
  const [filterType, setFilterType] = useState<NotificationType | null>(null)
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)

  const { data: notifications, isLoading } = useNotifications(
    0,
    50,
    showUnreadOnly,
    filterType
  )
  const markAsReadMutation = useMarkAsRead()
  const markAllAsReadMutation = useMarkAllAsRead()
  const deleteNotificationMutation = useDeleteNotification()
  const deleteAllMutation = useDeleteAllNotifications()

  const handleMarkAsRead = (notificationId: number) => {
    markAsReadMutation.mutate([notificationId])
  }

  const handleMarkAllAsRead = () => {
    if (confirm('Отметить все уведомления как прочитанные?')) {
      markAllAsReadMutation.mutate()
    }
  }

  const handleDelete = (notificationId: number) => {
    deleteNotificationMutation.mutate(notificationId)
  }

  const handleDeleteAll = () => {
    if (confirm('Удалить все уведомления? Это действие нельзя отменить.')) {
      deleteAllMutation.mutate()
    }
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
  }

  return (
    <div className="min-h-screen bg-dark-bg pt-24 pb-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-text-primary mb-2">Уведомления</h1>
          <p className="text-text-secondary">
            Все ваши уведомления о проблемах, комментариях и активности
          </p>
        </div>

        {/* Filters and Actions */}
        <div className="bg-dark-card rounded-lg p-4 mb-6 border border-dark-border">
          <div className="flex flex-wrap items-center gap-3">
            {/* Unread filter */}
            <button
              onClick={() => setShowUnreadOnly(!showUnreadOnly)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                showUnreadOnly
                  ? 'bg-primary text-white'
                  : 'bg-dark-hover text-text-secondary hover:text-text-primary'
              }`}
            >
              <Filter className="w-4 h-4" />
              Только непрочитанные
            </button>

            {/* Type filter */}
            <select
              value={filterType || ''}
              onChange={(e) => setFilterType(e.target.value as NotificationType || null)}
              className="px-3 py-1.5 rounded-lg text-sm bg-dark-hover text-text-primary border border-dark-border"
            >
              <option value="">Все типы</option>
              {Object.entries(notificationTypeLabels).map(([type, label]) => (
                <option key={type} value={type}>
                  {label}
                </option>
              ))}
            </select>

            <div className="ml-auto flex gap-2">
              <button
                onClick={handleMarkAllAsRead}
                disabled={markAllAsReadMutation.isPending}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm bg-dark-hover text-text-primary hover:bg-dark-border transition-colors disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                Прочитать все
              </button>
              <button
                onClick={handleDeleteAll}
                disabled={deleteAllMutation.isPending}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm bg-danger/10 text-danger hover:bg-danger/20 transition-colors disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" />
                Удалить все
              </button>
            </div>
          </div>
        </div>

        {/* Notifications List */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : notifications && notifications.notifications.length > 0 ? (
          <div className="space-y-2">
            {notifications.notifications.map((notification) => (
              <div
                key={notification.entity_id}
                className={`bg-dark-card rounded-lg border border-dark-border hover:border-primary/30 transition-colors ${
                  !notification.is_read ? 'bg-primary/5' : ''
                }`}
              >
                <div className="p-4">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                        <Bell className="w-5 h-5 text-primary" />
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* <Link
                        to={getNotificationLink(notification)}
                        onClick={() => handleNotificationClick(notification)}
                        className="block group"
                      > */}
                      <div
                        className="block group cursor-pointer"
                        onClick={() => {
                          handleNotificationClick(notification)
                          navigate(getNotificationLink(notification))
                        }}
                      >
                        <h3 className="text-sm font-semibold text-text-primary mb-1 group-hover:text-primary transition-colors">
                          {notification.title}
                        </h3>
                        <p className="text-sm text-text-secondary mb-2">
                          {notification.message}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-text-muted">
                          {notification.actor_entity_id && (
                            <div className="flex items-center gap-1">
                              <span>От:</span>
                              <UserName userId={notification.actor_entity_id} />
                            </div>
                          )}
                          <span>
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                              locale: ru,
                            })}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-dark-hover text-text-secondary">
                            {notificationTypeLabels[notification.notification_type]}
                          </span>
                        </div>
                      {/* </Link> */}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      {!notification.is_read && (
                        <button
                          onClick={() => handleMarkAsRead(notification.entity_id)}
                          disabled={markAsReadMutation.isPending}
                          className="p-2 rounded-lg hover:bg-dark-hover transition-colors disabled:opacity-50"
                          title="Отметить прочитанным"
                        >
                          <Check className="w-4 h-4 text-primary" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(notification.entity_id)}
                        disabled={deleteNotificationMutation.isPending}
                        className="p-2 rounded-lg hover:bg-dark-hover transition-colors disabled:opacity-50"
                        title="Удалить"
                      >
                        <Trash2 className="w-4 h-4 text-danger" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-dark-card rounded-lg border border-dark-border p-12 text-center">
            <Bell className="w-16 h-16 text-text-muted mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              Нет уведомлений
            </h3>
            <p className="text-text-secondary">
              {showUnreadOnly
                ? 'У вас нет непрочитанных уведомлений'
                : 'Здесь будут отображаться ваши уведомления'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
