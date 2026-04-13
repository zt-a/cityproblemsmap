/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReputationLogPublic } from './ReputationLogPublic';
/**
 * История репутации с текущим значением.
 */
export type ReputationHistory = {
    current_reputation: number;
    logs: Array<ReputationLogPublic>;
};

