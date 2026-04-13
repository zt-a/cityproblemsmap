/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemNature } from './ProblemNature';
import type { ProblemStatus } from './ProblemStatus';
import type { ProblemType } from './ProblemType';
/**
 * Публичные данные проблемы — возвращаем в ответах.
 */
export type ProblemPublic = {
    entity_id: number;
    version: number;
    author_entity_id: number;
    zone_entity_id: (number | null);
    title: string;
    description: (string | null);
    country: string;
    city: string;
    district: (string | null);
    address: (string | null);
    latitude: (number | null);
    longitude: (number | null);
    problem_type: ProblemType;
    nature: ProblemNature;
    status: ProblemStatus;
    resolved_by_entity_id: (number | null);
    resolved_at: (string | null);
    resolution_note: (string | null);
    truth_score: number;
    urgency_score: number;
    impact_score: number;
    inconvenience_score: number;
    priority_score: number;
    vote_count: number;
    comment_count: number;
    tags: (Array<string> | null);
    change_reason: (string | null);
    created_at: (string | null);
};

