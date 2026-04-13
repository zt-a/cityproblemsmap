/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Одна запись истории репутации.
 */
export type ReputationLogPublic = {
    id: number;
    delta: number;
    reason: string;
    note: (string | null);
    related_problem_entity_id: (number | null);
    snapshot_reputation: number;
    created_at: string;
};

