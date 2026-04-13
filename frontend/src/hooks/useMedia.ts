import { useMutation, useQueryClient } from '@tanstack/react-query'
import { MediaService } from '../api/generated/services/MediaService'
import { useToast } from './useToast'
import type { MediaCategory } from '../api/generated/models/MediaCategory'

interface UploadMediaParams {
  problemEntityId: number
  file: File
  caption?: string
  category?: MediaCategory
}

export const useUploadMedia = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async ({ problemEntityId, file, caption, category }: UploadMediaParams) => {
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
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['problem', variables.problemEntityId] })
      queryClient.invalidateQueries({ queryKey: ['media', variables.problemEntityId] })
      toast.success('Медиа загружено')
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось загрузить медиа'
      toast.error('Ошибка', message)
    },
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
