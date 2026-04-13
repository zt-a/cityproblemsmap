import { useState, useEffect } from 'react';
import { Bell, MapPin, AlertCircle, Trash2, Settings as SettingsIcon } from 'lucide-react';
import { SubscriptionsService } from '../api/generated/services/SubscriptionsService';
import type { SubscriptionList } from '../api/generated/models/SubscriptionList';
import type { SubscriptionPublic } from '../api/generated/models/SubscriptionPublic';
import { useNavigate } from 'react-router-dom';

const targetTypeLabels: Record<string, string> = {
  problem: 'Проблема',
  zone: 'Зона',
  user: 'Пользователь',
};

const targetTypeIcons: Record<string, any> = {
  problem: AlertCircle,
  zone: MapPin,
  user: Bell,
};

export const Subscriptions = () => {
  const navigate = useNavigate();
  const [subscriptions, setSubscriptions] = useState<SubscriptionList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string | null>(null);

  useEffect(() => {
    loadSubscriptions();
  }, [filter]);

  const loadSubscriptions = async () => {
    setIsLoading(true);
    try {
      const data = await SubscriptionsService.getMySubscriptionsApiV1SubscriptionsGet(filter);
      setSubscriptions(data);
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnsubscribe = async (subscription: SubscriptionPublic) => {
    if (!confirm('Вы уверены, что хотите отписаться?')) return;

    try {
      if (subscription.target_type === 'problem') {
        await SubscriptionsService.unsubscribeFromProblemApiV1SubscriptionsProblemsProblemIdDelete(
          subscription.target_entity_id
        );
      } else if (subscription.target_type === 'zone') {
        await SubscriptionsService.unsubscribeFromZoneApiV1SubscriptionsZonesZoneIdDelete(
          subscription.target_entity_id
        );
      }
      loadSubscriptions();
    } catch (error) {
      console.error('Failed to unsubscribe:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const groupedSubscriptions = subscriptions?.items.reduce((acc, sub) => {
    if (!acc[sub.target_type]) {
      acc[sub.target_type] = [];
    }
    acc[sub.target_type].push(sub);
    return acc;
  }, {} as Record<string, SubscriptionPublic[]>);

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#3B82F6]/10 rounded-lg">
            <Bell className="w-6 h-6 text-[#3B82F6]" />
          </div>
          <h1 className="text-3xl font-bold text-[#E5E7EB]">Подписки</h1>
        </div>
        <p className="text-[#9CA3AF]">
          Управляйте подписками на проблемы, зоны и пользователей
        </p>
      </div>

      {/* Stats */}
      {subscriptions && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <div className="flex items-center gap-2 mb-1">
              <AlertCircle className="w-5 h-5 text-[#EF4444]" />
              <p className="text-sm text-[#9CA3AF]">Проблемы</p>
            </div>
            <p className="text-2xl font-bold text-[#E5E7EB]">
              {subscriptions.items.filter((s) => s.target_type === 'problem').length}
            </p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <div className="flex items-center gap-2 mb-1">
              <MapPin className="w-5 h-5 text-[#10B981]" />
              <p className="text-sm text-[#9CA3AF]">Зоны</p>
            </div>
            <p className="text-2xl font-bold text-[#E5E7EB]">
              {subscriptions.items.filter((s) => s.target_type === 'zone').length}
            </p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <div className="flex items-center gap-2 mb-1">
              <Bell className="w-5 h-5 text-[#3B82F6]" />
              <p className="text-sm text-[#9CA3AF]">Всего</p>
            </div>
            <p className="text-2xl font-bold text-[#E5E7EB]">{subscriptions.total}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-[#111827] rounded-xl p-4 shadow-xl mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter(null)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === null
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Все
          </button>
          <button
            onClick={() => setFilter('problem')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'problem'
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Проблемы
          </button>
          <button
            onClick={() => setFilter('zone')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'zone'
                ? 'bg-[#3B82F6] text-white'
                : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
            }`}
          >
            Зоны
          </button>
        </div>
      </div>

      {/* Subscriptions List */}
      {isLoading ? (
        <div className="bg-[#111827] rounded-xl p-8 shadow-xl text-center">
          <p className="text-[#9CA3AF]">Загрузка...</p>
        </div>
      ) : subscriptions && subscriptions.items && subscriptions.items.length > 0 ? (
        <div className="space-y-6">
          {Object.entries(groupedSubscriptions || {}).map(([type, subs]) => {
            const Icon = targetTypeIcons[type];
            return (
              <div key={type} className="bg-[#111827] rounded-xl shadow-xl overflow-hidden">
                <div className="p-4 border-b border-[#374151] flex items-center gap-2">
                  <Icon className="w-5 h-5 text-[#3B82F6]" />
                  <h2 className="text-lg font-bold text-[#E5E7EB]">
                    {targetTypeLabels[type]} ({subs.length})
                  </h2>
                </div>
                <div className="divide-y divide-[#374151]">
                  {subs.map((subscription) => (
                    <div
                      key={subscription.entity_id}
                      className="p-4 hover:bg-[#1F2937] transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="text-lg font-semibold text-[#E5E7EB]">
                              {targetTypeLabels[subscription.target_type]} #{subscription.target_entity_id}
                            </h3>
                          </div>

                          {/* Notification Types */}
                          <div className="flex flex-wrap gap-2 mb-2">
                            {subscription.notify_on_status_change && (
                              <span className="px-2 py-1 bg-[#3B82F6]/10 text-[#3B82F6] text-xs rounded-full">
                                Изменение статуса
                              </span>
                            )}
                            {subscription.notify_on_comment && (
                              <span className="px-2 py-1 bg-[#10B981]/10 text-[#10B981] text-xs rounded-full">
                                Комментарии
                              </span>
                            )}
                            {subscription.notify_on_resolution && (
                              <span className="px-2 py-1 bg-[#F59E0B]/10 text-[#F59E0B] text-xs rounded-full">
                                Решение
                              </span>
                            )}
                          </div>

                          <p className="text-sm text-[#6B7280]">
                            Подписка с {formatDate(subscription.created_at)}
                          </p>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              if (subscription.target_type === 'problem') {
                                navigate(`/problems/${subscription.target_entity_id}`);
                              }
                            }}
                            className="p-2 hover:bg-[#374151] rounded-lg transition-colors"
                            title="Перейти"
                          >
                            <SettingsIcon className="w-4 h-4 text-[#9CA3AF]" />
                          </button>
                          <button
                            onClick={() => handleUnsubscribe(subscription)}
                            className="p-2 hover:bg-[#374151] rounded-lg transition-colors"
                            title="Отписаться"
                          >
                            <Trash2 className="w-4 h-4 text-[#EF4444]" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-[#111827] rounded-xl p-8 shadow-xl text-center">
          <div className="w-16 h-16 bg-[#374151] rounded-full flex items-center justify-center mx-auto mb-4">
            <Bell className="w-8 h-8 text-[#6B7280]" />
          </div>
          <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Нет подписок</h3>
          <p className="text-sm text-[#9CA3AF] mb-4">
            Вы еще не подписались ни на одну проблему или зону
          </p>
          <button
            onClick={() => navigate('/map')}
            className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
          >
            Перейти к карте
          </button>
        </div>
      )}
    </div>
  );
};
