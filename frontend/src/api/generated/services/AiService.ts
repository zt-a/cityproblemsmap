/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DuplicatesList } from '../models/DuplicatesList';
import type { FindDuplicatesRequest } from '../models/FindDuplicatesRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AiService {
    /**
     * Get Similar Problems
     * Найти похожие проблемы для существующей проблемы.
     *
     * Методы:
     * - text: Только текстовое сходство (TF-IDF)
     * - location: Только геолокация (в радиусе 500м)
     * - combined: Комбинация текста и геолокации (рекомендуется)
     * @param entityId
     * @param method Метод: text/location/combined
     * @param limit
     * @returns DuplicatesList Successful Response
     * @throws ApiError
     */
    public static getSimilarProblemsApiV1AiSimilarProblemsEntityIdGet(
        entityId: number,
        method: string = 'combined',
        limit: number = 10,
    ): CancelablePromise<DuplicatesList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai/similar-problems/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            query: {
                'method': method,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Find Duplicates Before Create
     * Найти дубликаты перед созданием проблемы.
     * Используется на фронтенде для предупреждения пользователя.
     *
     * Создает временную проблему в памяти (не сохраняет в БД)
     * и ищет похожие существующие проблемы.
     * @param requestBody
     * @returns DuplicatesList Successful Response
     * @throws ApiError
     */
    public static findDuplicatesBeforeCreateApiV1AiFindDuplicatesPost(
        requestBody: FindDuplicatesRequest,
    ): CancelablePromise<DuplicatesList> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ai/find-duplicates',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Duplicates Stats
     * Статистика потенциальных дубликатов в городе.
     * Полезно для модераторов для очистки базы.
     * @param city Город для анализа
     * @param threshold Порог сходства
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDuplicatesStatsApiV1AiDuplicatesStatsGet(
        city: string,
        threshold: number = 0.8,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ai/duplicates-stats',
            query: {
                'city': city,
                'threshold': threshold,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
