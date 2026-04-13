/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommentPublic } from '../models/CommentPublic';
import type { ProblemList } from '../models/ProblemList';
import type { ProblemStatus } from '../models/ProblemStatus';
import type { ReputationHistory } from '../models/ReputationHistory';
import type { UpdateEmailRequest } from '../models/UpdateEmailRequest';
import type { UpdateProfileRequest } from '../models/UpdateProfileRequest';
import type { UserPublic } from '../models/UserPublic';
import type { VotePublic } from '../models/VotePublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UsersService {
    /**
     * Get Me
     * Текущий авторизованный пользователь.
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static getMeApiV1UsersMeGet(): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me',
        });
    }
    /**
     * Update Profile
     * Смена username.
     * Создаёт новую версию пользователя.
     * @param requestBody
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static updateProfileApiV1UsersMeProfilePatch(
        requestBody: UpdateProfileRequest,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me/profile',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Email
     * Смена email.
     * Требует подтверждение текущего пароля.
     * Создаёт новую версию пользователя.
     * @param requestBody
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static updateEmailApiV1UsersMeEmailPatch(
        requestBody: UpdateEmailRequest,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me/email',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Location
     * Обновить геолокацию пользователя.
     * @param country
     * @param city
     * @param district
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static updateLocationApiV1UsersMeLocationPatch(
        country?: (string | null),
        city?: (string | null),
        district?: (string | null),
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me/location',
            query: {
                'country': country,
                'city': city,
                'district': district,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Deactivate Me
     * Деактивация аккаунта — мягкая метка.
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static deactivateMeApiV1UsersMeDeactivatePatch(): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/users/me/deactivate',
        });
    }
    /**
     * Get My Problems
     * Мои проблемы — только текущие версии.
     * Фильтр по статусу опциональный.
     * @param status
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static getMyProblemsApiV1UsersMeProblemsGet(
        status?: (ProblemStatus | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me/problems',
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
     * Get My Votes
     * Мои текущие голоса.
     * Показывает последнюю версию каждого голоса.
     * @param offset
     * @param limit
     * @returns VotePublic Successful Response
     * @throws ApiError
     */
    public static getMyVotesApiV1UsersMeVotesGet(
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<Array<VotePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me/votes',
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
     * Get My Comments
     * Мои текущие комментарии.
     * @param offset
     * @param limit
     * @returns CommentPublic Successful Response
     * @throws ApiError
     */
    public static getMyCommentsApiV1UsersMeCommentsGet(
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<Array<CommentPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me/comments',
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
     * Get My Reputation
     * История изменений моей репутации.
     * Показывает все начисления и списания с причинами.
     * @param offset
     * @param limit
     * @returns ReputationHistory Successful Response
     * @throws ApiError
     */
    public static getMyReputationApiV1UsersMeReputationGet(
        offset?: number,
        limit: number = 50,
    ): CancelablePromise<ReputationHistory> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/me/reputation',
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
     * Get User
     * Публичный профиль пользователя.
     * @param entityId
     * @returns UserPublic Successful Response
     * @throws ApiError
     */
    public static getUserApiV1UsersEntityIdGet(
        entityId: number,
    ): CancelablePromise<UserPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Problems
     * Публичные проблемы пользователя.
     * Доступно без авторизации.
     * @param entityId
     * @param status
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static getUserProblemsApiV1UsersEntityIdProblemsGet(
        entityId: number,
        status?: (ProblemStatus | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/users/{entity_id}/problems',
            path: {
                'entity_id': entityId,
            },
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
}
