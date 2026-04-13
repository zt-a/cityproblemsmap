import { useState, useEffect } from 'react';
import { Users, UserPlus, TrendingUp, Activity } from 'lucide-react';
import { SocialService } from '../api/generated/services/SocialService';
import { useNavigate } from 'react-router-dom';

export const SocialFeed = () => {
  const navigate = useNavigate();
  const [feed, setFeed] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadFeed();
  }, []);

  const loadFeed = async () => {
    setIsLoading(true);
    try {
      const data = await SocialService.getActivityFeedApiV1SocialFeedGet();
      setFeed(data.items || []);
    } catch (error) {
      console.error('Failed to load feed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} д назад`;

    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
    });
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'problem_created':
        return '📝';
      case 'problem_resolved':
        return '✅';
      case 'comment_added':
        return '💬';
      case 'user_followed':
        return '👤';
      case 'achievement_unlocked':
        return '🏆';
      default:
        return '📌';
    }
  };

  const getActivityText = (activity: any) => {
    switch (activity.type) {
      case 'problem_created':
        return `создал(а) проблему "${activity.problem_title}"`;
      case 'problem_resolved':
        return `решил(а) проблему "${activity.problem_title}"`;
      case 'comment_added':
        return `прокомментировал(а) проблему "${activity.problem_title}"`;
      case 'user_followed':
        return `подписался на ${activity.target_username}`;
      case 'achievement_unlocked':
        return `получил(а) достижение "${activity.achievement_name}"`;
      default:
        return activity.description || 'выполнил действие';
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#3B82F6]/10 rounded-lg">
            <Activity className="w-6 h-6 text-[#3B82F6]" />
          </div>
          <h1 className="text-3xl font-bold text-[#E5E7EB]">Лента активности</h1>
        </div>
        <p className="text-[#9CA3AF]">
          Следите за активностью пользователей, на которых вы подписаны
        </p>
      </div>

      {/* Feed */}
      <div className="bg-[#111827] rounded-xl shadow-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <p className="text-[#9CA3AF]">Загрузка...</p>
          </div>
        ) : feed.length > 0 ? (
          <div className="divide-y divide-[#374151]">
            {feed.map((activity, index) => (
              <div key={index} className="p-4 hover:bg-[#1F2937] transition-colors">
                <div className="flex items-start gap-4">
                  {/* Avatar */}
                  <img
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${activity.username}`}
                    alt={activity.username}
                    className="w-12 h-12 rounded-full"
                  />

                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-[#E5E7EB]">{activity.username}</span>
                      <span className="text-2xl">{getActivityIcon(activity.type)}</span>
                      <span className="text-sm text-[#9CA3AF]">{getActivityText(activity)}</span>
                    </div>
                    <p className="text-xs text-[#6B7280]">{formatDate(activity.created_at)}</p>

                    {/* Action Button */}
                    {activity.problem_id && (
                      <button
                        onClick={() => navigate(`/problems/${activity.problem_id}`)}
                        className="mt-2 text-sm text-[#3B82F6] hover:text-[#60A5FA]"
                      >
                        Посмотреть →
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-[#374151] rounded-full flex items-center justify-center mx-auto mb-4">
              <Activity className="w-8 h-8 text-[#6B7280]" />
            </div>
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Лента пуста</h3>
            <p className="text-sm text-[#9CA3AF] mb-4">
              Подпишитесь на пользователей, чтобы видеть их активность
            </p>
            <button
              onClick={() => navigate('/users')}
              className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
            >
              Найти пользователей
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
