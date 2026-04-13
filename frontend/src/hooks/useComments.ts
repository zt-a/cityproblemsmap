import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CommentsService } from '../api/generated/services/CommentsService'
import { useToast } from './useToast'
import type { CommentCreate } from '../api/generated/models/CommentCreate'
import type { CommentEdit } from '../api/generated/models/CommentEdit'

export const useComments = (problemEntityId: number | undefined) => {
  return useQuery({
    queryKey: ['comments', problemEntityId],
    queryFn: async () => {
      if (!problemEntityId) throw new Error('Problem ID is required')
      const response = await CommentsService.getCommentsApiV1ProblemsProblemEntityIdCommentsGet(problemEntityId)
      return response
    },
    enabled: !!problemEntityId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

export const useCreateComment = (problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (data: CommentCreate) => {
      const response = await CommentsService.createCommentApiV1ProblemsProblemEntityIdCommentsPost(
        problemEntityId,
        data
      )
      return response
    },
    onSuccess: () => {
      // Invalidate comments list
      queryClient.invalidateQueries({ queryKey: ['comments', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      toast.success('Комментарий добавлен')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось добавить комментарий'
      toast.error('Ошибка', message)
    },
  })
}

export const useUpdateComment = (commentEntityId: number, problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (data: CommentEdit) => {
      const response = await CommentsService.updateCommentApiV1CommentsEntityIdPatch(
        commentEntityId,
        data
      )
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', problemEntityId] })
      toast.success('Комментарий обновлён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось обновить комментарий'
      toast.error('Ошибка', message)
    },
  })
}

export const useDeleteComment = (commentEntityId: number, problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async () => {
      await CommentsService.deleteCommentApiV1CommentsEntityIdDelete(commentEntityId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      toast.success('Комментарий удалён')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось удалить комментарий'
      toast.error('Ошибка', message)
    },
  })
}

export const useFlagComment = (commentEntityId: number, problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (reason: string) => {
      await CommentsService.flagCommentApiV1CommentsEntityIdFlagPost(commentEntityId, { reason })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', problemEntityId] })
      toast.success('Жалоба отправлена')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось отправить жалобу'
      toast.error('Ошибка', message)
    },
  })
}
