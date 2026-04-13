/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OfficialEfficiency } from '../models/OfficialEfficiency';
import type { ProblemTrend } from '../models/ProblemTrend';
import type { TopZone } from '../models/TopZone';
import type { UserLeaderboard } from '../models/UserLeaderboard';
import type { ZoneComparison } from '../models/ZoneComparison';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnalyticsExtendedService {
    /**
     * Compare Zones
     * Сравнение нескольких зон
     * @param zoneIds Comma-separated zone IDs
     * @returns ZoneComparison Successful Response
     * @throws ApiError
     */
    public static compareZonesApiV1AnalyticsZonesComparisonGet(
        zoneIds: string,
    ): CancelablePromise<Array<ZoneComparison>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/zones/comparison',
            query: {
                'zone_ids': zoneIds,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Top Problematic Zones
     * Топ проблемных зон города
     * @param city
     * @param limit
     * @returns TopZone Successful Response
     * @throws ApiError
     */
    public static topProblematicZonesApiV1AnalyticsZonesTopGet(
        city: string,
        limit: number = 10,
    ): CancelablePromise<Array<TopZone>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/zones/top',
            query: {
                'city': city,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * User Leaderboard
     * Рейтинг активных пользователей
     * @param city
     * @param limit
     * @param periodDays
     * @returns UserLeaderboard Successful Response
     * @throws ApiError
     */
    public static userLeaderboardApiV1AnalyticsLeaderboardUsersGet(
        city: string,
        limit: number = 50,
        periodDays: number = 30,
    ): CancelablePromise<Array<UserLeaderboard>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/leaderboard/users',
            query: {
                'city': city,
                'limit': limit,
                'period_days': periodDays,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Officials Efficiency
     * Рейтинг эффективности официальных лиц
     * @param city
     * @param limit
     * @returns OfficialEfficiency Successful Response
     * @throws ApiError
     */
    public static officialsEfficiencyApiV1AnalyticsLeaderboardOfficialsGet(
        city: string,
        limit: number = 20,
    ): CancelablePromise<Array<OfficialEfficiency>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/leaderboard/officials',
            query: {
                'city': city,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Problem Trends By Type
     * Тренды по типам проблем
     * @param city
     * @param days
     * @returns ProblemTrend Successful Response
     * @throws ApiError
     */
    public static problemTrendsByTypeApiV1AnalyticsTrendsByTypeGet(
        city: string,
        days: number = 30,
    ): CancelablePromise<Array<ProblemTrend>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/trends/by-type',
            query: {
                'city': city,
                'days': days,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Problems
     * Экспорт данных о проблемах
     * @param city
     * @param format
     * @param status
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportProblemsApiV1AnalyticsExportProblemsGet(
        city: string,
        format: string = 'csv',
        status?: (string | null),
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/export/problems',
            query: {
                'city': city,
                'format': format,
                'status': status,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Zones
     * Экспорт данных о зонах
     * @param city
     * @param format
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportZonesApiV1AnalyticsExportZonesGet(
        city: string,
        format: string = 'csv',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/export/zones',
            query: {
                'city': city,
                'format': format,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Users
     * Экспорт данных о пользователях
     * @param city
     * @param format
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportUsersApiV1AnalyticsExportUsersGet(
        city: string,
        format: string = 'csv',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analytics/export/users',
            query: {
                'city': city,
                'format': format,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
