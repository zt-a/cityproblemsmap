import { useState, useEffect } from 'react';
import { Settings, Bell, Mail, Smartphone, Save } from 'lucide-react';
import { UserSettingsService } from '../api/generated/services/UserSettingsService';
import type { UserNotificationSettingsPublic } from '../api/generated/models/UserNotificationSettingsPublic';

export const UserSettings = () => {
  const [settings, setSettings] = useState<UserNotificationSettingsPublic | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Local state for form
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [pushEnabled, setPushEnabled] = useState(false);
  const [problemStatusChanged, setProblemStatusChanged] = useState(false);
  const [newComment, setNewComment] = useState(false);
  const [commentReply, setCommentReply] = useState(false);
  const [problemResolved, setProblemResolved] = useState(false);
  const [newFollower, setNewFollower] = useState(false);
  const [mention, setMention] = useState(false);
  const [achievementUnlocked, setAchievementUnlocked] = useState(false);
  const [subscriptionUpdate, setSubscriptionUpdate] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    try {
      const data = await UserSettingsService.getNotificationSettingsApiV1SettingsNotificationsGet();
      setSettings(data);

      // Populate form
      setEmailEnabled(data.email_enabled);
      setPushEnabled(data.push_enabled);
      setProblemStatusChanged(data.problem_status_changed);
      setNewComment(data.new_comment);
      setCommentReply(data.comment_reply);
      setProblemResolved(data.problem_resolved);
      setNewFollower(data.new_follower);
      setMention(data.mention);
      setAchievementUnlocked(data.achievement_unlocked);
      setSubscriptionUpdate(data.subscription_update);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      const updatedSettings = await UserSettingsService.updateNotificationSettingsApiV1SettingsNotificationsPatch({
        email_enabled: emailEnabled,
        push_enabled: pushEnabled,
        problem_status_changed: problemStatusChanged,
        new_comment: newComment,
        comment_reply: commentReply,
        problem_resolved: problemResolved,
        new_follower: newFollower,
        mention: mention,
        achievement_unlocked: achievementUnlocked,
        subscription_update: subscriptionUpdate,
      });

      setSettings(updatedSettings);
      setSaveSuccess(true);

      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const notificationTypes = [
    {
      id: 'problem_status_changed',
      label: 'Изменение статуса проблемы',
      description: 'Когда статус вашей проблемы изменяется',
      value: problemStatusChanged,
      setValue: setProblemStatusChanged,
      icon: '🔄',
    },
    {
      id: 'new_comment',
      label: 'Новый комментарий',
      description: 'Когда кто-то комментирует вашу проблему',
      value: newComment,
      setValue: setNewComment,
      icon: '💬',
    },
    {
      id: 'comment_reply',
      label: 'Ответ на комментарий',
      description: 'Когда кто-то отвечает на ваш комментарий',
      value: commentReply,
      setValue: setCommentReply,
      icon: '↩️',
    },
    {
      id: 'problem_resolved',
      label: 'Проблема решена',
      description: 'Когда ваша проблема помечена как решенная',
      value: problemResolved,
      setValue: setProblemResolved,
      icon: '✅',
    },
    {
      id: 'new_follower',
      label: 'Новый подписчик',
      description: 'Когда кто-то подписывается на вас',
      value: newFollower,
      setValue: setNewFollower,
      icon: '👤',
    },
    {
      id: 'mention',
      label: 'Упоминание',
      description: 'Когда вас упоминают в комментарии',
      value: mention,
      setValue: setMention,
      icon: '@',
    },
    {
      id: 'achievement_unlocked',
      label: 'Новое достижение',
      description: 'Когда вы получаете новое достижение',
      value: achievementUnlocked,
      setValue: setAchievementUnlocked,
      icon: '🏆',
    },
    {
      id: 'subscription_update',
      label: 'Обновление подписки',
      description: 'Обновления по вашим подпискам на проблемы и зоны',
      value: subscriptionUpdate,
      setValue: setSubscriptionUpdate,
      icon: '🔔',
    },
  ];

  if (isLoading) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <p className="text-[#9CA3AF]">Загрузка настроек...</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-[#3B82F6]/10 rounded-lg">
            <Settings className="w-6 h-6 text-[#3B82F6]" />
          </div>
          <h1 className="text-3xl font-bold text-[#E5E7EB]">Настройки уведомлений</h1>
        </div>
        <p className="text-[#9CA3AF]">
          Управляйте тем, как и когда вы получаете уведомления
        </p>
      </div>

      {/* Success Message */}
      {saveSuccess && (
        <div className="mb-6 p-4 bg-[#10B981]/10 border border-[#10B981]/20 rounded-lg">
          <p className="text-sm text-[#10B981]">✓ Настройки успешно сохранены</p>
        </div>
      )}

      {/* Delivery Methods */}
      <div className="bg-[#111827] rounded-xl p-6 shadow-xl mb-6">
        <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Способы доставки</h2>

        <div className="space-y-4">
          {/* Email */}
          <label className="flex items-center justify-between p-4 bg-[#1F2937] rounded-lg cursor-pointer hover:bg-[#374151] transition-colors">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-[#3B82F6]" />
              <div>
                <p className="font-medium text-[#E5E7EB]">Email уведомления</p>
                <p className="text-sm text-[#9CA3AF]">Получать уведомления на email</p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={emailEnabled}
              onChange={(e) => setEmailEnabled(e.target.checked)}
              className="w-5 h-5 rounded border-[#374151] bg-[#111827] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
            />
          </label>

          {/* Push */}
          <label className="flex items-center justify-between p-4 bg-[#1F2937] rounded-lg cursor-pointer hover:bg-[#374151] transition-colors">
            <div className="flex items-center gap-3">
              <Smartphone className="w-5 h-5 text-[#3B82F6]" />
              <div>
                <p className="font-medium text-[#E5E7EB]">Push уведомления</p>
                <p className="text-sm text-[#9CA3AF]">Получать push-уведомления в браузере</p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={pushEnabled}
              onChange={(e) => setPushEnabled(e.target.checked)}
              className="w-5 h-5 rounded border-[#374151] bg-[#111827] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
            />
          </label>
        </div>
      </div>

      {/* Notification Types */}
      <div className="bg-[#111827] rounded-xl p-6 shadow-xl mb-6">
        <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Типы уведомлений</h2>

        <div className="space-y-3">
          {notificationTypes.map((type) => (
            <label
              key={type.id}
              className="flex items-center justify-between p-4 bg-[#1F2937] rounded-lg cursor-pointer hover:bg-[#374151] transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{type.icon}</span>
                <div>
                  <p className="font-medium text-[#E5E7EB]">{type.label}</p>
                  <p className="text-sm text-[#9CA3AF]">{type.description}</p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={type.value}
                onChange={(e) => type.setValue(e.target.checked)}
                className="w-5 h-5 rounded border-[#374151] bg-[#111827] text-[#3B82F6] focus:ring-[#3B82F6] focus:ring-offset-0"
              />
            </label>
          ))}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
            isSaving
              ? 'bg-[#374151] text-[#6B7280] cursor-not-allowed'
              : 'bg-[#3B82F6] hover:bg-[#2563EB] text-white'
          }`}
        >
          <Save className="w-5 h-5" />
          {isSaving ? 'Сохранение...' : 'Сохранить настройки'}
        </button>
      </div>
    </div>
  );
};
