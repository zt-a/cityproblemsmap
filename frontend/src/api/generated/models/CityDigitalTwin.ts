/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CityOverview } from './CityOverview';
import type { HeatmapPoint } from './HeatmapPoint';
import type { PeriodStats } from './PeriodStats';
import type { ResponseTimeStats } from './ResponseTimeStats';
import type { ZoneIndexes } from './ZoneIndexes';
/**
 * Полный Digital Twin срез города.
 * Всё что нужно для симуляций и AI.
 */
export type CityDigitalTwin = {
    city: string;
    snapshot_at: string;
    overview: CityOverview;
    zone_indexes: Array<ZoneIndexes>;
    heatmap: Array<HeatmapPoint>;
    response_time: ResponseTimeStats;
    period_trend: Array<PeriodStats>;
};

