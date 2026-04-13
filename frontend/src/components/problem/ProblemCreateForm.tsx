import { useState, useEffect } from 'react'
import { X, MapPin, Loader2, Image } from 'lucide-react'
import { useCreateProblem } from '../../hooks/useCreateProblem'
import { useUploadMedia } from '../../hooks/useMedia'
import { ProblemType } from '../../api/generated/models/ProblemType'
import { ProblemNature } from '../../api/generated/models/ProblemNature'
import type { ProblemCreate } from '../../api/generated/models/ProblemCreate'
import MediaUploader from './MediaUploader'
import LocationPicker from './LocationPicker'

interface MediaFile {
  id: string
  file: File
  preview: string
  type: 'image' | 'video'
}

interface ProblemCreateFormProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: (problemId: number) => void
  initialLocation?: { lat: number; lng: number }
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

const problemNatureLabels: Record<ProblemNature, string> = {
  [ProblemNature.TEMPORARY]: 'Временная',
  [ProblemNature.PERMANENT]: 'Постоянная',
}

export default function ProblemCreateForm({
  isOpen,
  onClose,
  onSuccess,
  initialLocation,
}: ProblemCreateFormProps) {
  const createProblem = useCreateProblem()
  const uploadMedia = useUploadMedia()
  const [isLocationPickerOpen, setIsLocationPickerOpen] = useState(false)
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([])
  const [selectedAddress, setSelectedAddress] = useState<string>('')

  const [formData, setFormData] = useState<ProblemCreate>({
    title: '',
    description: '',
    city: 'Алматы',
    country: 'Казахстан',
    district: '',
    address: '',
    latitude: initialLocation?.lat || 43.238293,
    longitude: initialLocation?.lng || 76.945465,
    problem_type: ProblemType.OTHER,
    nature: ProblemNature.PERMANENT,
    tags: [],
  })

  useEffect(() => {
    if (initialLocation) {
      setFormData((prev) => ({
        ...prev,
        latitude: initialLocation.lat,
        longitude: initialLocation.lng,
      }))
    }
  }, [initialLocation])

  const handleLocationSelect = (lat: number, lng: number, address?: string) => {
    setFormData((prev) => ({
      ...prev,
      latitude: lat,
      longitude: lng,
      address: address || prev.address,
    }))
    if (address) {
      setSelectedAddress(address)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      alert('Введите название проблемы')
      return
    }

    if (!formData.city.trim()) {
      alert('Введите город')
      return
    }

    createProblem.mutate(formData, {
      onSuccess: async (newProblem) => {
        // Upload media files if any
        if (mediaFiles.length > 0) {
          try {
            await Promise.all(
              mediaFiles.map((mediaFile) =>
                uploadMedia.mutateAsync({
                  problemEntityId: newProblem.entity_id,
                  file: mediaFile.file,
                  category: 'problem',
                })
              )
            )
          } catch (error) {
            console.error('Failed to upload some media files:', error)
          }
        }

        onSuccess?.(newProblem.entity_id)
        onClose()

        // Reset form
        setFormData({
          title: '',
          description: '',
          city: 'Алматы',
          country: 'Казахстан',
          district: '',
          address: '',
          latitude: 43.238293,
          longitude: 76.945465,
          problem_type: ProblemType.OTHER,
          nature: ProblemNature.PERMANENT,
          tags: [],
        })
        setMediaFiles([])
        setSelectedAddress('')
      },
    })
  }

  if (!isOpen) return null

  return (
    <>
      <div className="fixed inset-0 z-[10001] bg-black/60 backdrop-blur-sm overflow-y-auto">
        <div className="min-h-full flex items-center justify-center p-4 py-8">
          <div className="bg-dark-card rounded-2xl shadow-2xl w-full max-w-3xl">
          {/* Header */}
          <div className="bg-dark-card border-b border-border p-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-text-primary">Создать проблему</h2>
              <p className="text-sm text-text-secondary mt-1">
                Расскажите о проблеме в вашем городе
              </p>
            </div>
            <button
              onClick={onClose}
              className="btn-ghost p-2 hover:bg-dark-hover rounded-lg"
              disabled={createProblem.isPending}
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Название проблемы <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Например: Яма на дороге возле дома"
                className="input w-full"
                required
                disabled={createProblem.isPending}
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Описание
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Подробное описание проблемы..."
                className="input w-full min-h-[120px] resize-none"
                disabled={createProblem.isPending}
              />
            </div>

            {/* Problem Type */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Тип проблемы <span className="text-danger">*</span>
              </label>
              <select
                value={formData.problem_type}
                onChange={(e) =>
                  setFormData({ ...formData, problem_type: e.target.value as ProblemType })
                }
                className="input w-full"
                required
                disabled={createProblem.isPending}
              >
                {Object.entries(problemTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Nature */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Характер проблемы
              </label>
              <select
                value={formData.nature || ProblemNature.PERMANENT}
                onChange={(e) =>
                  setFormData({ ...formData, nature: e.target.value as ProblemNature })
                }
                className="input w-full"
                disabled={createProblem.isPending}
              >
                {Object.entries(problemNatureLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Местоположение <span className="text-danger">*</span>
              </label>
              <button
                type="button"
                onClick={() => setIsLocationPickerOpen(true)}
                disabled={createProblem.isPending}
                className="w-full btn-ghost justify-start text-left p-4 border border-border hover:border-primary/50"
              >
                <MapPin className="w-5 h-5 text-primary flex-shrink-0" />
                <div className="ml-3 flex-1 min-w-0">
                  {selectedAddress ? (
                    <>
                      <p className="text-sm text-text-primary truncate">{selectedAddress}</p>
                      <p className="text-xs text-text-muted mt-1">
                        {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
                      </p>
                    </>
                  ) : (
                    <p className="text-sm text-text-secondary">
                      Нажмите, чтобы выбрать на карте
                    </p>
                  )}
                </div>
              </button>
            </div>

            {/* City */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                Город <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                placeholder="Алматы"
                className="input w-full"
                required
                disabled={createProblem.isPending}
              />
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Адрес</label>
              <input
                type="text"
                value={formData.address || ''}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Улица, дом"
                className="input w-full"
                disabled={createProblem.isPending}
              />
            </div>

            {/* District */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">Район</label>
              <input
                type="text"
                value={formData.district || ''}
                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                placeholder="Название района"
                className="input w-full"
                disabled={createProblem.isPending}
              />
            </div>

            {/* Media Upload */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                <Image className="w-4 h-4 inline mr-2" />
                Фото и видео
              </label>
              <MediaUploader
                files={mediaFiles}
                onChange={setMediaFiles}
                maxImageSize={30}
                maxVideoSize={250}
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="btn-ghost flex-1"
                disabled={createProblem.isPending}
              >
                Отмена
              </button>
              <button
                type="submit"
                className="btn-primary flex-1 flex items-center justify-center gap-2 py-3 text-base font-semibold"
                disabled={createProblem.isPending}
              >
                {createProblem.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Создание...
                  </>
                ) : (
                  'Создать проблему'
                )}
              </button>
            </div>
          </form>
        </div>
        </div>
      </div>

      {/* Location Picker Modal */}
      <LocationPicker
        isOpen={isLocationPickerOpen}
        onClose={() => setIsLocationPickerOpen(false)}
        onSelect={handleLocationSelect}
        initialPosition={{ lat: formData.latitude, lng: formData.longitude }}
      />
    </>
  )
}
