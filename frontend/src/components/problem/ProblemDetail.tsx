import { useState } from 'react'
import { Share2, Flag, MapPin, Eye, Calendar, User, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { Link } from 'react-router-dom'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import { ReportModal } from '../ReportModal'
import { useProblem } from '../../hooks/useProblem'
import { useComments } from '../../hooks/useComments'
import { useVote, useVoteStats } from '../../hooks/useVotes'
import { useAuth } from '../../hooks/useAuth'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

// Fix Leaflet default marker icon
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface ProblemDetailProps {
  problemId: number
}

export default function ProblemDetail({ problemId }: ProblemDetailProps) {
  const [isReportModalOpen, setIsReportModalOpen] = useState(false)
  const [reportTarget, setReportTarget] = useState<{
    type: 'problem' | 'comment'
    id: number
    title: string
  } | null>(null)

  const handleOpenReportModal = (type: 'problem' | 'comment', id: number, title: string) => {
    setReportTarget({ type, id, title })
    setIsReportModalOpen(true)
  }

  const handleCloseReportModal = () => {
    setIsReportModalOpen(false)
    setReportTarget(null)
  }
  const { user, isAuthenticated } = useAuth()

  // Load problem data
  const { data: problem, isLoading, error } = useProblem(problemId)
  const { data: comments, isLoading: commentsLoading } = useComments(problemId)
  const { data: voteStats } = useVoteStats(problemId)

  // Vote mutations
  const voteMutation = useVote(problemId)

  const handleVoteTrue = () => {
    if (!isAuthenticated) {
      alert('Войдите, чтобы голосовать')
      return
    }
    voteMutation.mutate({ isUpvote: true, isTrue: true })
  }

  const handleVoteFalse = () => {
    if (!isAuthenticated) {
      alert('Войдите, чтобы голосовать')
      return
    }
    voteMutation.mutate({ isUpvote: false, isTrue: false })
  }

  const handleShare = () => {
    const url = window.location.href
    if (navigator.share) {
      navigator.share({
        title: problem?.title,
        text: problem?.description || '',
        url: url,
      }).catch((error) => console.log('Error sharing:', error))
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(url).then(() => {
        alert('Ссылка скопирована в буфер обмена!')
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-dark-bg">
        <Loader2 className="w-12 h-12 text-primary animate-spin" />
      </div>
    )
  }

  if (error || !problem) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-dark-bg">
        <div className="text-center">
          <p className="text-text-secondary text-lg mb-2">Проблема не найдена</p>
          <p className="text-text-muted text-sm">{(error as any)?.message || 'Попробуйте позже'}</p>
        </div>
      </div>
    )
  }

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

  return (
    <div className="flex bg-dark-bg">
      {/* Left side - Media viewer + Description + Comments */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          {/* Media Viewer - уменьшенный */}
          <div className="bg-black rounded-2xl overflow-hidden m-6 h-[500px] flex items-center justify-center">
            {problem.media && problem.media.length > 0 ? (
              <img
                src={problem.media[0].url}
                alt={problem.title}
                className="w-full h-full object-contain"
              />
            ) : (
              <div className="flex items-center justify-center text-text-muted">
                <MapPin className="w-16 h-16" />
              </div>
            )}
          </div>

          {/* Title + Description */}
          <div className="px-6 pb-4 border-b border-border">
            <h1 className="text-2xl font-bold text-text-primary mb-3">
              {problem.title}
            </h1>

            <div className="flex items-center gap-2 text-sm text-text-secondary mb-4">
              <MapPin className="w-4 h-4" />
              <span>{problem.address || 'Адрес не указан'}</span>
            </div>

            <p className="text-text-primary leading-relaxed whitespace-pre-wrap">
              {problem.description}
            </p>
          </div>

          {/* Actions Bar */}
          <div className="px-6 py-4 border-b border-border flex items-center gap-3">
            <button
              onClick={handleVoteTrue}
              disabled={voteMutation.isPending || !isAuthenticated}
              className="btn-ghost flex items-center gap-2 text-success disabled:opacity-50 hover:scale-105 active:scale-95"
              title="Это правда"
            >
              <CheckCircle className="w-5 h-5" />
              <span>Правда</span>
              <span className="text-sm">({Math.round((problem.truth_score || 0) * 100)}%)</span>
            </button>

            <button
              onClick={handleVoteFalse}
              disabled={voteMutation.isPending || !isAuthenticated}
              className="btn-ghost flex items-center gap-2 text-danger disabled:opacity-50 hover:scale-105 active:scale-95"
              title="Это фейк"
            >
              <XCircle className="w-5 h-5" />
              <span>Фейк</span>
            </button>

            <div className="flex-1" />

            <button
              onClick={handleShare}
              className="btn-ghost flex items-center gap-2 hover:scale-105 active:scale-95"
              title="Поделиться"
            >
              <Share2 className="w-5 h-5" />
              <span>Поделиться</span>
            </button>

            <button
              onClick={() => handleOpenReportModal('problem', problem.entity_id, problem.title)}
              className="btn-ghost flex items-center gap-2 text-danger hover:scale-105 active:scale-95"
              title="Пожаловаться"
            >
              <Flag className="w-5 h-5" />
            </button>
          </div>

          {/* Comments Section */}
          <div className="p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              Комментарии ({comments?.length || 0})
            </h3>

            {/* Comment Input */}
            {isAuthenticated ? (
              <div className="mb-6">
                <textarea
                  placeholder="Добавить комментарий..."
                  className="input w-full min-h-[80px] resize-none"
                />
                <div className="flex justify-end mt-3">
                  <button className="btn-primary hover:scale-105 active:scale-95">
                    Отправить
                  </button>
                </div>
              </div>
            ) : (
              <div className="mb-6 p-4 bg-dark-card rounded-lg text-center">
                <p className="text-text-secondary">
                  <Link to="/login" className="text-primary hover:underline">
                    Войдите
                  </Link>
                  , чтобы оставить комментарий
                </p>
              </div>
            )}

            {/* Comments List */}
            {commentsLoading ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            ) : comments && comments.length > 0 ? (
              <div className="space-y-4">
                {comments.map((comment) => (
                  <div key={comment.entity_id} className="space-y-3">
                    <div className="flex gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-primary" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-text-primary">
                            {comment.author?.username || 'Аноним'}
                          </span>
                          <span className="text-xs text-text-muted">
                            {formatDistanceToNow(new Date(comment.created_at), {
                              addSuffix: true,
                              locale: ru,
                            })}
                          </span>
                        </div>
                        <p className="text-text-secondary text-sm mb-2">
                          {comment.content}
                        </p>
                        <div className="flex gap-3 text-xs">
                          <button className="text-text-muted hover:text-primary transition-colors duration-200">
                            Ответить
                          </button>
                          <button
                            onClick={() => handleOpenReportModal('comment', comment.entity_id, `Комментарий от ${comment.author?.username || 'Аноним'}`)}
                            className="text-text-muted hover:text-danger transition-colors duration-200 flex items-center gap-1"
                          >
                            <Flag className="w-3 h-3" />
                            Пожаловаться
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-text-muted py-8">
                Комментариев пока нет. Будьте первым!
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Right side - Info Panel (увеличенная) */}
      <div className="w-96 border-l border-border overflow-y-auto bg-dark-card">
        <div className="p-6 space-y-6">
          {/* Mini Map */}
          <div>
            <h4 className="text-xs font-medium text-text-muted mb-2">Местоположение</h4>
            {problem.latitude && problem.longitude ? (
              <div className="aspect-video rounded-xl overflow-hidden border border-border">
                <MapContainer
                  center={[problem.latitude, problem.longitude]}
                  zoom={15}
                  className="w-full h-full"
                  zoomControl={false}
                  attributionControl={false}
                  dragging={false}
                  scrollWheelZoom={false}
                  doubleClickZoom={false}
                  touchZoom={false}
                  style={{ background: '#0B1220' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution=""
                  />
                  <Marker position={[problem.latitude, problem.longitude]} />
                </MapContainer>
              </div>
            ) : (
              <div className="aspect-video bg-dark-hover rounded-xl flex items-center justify-center">
                <MapPin className="w-8 h-8 text-text-muted" />
              </div>
            )}
          </div>

          {/* Status */}
          <div>
            <h4 className="text-xs font-medium text-text-muted mb-2">Статус</h4>
            <span className={`badge ${statusColors[problem.status as keyof typeof statusColors]}`}>
              {statusLabels[problem.status as keyof typeof statusLabels]}
            </span>
          </div>

          {/* Truth Score */}
          {problem.truth_score !== undefined && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Достоверность</h4>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-success transition-all"
                    style={{ width: `${problem.truth_score * 100}%` }}
                  />
                </div>
                <span className="text-sm text-text-primary">
                  {Math.round(problem.truth_score * 100)}%
                </span>
              </div>
            </div>
          )}

          {/* Author */}
          <div>
            <h4 className="text-xs font-medium text-text-muted mb-2">Автор</h4>
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <User className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">
                  {problem.author?.username || 'Аноним'}
                </p>
                {problem.author?.reputation !== undefined && (
                  <p className="text-xs text-text-muted">
                    Репутация: {problem.author.reputation}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Category */}
          {problem.problem_type && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Категория</h4>
              <span className="badge bg-primary/20 text-primary">
                {problem.problem_type}
              </span>
            </div>
          )}

          {/* Zone */}
          {problem.zone_name && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Район</h4>
              <p className="text-sm text-text-primary">{problem.zone_name}</p>
            </div>
          )}

          {/* Stats */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-muted flex items-center gap-2">
                <Eye className="w-4 h-4" />
                Просмотры
              </span>
              <span className="text-text-primary">{problem.views_count || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-muted flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Создано
              </span>
              <span className="text-text-primary">
                {formatDistanceToNow(new Date(problem.created_at), {
                  addSuffix: true,
                  locale: ru,
                })}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Report Modal */}
      <ReportModal
        isOpen={isReportModalOpen}
        onClose={handleCloseReportModal}
        targetType={reportTarget?.type || 'problem'}
        targetEntityId={reportTarget?.id || problemId}
        targetTitle={reportTarget?.title || problem.title}
      />
    </div>
  )
}
