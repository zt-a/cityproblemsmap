/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimEventStatus } from './SimEventStatus';
import type { SimEventType } from './SimEventType';
/**
 * Публичные данные события.
 */
export type SimulationEventPublic = {
    entity_id: number;
    version: number;
    zone_entity_id: number;
    created_by_entity_id: number;
    event_type: SimEventType;
    status: SimEventStatus;
    title: string;
    description: (string | null);
    planned_start: (string | null);
    planned_end: (string | null);
    actual_start: (string | null);
    actual_end: (string | null);
    traffic_impact: number;
    pollution_impact: number;
    risk_delta: number;
    simulation_params: (Record<string, any> | null);
    is_current: boolean;
    created_at: string;
};

