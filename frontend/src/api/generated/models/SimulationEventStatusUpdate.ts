/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SimEventStatus } from './SimEventStatus';
/**
 * Смена статуса события.
 */
export type SimulationEventStatusUpdate = {
    status: SimEventStatus;
    actual_start?: (string | null);
    actual_end?: (string | null);
};

