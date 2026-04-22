/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemType } from './ProblemType';
/**
 * Обновление проблемы (только автор).
 */
export type ProblemUpdate = {
    title?: (string | null);
    description?: (string | null);
    address?: (string | null);
    latitude?: (number | null);
    longitude?: (number | null);
    problem_type?: (ProblemType | null);
    tags?: (Array<string> | null);
};

