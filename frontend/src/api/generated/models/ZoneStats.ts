/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Детальная статистика зоны.
 * Используется для Digital Twin дашборда.
 */
export type ZoneStats = {
    entity_id: number;
    name: string;
    zone_type: string;
    total_problems: number;
    open_problems: number;
    solved_problems: number;
    rejected_problems: number;
    in_progress: number;
    solve_rate: number;
    pollution_index: number;
    traffic_index: number;
    risk_score: number;
    top_problem_types: Array<Record<string, any>>;
};

