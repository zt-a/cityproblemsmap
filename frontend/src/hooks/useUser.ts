import { useQuery } from '@tanstack/react-query'
import { UsersService } from '../api/generated/services/UsersService'
import { apiClient } from '../api/client'

export const useUser = (entityId: number | undefined) => {
  return useQuery({
    queryKey: ['user', entityId],
    queryFn: async () => {
      if (!entityId) throw new Error('User ID is required')
      const response = await UsersService.getUserApiV1UsersEntityIdGet(entityId)
      return response
    },
    enabled: !!entityId,
    staleTime: 10 * 60 * 1000, // 10 minutes - user data doesn't change often
  })
}

export const useUserProfile = (userId: number | undefined) => {
  return useQuery({
    queryKey: ['userProfile', userId],
    queryFn: async () => {
      if (!userId) throw new Error('User ID is required')
      const response = await apiClient.get(`/api/v1/social/profile/${userId}`)
      return response.data
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
