import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { VotesService } from '../api/generated/services/VotesService'
import { useToast } from './useToast'

export const useMyVote = (problemEntityId: number | undefined) => {
  return useQuery({
    queryKey: ['myVote', problemEntityId],
    queryFn: async () => {
      if (!problemEntityId) throw new Error('Problem ID is required')
      try {
        const response = await VotesService.getMyVoteApiV1ProblemsProblemEntityIdVotesMyGet(problemEntityId)
        return response
      } catch (error: any) {
        // If 404, user hasn't voted yet
        if (error?.status === 404) {
          return null
        }
        throw error
      }
    },
    enabled: !!problemEntityId,
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

export const useVoteStats = (problemEntityId: number | undefined) => {
  return useQuery({
    queryKey: ['votes', 'stats', problemEntityId],
    queryFn: async () => {
      if (!problemEntityId) throw new Error('Problem ID is required')
      const response = await VotesService.getVoteStatsApiV1ProblemsProblemEntityIdVotesStatsGet(problemEntityId)
      return response
    },
    enabled: !!problemEntityId,
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

export const useVote = (problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (params: { isTrue?: boolean | null; urgency?: number | null; impact?: number | null; inconvenience?: number | null }) => {
      const response = await VotesService.castVoteApiV1ProblemsProblemEntityIdVotesPost(
        problemEntityId,
        {
          is_true: params.isTrue,
          urgency: params.urgency,
          impact: params.impact,
          inconvenience: params.inconvenience,
        }
      )
      return response
    },
    onSuccess: () => {
      // Invalidate vote stats, problem data, and my vote
      queryClient.invalidateQueries({ queryKey: ['votes', 'stats', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['myVote', problemEntityId] })
      toast.success('Голос учтён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось проголосовать'
      toast.error('Ошибка', message)
    },
  })
}

export const useDeleteVote = (problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async () => {
      await VotesService.deleteMyVoteApiV1ProblemsProblemEntityIdVotesMyDelete(problemEntityId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['votes', 'stats', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['myVote', problemEntityId] })
      toast.success('Голос отменён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось отменить голос'
      toast.error('Ошибка', message)
    },
  })
}
