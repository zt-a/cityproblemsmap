/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { app__schemas__auth__MessageResponse } from '../models/app__schemas__auth__MessageResponse';
import type { ChangePasswordRequest } from '../models/ChangePasswordRequest';
import type { ForgotPasswordRequest } from '../models/ForgotPasswordRequest';
import type { LogoutRequest } from '../models/LogoutRequest';
import type { RefreshRequest } from '../models/RefreshRequest';
import type { ResetPasswordRequest } from '../models/ResetPasswordRequest';
import type { TokenResponse } from '../models/TokenResponse';
import type { UserLogin } from '../models/UserLogin';
import type { UserRegister } from '../models/UserRegister';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Register
     * Регистрация нового пользователя.
     * @param requestBody
     * @param xCaptchaToken CAPTCHA token
     * @param xCaptchaType CAPTCHA type: recaptcha, hcaptcha, turnstile
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public static registerApiV1AuthRegisterPost(
        requestBody: UserRegister,
        xCaptchaToken?: (string | null),
        xCaptchaType?: (string | null),
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/register',
            headers: {
                'x-captcha-token': xCaptchaToken,
                'x-captcha-type': xCaptchaType,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Login
     * Логин по email + паролю.
     * @param requestBody
     * @param xCaptchaToken CAPTCHA token
     * @param xCaptchaType CAPTCHA type: recaptcha, hcaptcha, turnstile
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public static loginApiV1AuthLoginPost(
        requestBody: UserLogin,
        xCaptchaToken?: (string | null),
        xCaptchaType?: (string | null),
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/login',
            headers: {
                'x-captcha-token': xCaptchaToken,
                'x-captcha-type': xCaptchaType,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Refresh
     * Обновление access токена через refresh токен.
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public static refreshApiV1AuthRefreshPost(
        requestBody: RefreshRequest,
    ): CancelablePromise<TokenResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/refresh',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout
     * Инвалидация refresh токена через Redis blacklist.
     * После logout — токен больше не работает для /refresh.
     * @param requestBody
     * @returns app__schemas__auth__MessageResponse Successful Response
     * @throws ApiError
     */
    public static logoutApiV1AuthLogoutPost(
        requestBody: LogoutRequest,
    ): CancelablePromise<app__schemas__auth__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/logout',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Change Password
     * Смена пароля авторизованного пользователя.
     * Требует старый пароль для подтверждения.
     * Создаёт новую версию пользователя.
     * @param requestBody
     * @returns app__schemas__auth__MessageResponse Successful Response
     * @throws ApiError
     */
    public static changePasswordApiV1AuthChangePasswordPost(
        requestBody: ChangePasswordRequest,
    ): CancelablePromise<app__schemas__auth__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/change-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Forgot Password
     * Запрос сброса пароля.
     * Отправляет письмо со ссылкой если email найден.
     *
     * Всегда возвращает 200 — не раскрываем существует ли email.
     * @param requestBody
     * @returns app__schemas__auth__MessageResponse Successful Response
     * @throws ApiError
     */
    public static forgotPasswordApiV1AuthForgotPasswordPost(
        requestBody: ForgotPasswordRequest,
    ): CancelablePromise<app__schemas__auth__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/forgot-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reset Password
     * Сброс пароля по токену из письма.
     * Токен одноразовый — удаляется после использования.
     * @param requestBody
     * @returns app__schemas__auth__MessageResponse Successful Response
     * @throws ApiError
     */
    public static resetPasswordApiV1AuthResetPasswordPost(
        requestBody: ResetPasswordRequest,
    ): CancelablePromise<app__schemas__auth__MessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/auth/reset-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
