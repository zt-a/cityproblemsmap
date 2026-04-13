/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemList } from '../models/ProblemList';
import type { ZoneCreate } from '../models/ZoneCreate';
import type { ZonePublic } from '../models/ZonePublic';
import type { ZoneStats } from '../models/ZoneStats';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ZonesService {
    /**
     * Create Zone
     * Создать зону — только admin или official.
     * Зоны создаются вручную администраторами системы.
     * @param requestBody
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static createZoneApiV1ZonesPost(
        requestBody: ZoneCreate,
    ): CancelablePromise<ZonePublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/zones/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Zones
     * Список всех зон.
     * Используется для построения иерархии на карте.
     * @param zoneType country / city / district / neighborhood
     * @param city Фильтр по городу
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static listZonesApiV1ZonesGet(
        zoneType?: (string | null),
        city?: (string | null),
    ): CancelablePromise<Array<ZonePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/',
            query: {
                'zone_type': zoneType,
                'city': city,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Zone
     * Получить зону по entity_id.
     * @param entityId
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static getZoneApiV1ZonesEntityIdGet(
        entityId: number,
    ): CancelablePromise<ZonePublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Zone Stats
     * Детальная статистика зоны для Digital Twin дашборда.
     * Включает распределение по типам проблем и индексы.
     * @param entityId
     * @returns ZoneStats Successful Response
     * @throws ApiError
     */
    public static getZoneStatsApiV1ZonesEntityIdStatsGet(
        entityId: number,
    ): CancelablePromise<ZoneStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/{entity_id}/stats',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Zone Problems
     * Все проблемы зоны с фильтрацией и пагинацией.
     * Удобно для отображения проблем конкретного района на карте.
     * @param entityId
     * @param status
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static getZoneProblemsApiV1ZonesEntityIdProblemsGet(
        entityId: number,
        status?: (string | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/{entity_id}/problems',
            path: {
                'entity_id': entityId,
            },
            query: {
                'status': status,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Zone Children
     * Дочерние зоны — подрайоны.
     * Например: город Бишкек → [Первомайский, Свердловский, Октябрьский, Ленинский]
     * @param entityId
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static getZoneChildrenApiV1ZonesEntityIdChildrenGet(
        entityId: number,
    ): CancelablePromise<Array<ZonePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/{entity_id}/children',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Zone History
     * История версий зоны — как менялась статистика со временем.
     * Только для админов — данные для аналитики и Digital Twin.
     * @param entityId
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static getZoneHistoryApiV1ZonesEntityIdHistoryGet(
        entityId: number,
    ): CancelablePromise<Array<ZonePublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/zones/{entity_id}/history',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Recalculate Zone
     * Принудительный пересчёт статистики зоны.
     * Обычно вызывается автоматически Celery — этот эндпоинт для ручного запуска.
     * @param entityId
     * @returns ZonePublic Successful Response
     * @throws ApiError
     */
    public static recalculateZoneApiV1ZonesEntityIdRecalculatePost(
        entityId: number,
    ): CancelablePromise<ZonePublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/zones/{entity_id}/recalculate',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
