import { useState } from 'react'
import { Search, Filter, SlidersHorizontal, X, Loader2 } from 'lucide-react'
import ProblemCard from './ProblemCard'
import { useProblems, type ProblemFilters } from '../../hooks/useProblems'
import type { ProblemStatus } from '../../api/generated/models/ProblemStatus'
import type { ProblemPublic } from '../../api/generated/models/ProblemPublic'

interface ProblemListProps {
  selectedProblemId: number | null
  onCardClick: (id: number, lat: number, lng: number) => void
  onClose: () => void
}

export default function ProblemList({ selectedProblemId, onCardClick, onClose }: ProblemListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [statusFilter, setStatusFilter] = useState<ProblemStatus | undefined>(undefined)
  const [cityFilter, setCityFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')

  // Build filters
  const filters: ProblemFilters = {
    status: statusFilter,
    city: cityFilter || undefined,
    problemType: typeFilter || undefined,
    limit: 50,
  }

  // Load problems from API
  const { data: problemsData, isLoading, error } = useProblems(filters)

  // Convert API data to component format
  const problems: ProblemPublic[] = problemsData?.items || []

  // Filter by search query on client side (since API doesn't support search yet)
  const filteredProblems = searchQuery
    ? problems.filter(
        (p) =>
          p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : problems

  return (
    <div className="h-full flex flex-col bg-dark-bg md:overflow-hidden">
      {/* Header with filters */}
      <div className="p-4 border-b border-border space-y-3">
        {/* Title */}
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text-primary">Проблемы</h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-ghost p-2"
            >
              <SlidersHorizontal className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="btn-ghost p-2"
              aria-label="Закрыть панель"
            >
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
        </div>

        {/* Filters (collapsible) */}
        {showFilters && (
          <div className="space-y-3 pt-2">
            {/* Status Filter */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Статус</label>
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => setStatusFilter(undefined)}
                  className={`badge cursor-pointer ${
                    !statusFilter
                      ? 'bg-primary/20 text-primary hover:bg-primary/30'
                      : 'bg-dark-hover text-text-secondary hover:bg-dark-input'
                  }`}
                >
                  Все
                </button>
                <button
                  onClick={() => setStatusFilter('pending' as ProblemStatus)}
                  className={`badge cursor-pointer ${
                    statusFilter === 'pending'
                      ? 'bg-primary/20 text-primary hover:bg-primary/30'
                      : 'bg-dark-hover text-text-secondary hover:bg-dark-input'
                  }`}
                >
                  Новые
                </button>
                <button
                  onClick={() => setStatusFilter('in_progress' as ProblemStatus)}
                  className={`badge cursor-pointer ${
                    statusFilter === 'in_progress'
                      ? 'bg-primary/20 text-primary hover:bg-primary/30'
                      : 'bg-dark-hover text-text-secondary hover:bg-dark-input'
                  }`}
                >
                  В работе
                </button>
                <button
                  onClick={() => setStatusFilter('resolved' as ProblemStatus)}
                  className={`badge cursor-pointer ${
                    statusFilter === 'resolved'
                      ? 'bg-primary/20 text-primary hover:bg-primary/30'
                      : 'bg-dark-hover text-text-secondary hover:bg-dark-input'
                  }`}
                >
                  Решённые
                </button>
              </div>
            </div>

            {/* City Filter */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Город</label>
              <input
                type="text"
                placeholder="Например: Алматы"
                value={cityFilter}
                onChange={(e) => setCityFilter(e.target.value)}
                className="input w-full text-sm"
              />
            </div>

            {/* Type Filter */}
            <div>
              <label className="text-xs text-text-muted mb-2 block">Тип проблемы</label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="input w-full text-sm"
              >
                <option value="">Все типы</option>
                <option value="pothole">Яма на дороге</option>
                <option value="garbage">Мусор</option>
                <option value="road_work">Дорожные работы</option>
                <option value="pollution">Загрязнение</option>
                <option value="traffic_light">Светофор</option>
                <option value="flooding">Затопление</option>
                <option value="lighting">Освещение</option>
                <option value="construction">Строительство</option>
                <option value="roads">Дороги</option>
                <option value="infrastructure">Инфраструктура</option>
                <option value="other">Другое</option>
              </select>
            </div>

            {/* Clear Filters */}
            {(statusFilter || cityFilter || typeFilter) && (
              <button
                onClick={() => {
                  setStatusFilter(undefined)
                  setCityFilter('')
                  setTypeFilter('')
                }}
                className="text-sm text-primary hover:text-primary-hover"
              >
                Сбросить фильтры
              </button>
            )}
          </div>
        )}
      </div>

      {/* Problem list */}
      <div className="flex-1 p-4 space-y-3 md:overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-text-secondary mb-2">Ошибка загрузки проблем</p>
            <p className="text-sm text-text-muted">{(error as any)?.message || 'Попробуйте позже'}</p>
          </div>
        ) : filteredProblems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-text-secondary">Проблемы не найдены</p>
            <p className="text-sm text-text-muted mt-1">Попробуйте изменить фильтры</p>
          </div>
        ) : (
          filteredProblems.map((problem) => (
            <ProblemCard
              key={problem.entity_id}
              problem={problem}
              isActive={selectedProblemId === problem.entity_id}
              onCardClick={() => onCardClick(problem.entity_id, problem.latitude, problem.longitude)}
            />
          ))
        )}
      </div>
    </div>
  )
}
