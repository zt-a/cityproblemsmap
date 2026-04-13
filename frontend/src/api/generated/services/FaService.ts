/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__api__v1__two_factor__MessageResponse } from '../models/app__api__v1__two_factor__MessageResponse';
import type { TwoFactorDisableRequest } from '../models/TwoFactorDisableRequest';
import type { TwoFactorSetupResponse } from '../models/TwoFactorSetupResponse';
import type { TwoFactorVerifyRequest } from '../models/TwoFactorVerifyRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FaService {
    /**
     * Setup 2Fa
     * Начать настройку 2FA.
     * Генерирует секрет и QR код URI для сканирования в приложении.
     * @returns TwoFactorSetupResponse Successful Response
     * @throws ApiError
     */
    public static setup2FaApiV12FaSetupPost(): CancelablePromise<TwoFactorSetupResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/2fa/setup',
        });
    }
    /**
     * Enable 2Fa
     * Активировать 2FA после проверки кода.
     * Пользователь должен ввести код из приложения для подтверждения.
     * @param requestBody
     * @returns app__api__v1__two_factor__MessageResponse Successful Response
     * @throws ApiError
     */
    public static enable2FaApiV12FaEnablePost(
        requestBody: TwoFactorVerifyRequest,
    ): CancelablePromise<app__api__v1__two_factor__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/2fa/enable',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Disable 2Fa
     * Отключить 2FA.
     * Требует пароль и код (или резервный код).
     * @param requestBody
     * @returns app__api__v1__two_factor__MessageResponse Successful Response
     * @throws ApiError
     */
    public static disable2FaApiV12FaDisablePost(
        requestBody: TwoFactorDisableRequest,
    ): CancelablePromise<app__api__v1__two_factor__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/2fa/disable',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Verify 2Fa Code
     * Проверить 2FA код (для тестирования).
     * @param requestBody
     * @returns app__api__v1__two_factor__MessageResponse Successful Response
     * @throws ApiError
     */
    public static verify2FaCodeApiV12FaVerifyPost(
        requestBody: TwoFactorVerifyRequest,
    ): CancelablePromise<app__api__v1__two_factor__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/2fa/verify',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get 2Fa Status
     * Получить статус 2FA для текущего пользователя
     * @returns any Successful Response
     * @throws ApiError
     */
    public static get2FaStatusApiV12FaStatusGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/2fa/status',
        });
    }
}
