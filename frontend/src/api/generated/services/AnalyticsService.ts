/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CityDigitalTwin } from '../models/CityDigitalTwin';
import type { CityOverview } from '../models/CityOverview';
import type { HeatmapPoint } from '../models/HeatmapPoint';
import type { PeriodStats } from '../models/PeriodStats';
import type { ResponseTimeStats } from '../models/ResponseTimeStats';
import type { ZoneIndexes } from '../models/ZoneIndexes';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnalyticsService {
    /**
     * City Overview
     * Главная сводка по городу.
     * Статусы, типы проблем, solve rate, активная зона.
     * @param city
     * @returns CityOverview Successful Response
     * @throws ApiError
     */
    public static cityOverviewApiV1AnalyticsCitiesCityOverviewGet(
        city: string,
    ): CancelablePromise<CityOverview> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/overview',
            path: {
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * City Trend
     * Динамика активности за период.
     * Новые проблемы, решённые, голоса, комментарии по дням.
     * Используется для графиков на дашборде.
     * @param city
     * @param days Период в днях
     * @returns PeriodStats Successful Response
     * @throws ApiError
     */
    public static cityTrendApiV1AnalyticsCitiesCityTrendGet(
        city: string,
        days: number = 30,
    ): CancelablePromise<Array<PeriodStats>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/trend',
            path: {
                'city': city,
            },
            query: {
                'days': days,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * City Heatmap
     * Данные тепловой карты — все активные проблемы с координатами и весом.
     * Передаётся напрямую в Leaflet heatmap layer или MapboxGL.
     * @param city
     * @returns HeatmapPoint Successful Response
     * @throws ApiError
     */
    public static cityHeatmapApiV1AnalyticsCitiesCityHeatmapGet(
        city: string,
    ): CancelablePromise<Array<HeatmapPoint>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/heatmap',
            path: {
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * City Zone Indexes
     * Индексы всех зон города — pollution, traffic, risk.
     * Используется для окрашивания районов на карте Digital Twin.
     * Отсортированы по risk_score — самые опасные первыми.
     * @param city
     * @returns ZoneIndexes Successful Response
     * @throws ApiError
     */
    public static cityZoneIndexesApiV1AnalyticsCitiesCityZonesGet(
        city: string,
    ): CancelablePromise<Array<ZoneIndexes>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/zones',
            path: {
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * City Response Time
     * Статистика времени реакции властей/волонтёров.
     * Среднее, минимальное, максимальное время решения проблем.
     * Показывает насколько эффективно работают службы города.
     * @param city
     * @returns ResponseTimeStats Successful Response
     * @throws ApiError
     */
    public static cityResponseTimeApiV1AnalyticsCitiesCityResponseTimeGet(
        city: string,
    ): CancelablePromise<ResponseTimeStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/response-time',
            path: {
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * City Digital Twin
     * Полный Digital Twin срез города — все данные одним запросом.
     * Используется для главного дашборда симуляций.
     *
     * Включает:
     * - Сводку по городу
     * - Индексы всех зон
     * - Тепловую карту
     * - Время реакции властей
     * - Тренд за 30 дней
     * @param city
     * @returns CityDigitalTwin Successful Response
     * @throws ApiError
     */
    public static cityDigitalTwinApiV1AnalyticsCitiesCityDigitalTwinGet(
        city: string,
    ): CancelablePromise<CityDigitalTwin> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/cities/{city}/digital-twin',
            path: {
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
