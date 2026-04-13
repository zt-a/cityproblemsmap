import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import { useToast } from './useToast'

interface ActivityItem {
  id: number
  user_id: number
  action_type: string
  target_type: string
  target_id: number
  description: string
  created_at: string
}

interface ActivityFeedResponse {
  activities: ActivityItem[]
  total: number
}

export const useFollowUser = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (userId: number) => {
      const response = await apiClient.post(`/api/v1/social/follow/${userId}`)
      return response.data
    },
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', userId] })
      queryClient.invalidateQueries({ queryKey: ['followStatus', userId] })
      toast.success('Вы подписались на пользователя')
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Не удалось подписаться'
      toast.error('Ошибка', message)
    },
  })
}

export const useUnfollowUser = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (userId: number) => {
      const response = await apiClient.delete(`/api/v1/social/follow/${userId}`)
      return response.data
    },
    onSuccess: (_, userId) => {
      queryClient.invalidateQueries({ queryKey: ['userProfile', userId] })
      queryClient.invalidateQueries({ queryKey: ['followStatus', userId] })
      toast.success('Вы отписались от пользователя')
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Не удалось отписаться'
      toast.error('Ошибка', message)
    },
  })
}

export const useFollowStatus = (userId: number | undefined) => {
  return useQuery({
    queryKey: ['followStatus', userId],
    queryFn: async () => {
      if (!userId) throw new Error('User ID is required')
      const response = await apiClient.get(`/api/v1/social/follow/${userId}/status`)
      return response.data
    },
    enabled: !!userId,
    staleTime: 30 * 1000, // 30 seconds
  })
}

export const useActivityFeed = (limit = 20, offset = 0) => {
  return useQuery({
    queryKey: ['activityFeed', limit, offset],
    queryFn: async () => {
      const response = await apiClient.get<ActivityFeedResponse>('/api/v1/social/feed', {
        params: { limit, offset }
      })
      return response.data
    },
    staleTime: 60 * 1000, // 1 minute
  })
}
