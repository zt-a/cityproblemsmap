/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UserNotificationSettingsUpdate = {
    email_enabled?: (boolean | null);
    email_on_comment?: (boolean | null);
    email_on_status_change?: (boolean | null);
    email_on_official_response?: (boolean | null);
    email_on_problem_solved?: (boolean | null);
    email_on_mention?: (boolean | null);
    push_enabled?: (boolean | null);
    push_on_comment?: (boolean | null);
    push_on_status_change?: (boolean | null);
    digest_enabled?: (boolean | null);
    digest_frequency?: (string | null);
    digest_day?: (number | null);
    quiet_hours_enabled?: (boolean | null);
    quiet_hours_start?: (number | null);
    quiet_hours_end?: (number | null);
};

