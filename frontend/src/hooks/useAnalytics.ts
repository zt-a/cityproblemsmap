import { useQuery } from '@tanstack/react-query'
import { AnalyticsService } from '../api/generated/services/AnalyticsService'

export const useCityOverview = (city: string) => {
  return useQuery({
    queryKey: ['analytics', 'overview', city],
    queryFn: async () => {
      const response = await AnalyticsService.cityOverviewApiV1AnalyticsCitiesCityOverviewGet(city)
      return response
    },
    enabled: !!city,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useCityTrend = (city: string, days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'trend', city, days],
    queryFn: async () => {
      const response = await AnalyticsService.cityTrendApiV1AnalyticsCitiesCityTrendGet(city, days)
      return response
    },
    enabled: !!city,
    staleTime: 5 * 60 * 1000,
  })
}

export const useCityHeatmap = (city: string) => {
  return useQuery({
    queryKey: ['analytics', 'heatmap', city],
    queryFn: async () => {
      const response = await AnalyticsService.cityHeatmapApiV1AnalyticsCitiesCityHeatmapGet(city)
      return response
    },
    enabled: !!city,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

export const useCityZones = (city: string) => {
  return useQuery({
    queryKey: ['analytics', 'zones', city],
    queryFn: async () => {
      const response = await AnalyticsService.cityZoneIndexesApiV1AnalyticsCitiesCityZonesGet(city)
      return response
    },
    enabled: !!city,
    staleTime: 10 * 60 * 1000,
  })
}

export const useResponseTime = (city: string) => {
  return useQuery({
    queryKey: ['analytics', 'response-time', city],
    queryFn: async () => {
      const response = await AnalyticsService.cityResponseTimeApiV1AnalyticsCitiesCityResponseTimeGet(city)
      return response
    },
    enabled: !!city,
    staleTime: 10 * 60 * 1000,
  })
}
