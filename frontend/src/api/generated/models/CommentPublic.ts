/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Публичные данные комментария.
 */
export type CommentPublic = {
    entity_id: number;
    version: number;
    problem_entity_id: number;
    author_entity_id: number;
    parent_entity_id: (number | null);
    content: string;
    comment_type: string;
    is_flagged: boolean;
    is_current: boolean;
    created_at: string;
};

