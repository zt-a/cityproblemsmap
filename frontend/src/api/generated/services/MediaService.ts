/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_replace_media_api_v1_problems__problem_entity_id__media__media_entity_id__patch } from '../models/Body_replace_media_api_v1_problems__problem_entity_id__media__media_entity_id__patch';
import type { Body_upload_media_api_v1_problems__problem_entity_id__media_post } from '../models/Body_upload_media_api_v1_problems__problem_entity_id__media_post';
import type { MediaPublic } from '../models/MediaPublic';
import type { MediaReorder } from '../models/MediaReorder';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MediaService {
    /**
     * Upload Media
     * Загрузить фото или видео к проблеме.
     *
     * Категории медиа:
     * - problem: Исходная проблема (любой пользователь)
     * - in_progress: Процесс работы (только volunteer, moderator, official, admin)
     * - result: Результат работы (только volunteer, moderator, official, admin)
     *
     * Хранилище выбирается через MEDIA_STORAGE в .env:
     * - local      — локальная папка (разработка)
     * - cloudinary — облако (продакшн)
     * @param problemEntityId
     * @param formData
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static uploadMediaApiV1ProblemsProblemEntityIdMediaPost(
        problemEntityId: number,
        formData: Body_upload_media_api_v1_problems__problem_entity_id__media_post,
    ): CancelablePromise<MediaPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/media',
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
     * Get Problem Media
     * Все активные медиафайлы проблемы.
     * @param problemEntityId
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static getProblemMediaApiV1ProblemsProblemEntityIdMediaGet(
        problemEntityId: number,
    ): CancelablePromise<Array<MediaPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/media',
            path: {
                'problem_entity_id': problemEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Remove Media
     * Мягкое удаление медиафайла — status=removed.
     * @param problemEntityId
     * @param mediaEntityId
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static removeMediaApiV1ProblemsProblemEntityIdMediaMediaEntityIdDelete(
        problemEntityId: number,
        mediaEntityId: number,
    ): CancelablePromise<MediaPublic> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/problems/{problem_entity_id}/media/{media_entity_id}',
            path: {
                'problem_entity_id': problemEntityId,
                'media_entity_id': mediaEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Replace Media
     * Заменить медиафайл или обновить caption.
     *
     * - Если передан file: загружает новый файл, старый помечается status=replaced
     * - Если передан только caption: обновляет подпись без замены файла
     * - Только uploader или автор проблемы может заменять медиа
     * @param problemEntityId
     * @param mediaEntityId
     * @param formData
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static replaceMediaApiV1ProblemsProblemEntityIdMediaMediaEntityIdPatch(
        problemEntityId: number,
        mediaEntityId: number,
        formData?: Body_replace_media_api_v1_problems__problem_entity_id__media__media_entity_id__patch,
    ): CancelablePromise<MediaPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/problems/{problem_entity_id}/media/{media_entity_id}',
            path: {
                'problem_entity_id': problemEntityId,
                'media_entity_id': mediaEntityId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reorder Media
     * Изменить порядок отображения медиафайлов.
     * Передать список entity_id в нужном порядке.
     * Только автор проблемы может менять порядок.
     * @param problemEntityId
     * @param requestBody
     * @returns MediaPublic Successful Response
     * @throws ApiError
     */
    public static reorderMediaApiV1ProblemsProblemEntityIdMediaReorderPatch(
        problemEntityId: number,
        requestBody: MediaReorder,
    ): CancelablePromise<Array<MediaPublic>> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/problems/{problem_entity_id}/media/reorder',
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
}
