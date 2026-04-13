import { useState, useEffect } from 'react';
import { Trophy, Award, TrendingUp, Target, Star, Lock } from 'lucide-react';
import { GamificationService } from '../api/generated/services/GamificationService';
import type { AchievementResponse } from '../api/generated/models/AchievementResponse';
import type { UserStatsResponse } from '../api/generated/models/UserStatsResponse';

export const Gamification = () => {
  const [achievements, setAchievements] = useState<AchievementResponse[]>([]);
  const [stats, setStats] = useState<UserStatsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unlocked' | 'locked'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [achievementsData, statsData] = await Promise.all([
        GamificationService.getAchievementsApiV1GamificationAchievementsGet(),
        GamificationService.getMyStatsApiV1GamificationStatsGet(),
      ]);
      setAchievements(achievementsData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load gamification data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredAchievements = achievements.filter((achievement) => {
    if (filter === 'unlocked') return achievement.unlocked;
    if (filter === 'locked') return !achievement.unlocked;
    return true;
  });

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'bg-[#10B981]';
    if (progress >= 75) return 'bg-[#3B82F6]';
    if (progress >= 50) return 'bg-[#F59E0B]';
    return 'bg-[#6B7280]';
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'text-[#F59E0B] border-[#F59E0B]';
      case 'epic':
        return 'text-[#8B5CF6] border-[#8B5CF6]';
      case 'rare':
        return 'text-[#3B82F6] border-[#3B82F6]';
      case 'common':
        return 'text-[#10B981] border-[#10B981]';
      default:
        return 'text-[#6B7280] border-[#6B7280]';
    }
  };

  const getRarityLabel = (rarity: string) => {
    switch (rarity) {
      case 'legendary':
        return 'Легендарное';
      case 'epic':
        return 'Эпическое';
      case 'rare':
        return 'Редкое';
      case 'common':
        return 'Обычное';
      default:
        return rarity;
    }
  };

  if (isLoading) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <p className="text-[#9CA3AF]">Загрузка...</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#F59E0B]/10 rounded-lg">
            <Trophy className="w-6 h-6 text-[#F59E0B]" />
          </div>
          <h1 className="text-3xl font-bold text-[#E5E7EB]">Достижения</h1>
        </div>
        <p className="text-[#9CA3AF]">
          Ваш прогресс и достижения в CityProblemMap
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-[#111827] rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-2">
              <Star className="w-5 h-5 text-[#F59E0B]" />
              <p className="text-sm text-[#9CA3AF]">Уровень</p>
            </div>
            <p className="text-3xl font-bold text-[#E5E7EB]">{stats.level}</p>
            <div className="mt-3">
              <div className="flex justify-between text-xs text-[#9CA3AF] mb-1">
                <span>Опыт</span>
                <span>{stats.experience} / {stats.next_level_experience}</span>
              </div>
              <div className="w-full bg-[#1F2937] rounded-full h-2">
                <div
                  className="bg-[#F59E0B] h-2 rounded-full transition-all"
                  style={{
                    width: `${(stats.experience / stats.next_level_experience) * 100}%`,
                  }}
                />
              </div>
            </div>
          </div>

          <div className="bg-[#111827] rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-2">
              <Trophy className="w-5 h-5 text-[#3B82F6]" />
              <p className="text-sm text-[#9CA3AF]">Достижения</p>
            </div>
            <p className="text-3xl font-bold text-[#E5E7EB]">
              {achievements.filter((a) => a.unlocked).length}
            </p>
            <p className="text-sm text-[#9CA3AF] mt-1">
              из {achievements.length}
            </p>
          </div>

          <div className="bg-[#111827] rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-[#10B981]" />
              <p className="text-sm text-[#9CA3AF]">Рейтинг</p>
            </div>
            <p className="text-3xl font-bold text-[#E5E7EB]">#{stats.rank}</p>
            <p className="text-sm text-[#9CA3AF] mt-1">
              в общем зачете
            </p>
          </div>

          <div className="bg-[#111827] rounded-xl p-6 shadow-xl">
            <div className="flex items-center gap-3 mb-2">
              <Target className="w-5 h-5 text-[#8B5CF6]" />
              <p className="text-sm text-[#9CA3AF]">Прогресс</p>
            </div>
            <p className="text-3xl font-bold text-[#E5E7EB]">
              {Math.round((achievements.filter((a) => a.unlocked).length / achievements.length) * 100)}%
            </p>
            <p className="text-sm text-[#9CA3AF] mt-1">
              завершено
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-[#111827] rounded-xl p-4 shadow-xl mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Все ({achievements.length})
          </button>
          <button
            onClick={() => setFilter('unlocked')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'unlocked'
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Получено ({achievements.filter((a) => a.unlocked).length})
          </button>
          <button
            onClick={() => setFilter('locked')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'locked'
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Заблокировано ({achievements.filter((a) => !a.unlocked).length})
          </button>
        </div>
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAchievements.map((achievement) => (
          <div
            key={achievement.id}
            className={`bg-[#111827] rounded-xl p-6 shadow-xl transition-all ${
              achievement.unlocked
                ? 'border-2 border-[#10B981]'
                : 'opacity-60 grayscale'
            }`}
          >
            {/* Icon & Title */}
            <div className="flex items-start gap-4 mb-4">
              <div
                className={`w-16 h-16 rounded-xl flex items-center justify-center text-3xl ${
                  achievement.unlocked ? 'bg-[#1F2937]' : 'bg-[#374151]'
                }`}
              >
                {achievement.unlocked ? achievement.icon : <Lock className="w-8 h-8 text-[#6B7280]" />}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-[#E5E7EB] mb-1">
                  {achievement.name}
                </h3>
                <span
                  className={`text-xs px-2 py-1 rounded-full border ${getRarityColor(
                    achievement.rarity
                  )}`}
                >
                  {getRarityLabel(achievement.rarity)}
                </span>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-[#9CA3AF] mb-4">
              {achievement.description}
            </p>

            {/* Progress */}
            {!achievement.unlocked && achievement.progress !== undefined && (
              <div>
                <div className="flex justify-between text-xs text-[#9CA3AF] mb-1">
                  <span>Прогресс</span>
                  <span>
                    {achievement.current_value} / {achievement.target_value}
                  </span>
                </div>
                <div className="w-full bg-[#1F2937] rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getProgressColor(
                      achievement.progress
                    )}`}
                    style={{ width: `${Math.min(achievement.progress, 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Unlocked Date */}
            {achievement.unlocked && achievement.unlocked_at && (
              <div className="mt-4 pt-4 border-t border-[#374151]">
                <p className="text-xs text-[#9CA3AF]">
                  Получено:{' '}
                  {new Date(achievement.unlocked_at).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              </div>
            )}

            {/* Reward */}
            {achievement.reward_points && (
              <div className="mt-4 flex items-center gap-2 text-sm">
                <Award className="w-4 h-4 text-[#F59E0B]" />
                <span className="text-[#E5E7EB]">+{achievement.reward_points} опыта</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredAchievements.length === 0 && (
        <div className="bg-[#111827] rounded-xl p-8 shadow-xl text-center">
          <Trophy className="w-16 h-16 text-[#6B7280] mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">
            Нет достижений
          </h3>
          <p className="text-sm text-[#9CA3AF]">
            {filter === 'unlocked'
              ? 'У вас пока нет полученных достижений'
              : 'Все достижения уже получены!'}
          </p>
        </div>
      )}
    </div>
  );
};
