/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FlaggedCommentList } from '../models/FlaggedCommentList';
import type { HideCommentRequest } from '../models/HideCommentRequest';
import type { ModeratorStats } from '../models/ModeratorStats';
import type { ProblemList } from '../models/ProblemList';
import type { ProblemPublic } from '../models/ProblemPublic';
import type { SuspiciousProblemList } from '../models/SuspiciousProblemList';
import type { VerifyProblemRequest } from '../models/VerifyProblemRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ModeratorService {
    /**
     * Get Flagged Comments
     * Комментарии с жалобами от пользователей.
     * Требуют проверки модератором.
     * @param offset
     * @param limit
     * @returns FlaggedCommentList Successful Response
     * @throws ApiError
     */
    public static getFlaggedCommentsApiV1ModeratorCommentsFlaggedGet(
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<FlaggedCommentList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderator/comments/flagged',
            query: {
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Hide Comment
     * Скрыть комментарий нарушающий правила.
     * Комментарий остаётся в БД но помечается как скрытый.
     * @param entityId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static hideCommentApiV1ModeratorCommentsEntityIdHidePost(
        entityId: number,
        requestBody: HideCommentRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderator/comments/{entity_id}/hide',
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
     * Restore Comment
     * Восстановить скрытый комментарий.
     * Снимает флаг и причину жалобы.
     * @param entityId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static restoreCommentApiV1ModeratorCommentsEntityIdRestorePost(
        entityId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderator/comments/{entity_id}/restore',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Suspicious Problems
     * Проблемы с низким truth_score — возможно фейки.
     * По умолчанию показывает проблемы с truth_score < 0.3.
     * @param threshold Порог truth_score
     * @param offset
     * @param limit
     * @returns SuspiciousProblemList Successful Response
     * @throws ApiError
     */
    public static getSuspiciousProblemsApiV1ModeratorProblemsSuspiciousGet(
        threshold: number = 0.3,
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<SuspiciousProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderator/problems/suspicious',
            query: {
                'threshold': threshold,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Pending Problems
     * Новые проблемы требующие проверки.
     * По умолчанию показывает проблемы за последние 24 часа.
     * @param hours Проблемы за последние N часов
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static getPendingProblemsApiV1ModeratorProblemsPendingGet(
        hours: number = 24,
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderator/problems/pending',
            query: {
                'hours': hours,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Verify Problem
     * Подтвердить проблему как валидную.
     * Модератор проверил и подтверждает что проблема реальна.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static verifyProblemApiV1ModeratorProblemsEntityIdVerifyPost(
        entityId: number,
        requestBody: VerifyProblemRequest,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderator/problems/{entity_id}/verify',
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
     * Get Moderator Stats
     * Статистика работы текущего модератора.
     * Показывает сколько проблем проверено, комментариев скрыто и т.д.
     * @returns ModeratorStats Successful Response
     * @throws ApiError
     */
    public static getModeratorStatsApiV1ModeratorStatsGet(): CancelablePromise<ModeratorStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderator/stats',
        });
    }
}
