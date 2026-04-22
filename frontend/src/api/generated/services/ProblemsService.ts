/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemCreate } from '../models/ProblemCreate';
import type { ProblemList } from '../models/ProblemList';
import type { ProblemPublic } from '../models/ProblemPublic';
import type { ProblemStatus } from '../models/ProblemStatus';
import type { ProblemStatusUpdate } from '../models/ProblemStatusUpdate';
import type { ProblemUpdate } from '../models/ProblemUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProblemsService {
    /**
     * Create Problem
     * Создать новую проблему.
     * Пользователь может добавить проблему только в своём городе.
     * @param requestBody
     * @param xCaptchaToken CAPTCHA token
     * @param xCaptchaType CAPTCHA type: recaptcha, hcaptcha, turnstile
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static createProblemApiV1ProblemsPost(
        requestBody: ProblemCreate,
        xCaptchaToken?: (string | null),
        xCaptchaType?: (string | null),
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/',
            headers: {
                'x-captcha-token': xCaptchaToken,
                'x-captcha-type': xCaptchaType,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Problems
     * Список актуальных проблем с фильтрацией и пагинацией.
     * Всегда возвращает только is_current=True версии.
     * @param city Фильтр по городу
     * @param problemType Тип проблемы
     * @param status Статус
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static listProblemsApiV1ProblemsGet(
        city?: (string | null),
        problemType?: (string | null),
        status?: (ProblemStatus | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/',
            query: {
                'city': city,
                'problem_type': problemType,
                'status': status,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Problem
     * Получить текущую версию проблемы по entity_id.
     * @param entityId
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static getProblemApiV1ProblemsEntityIdGet(
        entityId: number,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Problem
     * Обновить проблему (только автор).
     * Можно изменить: title, description, address, location, problem_type, tags.
     * Создаёт новую версию — история изменений сохраняется.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static updateProblemApiV1ProblemsEntityIdPatch(
        entityId: number,
        requestBody: ProblemUpdate,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/problems/{entity_id}',
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
     * Get Problem History
     * История всех версий проблемы.
     * Показывает как менялся статус, описание, scores.
     * @param entityId
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static getProblemHistoryApiV1ProblemsEntityIdHistoryGet(
        entityId: number,
    ): CancelablePromise<Array<ProblemPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{entity_id}/history',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Status
     * Обновить статус проблемы.
     * - Автор может закрыть свою проблему
     * - Модератор/админ/official может менять любой статус
     * Создаёт новую версию — история статусов сохраняется.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static updateStatusApiV1ProblemsEntityIdStatusPatch(
        entityId: number,
        requestBody: ProblemStatusUpdate,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/problems/{entity_id}/status',
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
}
