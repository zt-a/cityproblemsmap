/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type BanUserRequest = {
    /**
     * Причина блокировки
     */
    reason: string;
    /**
     * Длительность в днях (None = постоянно)
     */
    duration_days?: (number | null);
};

