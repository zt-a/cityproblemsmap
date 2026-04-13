/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserProfileResponse } from '../models/UserProfileResponse';
import type { UserProfileUpdate } from '../models/UserProfileUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SocialService {
    /**
     * Get User Profile
     * Получить профиль пользователя
     * @param userId
     * @returns UserProfileResponse Successful Response
     * @throws ApiError
     */
    public static getUserProfileApiV1SocialProfileUserIdGet(
        userId: number,
    ): CancelablePromise<UserProfileResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/social/profile/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update My Profile
     * Обновить свой профиль
     * @param requestBody
     * @returns UserProfileResponse Successful Response
     * @throws ApiError
     */
    public static updateMyProfileApiV1SocialProfilePatch(
        requestBody: UserProfileUpdate,
    ): CancelablePromise<UserProfileResponse> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/social/profile',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Follow User
     * Подписаться на пользователя
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static followUserApiV1SocialFollowUserIdPost(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/social/follow/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Unfollow User
     * Отписаться от пользователя
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static unfollowUserApiV1SocialFollowUserIdDelete(
        userId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/social/follow/{user_id}',
            path: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Activity Feed
     * Получить ленту активности подписок
     * @param limit
     * @param offset
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getActivityFeedApiV1SocialFeedGet(
        limit: number = 20,
        offset?: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/social/feed',
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
