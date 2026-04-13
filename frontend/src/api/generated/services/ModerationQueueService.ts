/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommentPublic } from '../models/CommentPublic';
import type { ProblemPublic } from '../models/ProblemPublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ModerationQueueService {
    /**
     * Get Problems Queue
     * Получить очередь проблем для модерации.
     *
     * Показывает:
     * - Новые проблемы (pending)
     * - Проблемы с жалобами (flagged)
     * - Проблемы требующие внимания
     * @param status Фильтр по статусу: pending, flagged
     * @param priority Приоритет: high, medium, low
     * @param limit
     * @param offset
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static getProblemsQueueApiV1ModerationQueueProblemsGet(
        status?: (string | null),
        priority?: (string | null),
        limit: number = 50,
        offset?: number,
    ): CancelablePromise<Array<ProblemPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderation/queue/problems',
            query: {
                'status': status,
                'priority': priority,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Comments Queue
     * Получить очередь комментариев для модерации.
     *
     * Показывает комментарии с жалобами.
     * @param status Фильтр: flagged
     * @param limit
     * @param offset
     * @returns CommentPublic Successful Response
     * @throws ApiError
     */
    public static getCommentsQueueApiV1ModerationQueueCommentsGet(
        status?: (string | null),
        limit: number = 50,
        offset?: number,
    ): CancelablePromise<Array<CommentPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderation/queue/comments',
            query: {
                'status': status,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Moderation Stats
     * Статистика очереди модерации.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getModerationStatsApiV1ModerationQueueStatsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderation/queue/stats',
        });
    }
}
