import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { MapPin, ThumbsUp, MessageCircle, Eye, Clock, Search, Filter, X } from 'lucide-react'
import { useInfiniteProblems } from '../hooks/useProblems'
import { useProblemMedia } from '../hooks/useMedia'
import type { IntersectionObserverEntry } from 'react-dom'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { ProblemPublic } from '../api/generated/models/ProblemPublic'

interface ProblemCardProps {
  problem: ProblemPublic
}

function ProblemCard({ problem }: ProblemCardProps) {
  const navigate = useNavigate()
  const [currentMediaIndex, setCurrentMediaIndex] = useState(0)

  // Загружаем медиа для этой проблемы
  const { data: media, isLoading: mediaLoading } = useProblemMedia(problem.entity_id)

  // Filter only photos
  const photos = media?.filter(m => m.media_type === 'photo') || []
  
  // Only media carousel (no map)
  const totalItems = photos.length

  useEffect(() => {
    if (totalItems <= 1) return

    const interval = setInterval(() => {
      setCurrentMediaIndex((prev) => (prev + 1) % totalItems)
    }, 2000)

    return () => clearInterval(interval)
  }, [totalItems])

  const currentMedia = photos[currentMediaIndex]

  return (
    <div
      onClick={() => navigate(`/problems/${problem.entity_id}`)}
      className="bg-dark-card rounded-xl overflow-hidden hover:ring-2 hover:ring-primary/50 transition-all cursor-pointer group"
    >
      {/* Thumbnail / Media Carousel */}
      <div className="relative aspect-video bg-dark-hover overflow-hidden">
        {mediaLoading ? (
          <div className="w-full h-full flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : photos.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center bg-dark-hover">
            <MapPin className="w-12 h-12 text-text-muted" />
          </div>
        ) : (
          <>
            {currentMedia.media_type === 'photo' ? (
              <img
                src={currentMedia.url}
                alt={problem.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <video
                src={currentMedia.url}
                className="w-full h-full object-cover"
                muted
                playsInline
              />
            )}
          </>
        )}

        {/* Carousel Indicators */}
        {totalItems > 1 && (
          <div className="absolute bottom-2 right-2 flex gap-1">
            {Array.from({ length: totalItems }).map((_, idx) => (
              <div
                key={idx}
                className={`h-1 rounded-full transition-all ${
                  idx === currentMediaIndex
                    ? 'w-4 bg-primary'
                    : 'w-1 bg-white/50'
                }`}
              />
            ))}
          </div>
        )}

        {/* Status Badge */}
        <div className="absolute top-2 left-2">
          <span
            className={`badge text-xs ${
              problem.status === 'resolved'
                ? 'badge-resolved'
                : problem.status === 'in_progress'
                ? 'badge-in-progress'
                : 'badge-pending'
            }`}
          >
            {problem.status === 'resolved'
              ? 'Решена'
              : problem.status === 'in_progress'
              ? 'В работе'
              : 'Новая'}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="text-text-primary font-semibold mb-2 line-clamp-2 group-hover:text-primary transition-colors">
          {problem.title}
        </h3>

        {/* Location */}
        <div className="flex items-center gap-1 text-sm text-text-secondary mb-3">
          <MapPin className="w-4 h-4" />
          <span className="truncate">{problem.address || problem.city}</span>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-4 text-sm text-text-muted">
          <div className="flex items-center gap-1" title="Голоса">
            <ThumbsUp className="w-4 h-4" />
            <span>{problem.vote_count || 0}</span>
          </div>
          <div className="flex items-center gap-1" title="Комментарии">
            <MessageCircle className="w-4 h-4" />
            <span>{problem.comment_count || 0}</span>
          </div>
          <div className="flex items-center gap-1" title="Приоритет">
            <Eye className="w-4 h-4" />
            <span>{problem.priority_score?.toFixed(1) || '0.0'}</span>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
              <span className="text-xs text-primary font-semibold">
                {problem.author?.username?.[0]?.toUpperCase() || 'A'}
              </span>
            </div>
            <span className="text-xs text-text-secondary">
              {problem.author?.username || 'Аноним'}
            </span>
          </div>
          <div className="flex items-center gap-1 text-xs text-text-muted">
            <Clock className="w-3 h-3" />
            {formatDistanceToNow(new Date(problem.created_at), {
              addSuffix: true,
              locale: ru,
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ProblemsPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()

  // Get filters from URL
  const statusFilter = searchParams.get('status')
  const categoryFilter = searchParams.get('category')
  const sortFilter = searchParams.get('sort') || 'newest'
  const countryFilter = searchParams.get('country')
  const cityFilter = searchParams.get('city')
  const districtFilter = searchParams.get('district')
  const natureFilter = searchParams.get('nature')

  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  const { data: problemsData, isLoading, hasNextPage, fetchNextPage } = useInfiniteProblems({
    status: statusFilter || undefined,
    problemType: categoryFilter || undefined,
  })
  const problems = problemsData?.pages.flatMap(page => page.items) || []

  // Get unique values for filters
  const uniqueCountries = Array.from(new Set(problems.map(p => p.country).filter(Boolean)))
  const uniqueCities = Array.from(new Set(problems.map(p => p.city).filter(Boolean)))
  const uniqueDistricts = Array.from(new Set(problems.map(p => p.district).filter(Boolean)))

  // Calculate total for display
  const total = problemsData?.pages[0]?.total || 0

  // Infinite scroll observer
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const [target] = entries
    if (target.isIntersecting && hasNextPage && !isLoading) {
      fetchNextPage()
    }
  }, [hasNextPage, fetchNextPage, isLoading])

  useEffect(() => {
    const element = loadMoreRef.current
    if (!element) return

    const observer = new IntersectionObserver(handleObserver, {
      threshold: 0.1,
    })

    observer.observe(element)
    return () => observer.disconnect()
  }, [handleObserver])

  // Client-side filtering
  let filteredProblems = problems

  // Filter by country
  if (countryFilter) {
    filteredProblems = filteredProblems.filter(p => p.country === countryFilter)
  }

  // Filter by city
  if (cityFilter) {
    filteredProblems = filteredProblems.filter(p => p.city === cityFilter)
  }

  // Filter by district
  if (districtFilter) {
    filteredProblems = filteredProblems.filter(p => p.district === districtFilter)
  }

  // Filter by nature
  if (natureFilter) {
    filteredProblems = filteredProblems.filter(p => p.nature === natureFilter)
  }

  // Filter by search query
  if (searchQuery) {
    filteredProblems = filteredProblems.filter(
      (p) =>
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.address?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }

  // Update URL params
  const updateFilter = (key: string, value: string | null) => {
    const newParams = new URLSearchParams(searchParams)
    if (value) {
      newParams.set(key, value)
    } else {
      newParams.delete(key)
    }
    setSearchParams(newParams)
  }

  // Clear all filters
  const clearFilters = () => {
    setSearchParams({})
    setSearchQuery('')
  }

  // Get filter label for header
  const getFilterLabel = () => {
    const parts = []
    if (statusFilter) {
      const labels: Record<string, string> = {
        pending: 'Новые',
        in_progress: 'В работе',
        resolved: 'Решенные',
        rejected: 'Отклоненные'
      }
      parts.push(labels[statusFilter])
    }
    if (categoryFilter) parts.push(categoryFilter)
    if (cityFilter) parts.push(cityFilter)
    if (districtFilter) parts.push(districtFilter)

    return parts.length > 0 ? parts.join(' · ') + ' проблемы' : 'Все проблемы'
  }

  const hasActiveFilters = statusFilter || categoryFilter || sortFilter !== 'newest' ||
                          countryFilter || cityFilter || districtFilter || natureFilter

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex gap-6">
          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-text-primary mb-2">{getFilterLabel()}</h1>
              <p className="text-text-secondary">
                {total} {total === 1 ? 'проблема' : 'проблем'} найдено
              </p>
            </div>

            {/* Search */}
            <div className="mb-6 flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
                <input
                  type="text"
                  placeholder="Поиск проблем..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input w-full pl-10"
                />
              </div>

              {/* Mobile Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="btn btn-secondary lg:hidden flex items-center gap-2"
              >
                <Filter className="w-5 h-5" />
                {hasActiveFilters && <span className="w-2 h-2 bg-primary rounded-full" />}
              </button>
            </div>

            {/* Mobile Filters */}
            {showFilters && (
              <div className="lg:hidden mb-6 bg-dark-card rounded-xl p-4 border border-border space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-text-primary">Фильтры</h3>
                  <button onClick={() => setShowFilters(false)}>
                    <X className="w-5 h-5 text-text-muted" />
                  </button>
                </div>
                {/* Filters content - same as sidebar */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">Статус</label>
                    <select
                      value={statusFilter || ''}
                      onChange={(e) => updateFilter('status', e.target.value || null)}
                      className="input w-full"
                    >
                      <option value="">Все</option>
                      <option value="pending">Новые</option>
                      <option value="in_progress">В работе</option>
                      <option value="resolved">Решенные</option>
                      <option value="rejected">Отклоненные</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-text-secondary mb-2">Категория</label>
                    <select
                      value={categoryFilter || ''}
                      onChange={(e) => updateFilter('category', e.target.value || null)}
                      className="input w-full"
                    >
                      <option value="">Все</option>
                      <option value="roads">Дороги</option>
                      <option value="lighting">Освещение</option>
                      <option value="garbage">Мусор</option>
                      <option value="infrastructure">Инфраструктура</option>
                      <option value="pollution">Загрязнение</option>
                      <option value="construction">Строительство</option>
                      <option value="flooding">Затопление</option>
                      <option value="traffic_light">Светофоры</option>
                      <option value="pothole">Ямы</option>
                      <option value="other">Другое</option>
                    </select>
                  </div>
                  {hasActiveFilters && (
                    <button onClick={clearFilters} className="btn btn-secondary w-full">
                      <X className="w-4 h-4 mr-2" />
                      Сбросить
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Grid */}
            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                {Array.from({ length: 9 }).map((_, i) => (
                  <div key={i} className="bg-dark-card rounded-xl overflow-hidden animate-pulse">
                    <div className="aspect-video bg-dark-hover" />
                    <div className="p-4 space-y-3">
                      <div className="h-4 bg-dark-hover rounded w-3/4" />
                      <div className="h-3 bg-dark-hover rounded w-1/2" />
                      <div className="h-3 bg-dark-hover rounded w-full" />
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredProblems.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-text-secondary text-lg">Проблемы не найдены</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredProblems.map((problem) => (
                    <ProblemCard key={problem.entity_id} problem={problem} />
                  ))}
                </div>
                <div ref={loadMoreRef} className="h-10 flex items-center justify-center">
                  {isLoading && (
                    <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                  )}
                </div>
              </>
            )}
          </div>

          {/* Sidebar Filters (Desktop) */}
          <div className="hidden lg:block w-80 flex-shrink-0">
            <div className="sticky top-24 bg-dark-card rounded-xl p-6 border border-border space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-text-primary">Фильтры</h3>
                {hasActiveFilters && (
                  <button
                    onClick={clearFilters}
                    className="text-sm text-primary hover:text-primary/80 flex items-center gap-1"
                  >
                    <X className="w-4 h-4" />
                    Сбросить
                  </button>
                )}
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Статус
                </label>
                <select
                  value={statusFilter || ''}
                  onChange={(e) => updateFilter('status', e.target.value || null)}
                  className="input w-full"
                >
                  <option value="">Все статусы</option>
                  <option value="pending">Новые</option>
                  <option value="in_progress">В работе</option>
                  <option value="resolved">Решенные</option>
                  <option value="rejected">Отклоненные</option>
                </select>
              </div>

              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Категория
                </label>
                <select
                  value={categoryFilter || ''}
                  onChange={(e) => updateFilter('category', e.target.value || null)}
                  className="input w-full"
                >
                  <option value="">Все категории</option>
                  <option value="roads">Дороги</option>
                  <option value="lighting">Освещение</option>
                  <option value="garbage">Мусор</option>
                  <option value="infrastructure">Инфраструктура</option>
                  <option value="pollution">Загрязнение</option>
                  <option value="construction">Строительство</option>
                  <option value="flooding">Затопление</option>
                  <option value="traffic_light">Светофоры</option>
                  <option value="pothole">Ямы</option>
                  <option value="other">Другое</option>
                </select>
              </div>

              {/* Sort */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Сортировка
                </label>
                <select
                  value={sortFilter}
                  onChange={(e) => updateFilter('sort', e.target.value)}
                  className="input w-full"
                >
                  <option value="newest">Сначала новые</option>
                  <option value="oldest">Сначала старые</option>
                  <option value="most_voted">Больше голосов</option>
                  <option value="most_commented">Больше комментариев</option>
                  <option value="priority">По приоритету</option>
                </select>
              </div>

              {/* Country */}
              {uniqueCountries.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Страна
                  </label>
                  <select
                    value={countryFilter || ''}
                    onChange={(e) => updateFilter('country', e.target.value || null)}
                    className="input w-full"
                  >
                    <option value="">Все страны</option>
                    {uniqueCountries.map(country => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* City */}
              {uniqueCities.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Город
                  </label>
                  <select
                    value={cityFilter || ''}
                    onChange={(e) => updateFilter('city', e.target.value || null)}
                    className="input w-full"
                  >
                    <option value="">Все города</option>
                    {uniqueCities.map(city => (
                      <option key={city} value={city}>{city}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* District */}
              {uniqueDistricts.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-text-secondary mb-2">
                    Район
                  </label>
                  <select
                    value={districtFilter || ''}
                    onChange={(e) => updateFilter('district', e.target.value || null)}
                    className="input w-full"
                  >
                    <option value="">Все районы</option>
                    {uniqueDistricts.map(district => (
                      <option key={district} value={district}>{district}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Nature */}
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  Характер
                </label>
                <select
                  value={natureFilter || ''}
                  onChange={(e) => updateFilter('nature', e.target.value || null)}
                  className="input w-full"
                >
                  <option value="">Все типы</option>
                  <option value="complaint">Жалоба</option>
                  <option value="suggestion">Предложение</option>
                  <option value="question">Вопрос</option>
                  <option value="emergency">Срочно</option>
                </select>
              </div>

              {/* Active Filters */}
              {hasActiveFilters && (
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-text-muted mb-2">Активные:</p>
                  <div className="flex flex-wrap gap-2">
                    {statusFilter && (
                      <span className="badge badge-primary text-xs">{statusFilter}</span>
                    )}
                    {categoryFilter && (
                      <span className="badge badge-primary text-xs">{categoryFilter}</span>
                    )}
                    {cityFilter && (
                      <span className="badge badge-primary text-xs">{cityFilter}</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
