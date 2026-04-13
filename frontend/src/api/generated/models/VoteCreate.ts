/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Данные для создания/изменения голоса.
 * Все поля опциональны — можно голосовать только по одной оси.
 * Например: проголосовать за правдивость но не оценивать срочность.
 */
export type VoteCreate = {
    is_true?: (boolean | null);
    urgency?: (number | null);
    impact?: (number | null);
    inconvenience?: (number | null);
};

