import { MapPin, Eye, MessageCircle, ThumbsUp, ExternalLink, Image as ImageIcon, ChevronLeft, ChevronRight, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useProblemMedia } from '../../hooks/useMedia'
import { UserName } from '../UserName'
import type { ProblemPublic } from '../../api/generated/models/ProblemPublic'

interface ProblemCardProps {
  problem: ProblemPublic
  isActive?: boolean
  onCardClick?: () => void
}

export default function ProblemCard({ problem, isActive, onCardClick }: ProblemCardProps) {
  const navigate = useNavigate()
  const { data: media, isLoading: mediaLoading } = useProblemMedia(problem.entity_id)
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0)

  const statusColors = {
    open: 'badge-pending',
    in_progress: 'badge-in-progress',
    solved: 'badge-resolved',
    rejected: 'badge-rejected',
    archived: 'badge-rejected',
  }

  const statusLabels = {
    open: 'Открыта',
    in_progress: 'В работе',
    solved: 'Решена',
    rejected: 'Отклонена',
    archived: 'Архив',
  }

  const handleDetailClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/problems/${problem.entity_id}`)
  }

  // Фильтруем только фото (без видео)
  const photos = media?.filter(m => m.media_type === 'photo') || []

  // Автоматическая смена фото каждые 3 секунды
  useEffect(() => {
    if (photos.length <= 1) return

    const interval = setInterval(() => {
      setCurrentPhotoIndex((prev) => (prev + 1) % photos.length)
    }, 3000)

    return () => clearInterval(interval)
  }, [photos.length])

  const handlePrevPhoto = (e: React.MouseEvent) => {
    e.stopPropagation()
    setCurrentPhotoIndex((prev) => (prev - 1 + photos.length) % photos.length)
  }

  const handleNextPhoto = (e: React.MouseEvent) => {
    e.stopPropagation()
    setCurrentPhotoIndex((prev) => (prev + 1) % photos.length)
  }

  return (
    <div
      onClick={onCardClick}
      className={`
        card card-hover cursor-pointer relative overflow-hidden
        ${isActive ? 'ring-2 ring-primary shadow-glow' : ''}
      `}
    >
      {/* Detail button - top right */}
      <button
        onClick={handleDetailClick}
        className="absolute top-3 right-3 w-8 h-8 bg-dark-card/90 hover:bg-primary/20 border border-border hover:border-primary rounded-lg flex items-center justify-center z-10 transition-all backdrop-blur-sm"
        aria-label="Открыть детали"
      >
        <ExternalLink className="w-4 h-4 text-text-secondary hover:text-primary" />
      </button>

      {/* Image Section - Top */}
      <div className="relative w-full h-48 bg-dark-hover group">
        {mediaLoading ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : photos.length > 0 ? (
          <>
            <img
              src={photos[currentPhotoIndex].thumbnail_url || photos[currentPhotoIndex].url}
              alt={problem.title}
              className="w-full h-full object-cover transition-opacity duration-300"
            />

            {/* Navigation arrows - показываются при наведении */}
            {photos.length > 1 && (
              <>
                <button
                  onClick={handlePrevPhoto}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-dark-card/90 hover:bg-primary/20 border border-border hover:border-primary rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm z-10"
                  aria-label="Предыдущее фото"
                >
                  <ChevronLeft className="w-4 h-4 text-text-primary" />
                </button>
                <button
                  onClick={handleNextPhoto}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-dark-card/90 hover:bg-primary/20 border border-border hover:border-primary rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm z-10"
                  aria-label="Следующее фото"
                >
                  <ChevronRight className="w-4 h-4 text-text-primary" />
                </button>
              </>
            )}

            {/* Photo counter and indicator dots */}
            {photos.length > 1 && (
              <div className="absolute bottom-2 left-0 right-0 flex flex-col items-center gap-2">
                {/* Indicator dots */}
                <div className="flex gap-1">
                  {photos.map((_, index) => (
                    <button
                      key={index}
                      onClick={(e) => {
                        e.stopPropagation()
                        setCurrentPhotoIndex(index)
                      }}
                      className={`w-2 h-2 rounded-full transition-all ${
                        index === currentPhotoIndex
                          ? 'bg-primary w-4'
                          : 'bg-white/50 hover:bg-white/80'
                      }`}
                      aria-label={`Фото ${index + 1}`}
                    />
                  ))}
                </div>

                {/* Photo counter badge */}
                <div className="px-2 py-1 bg-dark-card/90 backdrop-blur-sm rounded-lg flex items-center gap-1 text-xs text-text-primary">
                  <ImageIcon className="w-3 h-3" />
                  <span>{currentPhotoIndex + 1} / {photos.length}</span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <MapPin className="w-12 h-12 text-text-muted" />
          </div>
        )}
      </div>

      {/* Content Section - Bottom */}
      <div className="p-4">
        {/* Category Badge */}
        <span className="badge bg-primary/20 text-primary text-xs mb-2 inline-block">
          {problem.category}
        </span>

        {/* Title */}
        <h3 className="text-base font-semibold text-text-primary mb-2 line-clamp-2">
          {problem.title}
        </h3>

        {/* Address */}
        <div className="flex items-center gap-1 text-sm text-text-secondary mb-2">
          <MapPin className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">{problem.address || problem.city}</span>
        </div>

        {/* Author */}
        <div className="flex items-center gap-1 text-sm text-text-secondary mb-3">
          <User className="w-4 h-4 flex-shrink-0" />
          <UserName userId={problem.author_entity_id} className="text-sm" />
        </div>

        {/* Metadata */}
        <div className="flex items-center flex-wrap gap-2 text-xs text-text-muted">
          <span className={`badge ${statusColors[problem.status]}`}>
            {statusLabels[problem.status]}
          </span>

          {problem.vote_count !== undefined && problem.vote_count > 0 && (
            <div className="flex items-center gap-1">
              <ThumbsUp className="w-3 h-3" />
              <span>{problem.vote_count}</span>
            </div>
          )}

          {problem.comment_count !== undefined && problem.comment_count > 0 && (
            <div className="flex items-center gap-1">
              <MessageCircle className="w-3 h-3" />
              <span>{problem.comment_count}</span>
            </div>
          )}

          {problem.created_at && (
            <span className="ml-auto">
              {formatDistanceToNow(new Date(problem.created_at), {
                addSuffix: true,
                locale: ru,
              })}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
