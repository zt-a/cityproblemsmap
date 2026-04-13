import { useState } from 'react'
import { X, MapPin, Loader2, Save, Trash2, Upload } from 'lucide-react'
import { useUpdateProblem } from '../../hooks/useProblems'
import { useProblemMedia, useUploadMedia, useDeleteMedia } from '../../hooks/useMedia'
import { ProblemType } from '../../api/generated/models/ProblemType'
import type { ProblemPublic } from '../../api/generated/models/ProblemPublic'
import LocationPicker from './LocationPicker'

interface ProblemEditFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
  problem: ProblemPublic
}

const problemTypeLabels: Record<ProblemType, string> = {
  [ProblemType.POTHOLE]: 'Яма на дороге',
  [ProblemType.GARBAGE]: 'Мусор',
  [ProblemType.ROAD_WORK]: 'Дорожные работы',
  [ProblemType.POLLUTION]: 'Загрязнение',
  [ProblemType.TRAFFIC_LIGHT]: 'Светофор',
  [ProblemType.FLOODING]: 'Затопление',
  [ProblemType.LIGHTING]: 'Освещение',
  [ProblemType.CONSTRUCTION]: 'Строительство',
  [ProblemType.ROADS]: 'Дороги',
  [ProblemType.INFRASTRUCTURE]: 'Инфраструктура',
  [ProblemType.OTHER]: 'Другое',
}

export default function ProblemEditForm({
  isOpen,
  onClose,
  onSuccess,
  problem,
}: ProblemEditFormProps) {
  const updateProblem = useUpdateProblem(problem.entity_id)
  const { data: media, isLoading: mediaLoading } = useProblemMedia(problem.entity_id)
  const uploadMediaMutation = useUploadMedia(problem.entity_id)
  const deleteMediaMutation = useDeleteMedia(problem.entity_id)
  const [isLocationPickerOpen, setIsLocationPickerOpen] = useState(false)

  const [formData, setFormData] = useState({
    title: problem.title,
    description: problem.description || '',
    address: problem.address || '',
    latitude: problem.latitude || 0,
    longitude: problem.longitude || 0,
    problem_type: problem.problem_type,
    tags: problem.tags || [],
  })

  const handleLocationSelect = (lat: number, lng: number, address?: string) => {
    setFormData((prev) => ({
      ...prev,
      latitude: lat,
      longitude: lng,
      address: address || prev.address,
    }))
  }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    for (const file of Array.from(files)) {
      try {
        await uploadMediaMutation.mutateAsync({ file })
      } catch (error) {
        console.error('Failed to upload media:', error)
      }
    }

    // Reset input
    e.target.value = ''
  }

  const handleDeleteMedia = async (mediaEntityId: number) => {
    if (!confirm('Удалить это медиа?')) return

    try {
      await deleteMediaMutation.mutateAsync(mediaEntityId)
    } catch (error) {
      console.error('Failed to delete media:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      alert('Введите название проблемы')
      return
    }

    try {
      await updateProblem.mutateAsync(formData)
      onSuccess?.()
      onClose()
    } catch (error: unknown) {
      console.error('Failed to update problem:', error)
      const err = error as { response?: { data?: { detail?: string } } }
      alert(err.response?.data?.detail || 'Не удалось обновить проблему')
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-[10002] flex items-center justify-center p-4">
        <div className="bg-dark-card rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-dark-card border-b border-border p-4 flex items-center justify-between z-10">
            <h2 className="text-xl font-semibold text-text-primary">Редактировать проблему</h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-dark-hover"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Название проблемы *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Например: Яма на дороге"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Описание
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                rows={4}
                placeholder="Подробное описание проблемы..."
              />
            </div>

            {/* Problem Type */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Тип проблемы *
              </label>
              <select
                value={formData.problem_type}
                onChange={(e) => setFormData({ ...formData, problem_type: e.target.value as ProblemType })}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                required
              >
                {Object.entries(problemTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Media Management */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Медиа
              </label>

              {/* Existing Media */}
              {mediaLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 text-primary animate-spin" />
                </div>
              ) : media && media.length > 0 ? (
                <div className="grid grid-cols-3 gap-2 mb-3">
                  {media.map((item) => (
                    <div key={item.entity_id} className="relative group aspect-square rounded-lg overflow-hidden bg-dark-hover">
                      {item.media_type === 'photo' ? (
                        <img
                          src={item.thumbnail_url || item.url}
                          alt=""
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <video
                          src={item.url}
                          className="w-full h-full object-cover"
                        />
                      )}
                      <button
                        type="button"
                        onClick={() => handleDeleteMedia(item.entity_id)}
                        disabled={deleteMediaMutation.isPending}
                        className="absolute top-2 right-2 w-8 h-8 bg-danger/90 hover:bg-danger rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50"
                      >
                        <Trash2 className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-text-muted mb-3">Нет загруженных медиа</p>
              )}

              {/* Upload Button */}
              <label className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-secondary hover:bg-dark-card flex items-center justify-center gap-2 cursor-pointer">
                <input
                  type="file"
                  accept="image/*,video/*"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={uploadMediaMutation.isPending}
                />
                {uploadMediaMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Загрузка...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Добавить фото/видео
                  </>
                )}
              </label>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Местоположение *
              </label>
              <button
                type="button"
                onClick={() => setIsLocationPickerOpen(true)}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-secondary hover:bg-dark-card flex items-center gap-2"
              >
                <MapPin className="w-4 h-4" />
                <span className="flex-1 text-left">
                  {formData.address || `${formData.latitude.toFixed(6)}, ${formData.longitude.toFixed(6)}`}
                </span>
              </button>
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Адрес
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Улица, дом"
              />
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Теги (через запятую)
              </label>
              <input
                type="text"
                value={formData.tags.join(', ')}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean) })}
                className="w-full px-4 py-2 bg-dark-hover border border-border rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="яма, дорога, срочно"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-dark-hover text-text-primary rounded-lg hover:bg-dark-card"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={updateProblem.isPending}
                className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {updateProblem.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Сохранение...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Сохранить
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Location Picker Modal */}
      <LocationPicker
        isOpen={isLocationPickerOpen}
        onClose={() => setIsLocationPickerOpen(false)}
        onSelect={handleLocationSelect}
        initialPosition={{
          lat: formData.latitude,
          lng: formData.longitude,
        }}
      />
    </>
  )
}
