/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemType } from '../models/ProblemType';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DuplicatesService {
    /**
     * Check Duplicates
     * Проверить наличие дубликатов перед созданием проблемы.
     *
     * Использование:
     * ```
     * GET /api/v1/duplicates/check?lat=42.8746&lon=74.5698&problem_type=pothole&title=Яма на дороге
     * ```
     *
     * Ответ:
     * ```json
     * {
         * "has_duplicates": true,
         * "duplicates": [
             * {
                 * "entity_id": 123,
                 * "title": "Большая яма на дороге",
                 * "status": "open",
                 * "vote_count": 15,
                 * "similarity": 0.85,
                 * "distance_m": 45,
                 * "created_at": "2026-04-01T10:00:00",
                 * "url": "/problems/123"
                 * }
                 * ],
                 * "message": "Найдено 1 похожих проблем. Возможно, стоит проголосовать за существующую?"
                 * }
                 * ```
                 * @param lat Широта
                 * @param lon Долгота
                 * @param problemType Тип проблемы
                 * @param title Заголовок проблемы
                 * @param threshold Порог похожести (0.0-1.0)
                 * @returns any Successful Response
                 * @throws ApiError
                 */
                public static checkDuplicatesApiV1DuplicatesCheckGet(
                    lat: number,
                    lon: number,
                    problemType: ProblemType,
                    title: string,
                    threshold: number = 0.7,
                ): CancelablePromise<any> {
                    return __request(OpenAPI, {
                        method: 'GET',
                        url: '/api/v1/duplicates/check',
                        query: {
                            'lat': lat,
                            'lon': lon,
                            'problem_type': problemType,
                            'title': title,
                            'threshold': threshold,
                        },
                        errors: {
                            422: `Validation Error`,
                        },
                    });
                }
            }
