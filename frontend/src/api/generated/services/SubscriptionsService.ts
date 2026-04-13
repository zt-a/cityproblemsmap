/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SubscriptionCreate } from '../models/SubscriptionCreate';
import type { SubscriptionList } from '../models/SubscriptionList';
import type { SubscriptionPublic } from '../models/SubscriptionPublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SubscriptionsService {
    /**
     * Subscribe To Problem
     * Подписаться на проблему
     * @param problemId
     * @param requestBody
     * @returns SubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static subscribeToProblemApiV1SubscriptionsProblemsProblemIdPost(
        problemId: number,
        requestBody: SubscriptionCreate,
    ): CancelablePromise<SubscriptionPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/subscriptions/problems/{problem_id}',
            path: {
                'problem_id': problemId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Unsubscribe From Problem
     * Отписаться от проблемы
     * @param problemId
     * @returns void
     * @throws ApiError
     */
    public static unsubscribeFromProblemApiV1SubscriptionsProblemsProblemIdDelete(
        problemId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/subscriptions/problems/{problem_id}',
            path: {
                'problem_id': problemId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Subscribe To Zone
     * Подписаться на зону (район)
     * @param zoneId
     * @param requestBody
     * @returns SubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static subscribeToZoneApiV1SubscriptionsZonesZoneIdPost(
        zoneId: number,
        requestBody: SubscriptionCreate,
    ): CancelablePromise<SubscriptionPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/subscriptions/zones/{zone_id}',
            path: {
                'zone_id': zoneId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Unsubscribe From Zone
     * Отписаться от зоны
     * @param zoneId
     * @returns void
     * @throws ApiError
     */
    public static unsubscribeFromZoneApiV1SubscriptionsZonesZoneIdDelete(
        zoneId: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/subscriptions/zones/{zone_id}',
            path: {
                'zone_id': zoneId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Subscriptions
     * Получить все подписки текущего пользователя
     * @param targetType Фильтр по типу: problem/zone/user
     * @returns SubscriptionList Successful Response
     * @throws ApiError
     */
    public static getMySubscriptionsApiV1SubscriptionsGet(
        targetType?: (string | null),
    ): CancelablePromise<SubscriptionList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/subscriptions/',
            query: {
                'target_type': targetType,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Subscription
     * Обновить настройки подписки (типы уведомлений)
     * @param entityId
     * @param requestBody
     * @returns SubscriptionPublic Successful Response
     * @throws ApiError
     */
    public static updateSubscriptionApiV1SubscriptionsEntityIdPatch(
        entityId: number,
        requestBody: SubscriptionCreate,
    ): CancelablePromise<SubscriptionPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/subscriptions/{entity_id}',
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
