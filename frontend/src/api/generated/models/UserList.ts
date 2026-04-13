/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserAdminView } from './UserAdminView';
/**
 * Список пользователей с пагинацией.
 */
export type UserList = {
    items: Array<UserAdminView>;
    total: number;
    offset: number;
    limit: number;
};

