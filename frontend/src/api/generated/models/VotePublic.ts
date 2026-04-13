/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Публичные данные голоса.
 */
export type VotePublic = {
    entity_id: number;
    version: number;
    problem_entity_id: number;
    user_entity_id: number;
    is_true: (boolean | null);
    urgency: (number | null);
    impact: (number | null);
    inconvenience: (number | null);
    weight: number;
    is_current: boolean;
};

