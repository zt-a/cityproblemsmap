/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserPublic } from './UserPublic';
/**
 * Ответ после успешного логина/регистрации.
 */
export type TokenResponse = {
    access_token: string;
    refresh_token: string;
    token_type?: string;
    user: UserPublic;
};

