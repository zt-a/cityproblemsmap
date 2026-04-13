/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CommentCreate } from '../models/CommentCreate';
import type { CommentEdit } from '../models/CommentEdit';
import type { CommentPublic } from '../models/CommentPublic';
import type { CommentTree } from '../models/CommentTree';
import type { CursorPage_CommentPublic_ } from '../models/CursorPage_CommentPublic_';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class CommentsService {
    /**
     * Create Comment
     * Добавить комментарий к проблеме.
     * Если передан parent_entity_id — это ответ на другой комментарий.
     * @param problemEntityId
     * @param requestBody
     * @param xCaptchaToken CAPTCHA token
     * @param xCaptchaType CAPTCHA type: recaptcha, hcaptcha, turnstile
     * @returns CommentPublic Successful Response
     * @throws ApiError
     */
    public static createCommentApiV1ProblemsProblemEntityIdCommentsPost(
        problemEntityId: number,
        requestBody: CommentCreate,
        xCaptchaToken?: (string | null),
        xCaptchaType?: (string | null),
    ): CancelablePromise<CommentPublic> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/problems/{problem_entity_id}/comments',
            path: {
                'problem_entity_id': problemEntityId,
            },
            headers: {
                'x-captcha-token': xCaptchaToken,
                'x-captcha-type': xCaptchaType,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Comments
     * Дерево комментариев к проблеме.
     * Возвращает только актуальные версии в виде вложенной структуры.
     *
     * Пример ответа:
     * [
         * { entity_id: 1, content: "...", replies: [
             * { entity_id: 3, content: "...", replies: [] },
             * { entity_id: 4, content: "...", replies: [] },
             * ]},
             * { entity_id: 2, content: "...", replies: [] },
             * ]
             * @param problemEntityId
             * @returns CommentTree Successful Response
             * @throws ApiError
             */
            public static getCommentsApiV1ProblemsProblemEntityIdCommentsGet(
                problemEntityId: number,
            ): CancelablePromise<Array<CommentTree>> {
                return __request(OpenAPI, {
                    method: 'GET',
                    url: '/api/v1/problems/{problem_entity_id}/comments',
                    path: {
                        'problem_entity_id': problemEntityId,
                    },
                    errors: {
                        422: `Validation Error`,
                    },
                });
            }
            /**
             * Get Comments Paginated
             * Список комментариев с cursor-based пагинацией.
             * Используется для бесконечной прокрутки (infinite scroll).
             *
             * Cursor содержит информацию о последнем элементе предыдущей страницы.
             * @param problemEntityId
             * @param cursor Курсор для пагинации
             * @param limit Количество комментариев
             * @returns CursorPage_CommentPublic_ Successful Response
             * @throws ApiError
             */
            public static getCommentsPaginatedApiV1ProblemsProblemEntityIdCommentsPaginatedGet(
                problemEntityId: number,
                cursor?: (string | null),
                limit: number = 20,
            ): CancelablePromise<CursorPage_CommentPublic_> {
                return __request(OpenAPI, {
                    method: 'GET',
                    url: '/api/v1/problems/{problem_entity_id}/comments/paginated',
                    path: {
                        'problem_entity_id': problemEntityId,
                    },
                    query: {
                        'cursor': cursor,
                        'limit': limit,
                    },
                    errors: {
                        422: `Validation Error`,
                    },
                });
            }
            /**
             * Edit Comment
             * Редактировать свой комментарий.
             * Создаёт новую версию — оригинальный текст остаётся в БД.
             * @param problemEntityId
             * @param commentEntityId
             * @param requestBody
             * @returns CommentPublic Successful Response
             * @throws ApiError
             */
            public static editCommentApiV1ProblemsProblemEntityIdCommentsCommentEntityIdPatch(
                problemEntityId: number,
                commentEntityId: number,
                requestBody: CommentEdit,
            ): CancelablePromise<CommentPublic> {
                return __request(OpenAPI, {
                    method: 'PATCH',
                    url: '/api/v1/problems/{problem_entity_id}/comments/{comment_entity_id}',
                    path: {
                        'problem_entity_id': problemEntityId,
                        'comment_entity_id': commentEntityId,
                    },
                    body: requestBody,
                    mediaType: 'application/json',
                    errors: {
                        422: `Validation Error`,
                    },
                });
            }
            /**
             * Flag Comment
             * Пожаловаться на комментарий (любой пользователь)
             * или скрыть его (модератор/админ).
             *
             * Обычный пользователь: ставит is_flagged=True, виден модераторам.
             * Модератор/админ: дополнительно помечает comment_type='moderated'
             * что скрывает комментарий в публичном UI.
             * @param problemEntityId
             * @param commentEntityId
             * @param reason
             * @returns CommentPublic Successful Response
             * @throws ApiError
             */
            public static flagCommentApiV1ProblemsProblemEntityIdCommentsCommentEntityIdFlagPatch(
                problemEntityId: number,
                commentEntityId: number,
                reason: string,
            ): CancelablePromise<CommentPublic> {
                return __request(OpenAPI, {
                    method: 'PATCH',
                    url: '/api/v1/problems/{problem_entity_id}/comments/{comment_entity_id}/flag',
                    path: {
                        'problem_entity_id': problemEntityId,
                        'comment_entity_id': commentEntityId,
                    },
                    query: {
                        'reason': reason,
                    },
                    errors: {
                        422: `Validation Error`,
                    },
                });
            }
            /**
             * Get Comment History
             * История версий комментария — все редакции.
             * Только для модераторов и админов.
             * @param problemEntityId
             * @param commentEntityId
             * @returns CommentPublic Successful Response
             * @throws ApiError
             */
            public static getCommentHistoryApiV1ProblemsProblemEntityIdCommentsCommentEntityIdHistoryGet(
                problemEntityId: number,
                commentEntityId: number,
            ): CancelablePromise<Array<CommentPublic>> {
                return __request(OpenAPI, {
                    method: 'GET',
                    url: '/api/v1/problems/{problem_entity_id}/comments/{comment_entity_id}/history',
                    path: {
                        'problem_entity_id': problemEntityId,
                        'comment_entity_id': commentEntityId,
                    },
                    errors: {
                        422: `Validation Error`,
                    },
                });
            }
        }
