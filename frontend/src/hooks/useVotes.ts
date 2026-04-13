import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { VotesService } from '../api/generated/services/VotesService'
import { useToast } from './useToast'

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
    mutationFn: async (params: { isUpvote: boolean; isTrue?: boolean | null }) => {
      const response = await VotesService.voteApiV1ProblemsProblemEntityIdVotesPost(
        problemEntityId,
        {
          is_upvote: params.isUpvote,
          is_true: params.isTrue,
        }
      )
      return response
    },
    onSuccess: () => {
      // Invalidate vote stats and problem data
      queryClient.invalidateQueries({ queryKey: ['votes', 'stats', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      toast.success('Голос учтён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось проголосовать'
      toast.error('Ошибка', message)
    },
  })
}

export const useDeleteVote = (voteEntityId: number, problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async () => {
      await VotesService.deleteVoteApiV1VotesEntityIdDelete(voteEntityId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['votes', 'stats', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      toast.success('Голос отменён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось отменить голос'
      toast.error('Ошибка', message)
    },
  })
}
