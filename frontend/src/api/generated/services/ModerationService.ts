/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BanInfo } from '../models/BanInfo';
import type { BannedUsersList } from '../models/BannedUsersList';
import type { BanUserRequest } from '../models/BanUserRequest';
import type { UnbanUserRequest } from '../models/UnbanUserRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ModerationService {
    /**
     * Ban User
     * Заблокировать пользователя.
     * Доступно только модераторам и админам.
     *
     * duration_days:
     * - None или 0 = постоянная блокировка
     * - > 0 = временная блокировка на N дней
     * @param entityId
     * @param requestBody
     * @returns BanInfo Successful Response
     * @throws ApiError
     */
    public static banUserApiV1ModerationUsersEntityIdBanPost(
        entityId: number,
        requestBody: BanUserRequest,
    ): CancelablePromise<BanInfo> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderation/users/{entity_id}/ban',
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
     * Unban User
     * Разблокировать пользователя.
     * Доступно только модераторам и админам.
     * @param entityId
     * @param requestBody
     * @returns BanInfo Successful Response
     * @throws ApiError
     */
    public static unbanUserApiV1ModerationUsersEntityIdUnbanPost(
        entityId: number,
        requestBody: UnbanUserRequest,
    ): CancelablePromise<BanInfo> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderation/users/{entity_id}/unban',
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
     * Get Ban Info
     * Получить информацию о бане пользователя.
     * Доступно только модераторам и админам.
     * @param entityId
     * @returns BanInfo Successful Response
     * @throws ApiError
     */
    public static getBanInfoApiV1ModerationUsersEntityIdBanInfoGet(
        entityId: number,
    ): CancelablePromise<BanInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderation/users/{entity_id}/ban-info',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Banned Users
     * Получить список забаненных пользователей.
     * Доступно только модераторам и админам.
     * @param offset
     * @param limit
     * @returns BannedUsersList Successful Response
     * @throws ApiError
     */
    public static getBannedUsersApiV1ModerationBannedUsersGet(
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<BannedUsersList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/moderation/banned-users',
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
     * Check Expired Bans
     * Проверить и разбанить пользователей с истекшим сроком бана.
     * Доступно только админам.
     * Можно запускать по расписанию через Celery.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static checkExpiredBansApiV1ModerationCheckExpiredBansPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/moderation/check-expired-bans',
        });
    }
}
