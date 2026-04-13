import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ProblemsService } from '../api/generated/services/ProblemsService'
import type { ProblemStatus } from '../api/generated/models/ProblemStatus'
import { apiClient } from '../api/client'

export interface ProblemFilters {
  city?: string
  problemType?: string
  status?: ProblemStatus
  offset?: number
  limit?: number
}

export interface ProblemUpdateData {
  title?: string
  description?: string
  address?: string
  latitude?: number
  longitude?: number
  problem_type?: string
  tags?: string[]
}

export const useProblems = (filters?: ProblemFilters) => {
  return useQuery({
    queryKey: ['problems', filters],
    queryFn: async () => {
      const response = await ProblemsService.listProblemsApiV1ProblemsGet(
        filters?.city,
        filters?.problemType,
        filters?.status,
        filters?.offset,
        filters?.limit || 20
      )
      return response
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useUpdateProblem = (problemEntityId: number) => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: ProblemUpdateData) => {
      const response = await apiClient.patch(
        `/api/v1/problems/${problemEntityId}`,
        data
      )
      return response.data
    },
    onSuccess: () => {
      // Invalidate problem detail and list queries
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problems'] })
      queryClient.invalidateQueries({ queryKey: ['problemHistory', problemEntityId] })
    },
  })
}

