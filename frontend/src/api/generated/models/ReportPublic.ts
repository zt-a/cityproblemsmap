/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ReportPublic = {
    entity_id: number;
    version: number;
    is_current: boolean;
    created_at: string;
    reporter_entity_id: number;
    target_type: string;
    target_entity_id: number;
    reason: string;
    description: (string | null);
    status: string;
    resolved_by_entity_id: (number | null);
    resolution_note: (string | null);
    /**
     * ID проблемы (для comment reports)
     */
    problem_entity_id?: (number | null);
};

