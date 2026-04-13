/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MediaCategory } from './MediaCategory';
import type { MediaStatus } from './MediaStatus';
import type { MediaType } from './MediaType';
/**
 * Публичные данные медиафайла.
 */
export type MediaPublic = {
    entity_id: number;
    version: number;
    problem_entity_id: number;
    uploader_entity_id: number;
    media_type: MediaType;
    media_category: MediaCategory;
    status: MediaStatus;
    url: string;
    thumbnail_url: (string | null);
    file_size: (number | null);
    caption: (string | null);
    display_order: number;
    duration_seconds: (number | null);
    video_width: (number | null);
    video_height: (number | null);
    is_processed: number;
    hls_url: (string | null);
    exif_lat: (number | null);
    exif_lon: (number | null);
    exif_taken_at: (string | null);
    ai_tags: (string | null);
    is_current: boolean;
    created_at: string;
};

