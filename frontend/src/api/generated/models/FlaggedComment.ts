/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Комментарий с жалобой.
 */
export type FlaggedComment = {
    entity_id: number;
    problem_entity_id: number;
    author_entity_id: number;
    content: string;
    is_flagged: boolean;
    flag_reason: (string | null);
    created_at: string;
};

