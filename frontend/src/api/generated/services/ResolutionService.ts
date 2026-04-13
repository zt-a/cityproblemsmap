/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_complete_problem_resolution_api_v1_problems__problem_entity_id__complete_resolution_post } from '../models/Body_complete_problem_resolution_api_v1_problems__problem_entity_id__complete_resolution_post';
import type { Body_start_problem_resolution_api_v1_problems__problem_entity_id__start_resolution_post } from '../models/Body_start_problem_resolution_api_v1_problems__problem_entity_id__start_resolution_post';
import type { Body_upload_progress_media_api_v1_problems__problem_entity_id__upload_progress_post } from '../models/Body_upload_progress_media_api_v1_problems__problem_entity_id__upload_progress_post';
import type { Body_upload_result_media_api_v1_problems__problem_entity_id__upload_result_post } from '../models/Body_upload_result_media_api_v1_problems__problem_entity_id__upload_result_post';
import type { MediaCategory } from '../models/MediaCategory';
import type { MediaPublic } from '../models/MediaPublic';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ResolutionService {
    /**
     * Start Problem Resolution
     * Начать решение проблемы.
     *
     * Доступно для:
     * - volunteer: может начать решение как волонтер
     * - official: может начать решение как официальная организация
     * - moderator/admin: могут начать решение от любого имени
     *
     * Изменяет статус проблемы на 'in_progress'.
     * @param problemEntityId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static startProblemResolutionApiV1ProblemsProblemEntityIdStartResolutionPost(
        problemEntityId: number,
        formData: Body_start_problem_resolution_api_v1_problems__problem_entity_id__start_resolution_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/start-resolution',
            path: {
                'problem_entity_id': problemEntityId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Complete Problem Resolution
     * Завершить решение проблемы.
     *
     * Доступно для:
     * - Пользователь который начал решение (resolved_by_entity_id)
     * - moderator/admin
     *
     * Изменяет статус проблемы на 'solved'.
     * Устанавливает resolved_at в текущее время.
     * @param problemEntityId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public static completeProblemResolutionApiV1ProblemsProblemEntityIdCompleteResolutionPost(
        problemEntityId: number,
        formData?: Body_complete_problem_resolution_api_v1_problems__problem_entity_id__complete_resolution_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/complete-resolution',
            path: {
                'problem_entity_id': problemEntityId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload Progress Media
     * Загрузить фото/видео процесса работы над проблемой.
     *
     * Доступно только для:
     * - volunteer, official, moderator, admin
     *
     * Проблема должна быть в статусе 'in_progress' или 'solved'.
     * Автоматически устанавливает media_category='in_progress'.
     * @param problemEntityId
     * @param formData
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static uploadProgressMediaApiV1ProblemsProblemEntityIdUploadProgressPost(
        problemEntityId: number,
        formData: Body_upload_progress_media_api_v1_problems__problem_entity_id__upload_progress_post,
    ): CancelablePromise<MediaPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/upload-progress',
            path: {
                'problem_entity_id': problemEntityId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload Result Media
     * Загрузить фото/видео результата работы (после решения проблемы).
     *
     * Доступно только для:
     * - volunteer, official, moderator, admin
     *
     * Проблема должна быть в статусе 'solved'.
     * Автоматически устанавливает media_category='result'.
     * @param problemEntityId
     * @param formData
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static uploadResultMediaApiV1ProblemsProblemEntityIdUploadResultPost(
        problemEntityId: number,
        formData: Body_upload_result_media_api_v1_problems__problem_entity_id__upload_result_post,
    ): CancelablePromise<MediaPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/upload-result',
            path: {
                'problem_entity_id': problemEntityId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Media By Category
     * Получить медиа проблемы по категории.
     *
     * Категории:
     * - problem: Исходная проблема
     * - in_progress: Процесс работы
     * - result: Результат работы
     * @param problemEntityId
     * @param category
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static getMediaByCategoryApiV1ProblemsProblemEntityIdMediaByCategoryGet(
        problemEntityId: number,
        category: MediaCategory,
    ): CancelablePromise<Array<MediaPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/media/by-category',
            path: {
                'problem_entity_id': problemEntityId,
            },
            query: {
                'category': category,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
