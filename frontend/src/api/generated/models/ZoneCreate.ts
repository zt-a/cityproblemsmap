/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Создание новой зоны — только admin/official.
 */
export type ZoneCreate = {
    name: string;
    zone_type: string;
    parent_entity_id?: (number | null);
    country?: (string | null);
    city?: (string | null);
    center_lat?: (number | null);
    center_lon?: (number | null);
    extra_data?: (Record<string, any> | null);
};

