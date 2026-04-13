/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimEventType } from './SimEventType';
/**
 * Создание симуляционного события — только official/admin.
 */
export type SimulationEventCreate = {
    zone_entity_id: number;
    event_type: SimEventType;
    title: string;
    description?: (string | null);
    planned_start?: (string | null);
    planned_end?: (string | null);
    traffic_impact?: number;
    pollution_impact?: number;
    risk_delta?: number;
    simulation_params?: (Record<string, any> | null);
};

