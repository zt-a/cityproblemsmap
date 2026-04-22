import { useState, useEffect, useRef, useCallback } from 'react'
import { Search, SlidersHorizontal, X, Loader2, ChevronDown } from 'lucide-react'
import ProblemCard from './ProblemCard'
import { useAllProblems, useProblem } from '../../hooks/useProblems'
import type { ProblemStatus } from '../../api/generated/models/ProblemStatus'
import type { ProblemPublic } from '../../api/generated/models/ProblemPublic'
import type { IntersectionObserverEntry } from 'react-dom'

interface ProblemListProps {
  selectedProblemId: number | null
  onCardClick: (id: number, lat: number, lng: number) => void
  onClose: () => void
}

const STATUS_OPTIONS: { label: string; value: ProblemStatus | undefined }[] = [
  { label: 'Все', value: undefined },
  { label: 'Новые', value: 'pending' as ProblemStatus },
  { label: 'В работе', value: 'in_progress' as ProblemStatus },
  { label: 'Решённые', value: 'resolved' as ProblemStatus },
]

const TYPE_OPTIONS = [
  { label: 'Все типы', value: '' },
  { label: 'Яма на дороге', value: 'pothole' },
  { label: 'Мусор', value: 'garbage' },
  { label: 'Дорожные работы', value: 'road_work' },
  { label: 'Загрязнение', value: 'pollution' },
  { label: 'Светофор', value: 'traffic_light' },
  { label: 'Затопление', value: 'flooding' },
  { label: 'Освещение', value: 'lighting' },
  { label: 'Строительство', value: 'construction' },
  { label: 'Дороги', value: 'roads' },
  { label: 'Инфраструктура', value: 'infrastructure' },
  { label: 'Другое', value: 'other' },
]

export default function ProblemList({ selectedProblemId, onCardClick, onClose }: ProblemListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [statusFilter, setStatusFilter] = useState<ProblemStatus | undefined>(undefined)
  const [cityFilter, setCityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const cardRefs = useRef<Record<number, HTMLDivElement | null>>({})
  const listRef = useRef<HTMLDivElement>(null)
  const loadMoreRef = useRef<HTMLDivElement>(null)

  const { data: problemsData, isLoading, error, hasNextPage, fetchNextPage } = useAllProblems({
    ...(statusFilter && { status: statusFilter }),
    ...(cityFilter.trim() && { city: cityFilter.trim() }),
    ...(typeFilter && { problemType: typeFilter }),
  })
  const problems: ProblemPublic[] = problemsData?.items || []

  // Fetch problem if not in list
  const { data: singleProblem, isLoading: isLoadingSingle } = useProblem(
    selectedProblemId && !problems.find(p => p.entity_id === selectedProblemId)
      ? selectedProblemId
      : null
  )

  // Add single problem to list temporarily for display
  const displayProblems = problems.concat(
    singleProblem && selectedProblemId && !problems.find(p => p.entity_id === singleProblem.entity_id)
      ? [singleProblem]
      : []
  )

  // Client-side search on top of server-side filters
  const filteredProblems = searchQuery.trim()
    ? displayProblems.filter(
        (p) =>
          p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.description.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : displayProblems

  // Scroll to active card whenever selectedProblemId changes
  useEffect(() => {
    if (selectedProblemId == null) return
    
    // Wait for single problem to load if it's being fetched
    const checkAndScroll = () => {
      const el = cardRefs.current[selectedProblemId]
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        return true
      }
      return false
    }

    // If problem not in list yet and we're loading it, wait for it
    if (isLoadingSingle) {
      const timeout = setTimeout(checkAndScroll, 100)
      return () => clearTimeout(timeout)
    }

    checkAndScroll()
  }, [selectedProblemId, isLoadingSingle])

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

  const hasActiveFilters = !!statusFilter || !!cityFilter || !!typeFilter

  const clearFilters = () => {
    setStatusFilter(undefined)
    setCityFilter('')
    setTypeFilter('')
  }

  return (
    <div className="h-full flex flex-col bg-dark-bg md:overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-border space-y-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-text-primary">Проблемы</h2>
            {!isLoading && (
              <span className="text-xs text-text-muted bg-dark-hover px-2 py-0.5 rounded-full">
                {filteredProblems.length}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn-ghost p-2 relative ${showFilters ? 'text-primary' : ''}`}
            >
              <SlidersHorizontal className="w-5 h-5" />
              {hasActiveFilters && (
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
              )}
            </button>
            <button onClick={onClose} className="btn-ghost p-2" aria-label="Закрыть панель">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text"
            placeholder="Поиск проблем..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input w-full pl-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="space-y-3 pt-1">
            {/* Status */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Статус</label>
              <div className="flex gap-2 flex-wrap">
                {STATUS_OPTIONS.map((opt) => (
                  <button
                    key={String(opt.value)}
                    onClick={() => setStatusFilter(opt.value)}
                    className={`badge cursor-pointer transition-colors ${
                      statusFilter === opt.value
                        ? 'bg-primary/20 text-primary'
                        : 'bg-dark-hover text-text-secondary hover:bg-dark-input'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* City */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Город</label>
              <input
                type="text"
                placeholder="Например: Бишкек"
                value={cityFilter}
                onChange={(e) => setCityFilter(e.target.value)}
                className="input w-full text-sm"
              />
            </div>

            {/* Type */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Тип проблемы</label>
              <div className="relative">
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="input w-full text-sm appearance-none pr-8"
                >
                  {TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted pointer-events-none" />
              </div>
            </div>

            {/* Clear filters */}
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="text-sm text-primary hover:text-primary-hover flex items-center gap-1"
              >
                <X className="w-3.5 h-3.5" />
                Сбросить фильтры
              </button>
            )}
          </div>
        )}
      </div>

      {/* List */}
      <div ref={listRef} className="flex-1 p-4 space-y-3 md:overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-text-secondary mb-2">Ошибка загрузки</p>
            <p className="text-sm text-text-muted">{(error as any)?.message || 'Попробуйте позже'}</p>
          </div>
        ) : filteredProblems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-text-secondary">Проблемы не найдены</p>
            <p className="text-sm text-text-muted mt-1">Попробуйте изменить фильтры</p>
          </div>
        ) : (
          <>
            {filteredProblems.map((problem) => (
              <div
                key={problem.entity_id}
                ref={(el) => {
                  cardRefs.current[problem.entity_id] = el
                }}
              >
                <ProblemCard
                  problem={problem}
                  isActive={selectedProblemId === problem.entity_id}
                  onCardClick={() => onCardClick(problem.entity_id, problem.latitude, problem.longitude)}
                />
              </div>
            ))}
            <div ref={loadMoreRef} className="h-10 flex items-center justify-center">
              {isLoading && (
                <Loader2 className="w-6 h-6 text-primary animate-spin" />
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}