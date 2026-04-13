/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangeRoleRequest } from '../models/ChangeRoleRequest';
import type { ProblemList } from '../models/ProblemList';
import type { ProblemPublic } from '../models/ProblemPublic';
import type { ProblemStatus } from '../models/ProblemStatus';
import type { RejectProblemRequest } from '../models/RejectProblemRequest';
import type { SuspendRequest } from '../models/SuspendRequest';
import type { SystemStats } from '../models/SystemStats';
import type { UserAdminView } from '../models/UserAdminView';
import type { UserList } from '../models/UserList';
import type { UserRole } from '../models/UserRole';
import type { UserStatus } from '../models/UserStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AdminService {
    /**
     * List Users
     * Список всех пользователей.
     * Доступно: moderator, official, admin.
     *
     * Фильтры: роль, статус, город, поиск по username/email.
     * @param role
     * @param status
     * @param city
     * @param search Поиск по username или email
     * @param offset
     * @param limit
     * @returns UserList Successful Response
     * @throws ApiError
     */
    public static listUsersApiV1AdminUsersGet(
        role?: (UserRole | null),
        status?: (UserStatus | null),
        city?: (string | null),
        search?: (string | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<UserList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/users',
            query: {
                'role': role,
                'status': status,
                'city': city,
                'search': search,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Admin
     * Детальный профиль пользователя для модерации.
     * Включает email и полный статус.
     * @param entityId
     * @returns UserAdminView Successful Response
     * @throws ApiError
     */
    public static getUserAdminApiV1AdminUsersEntityIdGet(
        entityId: number,
    ): CancelablePromise<UserAdminView> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/users/{entity_id}',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Change User Role
     * Смена роли пользователя.
     * Только admin.
     *
     * Нельзя менять роль самому себе —
     * защита от случайного снятия прав.
     * @param entityId
     * @param requestBody
     * @returns UserAdminView Successful Response
     * @throws ApiError
     */
    public static changeUserRoleApiV1AdminUsersEntityIdRolePatch(
        entityId: number,
        requestBody: ChangeRoleRequest,
    ): CancelablePromise<UserAdminView> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/users/{entity_id}/role',
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
     * Suspend User
     * Блокировка пользователя.
     * Доступно: moderator, admin.
     *
     * Модератор не может заблокировать админа или другого модератора.
     * @param entityId
     * @param requestBody
     * @returns UserAdminView Successful Response
     * @throws ApiError
     */
    public static suspendUserApiV1AdminUsersEntityIdSuspendPatch(
        entityId: number,
        requestBody: SuspendRequest,
    ): CancelablePromise<UserAdminView> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/users/{entity_id}/suspend',
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
     * Unsuspend User
     * Снятие блокировки пользователя.
     * @param entityId
     * @returns UserAdminView Successful Response
     * @throws ApiError
     */
    public static unsuspendUserApiV1AdminUsersEntityIdUnsuspendPatch(
        entityId: number,
    ): CancelablePromise<UserAdminView> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/users/{entity_id}/unsuspend',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User History
     * Полная история версий пользователя.
     * Только admin — видит все изменения профиля.
     * @param entityId
     * @returns UserAdminView Successful Response
     * @throws ApiError
     */
    public static getUserHistoryApiV1AdminUsersEntityIdHistoryGet(
        entityId: number,
    ): CancelablePromise<Array<UserAdminView>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/users/{entity_id}/history',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Problems Admin
     * Все проблемы включая rejected и archived.
     * Доступно: moderator, official, admin.
     * @param status
     * @param city
     * @param problemType
     * @param authorId
     * @param offset
     * @param limit
     * @returns ProblemList Successful Response
     * @throws ApiError
     */
    public static listProblemsAdminApiV1AdminProblemsGet(
        status?: (ProblemStatus | null),
        city?: (string | null),
        problemType?: (string | null),
        authorId?: (number | null),
        offset?: number,
        limit: number = 20,
    ): CancelablePromise<ProblemList> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/problems',
            query: {
                'status': status,
                'city': city,
                'problem_type': problemType,
                'author_id': authorId,
                'offset': offset,
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reject Problem
     * Отклонить проблему — статус rejected.
     * Доступно: moderator, official, admin.
     *
     * Используется когда проблема нарушает правила
     * или является заведомо ложной.
     * @param entityId
     * @param requestBody
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static rejectProblemApiV1AdminProblemsEntityIdRejectPatch(
        entityId: number,
        requestBody: RejectProblemRequest,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/problems/{entity_id}/reject',
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
     * Restore Problem
     * Восстановить отклонённую проблему — статус open.
     * Только admin.
     * @param entityId
     * @returns ProblemPublic Successful Response
     * @throws ApiError
     */
    public static restoreProblemApiV1AdminProblemsEntityIdRestorePatch(
        entityId: number,
    ): CancelablePromise<ProblemPublic> {
        return __request(OpenAPI, {
            method: 'PATCH',
            url: '/api/v1/admin/problems/{entity_id}/restore',
            path: {
                'entity_id': entityId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get System Stats
     * Общая статистика системы.
     * Только admin.
     * @returns SystemStats Successful Response
     * @throws ApiError
     */
    public static getSystemStatsApiV1AdminStatsGet(): CancelablePromise<SystemStats> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/admin/stats',
        });
    }
}
