/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Одна точка тепловой карты.
 * Фронт рисует heatmap из этих точек.
 */
export type HeatmapPoint = {
    latitude: number;
    longitude: number;
    weight: number;
    problem_count: number;
    avg_priority: number;
};

