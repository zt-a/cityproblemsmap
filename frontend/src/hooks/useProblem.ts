import { useQuery } from '@tanstack/react-query'
import { ProblemsService } from '../api/generated/services/ProblemsService'

export const useProblem = (entityId: number | undefined) => {
  return useQuery({
    queryKey: ['problem', entityId],
    queryFn: async () => {
      if (!entityId) throw new Error('Problem ID is required')
      const response = await ProblemsService.getProblemApiV1ProblemsEntityIdGet(entityId)
      return response
    },
    enabled: !!entityId, // Only run query if entityId exists
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useProblemHistory = (entityId: number | undefined) => {
  return useQuery({
    queryKey: ['problem', entityId, 'history'],
    queryFn: async () => {
      if (!entityId) throw new Error('Problem ID is required')
      const response = await ProblemsService.getProblemHistoryApiV1ProblemsEntityIdHistoryGet(entityId)
      return response
    },
    enabled: !!entityId,
    staleTime: 10 * 60 * 1000, // 10 minutes (history changes less frequently)
  })
}
