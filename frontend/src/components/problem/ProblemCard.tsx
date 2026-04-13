import { MapPin, Eye, MessageCircle, ThumbsUp, ExternalLink } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useNavigate } from 'react-router-dom'

interface Media {
  entity_id: number
  url: string
  thumbnail_url?: string
  media_type: 'image' | 'video'
}

interface Problem {
  entity_id: number
  title: string
  description: string
  status: 'pending' | 'verified' | 'in_progress' | 'resolved' | 'rejected'
  category: string
  address: string
  upvotes: number
  downvotes: number
  comments_count: number
  views_count: number
  created_at: string
  media?: Media[]
}

interface ProblemCardProps {
  problem: Problem
  isActive?: boolean
  onCardClick?: () => void
}

export default function ProblemCard({ problem, isActive, onCardClick }: ProblemCardProps) {
  const navigate = useNavigate()

  const statusColors = {
    pending: 'badge-pending',
    verified: 'badge-in-progress',
    in_progress: 'badge-in-progress',
    resolved: 'badge-resolved',
    rejected: 'badge-rejected',
  }

  const statusLabels = {
    pending: 'Новая',
    verified: 'Проверена',
    in_progress: 'В работе',
    resolved: 'Решена',
    rejected: 'Отклонена',
  }

  const handleDetailClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    navigate(`/problems/${problem.entity_id}`)
  }

  return (
    <div
      onClick={onCardClick}
      className={`
        card card-hover p-4 cursor-pointer relative
        ${isActive ? 'border border-primary shadow-glow' : ''}
      `}
    >
      {/* Detail button - top right */}
      <button
        onClick={handleDetailClick}
        className="absolute top-3 right-3 w-8 h-8 bg-dark-card hover:bg-primary/20 border border-border hover:border-primary rounded-lg flex items-center justify-center z-10 transition-all"
        aria-label="Открыть детали"
      >
        <ExternalLink className="w-4 h-4 text-text-secondary hover:text-primary" />
      </button>

      <div className="flex gap-3">
        {/* Thumbnail */}
        <div className="w-20 h-20 flex-shrink-0 rounded-2xl overflow-hidden bg-dark-hover">
          {problem.media && problem.media.length > 0 ? (
            <img
              src={problem.media[0].thumbnail_url || problem.media[0].url}
              alt={problem.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <MapPin className="w-8 h-8 text-text-muted" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 pr-8">
          {/* Category Badge */}
          <span className="badge bg-primary/20 text-primary text-xs mb-2">
            {problem.category}
          </span>

          {/* Title */}
          <h3 className="text-sm font-semibold text-text-primary mb-1 line-clamp-2">
            {problem.title}
          </h3>

          {/* Address */}
          <div className="flex items-center gap-1 text-xs text-text-secondary mb-2">
            <MapPin className="w-3 h-3" />
            <span className="truncate">{problem.address}</span>
          </div>

          {/* Metadata */}
          <div className="flex items-center gap-3 text-xs text-text-muted">
            <span className={`badge ${statusColors[problem.status]}`}>
              {statusLabels[problem.status]}
            </span>
            <div className="flex items-center gap-1">
              <Eye className="w-3 h-3" />
              <span>{problem.views_count}</span>
            </div>
            <div className="flex items-center gap-1">
              <ThumbsUp className="w-3 h-3" />
              <span>{problem.upvotes}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageCircle className="w-3 h-3" />
              <span>{problem.comments_count}</span>
            </div>
            <span>
              {formatDistanceToNow(new Date(problem.created_at), {
                addSuffix: true,
                locale: ru,
              })}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
