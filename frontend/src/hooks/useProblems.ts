import { useQuery } from '@tanstack/react-query'
import { ProblemsService } from '../api/generated/services/ProblemsService'
import type { ProblemStatus } from '../api/generated/models/ProblemStatus'

export interface ProblemFilters {
  city?: string
  problemType?: string
  status?: ProblemStatus
  offset?: number
  limit?: number
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

