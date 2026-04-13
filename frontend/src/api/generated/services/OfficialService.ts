/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AssignedProblemList } from '../models/AssignedProblemList';
import type { OfficialCommentRequest } from '../models/OfficialCommentRequest';
import type { OfficialStats } from '../models/OfficialStats';
import type { OfficialZone } from '../models/OfficialZone';
import type { ProblemPublic } from '../models/ProblemPublic';
import type { ProblemStatus } from '../models/ProblemStatus';
import type { ResolveProblemRequest } from '../models/ResolveProblemRequest';
import type { TakeProblemRequest } from '../models/TakeProblemRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OfficialService {
    /**
     * Get Assigned Problems
     * Проблемы назначенные на текущего официала.
     * Показывает проблемы где resolved_by_entity_id = текущий пользователь
     * или проблемы в зонах закреплённых за официалом.
     * @param status
     * @param offset
     * @param limit
     * @returns AssignedProblemList Successful Response
     * @throws ApiError
     */
    public static getAssignedProblemsApiV1OfficialProblemsAssignedGet(
        status?: (ProblemStatus | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<AssignedProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/official/problems/assigned',
            query: {
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
     * Get In Progress Problems
     * Проблемы в работе у текущего официала.
     * Статус in_progress и назначены на официала.
     * @param offset
     * @param limit
     * @returns AssignedProblemList Successful Response
     * @throws ApiError
     */
    public static getInProgressProblemsApiV1OfficialProblemsInProgressGet(
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<AssignedProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/official/problems/in-progress',
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
     * Take Problem
     * Взять проблему в работу.
     * Официал назначает себя ответственным и меняет статус на in_progress.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static takeProblemApiV1OfficialProblemsEntityIdTakePost(
        entityId: number,
        requestBody: TakeProblemRequest,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/official/problems/{entity_id}/take',
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
     * Resolve Problem
     * Отметить проблему решённой с отчётом о выполненных работах.
     * Только официал назначенный на проблему может её закрыть.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static resolveProblemApiV1OfficialProblemsEntityIdResolvePost(
        entityId: number,
        requestBody: ResolveProblemRequest,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/official/problems/{entity_id}/resolve',
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
     * Add Official Comment
     * Добавить официальный ответ от городских служб.
     * Комментарий помечается как official_response.
     * @param entityId
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static addOfficialCommentApiV1OfficialProblemsEntityIdCommentPost(
        entityId: number,
        requestBody: OfficialCommentRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/official/problems/{entity_id}/comment',
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
     * Get Official Zones
     * Зоны закреплённые за официалом.
     * Показывает зоны города официала с статистикой проблем.
     * @returns OfficialZone Successful Response
     * @throws ApiError
     */
    public static getOfficialZonesApiV1OfficialZonesGet(): CancelablePromise<Array<OfficialZone>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/official/zones',
        });
    }
    /**
     * Get Official Stats
     * Статистика работы текущего официала.
     * Показывает сколько проблем назначено, решено, среднее время решения.
     * @returns OfficialStats Successful Response
     * @throws ApiError
     */
    public static getOfficialStatsApiV1OfficialStatsGet(): CancelablePromise<OfficialStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/official/stats',
        });
    }
}
