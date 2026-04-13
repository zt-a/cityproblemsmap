/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Публичные данные зоны.
 */
export type ZonePublic = {
    entity_id: number;
    version: number;
    name: string;
    zone_type: string;
    parent_entity_id: (number | null);
    country: (string | null);
    city: (string | null);
    center_lat: (number | null);
    center_lon: (number | null);
    total_problems: number;
    open_problems: number;
    solved_problems: number;
    pollution_index: number;
    traffic_index: number;
    risk_score: number;
    extra_data: (Record<string, any> | null);
};

