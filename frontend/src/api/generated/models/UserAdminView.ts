/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
import type { UserStatus } from './UserStatus';
/**
 * Расширенный профиль пользователя для админа.
 */
export type UserAdminView = {
    entity_id: number;
    version: number;
    username: string;
    email: string;
    role: UserRole;
    status: UserStatus;
    country: (string | null);
    city: (string | null);
    district: (string | null);
    reputation: number;
    is_verified: boolean;
    created_at: string;
};

