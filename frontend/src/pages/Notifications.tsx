import { useState, useEffect } from 'react';
import { Bell, Check, CheckCheck, Trash2, Filter, X } from 'lucide-react';
import { NotificationsService } from '../api/generated/services/NotificationsService';
import { useWebSocketNotifications } from '../hooks/useWebSocketNotifications';
import type { NotificationList } from '../api/generated/models/NotificationList';
import type { NotificationPublic } from '../api/generated/models/NotificationPublic';
import type { NotificationStats } from '../api/generated/models/NotificationStats';

const notificationTypeLabels: Record<string, string> = {
  problem_status_changed: 'Изменение статуса проблемы',
  new_comment: 'Новый комментарий',
  comment_reply: 'Ответ на комментарий',
  problem_resolved: 'Проблема решена',
  problem_verified: 'Проблема проверена',
  new_follower: 'Новый подписчик',
  mention: 'Упоминание',
  achievement_unlocked: 'Новое достижение',
  subscription_update: 'Обновление подписки',
};

const notificationTypeIcons: Record<string, string> = {
  problem_status_changed: '🔄',
  new_comment: '💬',
  comment_reply: '↩️',
  problem_resolved: '✅',
  problem_verified: '✓',
  new_follower: '👤',
  mention: '@',
  achievement_unlocked: '🏆',
  subscription_update: '🔔',
};

export const Notifications = () => {
  const [notifications, setNotifications] = useState<NotificationList | null>(null);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  useEffect(() => {
    loadNotifications();
    loadStats();
  }, [filter, typeFilter]);

  // WebSocket for real-time notifications
  useWebSocketNotifications({
    onMessage: (data) => {
      console.log('New notification received:', data);
      // Reload notifications and stats when new one arrives
      loadNotifications();
      loadStats();
    },
  });

  const loadNotifications = async () => {
    setIsLoading(true);
    try {
      const data = await NotificationsService.getNotificationsApiV1NotificationsGet(
        undefined,
        20,
        filter === 'unread',
        typeFilter as any
      );
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const data = await NotificationsService.getNotificationStatsApiV1NotificationsStatsGet();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleMarkAsRead = async (notificationIds: number[]) => {
    try {
      await NotificationsService.markNotificationsAsReadApiV1NotificationsMarkReadPost({
        notification_ids: notificationIds,
      });
      loadNotifications();
      loadStats();
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await NotificationsService.markAllNotificationsAsReadApiV1NotificationsMarkAllReadPost();
      loadNotifications();
      loadStats();
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const handleDelete = async (notificationId: number) => {
    try {
      await NotificationsService.deleteNotificationApiV1NotificationsNotificationIdDelete(notificationId);
      loadNotifications();
      loadStats();
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const handleDeleteAll = async () => {
    if (!confirm('Вы уверены, что хотите удалить все уведомления?')) return;

    try {
      await NotificationsService.deleteAllNotificationsApiV1NotificationsDelete();
      loadNotifications();
      loadStats();
    } catch (error) {
      console.error('Failed to delete all notifications:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} д назад`;

    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#3B82F6]/10 rounded-lg">
              <Bell className="w-6 h-6 text-[#3B82F6]" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-[#E5E7EB]">Уведомления</h1>
              {stats && stats.unread_count > 0 && (
                <p className="text-sm text-[#9CA3AF]">
                  {stats.unread_count} непрочитанных
                </p>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            {stats && stats.unread_count > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
              >
                <CheckCheck className="w-4 h-4" />
                Прочитать все
              </button>
            )}
            {notifications && notifications.total > 0 && (
              <button
                onClick={handleDeleteAll}
                className="flex items-center gap-2 px-4 py-2 bg-[#374151] hover:bg-[#4B5563] text-[#E5E7EB] rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Удалить все
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">Всего</p>
            <p className="text-2xl font-bold text-[#E5E7EB]">{stats.total_count}</p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">Непрочитанные</p>
            <p className="text-2xl font-bold text-[#3B82F6]">{stats.unread_count}</p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">Прочитанные</p>
            <p className="text-2xl font-bold text-[#10B981]">{stats.read_count}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-[#111827] rounded-xl p-4 shadow-xl mb-6">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-[#9CA3AF]" />
            <span className="text-sm text-[#9CA3AF]">Фильтры:</span>
          </div>

          {/* Read/Unread Filter */}
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
              }`}
            >
              Все
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === 'unread'
                  ? 'bg-[#3B82F6] text-white'
                  : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
              }`}
            >
              Непрочитанные
            </button>
          </div>

          {/* Type Filter */}
          {typeFilter && (
            <button
              onClick={() => setTypeFilter(null)}
              className="flex items-center gap-2 px-3 py-2 bg-[#3B82F6]/10 text-[#3B82F6] rounded-lg text-sm"
            >
              {notificationTypeLabels[typeFilter] || typeFilter}
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Notifications List */}
      <div className="bg-[#111827] rounded-xl shadow-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <p className="text-[#9CA3AF]">Загрузка...</p>
          </div>
        ) : notifications && notifications.items && notifications.items.length > 0 ? (
          <div className="divide-y divide-[#374151]">
            {notifications.items.map((notification: NotificationPublic) => (
              <div
                key={notification.id}
                className={`p-4 hover:bg-[#1F2937] transition-colors ${
                  !notification.is_read ? 'bg-[#3B82F6]/5 border-l-4 border-[#3B82F6]' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className="flex-shrink-0 w-10 h-10 bg-[#1F2937] rounded-full flex items-center justify-center text-xl">
                    {notificationTypeIcons[notification.notification_type] || '🔔'}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h3 className="text-sm font-medium text-[#E5E7EB]">
                        {notificationTypeLabels[notification.notification_type] || notification.notification_type}
                      </h3>
                      <span className="text-xs text-[#6B7280] whitespace-nowrap">
                        {formatDate(notification.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-[#9CA3AF] mb-2">{notification.message}</p>

                    {/* Metadata */}
                    {notification.metadata && (
                      <div className="flex gap-2 text-xs text-[#6B7280]">
                        {notification.metadata.problem_entity_id && (
                          <span>Проблема #{notification.metadata.problem_entity_id}</span>
                        )}
                        {notification.metadata.comment_entity_id && (
                          <span>Комментарий #{notification.metadata.comment_entity_id}</span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    {!notification.is_read && (
                      <button
                        onClick={() => handleMarkAsRead([notification.id])}
                        className="p-2 hover:bg-[#374151] rounded-lg transition-colors"
                        title="Отметить как прочитанное"
                      >
                        <Check className="w-4 h-4 text-[#3B82F6]" />
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(notification.id)}
                      className="p-2 hover:bg-[#374151] rounded-lg transition-colors"
                      title="Удалить"
                    >
                      <Trash2 className="w-4 h-4 text-[#EF4444]" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-[#374151] rounded-full flex items-center justify-center mx-auto mb-4">
              <Bell className="w-8 h-8 text-[#6B7280]" />
            </div>
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Нет уведомлений</h3>
            <p className="text-sm text-[#9CA3AF]">
              {filter === 'unread'
                ? 'У вас нет непрочитанных уведомлений'
                : 'У вас пока нет уведомлений'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
