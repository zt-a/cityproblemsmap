/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemTypeStats } from './ProblemTypeStats';
import type { StatusDistribution } from './StatusDistribution';
/**
 * Общая сводка по городу.
 * Главный экран дашборда.
 */
export type CityOverview = {
    city: string;
    total_problems: number;
    status_distribution: StatusDistribution;
    by_type: Array<ProblemTypeStats>;
    avg_priority_score: number;
    avg_truth_score: number;
    most_active_zone: (string | null);
    solve_rate: number;
};

