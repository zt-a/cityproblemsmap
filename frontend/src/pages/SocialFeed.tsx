import { Activity, Loader2, FileText, MessageCircle, UserPlus, Award } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { useActivityFeed } from '../hooks/useSocial'
import { UserName } from '../components/UserName'

export const SocialFeed = () => {
  const navigate = useNavigate()
  const { data: feedData, isLoading } = useActivityFeed()

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'created_problem':
        return <FileText className="w-5 h-5 text-primary" />
      case 'commented':
        return <MessageCircle className="w-5 h-5 text-info" />
      case 'voted':
        return <Award className="w-5 h-5 text-warning" />
      case 'resolved_problem':
        return <Award className="w-5 h-5 text-success" />
      default:
        return <Activity className="w-5 h-5 text-text-muted" />
    }
  }

  const getActivityText = (activity: any) => {
    switch (activity.action_type) {
      case 'created_problem':
        return 'создал(а) проблему'
      case 'commented':
        return 'прокомментировал(а)'
      case 'voted':
        return 'проголосовал(а)'
      case 'resolved_problem':
        return 'решил(а) проблему'
      default:
        return activity.description || 'выполнил(а) действие'
    }
  }

  const handleActivityClick = (activity: any) => {
    if (activity.target_type === 'problem' && activity.target_id) {
      navigate(`/problems/${activity.target_id}`)
    }
  }

  return (
    <div className="min-h-screen bg-dark-bg py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <h1 className="text-3xl font-bold text-text-primary">Лента активности</h1>
          </div>
          <p className="text-text-secondary">
            Следите за активностью пользователей, на которых вы подписаны
          </p>
        </div>

        {/* Feed */}
        <div className="bg-dark-card rounded-2xl shadow-xl overflow-hidden border border-border">
          {isLoading ? (
            <div className="p-12 text-center">
              <Loader2 className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
              <p className="text-text-secondary">Загрузка ленты...</p>
            </div>
          ) : feedData && feedData.activities.length > 0 ? (
            <div className="divide-y divide-border">
              {feedData.activities.map((activity) => (
                <div
                  key={activity.id}
                  onClick={() => handleActivityClick(activity)}
                  className="p-4 hover:bg-dark-hover transition-colors cursor-pointer"
                >
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className="w-10 h-10 rounded-full bg-dark-hover flex items-center justify-center flex-shrink-0">
                      {getActivityIcon(activity.action_type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <UserName userId={activity.user_id} className="font-semibold" showAvatar />
                        <span className="text-text-secondary">{getActivityText(activity)}</span>
                      </div>

                      {activity.description && (
                        <p className="text-sm text-text-muted mb-2 line-clamp-2">
                          {activity.description}
                        </p>
                      )}

                      <p className="text-xs text-text-muted">
                        {formatDistanceToNow(new Date(activity.created_at), {
                          addSuffix: true,
                          locale: ru,
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <div className="w-16 h-16 bg-dark-hover rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-text-muted" />
              </div>
              <h3 className="text-lg font-semibold text-text-primary mb-2">Лента пуста</h3>
              <p className="text-sm text-text-secondary mb-6">
                Подпишитесь на пользователей, чтобы видеть их активность
              </p>
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Найти пользователей
              </button>
            </div>
          )}
        </div>

        {/* Total count */}
        {feedData && feedData.total > 0 && (
          <div className="mt-4 text-center text-sm text-text-muted">
            Показано {feedData.activities.length} из {feedData.total} событий
          </div>
        )}
      </div>
    </div>
  )
}
