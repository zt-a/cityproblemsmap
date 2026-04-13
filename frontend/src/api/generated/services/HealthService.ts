/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HealthService {
    /**
     * Health Check
     * Базовая проверка работоспособности API
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthCheckApiV1HealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/',
        });
    }
    /**
     * Detailed Health Check
     * Детальная проверка всех компонентов системы.
     * Проверяет: PostgreSQL, Redis, Celery
     * @returns any Successful Response
     * @throws ApiError
     */
    public static detailedHealthCheckApiV1HealthDetailedGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/detailed',
        });
    }
    /**
     * Readiness Check
     * Проверка готовности к приёму запросов (для Kubernetes).
     * Проверяет только критичные сервисы: БД и Redis.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static readinessCheckApiV1HealthReadyGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/ready',
        });
    }
    /**
     * Liveness Check
     * Проверка живости приложения (для Kubernetes).
     * Простая проверка что процесс работает.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static livenessCheckApiV1HealthLiveGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/health/live',
        });
    }
}
