/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StreamingService {
    /**
     * Stream Video
     * Стриминг видео с поддержкой HTTP Range requests.
     *
     * Позволяет:
     * - Перематывать видео без полной загрузки
     * - Начинать воспроизведение с любого момента
     * - Экономить трафик
     *
     * Работает только для локального хранилища (local storage).
     * Для Cloudinary используется прямой URL с их CDN.
     * @param problemEntityId
     * @param mediaEntityId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static streamVideoApiV1ProblemsProblemEntityIdMediaMediaEntityIdStreamGet(
        problemEntityId: number,
        mediaEntityId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/media/{media_entity_id}/stream',
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
     * Get Hls Playlist
     * Получить HLS playlist для адаптивного стриминга.
     *
     * Требует предварительной обработки видео через Celery задачу.
     * Если видео не обработано (is_processed != 1) - возвращает ошибку.
     *
     * HLS (HTTP Live Streaming) позволяет:
     * - Адаптивный битрейт (качество подстраивается под скорость интернета)
     * - Быстрый старт воспроизведения
     * - Поддержка всех современных браузеров
     * @param problemEntityId
     * @param mediaEntityId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getHlsPlaylistApiV1ProblemsProblemEntityIdMediaMediaEntityIdHlsGet(
        problemEntityId: number,
        mediaEntityId: number,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/problems/{problem_entity_id}/media/{media_entity_id}/hls',
            path: {
                'problem_entity_id': problemEntityId,
                'media_entity_id': mediaEntityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
