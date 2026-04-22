/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NotificationType } from './NotificationType';
export type NotificationPublic = {
    notification_type: NotificationType;
    title: string;
    message: string;
    problem_entity_id?: (number | null);
    comment_entity_id?: (number | null);
    entity_id: number;
    user_entity_id: number;
    actor_entity_id?: (number | null);
    is_read: boolean;
    created_at: string;
    updated_at?: (string | null);
};

