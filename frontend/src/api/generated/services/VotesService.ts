/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { VoteCreate } from '../models/VoteCreate';
import type { VotePublic } from '../models/VotePublic';
import type { VoteStats } from '../models/VoteStats';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VotesService {
    /**
     * Cast Vote
     * Проголосовать за проблему.
     *
     * Если пользователь уже голосовал — старый голос помечается
     * is_current=False, создаётся новая версия голоса.
     * После голоса пересчитываются scores проблемы.
     * @param problemEntityId
     * @param requestBody
     * @returns VotePublic Successful Response
     * @throws ApiError
     */
    public static castVoteApiV1ProblemsProblemEntityIdVotesPost(
        problemEntityId: number,
        requestBody: VoteCreate,
    ): CancelablePromise<VotePublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/votes',
            path: {
                'problem_entity_id': problemEntityId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Vote
     * Получить свой текущий голос по проблеме.
     * @param problemEntityId
     * @returns VotePublic Successful Response
     * @throws ApiError
     */
    public static getMyVoteApiV1ProblemsProblemEntityIdVotesMyGet(
        problemEntityId: number,
    ): CancelablePromise<VotePublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/votes/my',
            path: {
                'problem_entity_id': problemEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete My Vote
     * Удалить свой голос (отменить голосование).
     *
     * На самом деле создаёт новую версию голоса с is_current=False,
     * чтобы сохранить историю в append-only архитектуре.
     * @param problemEntityId
     * @returns void
     * @throws ApiError
     */
    public static deleteMyVoteApiV1ProblemsProblemEntityIdVotesMyDelete(
        problemEntityId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/problems/{problem_entity_id}/votes/my',
            path: {
                'problem_entity_id': problemEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Vote Stats
     * Агрегированная статистика голосов по проблеме.
     * Берётся из scores проблемы — не считается каждый раз заново.
     * @param problemEntityId
     * @returns VoteStats Successful Response
     * @throws ApiError
     */
    public static getVoteStatsApiV1ProblemsProblemEntityIdVotesStatsGet(
        problemEntityId: number,
    ): CancelablePromise<VoteStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/votes/stats',
            path: {
                'problem_entity_id': problemEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Votes History
     * Полная история всех голосов включая изменённые.
     * Только для аналитики и AI — обычным пользователям не нужно.
     * @param problemEntityId
     * @returns VotePublic Successful Response
     * @throws ApiError
     */
    public static getVotesHistoryApiV1ProblemsProblemEntityIdVotesHistoryGet(
        problemEntityId: number,
    ): CancelablePromise<Array<VotePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/votes/history',
            path: {
                'problem_entity_id': problemEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
