/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Предпросмотр влияния события на зону.
 * Показывается перед созданием — "что изменится если запустить это событие".
 */
export type SimulationImpactPreview = {
    zone_entity_id: number;
    zone_name: string;
    current_pollution_index: number;
    current_traffic_index: number;
    current_risk_score: number;
    projected_pollution: number;
    projected_traffic: number;
    projected_risk: number;
    delta_summary: string;
};

