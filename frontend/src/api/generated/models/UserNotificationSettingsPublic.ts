/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UserNotificationSettingsPublic = {
    email_enabled?: boolean;
    email_on_comment?: boolean;
    email_on_status_change?: boolean;
    email_on_official_response?: boolean;
    email_on_problem_solved?: boolean;
    email_on_mention?: boolean;
    push_enabled?: boolean;
    push_on_comment?: boolean;
    push_on_status_change?: boolean;
    digest_enabled?: boolean;
    digest_frequency?: string;
    digest_day?: (number | null);
    quiet_hours_enabled?: boolean;
    quiet_hours_start?: (number | null);
    quiet_hours_end?: (number | null);
    entity_id: number;
    user_entity_id: number;
    version: number;
};

