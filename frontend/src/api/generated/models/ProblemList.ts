/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProblemPublic } from './ProblemPublic';
/**
 * Список проблем с пагинацией.
 */
export type ProblemList = {
    items: Array<ProblemPublic>;
    total: number;
    offset: number;
    limit: number;
};

