/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AchievementResponse } from '../models/AchievementResponse';
import type { UserStatsResponse } from '../models/UserStatsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GamificationService {
    /**
     * Get My Stats
     * Получить статистику геймификации текущего пользователя
     * @returns UserStatsResponse Successful Response
     * @throws ApiError
     */
    public static getMyStatsApiV1GamificationStatsGet(): CancelablePromise<UserStatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/gamification/stats',
        });
    }
    /**
     * Get Achievements
     * Получить все достижения и прогресс пользователя
     * @returns AchievementResponse Successful Response
     * @throws ApiError
     */
    public static getAchievementsApiV1GamificationAchievementsGet(): CancelablePromise<Array<AchievementResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/gamification/achievements',
        });
    }
    /**
     * Check Achievements
     * Проверить и выдать новые достижения
     * @returns any Successful Response
     * @throws ApiError
     */
    public static checkAchievementsApiV1GamificationCheckAchievementsPost(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/gamification/check-achievements',
        });
    }
}
