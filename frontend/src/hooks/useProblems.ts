import { useInfiniteQuery, useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ProblemsService } from '../api/generated/services/ProblemsService'
import type { ProblemStatus } from '../api/generated/models/ProblemStatus'
import { apiClient } from '../api/client'
import { useEffect, useState } from 'react'

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
    staleTime: 2 * 60 * 1000,
  })
}

export const useProblem = (entityId: number | null) => {
  return useQuery({
    queryKey: ['problem', entityId],
    queryFn: async () => {
      if (!entityId) return null
      const response = await ProblemsService.getProblemApiV1ProblemsEntityIdGet(entityId)
      return response
    },
    enabled: !!entityId,
    staleTime: 2 * 60 * 1000,
  })
}

export const useInfiniteProblems = (filters?: Omit<ProblemFilters, 'offset' | 'limit'>) => {
  const filtersWithoutPagination = {
    ...filters,
    limit: 20,
  }

  return useInfiniteQuery({
    queryKey: ['problems', filtersWithoutPagination],
    queryFn: async ({ pageParam = 0 }) => {
      const response = await ProblemsService.listProblemsApiV1ProblemsGet(
        filters?.city,
        filters?.problemType,
        filters?.status,
        pageParam,
        20
      )
      return response
    },
    getNextPageParam: (lastPage) => {
      const nextOffset = lastPage.offset + lastPage.limit
      return nextOffset < lastPage.total ? nextOffset : undefined
    },
    staleTime: 2 * 60 * 1000,
  })
}

export const useAllProblems = (filters?: Omit<ProblemFilters, 'offset' | 'limit'>) => {
  const [allItems, setAllItems] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const query = useInfiniteProblems(filters)

  useEffect(() => {
    if (!query.data) {
      setIsLoading(query.isLoading)
      return
    }

    const items = query.data.pages.flatMap(page => page.items)
    setAllItems(items)
    setTotal(query.data.pages[0]?.total || 0)
    setIsLoading(query.isLoading)
  }, [query.data, query.isLoading])

  return {
    ...query,
    data: {
      items: allItems,
      total,
      limit: 20,
      offset: 0,
    } as any,
    isLoading,
    hasNextPage: query.hasNextPage,
    fetchNextPage: query.fetchNextPage,
  }
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
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problems'] })
      queryClient.invalidateQueries({ queryKey: ['problemHistory', problemEntityId] })
    },
  })
}