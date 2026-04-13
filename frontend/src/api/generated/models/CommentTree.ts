/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Комментарий с вложенными ответами.
 * Используется для отображения треда на фронте.
 */
export type CommentTree = {
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
    replies?: Array<CommentTree>;
};

