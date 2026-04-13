/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReportCreate } from '../models/ReportCreate';
import type { ReportList } from '../models/ReportList';
import type { ReportPublic } from '../models/ReportPublic';
import type { ReportResolve } from '../models/ReportResolve';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ReportsService {
    /**
     * Create Report
     * Создать жалобу на проблему, комментарий или пользователя.
     * Доступно всем авторизованным пользователям.
     * @param requestBody
     * @returns ReportPublic Successful Response
     * @throws ApiError
     */
    public static createReportApiV1ReportsPost(
        requestBody: ReportCreate,
    ): CancelablePromise<ReportPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/reports/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Reports
     * Получить свои жалобы
     * @param statusFilter Фильтр по статусу
     * @param offset
     * @param limit
     * @returns ReportList Successful Response
     * @throws ApiError
     */
    public static getMyReportsApiV1ReportsMyGet(
        statusFilter?: (string | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ReportList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/reports/my',
            query: {
                'status_filter': statusFilter,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Moderation Queue
     * Очередь модерации жалоб.
     * Доступно только модераторам и админам.
     * @param statusFilter Фильтр по статусу
     * @param targetType Фильтр по типу цели
     * @param offset
     * @param limit
     * @returns ReportList Successful Response
     * @throws ApiError
     */
    public static getModerationQueueApiV1ReportsModerationQueueGet(
        statusFilter?: (string | null),
        targetType?: (string | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ReportList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/reports/moderation/queue',
            query: {
                'status_filter': statusFilter,
                'target_type': targetType,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Resolve Report
     * Разрешить жалобу (принять или отклонить).
     * Доступно только модераторам и админам.
     * @param entityId
     * @param requestBody
     * @returns ReportPublic Successful Response
     * @throws ApiError
     */
    public static resolveReportApiV1ReportsModerationEntityIdResolvePatch(
        entityId: number,
        requestBody: ReportResolve,
    ): CancelablePromise<ReportPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/reports/moderation/{entity_id}/resolve',
            path: {
                'entity_id': entityId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Moderation Stats
     * Статистика жалоб для модераторов.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getModerationStatsApiV1ReportsModerationStatsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/reports/moderation/stats',
        });
    }
}
