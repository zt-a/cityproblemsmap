/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MarkAsReadRequest } from '../models/MarkAsReadRequest';
import type { NotificationList } from '../models/NotificationList';
import type { NotificationStats } from '../models/NotificationStats';
import type { NotificationType } from '../models/NotificationType';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class NotificationsService {
    /**
     * Get Notifications
     * Получить список уведомлений текущего пользователя
     * @param offset
     * @param limit
     * @param unreadOnly
     * @param notificationType
     * @returns NotificationList Successful Response
     * @throws ApiError
     */
    public static getNotificationsApiV1NotificationsGet(
        offset?: number,
        limit: number = 20,
        unreadOnly: boolean = false,
        notificationType?: (NotificationType | null),
    ): CancelablePromise<NotificationList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/notifications/',
            query: {
                'offset': offset,
                'limit': limit,
                'unread_only': unreadOnly,
                'notification_type': notificationType,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete All Notifications
     * Удалить все уведомления пользователя (мягкое удаление)
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteAllNotificationsApiV1NotificationsDelete(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/notifications/',
        });
    }
    /**
     * Get Notification Stats
     * Получить статистику уведомлений
     * @returns NotificationStats Successful Response
     * @throws ApiError
     */
    public static getNotificationStatsApiV1NotificationsStatsGet(): CancelablePromise<NotificationStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/notifications/stats',
        });
    }
    /**
     * Mark Notifications As Read
     * Отметить уведомления как прочитанные (через версионирование)
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static markNotificationsAsReadApiV1NotificationsMarkReadPost(
        requestBody: MarkAsReadRequest,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/notifications/mark-read',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Mark All Notifications As Read
     * Отметить все уведомления как прочитанные (через версионирование)
     * @returns any Successful Response
     * @throws ApiError
     */
    public static markAllNotificationsAsReadApiV1NotificationsMarkAllReadPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/notifications/mark-all-read',
        });
    }
    /**
     * Delete Notification
     * Удалить уведомление (мягкое удаление через is_current)
     * @param notificationId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteNotificationApiV1NotificationsNotificationIdDelete(
        notificationId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/notifications/{notification_id}',
            path: {
                'notification_id': notificationId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
