/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimEventStatus } from '../models/SimEventStatus';
import type { SimulationEventCreate } from '../models/SimulationEventCreate';
import type { SimulationEventPublic } from '../models/SimulationEventPublic';
import type { SimulationEventStatusUpdate } from '../models/SimulationEventStatusUpdate';
import type { SimulationImpactPreview } from '../models/SimulationImpactPreview';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SimulationsService {
    /**
     * Preview Impact
     * Предпросмотр влияния события на зону.
     * Вызывается перед созданием — показывает что изменится.
     *
     * Пример: дорожные работы на главной улице
     * → трафик +30%, загрязнение +10%, риск +5%
     * @param zoneEntityId
     * @param trafficImpact
     * @param pollutionImpact
     * @param riskDelta
     * @returns SimulationImpactPreview Successful Response
     * @throws ApiError
     */
    public static previewImpactApiV1SimulationsPreviewPost(
        zoneEntityId: number,
        trafficImpact?: number,
        pollutionImpact?: number,
        riskDelta?: number,
    ): CancelablePromise<SimulationImpactPreview> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/simulations/preview',
            query: {
                'zone_entity_id': zoneEntityId,
                'traffic_impact': trafficImpact,
                'pollution_impact': pollutionImpact,
                'risk_delta': riskDelta,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Event
     * Создать симуляционное событие.
     * Только admin или official.
     *
     * Событие создаётся со статусом planned —
     * индексы зоны не меняются до перевода в active.
     * @param requestBody
     * @returns SimulationEventPublic Successful Response
     * @throws ApiError
     */
    public static createEventApiV1SimulationsPost(
        requestBody: SimulationEventCreate,
    ): CancelablePromise<SimulationEventPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/simulations/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Events
     * Список событий с фильтрацией.
     * Доступен публично — пользователи видят что планируется в городе.
     * @param zoneEntityId
     * @param status
     * @returns SimulationEventPublic Successful Response
     * @throws ApiError
     */
    public static listEventsApiV1SimulationsGet(
        zoneEntityId?: (number | null),
        status?: (SimEventStatus | null),
    ): CancelablePromise<Array<SimulationEventPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/simulations/',
            query: {
                'zone_entity_id': zoneEntityId,
                'status': status,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Event
     * Получить событие по entity_id.
     * @param entityId
     * @returns SimulationEventPublic Successful Response
     * @throws ApiError
     */
    public static getEventApiV1SimulationsEntityIdGet(
        entityId: number,
    ): CancelablePromise<SimulationEventPublic> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/simulations/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Event Status
     * Сменить статус события.
     *
     * Переходы статусов и их эффекты:
     * planned → active    : применяет дельты к индексам зоны
     * active  → completed : откатывает дельты (работы завершены)
     * active  → cancelled : откатывает дельты (работы отменены)
     * planned → cancelled : без изменений индексов (ещё не применялись)
     *
     * Каждый переход = новая версия события + новая версия зоны.
     * @param entityId
     * @param requestBody
     * @returns SimulationEventPublic Successful Response
     * @throws ApiError
     */
    public static updateEventStatusApiV1SimulationsEntityIdStatusPatch(
        entityId: number,
        requestBody: SimulationEventStatusUpdate,
    ): CancelablePromise<SimulationEventPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/simulations/{entity_id}/status',
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
    /**
     * Get Event History
     * История версий события.
     * Показывает все смены статуса с временными метками.
     * @param entityId
     * @returns SimulationEventPublic Successful Response
     * @throws ApiError
     */
    public static getEventHistoryApiV1SimulationsEntityIdHistoryGet(
        entityId: number,
    ): CancelablePromise<Array<SimulationEventPublic>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/simulations/{entity_id}/history',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
