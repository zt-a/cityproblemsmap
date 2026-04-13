/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ReportCreate = {
    /**
     * Тип цели: problem/comment/user
     */
    target_type: string;
    /**
     * ID цели
     */
    target_entity_id: number;
    /**
     * Причина: spam/offensive/inappropriate/other
     */
    reason: string;
    /**
     * Дополнительное описание
     */
    description?: (string | null);
};

