import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  Users,
  MapPin,
  BarChart3,
  Activity,
  Zap
} from 'lucide-react'
import { useCityOverview, useCityTrend, useCityZones } from '../hooks/useAnalytics'
import { useAuth } from '../hooks/useAuth'

export default function AnalyticsPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const city = user?.city || 'Бишкек'

  const { data: overview, isLoading: overviewLoading } = useCityOverview(city)
  const { data: trend, isLoading: trendLoading } = useCityTrend(city, 30)
  const { data: zones, isLoading: zonesLoading } = useCityZones(city)

  const isLoading = overviewLoading || trendLoading || zonesLoading

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-text-primary">Загрузка аналитики...</div>
      </div>
    )
  }

  if (!overview) {
    return (
      <div className="min-h-screen bg-dark-bg flex items-center justify-center">
        <div className="text-text-secondary">Нет данных для города {city}</div>
      </div>
    )
  }

  // Calculate trends from trend data (compare oldest vs newest)
  const calculateTrend = (trendData: any[], field: 'new_problems' | 'solved' = 'new_problems') => {
    if (!trendData || trendData.length < 2) return null
    const oldValue = trendData[0]?.[field] || 0
    const newValue = trendData[trendData.length - 1]?.[field] || 0
    if (oldValue === 0) return null
    return Math.round(((newValue - oldValue) / oldValue) * 100)
  }

  const stats = [
    {
      title: 'Всего проблем',
      value: overview.total_problems,
      change: calculateTrend(trend || [], 'new_problems'),
      icon: <AlertCircle className="w-6 h-6" />,
      color: 'text-primary',
      link: '/problems',
    },
    {
      title: 'Новые',
      value: overview.status_distribution?.open || 0,
      change: calculateTrend(trend || [], 'new_problems'),
      icon: <Clock className="w-6 h-6" />,
      color: 'text-danger',
      link: '/problems?status=open',
    },
    {
      title: 'В работе',
      value: overview.status_distribution?.in_progress || 0,
      change: null,
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'text-warning',
      link: '/problems?status=in_progress',
    },
    {
      title: 'Решено',
      value: overview.status_distribution?.solved || 0,
      change: calculateTrend(trend || [], 'solved'),
      icon: <CheckCircle className="w-6 h-6" />,
      color: 'text-success',
      link: '/problems?status=solved',
    },
  ]

  const typeLabels: Record<string, string> = {
    pothole: 'Ямы на дорогах',
    garbage: 'Мусор',
    road_work: 'Дорожные работы',
    pollution: 'Загрязнение',
    traffic_light: 'Светофоры',
    flooding: 'Затопление',
    lighting: 'Освещение',
    construction: 'Строительство',
    roads: 'Дороги',
    infrastructure: 'Инфраструктура',
    other: 'Другое',
  }

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-2">
            Аналитика — {city}
          </h1>
          <p className="text-text-secondary">
            Статистика и анализ городских проблем
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div
              key={index}
              onClick={() => navigate(stat.link)}
              className="bg-dark-card rounded-xl p-6 border border-border hover:border-primary/50 transition-all cursor-pointer hover:scale-105 active:scale-95"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={stat.color}>{stat.icon}</div>
                {stat.change !== null && (
                  <div className="flex items-center gap-1 text-sm">
                    {stat.change > 0 ? (
                      <>
                        <TrendingUp className="w-4 h-4 text-success" />
                        <span className="text-success">+{stat.change}%</span>
                      </>
                    ) : stat.change < 0 ? (
                      <>
                        <TrendingDown className="w-4 h-4 text-danger" />
                        <span className="text-danger">{stat.change}%</span>
                      </>
                    ) : null}
                  </div>
                )}
              </div>
              <div>
                <p className="text-3xl font-bold text-text-primary mb-1">{stat.value}</p>
                <p className="text-sm text-text-secondary">{stat.title}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Problem Types Chart */}
          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <h3 className="text-lg font-semibold text-text-primary mb-6">
              Типы проблем
            </h3>
            <div className="space-y-4">
              {overview.by_type && overview.by_type
                .sort((a, b) => b.count - a.count)
                .slice(0, 8)
                .map((item) => {
                  const percentage = overview.total_problems > 0 ? (item.count / overview.total_problems) * 100 : 0
                  return (
                    <div key={item.problem_type}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-text-secondary">
                          {typeLabels[item.problem_type] || item.problem_type}
                        </span>
                        <span className="text-sm font-semibold text-text-primary">
                          {item.count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>

          {/* Status Distribution */}
          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <h3 className="text-lg font-semibold text-text-primary mb-6">
              Распределение по статусам
            </h3>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-danger/20 flex items-center justify-center">
                    <Clock className="w-6 h-6 text-danger" />
                  </div>
                  <div>
                    <p className="text-sm text-text-secondary">Новые</p>
                    <p className="text-2xl font-bold text-text-primary">
                      {overview.status_distribution?.open || 0}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-muted">
                    {overview.total_problems > 0
                      ? (((overview.status_distribution?.open || 0) / overview.total_problems) * 100).toFixed(1)
                      : '0'}%
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-warning/20 flex items-center justify-center">
                    <BarChart3 className="w-6 h-6 text-warning" />
                  </div>
                  <div>
                    <p className="text-sm text-text-secondary">В работе</p>
                    <p className="text-2xl font-bold text-text-primary">
                      {overview.status_distribution?.in_progress || 0}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-muted">
                    {overview.total_problems > 0
                      ? (((overview.status_distribution?.in_progress || 0) / overview.total_problems) * 100).toFixed(1)
                      : '0'}%
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-success" />
                  </div>
                  <div>
                    <p className="text-sm text-text-secondary">Решено</p>
                    <p className="text-2xl font-bold text-text-primary">
                      {overview.status_distribution?.solved || 0}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-text-muted">
                    {overview.total_problems > 0
                      ? (((overview.status_distribution?.solved || 0) / overview.total_problems) * 100).toFixed(1)
                      : '0'}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <div className="flex items-center gap-3 mb-2">
              <Activity className="w-5 h-5 text-primary" />
              <p className="text-sm text-text-secondary">Solve Rate</p>
            </div>
            <p className="text-3xl font-bold text-text-primary">
              {(overview.solve_rate * 100).toFixed(1)}%
            </p>
          </div>

          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <div className="flex items-center gap-3 mb-2">
              <MapPin className="w-5 h-5 text-primary" />
              <p className="text-sm text-text-secondary">Самая активная зона</p>
            </div>
            <p className="text-xl font-bold text-text-primary">
              {overview.most_active_zone || 'Нет данных'}
            </p>
          </div>

          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-primary" />
              <p className="text-sm text-text-secondary">Всего зон</p>
            </div>
            <p className="text-3xl font-bold text-text-primary">
              {zones?.length || 0}
            </p>
          </div>
        </div>

        {/* Top Zones */}
        {zones && zones.length > 0 && (
          <div className="bg-dark-card rounded-xl p-6 border border-border">
            <h3 className="text-lg font-semibold text-text-primary mb-6">
              Топ зон по риску
            </h3>
            <div className="space-y-4">
              {zones.slice(0, 5).map((zone, index) => (
                <div key={zone.zone_name} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-primary">{index + 1}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-text-primary">
                        {zone.zone_name}
                      </span>
                      <span className="text-sm text-text-secondary">
                        Риск: {(zone.risk_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="h-2 bg-dark-hover rounded-full overflow-hidden">
                      <div
                        className="h-full bg-danger transition-all"
                        style={{ width: `${zone.risk_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
