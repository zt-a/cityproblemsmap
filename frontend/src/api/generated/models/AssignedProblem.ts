/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemStatus } from './ProblemStatus';
import type { ProblemType } from './ProblemType';
/**
 * Проблема назначенная на официала.
 */
export type AssignedProblem = {
    entity_id: number;
    title: string;
    description: (string | null);
    city: string;
    district: (string | null);
    address: (string | null);
    problem_type: ProblemType;
    status: ProblemStatus;
    priority_score: number;
    created_at: string;
    latitude: (number | null);
    longitude: (number | null);
};

