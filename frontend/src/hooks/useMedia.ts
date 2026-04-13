import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { MediaService } from '../api/generated/services/MediaService'
import { useToast } from './useToast'
import type { MediaCategory } from '../api/generated/models/MediaCategory'

export const useProblemMedia = (problemEntityId: number | undefined) => {
  return useQuery({
    queryKey: ['media', problemEntityId],
    queryFn: async () => {
      if (!problemEntityId) throw new Error('Problem ID is required')
      const response = await MediaService.getProblemMediaApiV1ProblemsProblemEntityIdMediaGet(
        problemEntityId
      )
      return response
    },
    enabled: !!problemEntityId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useGetProblemMedia = (problemEntityId: number) => {
  const queryClient = useQueryClient()

  return {
    getMedia: async () => {
      try {
        const response = await MediaService.getProblemMediaApiV1ProblemsProblemEntityIdMediaGet(
          problemEntityId
        )
        return response
      } catch (error) {
        console.error('Failed to get media:', error)
        return []
      }
    },
  }
}

export const useRemoveMedia = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async ({
      problemEntityId,
      mediaEntityId,
    }: {
      problemEntityId: number
      mediaEntityId: number
    }) => {
      const response = await MediaService.removeMediaApiV1ProblemsProblemEntityIdMediaMediaEntityIdDelete(
        problemEntityId,
        mediaEntityId
      )
      return response
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['problem', variables.problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['media', variables.problemEntityId] })
      toast.success('Медиа удалено')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось удалить медиа'
      toast.error('Ошибка', message)
    },
  })
}

export const useDeleteMedia = (problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (mediaEntityId: number) => {
      const response = await MediaService.removeMediaApiV1ProblemsProblemEntityIdMediaMediaEntityIdDelete(
        problemEntityId,
        mediaEntityId
      )
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['media', problemEntityId] })
      toast.success('Медиа удалено')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось удалить медиа'
      toast.error('Ошибка', message)
    },
  })
}

export const useUploadMedia = (problemEntityId: number) => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async ({ file, caption, category }: { file: File; caption?: string; category?: MediaCategory }) => {
      const formData = {
        file,
        caption: caption || null,
        category: category || 'problem' as MediaCategory,
      }

      const response = await MediaService.uploadMediaApiV1ProblemsProblemEntityIdMediaPost(
        problemEntityId,
        formData
      )
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['problem', problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['media', problemEntityId] })
      toast.success('Медиа загружено')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось загрузить медиа'
      toast.error('Ошибка', message)
    },
  })
}
