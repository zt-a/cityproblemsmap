import { MessageSquare, Flag, User } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { UserName } from '../UserName'
import { RoleBadge } from '../RoleBadge'
import { useUser } from '../../hooks/useUser'
import type { CommentTree } from '../../api/generated/models/CommentTree'

interface CommentItemProps {
  comment: CommentTree
  onReply: (commentId: number) => void
  onReport: (commentId: number, authorId: number) => void
  isAuthenticated: boolean
  level?: number
  parentAuthorId?: number
}

export function CommentItem({
  comment,
  onReply,
  onReport,
  isAuthenticated,
  level = 0,
  parentAuthorId
}: CommentItemProps) {
  const indent = level * 32 // 32px per level (ml-8 = 2rem = 32px)
  const { data: author } = useUser(comment.author_entity_id)

  const isOfficialComment = comment.comment_type === 'official_response'

  return (
    <div className="space-y-3">
      <div
        className={`flex gap-3 ${isOfficialComment ? 'bg-primary/5 -mx-4 px-4 py-3 rounded-lg border-l-2 border-primary' : ''}`}
        style={{ marginLeft: `${indent}px` }}
      >
        <div className={`${level === 0 ? 'w-10 h-10' : 'w-8 h-8'} rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0`}>
          <User className={`${level === 0 ? 'w-5 h-5' : 'w-4 h-4'} text-primary`} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`font-medium text-text-primary ${level > 0 ? 'text-sm' : ''}`}>
              <UserName userId={comment.author_entity_id} />
            </span>
            {author?.role && <RoleBadge role={author.role} />}
            {isOfficialComment && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full border font-medium text-xs bg-primary/20 text-primary border-primary/30">
                Официальный ответ
              </span>
            )}
            <span className="text-xs text-text-muted">
              {formatDistanceToNow(new Date(comment.created_at), {
                addSuffix: true,
                locale: ru,
              })}
            </span>
          </div>

          {/* Reply indicator */}
          {parentAuthorId && (
            <div className="text-xs text-primary mb-1">
              Ответ на <UserName userId={parentAuthorId} />
            </div>
          )}

          <p className="text-text-secondary text-sm mb-2 whitespace-pre-wrap">
            {comment.content}
          </p>

          <div className="flex gap-3 text-xs">
            {isAuthenticated && (
              <button
                onClick={() => onReply(comment.entity_id)}
                className="text-text-muted hover:text-primary transition-colors duration-200 flex items-center gap-1"
              >
                <MessageSquare className="w-3 h-3" />
                Ответить
              </button>
            )}
            <button
              onClick={() => onReport(comment.entity_id, comment.author_entity_id)}
              className="text-text-muted hover:text-danger transition-colors duration-200 flex items-center gap-1"
            >
              <Flag className="w-3 h-3" />
              Пожаловаться
            </button>
          </div>
        </div>
      </div>

      {/* Recursive replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="space-y-3">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.entity_id}
              comment={reply}
              onReply={onReply}
              onReport={onReport}
              isAuthenticated={isAuthenticated}
              level={level + 1}
              parentAuthorId={comment.author_entity_id}
            />
          ))}
        </div>
      )}
    </div>
  )
}
