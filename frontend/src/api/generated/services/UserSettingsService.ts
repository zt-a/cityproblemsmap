/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserNotificationSettingsPublic } from '../models/UserNotificationSettingsPublic';
import type { UserNotificationSettingsUpdate } from '../models/UserNotificationSettingsUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class UserSettingsService {
    /**
     * Get Notification Settings
     * Получить настройки уведомлений текущего пользователя
     * @returns UserNotificationSettingsPublic Successful Response
     * @throws ApiError
     */
    public static getNotificationSettingsApiV1SettingsNotificationsGet(): CancelablePromise<UserNotificationSettingsPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/settings/notifications',
        });
    }
    /**
     * Update Notification Settings
     * Обновить настройки уведомлений
     * @param requestBody
     * @returns UserNotificationSettingsPublic Successful Response
     * @throws ApiError
     */
    public static updateNotificationSettingsApiV1SettingsNotificationsPatch(
        requestBody: UserNotificationSettingsUpdate,
    ): CancelablePromise<UserNotificationSettingsPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/settings/notifications',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
