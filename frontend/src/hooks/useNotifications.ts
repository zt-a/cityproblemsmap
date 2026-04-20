import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { NotificationsService } from '../api/generated/services/NotificationsService'
import type { NotificationType } from '../api/generated/models/NotificationType'

export const useNotifications = (
  offset?: number,
  limit: number = 20,
  unreadOnly: boolean = false,
  notificationType?: NotificationType | null
) => {
  return useQuery({
    queryKey: ['notifications', offset, limit, unreadOnly, notificationType],
    queryFn: () =>
      NotificationsService.getNotificationsApiV1NotificationsGet(
        offset,
        limit,
        unreadOnly,
        notificationType
      ),
    staleTime: 30 * 1000, // 30 seconds - notifications should be fresh
    refetchInterval: 60 * 1000, // Auto-refetch every minute
  })
}

export const useNotificationStats = () => {
  return useQuery({
    queryKey: ['notificationStats'],
    queryFn: () => NotificationsService.getNotificationStatsApiV1NotificationsStatsGet(),
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000, // Auto-refetch every minute
  })
}

export const useMarkAsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (notificationIds: number[]) =>
      NotificationsService.markNotificationsAsReadApiV1NotificationsMarkReadPost({
        notification_ids: notificationIds,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notificationStats'] })
    },
  })
}

export const useMarkAllAsRead = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () =>
      NotificationsService.markAllNotificationsAsReadApiV1NotificationsMarkAllReadPost(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notificationStats'] })
    },
  })
}

export const useDeleteNotification = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (notificationId: number) =>
      NotificationsService.deleteNotificationApiV1NotificationsNotificationIdDelete(
        notificationId
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notificationStats'] })
    },
  })
}

export const useDeleteAllNotifications = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () =>
      NotificationsService.deleteAllNotificationsApiV1NotificationsDelete(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['notificationStats'] })
    },
  })
}
