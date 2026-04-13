/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Агрегированная статистика голосов по проблеме.
 * Показывается на странице проблемы.
 */
export type VoteStats = {
    total_votes: number;
    true_count: number;
    fake_count: number;
    truth_score: number;
    urgency_score: number;
    impact_score: number;
    inconvenience_score: number;
    priority_score: number;
};

