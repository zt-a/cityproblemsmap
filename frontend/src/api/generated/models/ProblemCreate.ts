/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemNature } from './ProblemNature';
import type { ProblemType } from './ProblemType';
/**
 * Данные для создания новой проблемы.
 */
export type ProblemCreate = {
    title: string;
    description?: (string | null);
    country?: string;
    city: string;
    district?: (string | null);
    address?: (string | null);
    latitude: number;
    longitude: number;
    problem_type: ProblemType;
    nature?: ProblemNature;
    tags?: (Array<string> | null);
};

