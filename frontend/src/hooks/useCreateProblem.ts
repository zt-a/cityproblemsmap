import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ProblemsService } from '../api/generated/services/ProblemsService'
import { useToast } from './useToast'
import type { ProblemCreate } from '../api/generated/models/ProblemCreate'

export const useCreateProblem = () => {
  const queryClient = useQueryClient()
  const toast = useToast()

  return useMutation({
    mutationFn: async (data: ProblemCreate) => {
      const response = await ProblemsService.createProblemApiV1ProblemsPost(data)
      return response
    },
    onSuccess: (newProblem) => {
      // Invalidate problems list to refetch with new problem
      queryClient.invalidateQueries({ queryKey: ['problems'] })
      toast.success('Проблема создана', 'Ваша проблема успешно опубликована')
      return newProblem
    },
    onError: (error: any) => {
      const message = error?.body?.detail || 'Не удалось создать проблему'
      toast.error('Ошибка', message)
    },
  })
}
