import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import {
  LogOut, Mail, MapPin, Award, Calendar, Edit2,
  FileText, MessageSquare, ThumbsUp, TrendingUp,
  Settings, User, AlertTriangle, X
} from 'lucide-react';
import { UsersService } from '../api/generated/services/UsersService';
import type { ProblemList } from '../api/generated/models/ProblemList';
import type { CommentPublic } from '../api/generated/models/CommentPublic';
import type { VotePublic } from '../api/generated/models/VotePublic';
import type { ReputationHistory } from '../api/generated/models/ReputationHistory';

type TabType = 'overview' | 'problems' | 'comments' | 'votes' | 'reputation' | 'settings';

export const Profile = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isLoading, setIsLoading] = useState(false);

  // Data states
  const [problems, setProblems] = useState<ProblemList | null>(null);
  const [comments, setComments] = useState<CommentPublic[]>([]);
  const [votes, setVotes] = useState<VotePublic[]>([]);
  const [reputation, setReputation] = useState<ReputationHistory | null>(null);

  // Edit states
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editUsername, setEditUsername] = useState('');
  const [isEditingEmail, setIsEditingEmail] = useState(false);
  const [editEmail, setEditEmail] = useState('');
  const [editPassword, setEditPassword] = useState('');
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [deactivateConfirmText, setDeactivateConfirmText] = useState('');

  useEffect(() => {
    if (user) {
      setEditUsername(user.username);
      setEditEmail(user.email);
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const loadProblems = async () => {
    setIsLoading(true);
    try {
      const data = await UsersService.getMyProblemsApiV1UsersMeProblemsGet();
      setProblems(data);
    } catch (error) {
      console.error('Failed to load problems:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadComments = async () => {
    setIsLoading(true);
    try {
      const data = await UsersService.getMyCommentsApiV1UsersMeCommentsGet();
      setComments(data);
    } catch (error) {
      console.error('Failed to load comments:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadVotes = async () => {
    setIsLoading(true);
    try {
      const data = await UsersService.getMyVotesApiV1UsersMeVotesGet();
      setVotes(data);
    } catch (error) {
      console.error('Failed to load votes:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadReputation = async () => {
    setIsLoading(true);
    try {
      const data = await UsersService.getMyReputationApiV1UsersMeReputationGet();
      setReputation(data);
    } catch (error) {
      console.error('Failed to load reputation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
    if (tab === 'problems' && !problems) loadProblems();
    if (tab === 'comments' && comments.length === 0) loadComments();
    if (tab === 'votes' && votes.length === 0) loadVotes();
    if (tab === 'reputation' && !reputation) loadReputation();
  };

  const handleUpdateProfile = async () => {
    if (!editUsername.trim()) return;
    try {
      await UsersService.updateProfileApiV1UsersMeProfilePatch({
        username: editUsername
      });
      setIsEditingProfile(false);
      window.location.reload();
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const handleUpdateEmail = async () => {
    if (!editEmail.trim() || !editPassword.trim()) return;
    try {
      await UsersService.updateEmailApiV1UsersMeEmailPatch({
        new_email: editEmail,
        password: editPassword
      });
      setIsEditingEmail(false);
      setEditPassword('');
      window.location.reload();
    } catch (error) {
      console.error('Failed to update email:', error);
    }
  };

  const handleDeactivateAccount = async () => {
    if (deactivateConfirmText !== 'DEACTIVATE') return;

    try {
      await UsersService.deactivateMeApiV1UsersMeDeactivatePatch();
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Failed to deactivate:', error);
    }
  };

  if (!user) {
    return null;
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-[#EF4444] text-white';
      case 'moderator': return 'bg-[#F59E0B] text-white';
      case 'official': return 'bg-[#3B82F6] text-white';
      case 'volunteer': return 'bg-[#10B981] text-white';
      default: return 'bg-[#6B7280] text-white';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'text-[#F59E0B]';
      case 'verified': return 'text-[#3B82F6]';
      case 'in_progress': return 'text-[#8B5CF6]';
      case 'resolved': return 'text-[#10B981]';
      case 'rejected': return 'text-[#EF4444]';
      default: return 'text-[#9CA3AF]';
    }
  };

  const tabs = [
    { id: 'overview', label: 'Обзор', icon: User },
    { id: 'problems', label: 'Проблемы', icon: FileText },
    { id: 'comments', label: 'Комментарии', icon: MessageSquare },
    { id: 'votes', label: 'Голоса', icon: ThumbsUp },
    { id: 'reputation', label: 'Репутация', icon: TrendingUp },
    { id: 'settings', label: 'Настройки', icon: Settings },
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-[#111827] rounded-xl p-8 shadow-xl mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[#E5E7EB] mb-2">{user.username}</h1>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRoleBadgeColor(user.role)}`}>
                {user.role}
              </span>
              {user.is_verified && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-[#10B981]/10 text-[#10B981] border border-[#10B981]">
                  Verified
                </span>
              )}
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Выйти
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-[#111827] rounded-xl shadow-xl mb-6">
        <div className="flex overflow-x-auto border-b border-[#374151]">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id as TabType)}
                className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'text-[#3B82F6] border-b-2 border-[#3B82F6]'
                    : 'text-[#9CA3AF] hover:text-[#E5E7EB]'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3 p-4 bg-[#1F2937] rounded-lg">
              <Mail className="w-5 h-5 text-[#3B82F6]" />
              <div>
                <p className="text-sm text-[#9CA3AF]">Email</p>
                <p className="text-[#E5E7EB]">{user.email}</p>
              </div>
            </div>

            {user.city && (
              <div className="flex items-center gap-3 p-4 bg-[#1F2937] rounded-lg">
                <MapPin className="w-5 h-5 text-[#3B82F6]" />
                <div>
                  <p className="text-sm text-[#9CA3AF]">Город</p>
                  <p className="text-[#E5E7EB]">{user.city}</p>
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 p-4 bg-[#1F2937] rounded-lg">
              <Award className="w-5 h-5 text-[#F59E0B]" />
              <div>
                <p className="text-sm text-[#9CA3AF]">Репутация</p>
                <p className="text-[#E5E7EB] font-semibold">{user.reputation}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 bg-[#1F2937] rounded-lg">
              <Calendar className="w-5 h-5 text-[#3B82F6]" />
              <div>
                <p className="text-sm text-[#9CA3AF]">Регистрация</p>
                <p className="text-[#E5E7EB]">{formatDate(user.created_at)}</p>
              </div>
            </div>

            {user.district && (
              <div className="flex items-center gap-3 p-4 bg-[#1F2937] rounded-lg md:col-span-2">
                <MapPin className="w-5 h-5 text-[#3B82F6]" />
                <div>
                  <p className="text-sm text-[#9CA3AF]">Район</p>
                  <p className="text-[#E5E7EB]">{user.district}</p>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'problems' && (
          <div>
            <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Мои проблемы</h2>
            {isLoading ? (
              <p className="text-[#9CA3AF]">Загрузка...</p>
            ) : problems ? (
              <div className="space-y-4">
                <div className="flex gap-4 text-sm text-[#9CA3AF] mb-4">
                  <span>Всего: {problems.total}</span>
                </div>
                {problems.items.map((problem) => (
                  <div key={problem.entity_id} className="p-4 bg-[#1F2937] rounded-lg hover:bg-[#374151] transition-colors cursor-pointer"
                    onClick={() => navigate(`/problems/${problem.entity_id}`)}>
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-[#E5E7EB] font-medium">{problem.title}</h3>
                      <span className={`text-sm font-medium ${getStatusColor(problem.status)}`}>
                        {problem.status}
                      </span>
                    </div>
                    <p className="text-sm text-[#9CA3AF] mb-2">{problem.description}</p>
                    <div className="flex items-center gap-4 text-xs text-[#6B7280]">
                      <span>{formatDate(problem.created_at)}</span>
                      {problem.address && <span>{problem.address}</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-[#9CA3AF]">Нет проблем</p>
            )}
          </div>
        )}

        {activeTab === 'comments' && (
          <div>
            <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Мои комментарии</h2>
            {isLoading ? (
              <p className="text-[#9CA3AF]">Загрузка...</p>
            ) : comments.length > 0 ? (
              <div className="space-y-4">
                {comments.map((comment) => (
                  <div key={comment.entity_id} className="p-4 bg-[#1F2937] rounded-lg">
                    <p className="text-[#E5E7EB] mb-2">{comment.content}</p>
                    <div className="flex items-center gap-4 text-xs text-[#6B7280]">
                      <span>{formatDate(comment.created_at)}</span>
                      {comment.is_flagged && <span className="text-[#EF4444]">Помечен</span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-[#9CA3AF]">Нет комментариев</p>
            )}
          </div>
        )}

        {activeTab === 'votes' && (
          <div>
            <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Мои голоса</h2>
            {isLoading ? (
              <p className="text-[#9CA3AF]">Загрузка...</p>
            ) : votes.length > 0 ? (
              <div className="space-y-4">
                {votes.map((vote) => (
                  <div key={vote.entity_id} className="p-4 bg-[#1F2937] rounded-lg flex justify-between items-center">
                    <div>
                      <p className="text-[#E5E7EB]">Проблема #{vote.problem_entity_id}</p>
                      <span className="text-xs text-[#6B7280]">Вес голоса: {vote.weight}</span>
                    </div>
                    <div className="text-sm text-[#9CA3AF]">
                      {vote.is_true !== null && <span className={vote.is_true ? 'text-[#10B981]' : 'text-[#EF4444]'}>
                        {vote.is_true ? '✓ Правда' : '✗ Ложь'}
                      </span>}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-[#9CA3AF]">Нет голосов</p>
            )}
          </div>
        )}

        {activeTab === 'reputation' && (
          <div>
            <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">История репутации</h2>
            {isLoading ? (
              <p className="text-[#9CA3AF]">Загрузка...</p>
            ) : reputation ? (
              <div className="space-y-4">
                <div className="p-4 bg-[#1F2937] rounded-lg">
                  <p className="text-sm text-[#9CA3AF]">Текущая репутация</p>
                  <p className="text-3xl font-bold text-[#E5E7EB]">{reputation.current_reputation}</p>
                </div>
                {reputation.logs && reputation.logs.length > 0 ? (
                  <div className="space-y-2">
                    {reputation.logs.map((entry) => (
                      <div key={entry.id} className="p-4 bg-[#1F2937] rounded-lg flex justify-between items-center">
                        <div>
                          <p className="text-[#E5E7EB]">{entry.reason}</p>
                          {entry.note && <p className="text-sm text-[#9CA3AF]">{entry.note}</p>}
                          <span className="text-xs text-[#6B7280]">{formatDate(entry.created_at)}</span>
                        </div>
                        <span className={`text-lg font-bold ${entry.delta > 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                          {entry.delta > 0 ? '+' : ''}{entry.delta}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-[#9CA3AF]">Нет истории изменений</p>
                )}
              </div>
            ) : (
              <p className="text-[#9CA3AF]">Нет истории</p>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-[#E5E7EB] mb-4">Настройки профиля</h2>

            {/* Username */}
            <div className="p-4 bg-[#1F2937] rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm text-[#9CA3AF]">Имя пользователя</label>
                <button
                  onClick={() => setIsEditingProfile(!isEditingProfile)}
                  className="text-[#3B82F6] hover:text-[#60A5FA] text-sm flex items-center gap-1"
                >
                  <Edit2 className="w-3 h-3" />
                  {isEditingProfile ? 'Отмена' : 'Изменить'}
                </button>
              </div>
              {isEditingProfile ? (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={editUsername}
                    onChange={(e) => setEditUsername(e.target.value)}
                    className="flex-1 px-3 py-2 bg-[#111827] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:border-[#3B82F6]"
                  />
                  <button
                    onClick={handleUpdateProfile}
                    className="px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
                  >
                    Сохранить
                  </button>
                </div>
              ) : (
                <p className="text-[#E5E7EB]">{user.username}</p>
              )}
            </div>

            {/* Email */}
            <div className="p-4 bg-[#1F2937] rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm text-[#9CA3AF]">Email</label>
                <button
                  onClick={() => setIsEditingEmail(!isEditingEmail)}
                  className="text-[#3B82F6] hover:text-[#60A5FA] text-sm flex items-center gap-1"
                >
                  <Edit2 className="w-3 h-3" />
                  {isEditingEmail ? 'Отмена' : 'Изменить'}
                </button>
              </div>
              {isEditingEmail ? (
                <div className="space-y-2">
                  <input
                    type="email"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    placeholder="Новый email"
                    className="w-full px-3 py-2 bg-[#111827] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:border-[#3B82F6]"
                  />
                  <input
                    type="password"
                    value={editPassword}
                    onChange={(e) => setEditPassword(e.target.value)}
                    placeholder="Текущий пароль"
                    className="w-full px-3 py-2 bg-[#111827] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:border-[#3B82F6]"
                  />
                  <button
                    onClick={handleUpdateEmail}
                    className="w-full px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
                  >
                    Сохранить
                  </button>
                </div>
              ) : (
                <p className="text-[#E5E7EB]">{user.email}</p>
              )}
            </div>

            {/* Danger Zone */}
            <div className="p-4 bg-[#1F2937] border border-[#EF4444]/20 rounded-lg">
              <h3 className="text-[#EF4444] font-medium mb-2">Опасная зона</h3>
              <p className="text-sm text-[#9CA3AF] mb-4">
                Деактивация аккаунта - это обратимое действие. Ваши данные будут скрыты, но не удалены.
              </p>
              <button
                onClick={() => setShowDeactivateModal(true)}
                className="px-4 py-2 bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-lg transition-colors"
              >
                Деактивировать аккаунт
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Deactivate Account Modal */}
      {showDeactivateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#111827] rounded-xl max-w-md w-full p-6 shadow-2xl border border-[#EF4444]/20">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-[#EF4444]/10 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-[#EF4444]" />
                </div>
                <h2 className="text-xl font-bold text-[#E5E7EB]">Деактивация аккаунта</h2>
              </div>
              <button
                onClick={() => {
                  setShowDeactivateModal(false);
                  setDeactivateConfirmText('');
                }}
                className="text-[#9CA3AF] hover:text-[#E5E7EB] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Warning */}
            <div className="mb-6 p-4 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg">
              <p className="text-sm text-[#E5E7EB] mb-2">
                Вы собираетесь деактивировать свой аккаунт. Это действие:
              </p>
              <ul className="text-sm text-[#9CA3AF] space-y-1 list-disc list-inside">
                <li>Скроет ваш профиль от других пользователей</li>
                <li>Скроет все ваши проблемы и комментарии</li>
                <li>Вы не сможете войти в систему</li>
                <li>Данные не будут удалены (обратимо)</li>
              </ul>
            </div>

            {/* Confirmation Input */}
            <div className="mb-6">
              <label className="block text-sm text-[#9CA3AF] mb-2">
                Для подтверждения введите <span className="text-[#EF4444] font-mono font-bold">DEACTIVATE</span>
              </label>
              <input
                type="text"
                value={deactivateConfirmText}
                onChange={(e) => setDeactivateConfirmText(e.target.value)}
                placeholder="Введите DEACTIVATE"
                className="w-full px-4 py-2 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#EF4444] transition-colors"
              />
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeactivateModal(false);
                  setDeactivateConfirmText('');
                }}
                className="flex-1 px-4 py-2 bg-[#374151] hover:bg-[#4B5563] text-[#E5E7EB] rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                onClick={handleDeactivateAccount}
                disabled={deactivateConfirmText !== 'DEACTIVATE'}
                className={`flex-1 px-4 py-2 rounded-lg transition-colors ${
                  deactivateConfirmText === 'DEACTIVATE'
                    ? 'bg-[#EF4444] hover:bg-[#DC2626] text-white'
                    : 'bg-[#374151] text-[#6B7280] cursor-not-allowed'
                }`}
              >
                Деактивировать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
