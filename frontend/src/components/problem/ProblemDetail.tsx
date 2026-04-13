import { useState } from 'react'
import { Share2, Flag, MapPin, Eye, Calendar, Loader2, CheckCircle, XCircle, ChevronLeft, ChevronRight, Play, History, MessageSquare, ThumbsUp, Clock, AlertTriangle, TrendingUp, Users as UsersIcon, ArrowLeft, ExternalLink, Navigation, Edit } from 'lucide-react'
import { formatDistanceToNow, differenceInDays } from 'date-fns'
import { ru } from 'date-fns/locale'
import { Link, useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker } from 'react-leaflet'
import { ReportModal } from '../ReportModal'
import { UserName } from '../UserName'
import { CommentItem } from './CommentItem'
import ProblemEditForm from './ProblemEditForm'
import { useProblem, useProblemHistory } from '../../hooks/useProblem'
import { useComments, useCreateComment } from '../../hooks/useComments'
import { useVote, useVoteStats, useMyVote, useDeleteVote } from '../../hooks/useVotes'
import { useProblemMedia } from '../../hooks/useMedia'
import { useUser } from '../../hooks/useUser'
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
  const navigate = useNavigate()
  const [isReportModalOpen, setIsReportModalOpen] = useState(false)
  const [reportTarget, setReportTarget] = useState<{
    type: 'problem' | 'comment'
    id: number
    title: string
  } | null>(null)
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)
  const [commentText, setCommentText] = useState('')
  const [replyTo, setReplyTo] = useState<number | null>(null)
  const [showHistory, setShowHistory] = useState(false)
  const [isEditFormOpen, setIsEditFormOpen] = useState(false)

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
  const { data: myVote } = useMyVote(problemId)
  const { data: history, isLoading: historyLoading } = useProblemHistory(problemId)
  const { data: media, isLoading: mediaLoading } = useProblemMedia(problemId)
  const { data: author } = useUser(problem?.author_entity_id)

  // Mutations
  const voteMutation = useVote(problemId)
  const deleteVoteMutation = useDeleteVote(problemId)
  const createCommentMutation = useCreateComment(problemId)

  const handleVoteTrue = () => {
    if (!isAuthenticated) {
      alert('Войдите, чтобы голосовать')
      return
    }
    if (myVote) {
      // Проверяем, был ли голос уже изменён (version > 2 означает, что было больше одного изменения)
      if (myVote.version > 2) {
        alert('Вы уже изменяли свой голос. Изменить голос можно только один раз.')
        return
      }
      // Если голос уже есть, но не был изменён больше одного раза - позволяем изменить
      if (confirm('Вы уже проголосовали. Хотите изменить свой голос? (Изменить можно только один раз)')) {
        voteMutation.mutate({ isTrue: true })
      }
      return
    }
    voteMutation.mutate({ isTrue: true })
  }

  const handleVoteFalse = () => {
    if (!isAuthenticated) {
      alert('Войдите, чтобы голосовать')
      return
    }
    if (myVote) {
      // Проверяем, был ли голос уже изменён (version > 2 означает, что было больше одного изменения)
      if (myVote.version > 2) {
        alert('Вы уже изменяли свой голос. Изменить голос можно только один раз.')
        return
      }
      // Если голос уже есть, но не был изменён больше одного раза - позволяем изменить
      if (confirm('Вы уже проголосовали. Хотите изменить свой голос? (Изменить можно только один раз)')) {
        voteMutation.mutate({ isTrue: false })
      }
      return
    }
    voteMutation.mutate({ isTrue: false })
  }

  const handleDeleteVote = () => {
    if (!isAuthenticated) {
      alert('Войдите, чтобы удалить голос')
      return
    }
    if (!myVote) {
      alert('Вы ещё не голосовали')
      return
    }
    if (confirm('Вы уверены, что хотите отменить свой голос?')) {
      deleteVoteMutation.mutate()
    }
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

  const handleSubmitComment = () => {
    if (!commentText.trim()) return

    createCommentMutation.mutate(
      {
        content: commentText,
        parent_entity_id: replyTo || undefined,
      },
      {
        onSuccess: () => {
          setCommentText('')
          setReplyTo(null)
        },
      }
    )
  }

  const handleReply = (commentId: number) => {
    setReplyTo(commentId)
    // Scroll to comment input
    document.querySelector('textarea')?.focus()
  }

  const handleCancelReply = () => {
    setReplyTo(null)
  }

  const handlePrevMedia = () => {
    if (!media || media.length === 0) return
    setCurrentMediaIndex((prev) => (prev === 0 ? media.length - 1 : prev - 1))
  }

  const handleNextMedia = () => {
    if (!media || media.length === 0) return
    setCurrentMediaIndex((prev) => (prev === media.length - 1 ? 0 : prev + 1))
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
    archived: 'Архивирована',
  }

  return (
    <div className="flex flex-col lg:flex-row bg-dark-bg min-h-screen">
      {/* Left side - Media viewer + Description + Comments (Desktop) / All content (Mobile) */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          {/* Back button - Desktop only */}
          <div className="hidden lg:block px-6 pt-6 pb-2">
            <button
              onClick={() => navigate('/')}
              className="btn-ghost flex items-center gap-2 hover:scale-105 active:scale-95"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Назад к списку</span>
            </button>
          </div>

          {/* Media Viewer - Fixed on mobile, normal on desktop */}
          <div className={`bg-black overflow-hidden flex items-center justify-center relative group ${
            'fixed lg:relative top-0 left-0 right-0 z-50 h-[250px] lg:h-auto lg:rounded-2xl lg:m-6 lg:aspect-video'
          }`}>
            {mediaLoading ? (
              <Loader2 className="w-12 h-12 text-primary animate-spin" />
            ) : media && media.length > 0 ? (
              <>
                {media[currentMediaIndex].media_type === 'photo' ? (
                  <img
                    src={media[currentMediaIndex].url}
                    alt={problem.title}
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <video
                    src={media[currentMediaIndex].url}
                    controls
                    className="w-full h-full object-contain"
                  />
                )}

                {/* Navigation arrows */}
                {media.length > 1 && (
                  <>
                    <button
                      onClick={handlePrevMedia}
                      className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ChevronLeft className="w-6 h-6" />
                    </button>
                    <button
                      onClick={handleNextMedia}
                      className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ChevronRight className="w-6 h-6" />
                    </button>

                    {/* Media counter */}
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/70 text-white px-3 py-1 rounded-full text-sm">
                      {currentMediaIndex + 1} / {media.length}
                    </div>

                    {/* Thumbnails */}
                    <div className="absolute bottom-4 left-4 right-4 flex gap-2 justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      {media.map((mediaItem, idx) => (
                        <button
                          key={idx}
                          onClick={() => setCurrentMediaIndex(idx)}
                          className={`w-16 h-16 rounded-lg overflow-hidden border-2 transition-all ${
                            idx === currentMediaIndex ? 'border-primary scale-110' : 'border-white/30 hover:border-white/60'
                          }`}
                        >
                          {mediaItem.media_type === 'photo' ? (
                            <img src={mediaItem.url} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full bg-dark-hover flex items-center justify-center">
                              <Play className="w-6 h-6 text-white" />
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </>
            ) : (
              <div className="flex items-center justify-center text-text-muted">
                <MapPin className="w-16 h-16" />
              </div>
            )}
          </div>

          {/* Title + Description + Pressure Indicators */}
          <div className="px-4 lg:px-6 pb-4 border-b border-border mt-[20px] lg:mt-0">
            {/* Back button - Mobile only */}
            <div className="lg:hidden mb-4">
              <button
                onClick={() => navigate('/')}
                className="btn-ghost flex items-center gap-2 hover:scale-105 active:scale-95"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Назад к списку</span>
              </button>
            </div>

            <h1 className="text-xl lg:text-2xl font-bold text-text-primary mb-3">
              {problem.title}
            </h1>

            <div className="flex items-center gap-2 text-sm text-text-secondary mb-4">
              <MapPin className="w-4 h-4" />
              <span>{problem.address || problem.city}</span>
            </div>

            {/* Pressure Indicators - показываем серьезность для властей */}
            {problem.status !== 'solved' && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 lg:gap-3 mb-4">
                {/* Days Waiting */}
                <div className="bg-danger/10 border border-danger/30 rounded-lg p-2 lg:p-3">
                  <div className="flex items-center gap-1 lg:gap-2 mb-1">
                    <Clock className="w-3 lg:w-4 h-3 lg:h-4 text-danger" />
                    <span className="text-xs text-text-muted">Не решена</span>
                  </div>
                  <p className="text-base lg:text-lg font-bold text-danger">
                    {differenceInDays(new Date(), new Date(problem.created_at!))} дней
                  </p>
                </div>

                {/* Citizen Pressure */}
                <div className="bg-warning/10 border border-warning/30 rounded-lg p-2 lg:p-3">
                  <div className="flex items-center gap-1 lg:gap-2 mb-1">
                    <UsersIcon className="w-3 lg:w-4 h-3 lg:h-4 text-warning" />
                    <span className="text-xs text-text-muted">Граждан</span>
                  </div>
                  <p className="text-base lg:text-lg font-bold text-warning">
                    {problem.vote_count + problem.comment_count}
                  </p>
                </div>

                {/* Urgency Score */}
                <div className="bg-danger/10 border border-danger/30 rounded-lg p-2 lg:p-3">
                  <div className="flex items-center gap-1 lg:gap-2 mb-1">
                    <AlertTriangle className="w-3 lg:w-4 h-3 lg:h-4 text-danger" />
                    <span className="text-xs text-text-muted">Срочность</span>
                  </div>
                  <p className="text-base lg:text-lg font-bold text-danger">
                    {Math.round(problem.urgency_score * 100)}%
                  </p>
                </div>

                {/* Priority Score */}
                <div className="bg-primary/10 border border-primary/30 rounded-lg p-2 lg:p-3">
                  <div className="flex items-center gap-1 lg:gap-2 mb-1">
                    <TrendingUp className="w-3 lg:w-4 h-3 lg:h-4 text-primary" />
                    <span className="text-xs text-text-muted">Приоритет</span>
                  </div>
                  <p className="text-base lg:text-lg font-bold text-primary">
                    {problem.priority_score.toFixed(2)}
                  </p>
                </div>
              </div>
            )}

            <p className="text-sm lg:text-base text-text-primary leading-relaxed whitespace-pre-wrap">
              {problem.description}
            </p>
          </div>

          {/* Actions Bar */}
          <div className="px-4 lg:px-6 py-3 lg:py-4 border-b border-border">
            {/* Информация о статусе голоса */}
            {myVote && myVote.version > 2 && (
              <div className="mb-2 px-3 py-2 bg-warning/10 border border-warning/30 rounded-lg text-sm text-warning flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                <span>Вы уже изменяли свой голос. Повторное изменение невозможно.</span>
              </div>
            )}

            <div className="flex items-center gap-1 lg:gap-3 overflow-x-auto">
              <button
                onClick={handleVoteTrue}
                disabled={voteMutation.isPending || !isAuthenticated || (myVote?.version ?? 0) > 2}
                className={`btn-ghost flex items-center gap-1 lg:gap-2 disabled:opacity-50 hover:scale-105 active:scale-95 whitespace-nowrap ${
                  myVote?.is_true === true ? 'text-success ring-2 ring-success' : 'text-success'
                }`}
                title={
                  !isAuthenticated
                    ? 'Войдите, чтобы голосовать'
                    : myVote?.version && myVote.version > 2
                    ? 'Вы уже изменяли голос'
                    : myVote
                    ? 'Изменить голос на "Правда"'
                    : 'Это правда'
                }
              >
                <CheckCircle className="w-4 lg:w-5 h-4 lg:h-5" />
                <span className="text-sm lg:text-base">Правда</span>
                <span className="text-xs lg:text-sm">({Math.round((problem.truth_score || 0) * 100)}%)</span>
              </button>

              <button
                onClick={handleVoteFalse}
                disabled={voteMutation.isPending || !isAuthenticated || (myVote?.version ?? 0) > 2}
                className={`btn-ghost flex items-center gap-1 lg:gap-2 disabled:opacity-50 hover:scale-105 active:scale-95 whitespace-nowrap ${
                  myVote?.is_true === false ? 'text-danger ring-2 ring-danger' : 'text-danger'
                }`}
                title={
                  !isAuthenticated
                    ? 'Войдите, чтобы голосовать'
                    : myVote?.version && myVote.version > 2
                    ? 'Вы уже изменяли голос'
                    : myVote
                    ? 'Изменить голос на "Фейк"'
                    : 'Это фейк'
                }
              >
                <XCircle className="w-4 lg:w-5 h-4 lg:h-5" />
                <span className="text-sm lg:text-base">Фейк</span>
              </button>

              {/* Delete vote button - показываем только если пользователь уже проголосовал */}
              {myVote && (
                <button
                  onClick={handleDeleteVote}
                  disabled={deleteVoteMutation.isPending}
                  className="btn-ghost flex items-center gap-1 lg:gap-2 text-text-muted hover:text-danger hover:scale-105 active:scale-95 disabled:opacity-50 whitespace-nowrap"
                  title="Отменить голос"
                >
                  <XCircle className="w-4 lg:w-5 h-4 lg:h-5" />
                  <span className="text-xs lg:text-sm">Отменить</span>
                </button>
              )}

              <div className="flex-1" />

              {/* Edit button - only for author */}
              {isAuthenticated && user?.entity_id === problem.author_entity_id && (
                <button
                  onClick={() => setIsEditFormOpen(true)}
                  className="btn-ghost flex items-center gap-1 lg:gap-2 hover:scale-105 active:scale-95"
                  title="Редактировать"
                >
                  <Edit className="w-4 lg:w-5 h-4 lg:h-5" />
                </button>
              )}

              <button
                onClick={handleShare}
                className="btn-ghost flex items-center gap-1 lg:gap-2 hover:scale-105 active:scale-95"
                title="Поделиться"
              >
                <Share2 className="w-4 lg:w-5 h-4 lg:h-5" />
              </button>

              <button
                onClick={() => handleOpenReportModal('problem', problem.entity_id, problem.title)}
                className="btn-ghost flex items-center gap-1 lg:gap-2 text-danger hover:scale-105 active:scale-95"
                title="Пожаловаться"
              >
                <Flag className="w-4 lg:w-5 h-4 lg:h-5" />
              </button>
            </div>
          </div>

          {/* Right Panel Content on Mobile only */}
          <div className="lg:hidden px-4 py-6 space-y-6 border-b border-border bg-dark-card pb-20">
            {/* Mini Map */}
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Местоположение</h4>
              {problem.latitude && problem.longitude ? (
                <div className="space-y-3">
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

                  {/* Координаты */}
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <MapPin className="w-3 h-3" />
                    <span>{problem.latitude.toFixed(6)}, {problem.longitude.toFixed(6)}</span>
                  </div>

                  {/* Ссылки */}
                  <div className="flex gap-2">
                    <Link
                      to={`/map?lat=${problem.latitude}&lng=${problem.longitude}&zoom=16`}
                      className="flex-1 btn-ghost text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95"
                    >
                      <Navigation className="w-4 h-4" />
                      <span>Открыть на карте</span>
                    </Link>
                    <a
                      href={`https://2gis.ru/geo/${problem.longitude},${problem.latitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 btn-ghost text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>2GIS</span>
                    </a>
                  </div>
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

            {/* Resolution Info */}
            {problem.status === 'solved' && problem.resolved_at && (
              <div className="bg-success/10 border border-success/30 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-success" />
                  <h4 className="text-sm font-semibold text-success">Проблема решена</h4>
                </div>
                <p className="text-xs text-text-secondary mb-2">
                  {formatDistanceToNow(new Date(problem.resolved_at), {
                    addSuffix: true,
                    locale: ru,
                  })}
                </p>
                {problem.resolution_note && (
                  <p className="text-sm text-text-primary mt-2 whitespace-pre-wrap">
                    {problem.resolution_note}
                  </p>
                )}
              </div>
            )}

            {/* Vote Stats */}
            {voteStats && (
              <div>
                <h4 className="text-xs font-medium text-text-muted mb-2">Статистика голосов</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary flex items-center gap-2">
                      <ThumbsUp className="w-4 h-4 text-success" />
                      За правду
                    </span>
                    <span className="text-text-primary font-medium">{voteStats.true_count || 0}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary flex items-center gap-2">
                      <XCircle className="w-4 h-4 text-danger" />
                      За фейк
                    </span>
                    <span className="text-text-primary font-medium">{voteStats.fake_count || 0}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-text-secondary">Всего голосов</span>
                    <span className="text-text-primary font-medium">{voteStats.total_votes || 0}</span>
                  </div>
                </div>
              </div>
            )}

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

            {/* Priority Score */}
            {problem.priority_score !== undefined && (
              <div>
                <h4 className="text-xs font-medium text-text-muted mb-2">Приоритет</h4>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-dark-hover rounded-full overflow-hidden">
                    <div
                      className="h-full bg-warning transition-all"
                      style={{ width: `${problem.priority_score * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-text-primary">
                    {problem.priority_score.toFixed(2)}
                  </span>
                </div>
              </div>
            )}

            {/* Author */}
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Автор</h4>
              <div className="flex items-center gap-2">
                <UserName
                  userId={problem.author_entity_id}
                  showAvatar
                  className="text-sm font-medium hover:text-primary transition-colors"
                />
              </div>
              {author?.reputation !== undefined && (
                <p className="text-xs text-text-muted mt-2">
                  Репутация: {author.reputation.toFixed(0)}
                </p>
              )}
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

            {/* Nature */}
            {problem.nature && (
              <div>
                <h4 className="text-xs font-medium text-text-muted mb-2">Характер</h4>
                <span className="badge bg-warning/20 text-warning">
                  {problem.nature === 'temporary' ? 'Временная' :
                   problem.nature === 'permanent' ? 'Постоянная' : problem.nature}
                </span>
              </div>
            )}

            {/* Zone */}
            {problem.zone_entity_id && (
              <div>
                <h4 className="text-xs font-medium text-text-muted mb-2">Зона</h4>
                <p className="text-sm text-text-primary">ID: {problem.zone_entity_id}</p>
              </div>
            )}

            {/* Stats */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Комментарии
                </span>
                <span className="text-text-primary">{problem.comment_count || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted flex items-center gap-2">
                  <ThumbsUp className="w-4 h-4" />
                  Голоса
                </span>
                <span className="text-text-primary">{problem.vote_count || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-text-muted flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Создано
                </span>
                <span className="text-text-primary">
                  {formatDistanceToNow(new Date(problem.created_at!), {
                    addSuffix: true,
                    locale: ru,
                  })}
                </span>
              </div>
            </div>

            {/* History Timeline */}
            <div>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="flex items-center gap-2 text-sm font-medium text-text-primary hover:text-primary transition-colors w-full"
              >
                <History className="w-4 h-4" />
                История изменений
                <ChevronRight className={`w-4 h-4 ml-auto transition-transform ${showHistory ? 'rotate-90' : ''}`} />
              </button>

              {showHistory && (
                <div className="mt-4">
                  {historyLoading ? (
                    <div className="flex justify-center py-4">
                      <Loader2 className="w-6 h-6 text-primary animate-spin" />
                    </div>
                  ) : history && history.length > 0 ? (
                    <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                      {history.map((item, idx) => {
                        const isLatest = idx === 0
                        const statusChanged = idx < history.length - 1 && item.status !== history[idx + 1].status

                        return (
                          <div key={idx} className="relative pl-6 pb-4 border-l-2 border-border last:border-l-0 last:pb-0">
                            <div className={`absolute left-0 top-0 -translate-x-1/2 w-3 h-3 rounded-full border-2 border-dark-card ${
                              isLatest ? 'bg-primary animate-pulse' : 'bg-text-muted'
                            }`} />
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                isLatest ? 'bg-primary/20 text-primary' : 'bg-dark-hover text-text-muted'
                              }`}>
                                v{item.version}
                              </span>
                              {isLatest && (
                                <span className="text-xs text-success font-medium">Текущая</span>
                              )}
                            </div>
                            <div className="text-xs text-text-muted mb-2">
                              {new Date(item.created_at!).toLocaleString('ru-RU', {
                                day: 'numeric',
                                month: 'long',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                              {' '}
                              <span className="text-text-muted/60">
                                ({formatDistanceToNow(new Date(item.created_at!), {
                                  addSuffix: true,
                                  locale: ru,
                                })})
                              </span>
                            </div>
                            {statusChanged && (
                              <div className="mb-2 flex items-center gap-2 text-xs">
                                <div className="flex items-center gap-1 px-2 py-1 bg-warning/10 border border-warning/30 rounded">
                                  <TrendingUp className="w-3 h-3 text-warning" />
                                  <span className="text-warning font-medium">
                                    Статус: {history[idx + 1].status} → {item.status}
                                  </span>
                                </div>
                              </div>
                            )}
                            {item.change_reason && (
                              <div className="text-sm text-text-primary bg-dark-hover/50 rounded-lg p-2 border border-border">
                                <p className="text-xs text-text-muted mb-1">Причина изменения:</p>
                                <p>{item.change_reason}</p>
                              </div>
                            )}
                            <div className="mt-2 text-xs text-text-secondary space-y-1">
                              <div className="flex items-center gap-2">
                                <span className="text-text-muted">Статус:</span>
                                <span className={`badge text-xs ${
                                  item.status === 'solved' ? 'badge-resolved' :
                                  item.status === 'in_progress' ? 'badge-in-progress' :
                                  item.status === 'rejected' ? 'badge-rejected' : 'badge-pending'
                                }`}>
                                  {item.status === 'solved' ? 'Решена' :
                                   item.status === 'in_progress' ? 'В работе' :
                                   item.status === 'rejected' ? 'Отклонена' :
                                   item.status === 'open' ? 'Открыта' : item.status}
                                </span>
                              </div>
                              {item.priority_score !== undefined && (
                                <div className="flex items-center gap-2">
                                  <span className="text-text-muted">Приоритет:</span>
                                  <span className="font-medium">{item.priority_score.toFixed(2)}</span>
                                </div>
                              )}
                              {item.truth_score !== undefined && (
                                <div className="flex items-center gap-2">
                                  <span className="text-text-muted">Достоверность:</span>
                                  <span className="font-medium">{Math.round(item.truth_score * 100)}%</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="text-center py-6 bg-dark-hover/30 rounded-lg border border-border">
                      <History className="w-8 h-8 text-text-muted mx-auto mb-2" />
                      <p className="text-xs text-text-muted">История изменений пуста</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Comments Section */}
          <div className="p-6 pb-20 lg:pb-6">
            <h3 className="text-lg font-semibold text-text-primary mb-4">
              Комментарии ({comments?.length || 0})
            </h3>

            {/* Comment Input */}
            {isAuthenticated ? (
              <div className="mb-6">
                {replyTo && (
                  <div className="mb-2 flex items-center gap-2 text-sm bg-primary/10 border border-primary/30 rounded-lg p-3">
                    <MessageSquare className="w-4 h-4 text-primary" />
                    <span className="text-text-primary">
                      Ответ на комментарий от{' '}
                      <span className="font-semibold">
                        <UserName userId={comments?.find(c => c.entity_id === replyTo)?.author_entity_id || 0} />
                      </span>
                    </span>
                    <button
                      onClick={handleCancelReply}
                      className="text-danger hover:underline ml-auto font-medium"
                    >
                      Отменить
                    </button>
                  </div>
                )}
                <textarea
                  placeholder={replyTo ? "Напишите ответ..." : "Добавить комментарий..."}
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  className="input w-full min-h-[80px] resize-none"
                  disabled={createCommentMutation.isPending}
                />
                <div className="flex justify-end mt-3">
                  <button
                    onClick={handleSubmitComment}
                    disabled={!commentText.trim() || createCommentMutation.isPending}
                    className="btn-primary hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {createCommentMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Отправка...
                      </>
                    ) : (
                      'Отправить'
                    )}
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
                {comments
                  .filter((c) => !c.parent_entity_id) // Top-level comments only
                  .map((comment) => (
                    <CommentItem
                      key={comment.entity_id}
                      comment={comment}
                      onReply={handleReply}
                      onReport={(commentId, authorId) =>
                        handleOpenReportModal(
                          'comment',
                          commentId,
                          `Комментарий от ID: ${authorId}`
                        )
                      }
                      isAuthenticated={isAuthenticated}
                    />
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

      {/* Right side - Info Panel (Desktop only) */}
      <div className="hidden lg:block w-96 border-l border-border overflow-y-auto bg-dark-card">
        <div className="p-6 space-y-6">
          {/* Mini Map */}
          <div className="lg:block">
            <h4 className="text-xs font-medium text-text-muted mb-2">Местоположение</h4>
            {problem.latitude && problem.longitude ? (
              <div className="space-y-3">
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

                {/* Координаты */}
                <div className="flex items-center gap-2 text-xs text-text-muted">
                  <MapPin className="w-3 h-3" />
                  <span>{problem.latitude.toFixed(6)}, {problem.longitude.toFixed(6)}</span>
                </div>

                {/* Ссылки */}
                <div className="flex gap-2">
                  <Link
                    to={`/map?lat=${problem.latitude}&lng=${problem.longitude}&zoom=16`}
                    className="flex-1 btn-ghost text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95"
                  >
                    <Navigation className="w-4 h-4" />
                    <span>Открыть на карте</span>
                  </Link>
                  <a
                    href={`https://2gis.ru/geo/${problem.longitude},${problem.latitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 btn-ghost text-sm flex items-center justify-center gap-2 hover:scale-105 active:scale-95"
                  >
                    <ExternalLink className="w-4 h-4" />
                    <span>2GIS</span>
                  </a>
                </div>
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

          {/* Resolution Info */}
          {problem.status === 'solved' && problem.resolved_at && (
            <div className="bg-success/10 border border-success/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-success" />
                <h4 className="text-sm font-semibold text-success">Проблема решена</h4>
              </div>
              <p className="text-xs text-text-secondary mb-2">
                {formatDistanceToNow(new Date(problem.resolved_at), {
                  addSuffix: true,
                  locale: ru,
                })}
              </p>
              {problem.resolution_note && (
                <p className="text-sm text-text-primary mt-2 whitespace-pre-wrap">
                  {problem.resolution_note}
                </p>
              )}
            </div>
          )}

          {/* Vote Stats */}
          {voteStats && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Статистика голосов</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary flex items-center gap-2">
                    <ThumbsUp className="w-4 h-4 text-success" />
                    За правду
                  </span>
                  <span className="text-text-primary font-medium">{voteStats.true_count || 0}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-danger" />
                    За фейк
                  </span>
                  <span className="text-text-primary font-medium">{voteStats.fake_count || 0}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Всего голосов</span>
                  <span className="text-text-primary font-medium">{voteStats.total_votes || 0}</span>
                </div>
              </div>

              {/* Информация о правилах голосования */}
              <div className="mt-3 px-3 py-2 bg-dark-hover rounded-lg text-xs text-text-muted">
                <p className="mb-1">ℹ️ Правила голосования:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Голос можно изменить один раз</li>
                  <li>После изменения повторное изменение невозможно</li>
                  <li>Голос можно полностью отменить</li>
                </ul>
              </div>
            </div>
          )}

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

          {/* Priority Score */}
          {problem.priority_score !== undefined && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Приоритет</h4>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 bg-dark-hover rounded-full overflow-hidden">
                  <div
                    className="h-full bg-warning transition-all"
                    style={{ width: `${problem.priority_score * 100}%` }}
                  />
                </div>
                <span className="text-sm text-text-primary">
                  {problem.priority_score.toFixed(2)}
                </span>
              </div>
            </div>
          )}

          {/* Author */}
          <div>
            <h4 className="text-xs font-medium text-text-muted mb-2">Автор</h4>
            <div className="flex items-center gap-2">
              <UserName
                userId={problem.author_entity_id}
                showAvatar
                className="text-sm font-medium hover:text-primary transition-colors"
              />
            </div>
            {author?.reputation !== undefined && (
              <p className="text-xs text-text-muted mt-2">
                Репутация: {author.reputation.toFixed(0)}
              </p>
            )}
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

          {/* Nature */}
          {problem.nature && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Характер</h4>
              <span className="badge bg-warning/20 text-warning">
                {problem.nature === 'temporary' ? 'Временная' :
                 problem.nature === 'permanent' ? 'Постоянная' : problem.nature}
              </span>
            </div>
          )}

          {/* Zone */}
          {problem.zone_entity_id && (
            <div>
              <h4 className="text-xs font-medium text-text-muted mb-2">Зона</h4>
              <p className="text-sm text-text-primary">ID: {problem.zone_entity_id}</p>
            </div>
          )}

          {/* Stats */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-muted flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Комментарии
              </span>
              <span className="text-text-primary">{problem.comment_count || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-muted flex items-center gap-2">
                <ThumbsUp className="w-4 h-4" />
                Голоса
              </span>
              <span className="text-text-primary">{problem.vote_count || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-text-muted flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Создано
              </span>
              <span className="text-text-primary">
                {formatDistanceToNow(new Date(problem.created_at!), {
                  addSuffix: true,
                  locale: ru,
                })}
              </span>
            </div>
          </div>

          {/* History Timeline */}
          <div>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center gap-2 text-sm font-medium text-text-primary hover:text-primary transition-colors w-full"
            >
              <History className="w-4 h-4" />
              История изменений
              <ChevronRight className={`w-4 h-4 ml-auto transition-transform ${showHistory ? 'rotate-90' : ''}`} />
            </button>

            {showHistory && (
              <div className="mt-4">
                {historyLoading ? (
                  <div className="flex justify-center py-4">
                    <Loader2 className="w-6 h-6 text-primary animate-spin" />
                  </div>
                ) : history && history.length > 0 ? (
                  <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                    {history
                      .filter((item, idx) => {
                        // Always show the first (latest) version
                        if (idx === 0) return true

                        // Filter out versions where only comment_count or vote_count changed
                        const prev = history[idx - 1]
                        const hasSignificantChange =
                          item.status !== prev.status ||
                          item.title !== prev.title ||
                          item.description !== prev.description ||
                          item.priority_score !== prev.priority_score ||
                          item.truth_score !== prev.truth_score ||
                          item.urgency_score !== prev.urgency_score

                        return hasSignificantChange
                      })
                      .map((item, idx, filteredArray) => {
                        const isLatest = idx === 0
                        const statusChanged = idx < filteredArray.length - 1 && item.status !== filteredArray[idx + 1].status

                      return (
                        <div key={idx} className="relative pl-6 pb-4 border-l-2 border-border last:border-l-0 last:pb-0">
                          {/* Timeline dot */}
                          <div className={`absolute left-0 top-0 -translate-x-1/2 w-3 h-3 rounded-full border-2 border-dark-card ${
                            isLatest ? 'bg-primary animate-pulse' : 'bg-text-muted'
                          }`} />

                          {/* Version badge */}
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                              isLatest ? 'bg-primary/20 text-primary' : 'bg-dark-hover text-text-muted'
                            }`}>
                              v{item.version}
                            </span>
                            {isLatest && (
                              <span className="text-xs text-success font-medium">Текущая</span>
                            )}
                          </div>

                          {/* Timestamp */}
                          <div className="text-xs text-text-muted mb-2">
                            {new Date(item.created_at!).toLocaleString('ru-RU', {
                              day: 'numeric',
                              month: 'long',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                            {' '}
                            <span className="text-text-muted/60">
                              ({formatDistanceToNow(new Date(item.created_at!), {
                                addSuffix: true,
                                locale: ru,
                              })})
                            </span>
                          </div>

                          {/* Status change indicator */}
                          {statusChanged && (
                            <div className="mb-2 flex items-center gap-2 text-xs">
                              <div className="flex items-center gap-1 px-2 py-1 bg-warning/10 border border-warning/30 rounded">
                                <TrendingUp className="w-3 h-3 text-warning" />
                                <span className="text-warning font-medium">
                                  Статус: {history[idx + 1].status} → {item.status}
                                </span>
                              </div>
                            </div>
                          )}

                          {/* Change reason */}
                          {item.change_reason && (
                            <div className="text-sm text-text-primary bg-dark-hover/50 rounded-lg p-2 border border-border">
                              <p className="text-xs text-text-muted mb-1">Причина изменения:</p>
                              <p>{item.change_reason}</p>
                            </div>
                          )}

                          {/* Problem details snapshot */}
                          <div className="mt-2 text-xs text-text-secondary space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-text-muted">Статус:</span>
                              <span className={`badge text-xs ${
                                item.status === 'solved' ? 'badge-resolved' :
                                item.status === 'in_progress' ? 'badge-in-progress' :
                                item.status === 'rejected' ? 'badge-rejected' : 'badge-pending'
                              }`}>
                                {item.status === 'solved' ? 'Решена' :
                                 item.status === 'in_progress' ? 'В работе' :
                                 item.status === 'rejected' ? 'Отклонена' :
                                 item.status === 'open' ? 'Открыта' : item.status}
                              </span>
                            </div>
                            {item.priority_score !== undefined && (
                              <div className="flex items-center gap-2">
                                <span className="text-text-muted">Приоритет:</span>
                                <span className="font-medium">{item.priority_score.toFixed(2)}</span>
                              </div>
                            )}
                            {item.truth_score !== undefined && (
                              <div className="flex items-center gap-2">
                                <span className="text-text-muted">Достоверность:</span>
                                <span className="font-medium">{Math.round(item.truth_score * 100)}%</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                ) : (
                  <div className="text-center py-6 bg-dark-hover/30 rounded-lg border border-border">
                    <History className="w-8 h-8 text-text-muted mx-auto mb-2" />
                    <p className="text-xs text-text-muted">История изменений пуста</p>
                  </div>
                )}
              </div>
            )}
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

      {/* Edit Form Modal */}
      <ProblemEditForm
        isOpen={isEditFormOpen}
        onClose={() => setIsEditFormOpen(false)}
        onSuccess={() => {
          setIsEditFormOpen(false)
          // Problem data will be automatically refetched by React Query
        }}
        problem={problem}
      />
    </div>
  )
}
