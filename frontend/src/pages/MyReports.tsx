import { useState, useEffect } from 'react';
import { Flag, Filter, Clock, CheckCircle, XCircle, AlertCircle, Plus, X, Send, Search } from 'lucide-react';
import { ReportsService } from '../api/generated/services/ReportsService';
import { ProblemsService } from '../api/generated/services/ProblemsService';
import type { ReportList } from '../api/generated/models/ReportList';
import type { ReportPublic } from '../api/generated/models/ReportPublic';
import type { ReportCreate } from '../api/generated/models/ReportCreate';
import type { ProblemPublic } from '../api/generated/models/ProblemPublic';

const statusOptions = [
  { value: 'all', label: 'Все' },
  { value: 'pending', label: 'На рассмотрении' },
  { value: 'approved', label: 'Одобрено' },
  { value: 'rejected', label: 'Отклонено' },
];

const reasonLabels: Record<string, string> = {
  spam: 'Спам',
  offensive: 'Оскорбительный контент',
  inappropriate: 'Неуместный контент',
  false_info: 'Ложная информация',
  duplicate: 'Дубликат',
  other: 'Другое',
};

const targetTypeLabels: Record<string, string> = {
  problem: 'Проблема',
  comment: 'Комментарий',
  user: 'Пользователь',
};

export const MyReports = () => {
  const [reports, setReports] = useState<ReportList | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form state
  const [formData, setFormData] = useState<ReportCreate>({
    target_type: 'problem',
    target_entity_id: 0,
    reason: 'spam',
    description: '',
  });

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ProblemPublic[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState<{ id: number; title: string } | null>(null);

  useEffect(() => {
    loadReports();
  }, [statusFilter]);

  const loadReports = async () => {
    setIsLoading(true);
    try {
      const data = await ReportsService.getMyReportsApiV1ReportsMyGet(
        statusFilter === 'all' ? null : statusFilter
      );
      setReports(data);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.target_entity_id || formData.target_entity_id <= 0) {
      alert('Пожалуйста, выберите объект для жалобы');
      return;
    }

    setIsSubmitting(true);
    try {
      await ReportsService.createReportApiV1ReportsPost(formData);
      alert('Жалоба успешно отправлена!');
      setShowCreateForm(false);
      setFormData({
        target_type: 'problem',
        target_entity_id: 0,
        reason: 'spam',
        description: '',
      });
      setSelectedTarget(null);
      setSearchQuery('');
      loadReports(); // Reload reports list
    } catch (error) {
      console.error('Failed to create report:', error);
      alert('Ошибка при отправке жалобы');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Search for problems
  const handleSearch = async (query: string) => {
    setSearchQuery(query);

    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    if (formData.target_type !== 'problem') {
      return; // Only search for problems
    }

    setIsSearching(true);
    try {
      const data = await ProblemsService.getProblemsApiV1ProblemsGet(
        0, // skip
        10, // limit
        undefined, // status
        undefined, // category
        undefined, // zone_id
        query, // search
      );
      setSearchResults(data.items || []);
    } catch (error) {
      console.error('Failed to search problems:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectTarget = (id: number, title: string) => {
    setSelectedTarget({ id, title });
    setFormData({ ...formData, target_entity_id: id });
    setSearchQuery('');
    setSearchResults([]);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-[#F59E0B]" />;
      case 'approved':
        return <CheckCircle className="w-5 h-5 text-[#10B981]" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-[#EF4444]" />;
      default:
        return <AlertCircle className="w-5 h-5 text-[#6B7280]" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
      case 'approved':
        return 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20';
      case 'rejected':
        return 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20';
      default:
        return 'bg-[#6B7280]/10 text-[#6B7280] border-[#6B7280]/20';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending':
        return 'На рассмотрении';
      case 'approved':
        return 'Одобрено';
      case 'rejected':
        return 'Отклонено';
      default:
        return status;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#F59E0B]/10 rounded-lg">
              <Flag className="w-6 h-6 text-[#F59E0B]" />
            </div>
            <h1 className="text-3xl font-bold text-[#E5E7EB]">Мои жалобы</h1>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 px-4 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors"
          >
            {showCreateForm ? (
              <>
                <X className="w-5 h-5" />
                Отмена
              </>
            ) : (
              <>
                <Plus className="w-5 h-5" />
                Создать жалобу
              </>
            )}
          </button>
        </div>
        <p className="text-[#9CA3AF]">
          История ваших жалоб на проблемы, комментарии и пользователей
        </p>
      </div>

      {/* Create Report Form */}
      {showCreateForm && (
        <div className="bg-[#111827] rounded-xl p-6 shadow-xl mb-6 border border-[#374151]">
          <h2 className="text-xl font-semibold text-[#E5E7EB] mb-4">Создать жалобу</h2>
          <form onSubmit={handleSubmitReport} className="space-y-6">
            {/* Target Type */}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                Тип объекта
              </label>
              <select
                value={formData.target_type}
                onChange={(e) => {
                  setFormData({ ...formData, target_type: e.target.value, target_entity_id: 0 });
                  setSelectedTarget(null);
                  setSearchQuery('');
                  setSearchResults([]);
                }}
                className="w-full px-4 py-2 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                required
              >
                <option value="problem">Проблема</option>
                <option value="comment">Комментарий</option>
                <option value="user">Пользователь</option>
              </select>
            </div>

            {/* Search Section for Problems */}
            {formData.target_type === 'problem' && !selectedTarget && (
              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                  Найдите проблему
                </label>
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#6B7280]" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => handleSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    placeholder="Начните вводить название проблемы..."
                  />
                  {isSearching && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <div className="w-5 h-5 border-2 border-[#3B82F6] border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                </div>

                {/* Search Results as Cards */}
                {searchResults.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-sm text-[#9CA3AF]">Найдено проблем: {searchResults.length}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto pr-2">
                      {searchResults.map((problem) => (
                        <button
                          key={problem.entity_id}
                          type="button"
                          onClick={() => handleSelectTarget(problem.entity_id, problem.title)}
                          className="bg-[#1F2937] rounded-lg overflow-hidden hover:ring-2 hover:ring-[#3B82F6] transition-all text-left group"
                        >
                          {/* Mini thumbnail */}
                          <div className="relative h-32 bg-[#374151] flex items-center justify-center">
                            <Flag className="w-12 h-12 text-[#6B7280]" />
                            {/* Status Badge */}
                            <div className="absolute top-2 left-2">
                              <span
                                className={`text-xs px-2 py-1 rounded ${
                                  problem.status === 'resolved'
                                    ? 'bg-[#10B981]/20 text-[#10B981]'
                                    : problem.status === 'in_progress'
                                    ? 'bg-[#F59E0B]/20 text-[#F59E0B]'
                                    : 'bg-[#EF4444]/20 text-[#EF4444]'
                                }`}
                              >
                                {problem.status === 'resolved'
                                  ? 'Решена'
                                  : problem.status === 'in_progress'
                                  ? 'В работе'
                                  : 'Новая'}
                              </span>
                            </div>
                          </div>

                          {/* Content */}
                          <div className="p-3">
                            <h3 className="text-sm font-semibold text-[#E5E7EB] mb-2 line-clamp-2 group-hover:text-[#3B82F6] transition-colors">
                              {problem.title}
                            </h3>

                            {/* Location */}
                            <div className="flex items-center gap-1 text-xs text-[#9CA3AF] mb-2">
                              <Flag className="w-3 h-3" />
                              <span className="truncate">{problem.address || problem.city}</span>
                            </div>

                            {/* Stats */}
                            <div className="flex items-center gap-3 text-xs text-[#6B7280]">
                              <span>ID: {problem.entity_id}</span>
                              <span>•</span>
                              <span>👍 {problem.vote_count || 0}</span>
                              <span>💬 {problem.comment_count || 0}</span>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {searchQuery.length >= 2 && searchResults.length === 0 && !isSearching && (
                  <div className="text-center py-8 text-[#6B7280]">
                    <p>Проблемы не найдены</p>
                  </div>
                )}
              </div>
            )}

            {/* Manual ID input for Comment/User */}
            {formData.target_type !== 'problem' && !selectedTarget && (
              <div>
                <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                  ID объекта
                </label>
                <input
                  type="number"
                  value={formData.target_entity_id || ''}
                  onChange={(e) => {
                    const id = parseInt(e.target.value) || 0;
                    setFormData({ ...formData, target_entity_id: id });
                    if (id > 0) {
                      setSelectedTarget({ id, title: `${formData.target_type} #${id}` });
                    }
                  }}
                  className="w-full px-4 py-2 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                  placeholder="Введите ID"
                  required
                  min="1"
                />
              </div>
            )}

            {/* Selected Target Display */}
            {selectedTarget && (
              <div className="p-4 bg-[#3B82F6]/10 border border-[#3B82F6]/30 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-xs text-[#9CA3AF] mb-1">Выбранный объект:</p>
                    <p className="text-base font-semibold text-[#E5E7EB] mb-1">{selectedTarget.title}</p>
                    <p className="text-sm text-[#6B7280]">
                      {targetTypeLabels[formData.target_type]} • ID: {selectedTarget.id}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedTarget(null);
                      setFormData({ ...formData, target_entity_id: 0 });
                      setSearchQuery('');
                    }}
                    className="p-2 hover:bg-[#374151] rounded-lg transition-colors"
                    title="Удалить выбор"
                  >
                    <X className="w-5 h-5 text-[#9CA3AF]" />
                  </button>
                </div>
              </div>
            )}

            {/* Reason */}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                Причина жалобы
              </label>
              <select
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                className="w-full px-4 py-2 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                required
              >
                <option value="spam">Спам</option>
                <option value="offensive">Оскорбительный контент</option>
                <option value="inappropriate">Неуместный контент</option>
                <option value="false_info">Ложная информация</option>
                <option value="duplicate">Дубликат</option>
                <option value="other">Другое</option>
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-[#9CA3AF] mb-2">
                Описание (необязательно)
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-2 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] focus:outline-none focus:ring-2 focus:ring-[#3B82F6] resize-none"
                rows={4}
                placeholder="Опишите подробнее причину жалобы..."
              />
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-6 py-2 bg-[#374151] hover:bg-[#4B5563] text-[#E5E7EB] rounded-lg transition-colors"
              >
                Отмена
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center gap-2 px-6 py-2 bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Отправка...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Отправить жалобу
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="bg-[#111827] rounded-xl p-4 shadow-xl mb-6">
        <div className="flex items-center gap-3">
          <Filter className="w-5 h-5 text-[#9CA3AF]" />
          <span className="text-sm text-[#9CA3AF]">Фильтр по статусу:</span>
          <div className="flex gap-2">
            {statusOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setStatusFilter(option.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === option.value
                    ? 'bg-[#3B82F6] text-white'
                    : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#E5E7EB] hover:bg-[#374151]'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-[#111827] rounded-xl shadow-xl overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">
            <p className="text-[#9CA3AF]">Загрузка...</p>
          </div>
        ) : reports && reports.items.length > 0 ? (
          <div className="divide-y divide-[#374151]">
            {reports.items.map((report: ReportPublic) => (
              <div key={report.entity_id} className="p-6 hover:bg-[#1F2937] transition-colors">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(report.status)}
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-[#9CA3AF]">
                          {targetTypeLabels[report.target_type] || report.target_type}
                        </span>
                        <span className="text-[#6B7280]">•</span>
                        <span className="text-sm text-[#6B7280]">
                          #{report.target_entity_id}
                        </span>
                      </div>
                      <h3 className="text-lg font-semibold text-[#E5E7EB]">
                        {reasonLabels[report.reason] || report.reason}
                      </h3>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                      report.status
                    )}`}
                  >
                    {getStatusLabel(report.status)}
                  </span>
                </div>

                {/* Description */}
                {report.description && (
                  <div className="mb-4 p-3 bg-[#1F2937] rounded-lg">
                    <p className="text-sm text-[#E5E7EB]">{report.description}</p>
                  </div>
                )}

                {/* Resolution Note */}
                {report.resolution_note && (
                  <div className="mb-4 p-3 bg-[#3B82F6]/10 border border-[#3B82F6]/20 rounded-lg">
                    <p className="text-xs text-[#9CA3AF] mb-1">Ответ модератора:</p>
                    <p className="text-sm text-[#E5E7EB]">{report.resolution_note}</p>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center gap-4 text-xs text-[#6B7280]">
                  <span>Создано: {formatDate(report.created_at)}</span>
                  {report.resolved_by_entity_id && (
                    <>
                      <span>•</span>
                      <span>Рассмотрено модератором #{report.resolved_by_entity_id}</span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-[#374151] rounded-full flex items-center justify-center mx-auto mb-4">
              <Flag className="w-8 h-8 text-[#6B7280]" />
            </div>
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Нет жалоб</h3>
            <p className="text-sm text-[#9CA3AF]">
              {statusFilter === 'all'
                ? 'Вы еще не отправляли жалобы'
                : `Нет жалоб со статусом "${statusOptions.find((o) => o.value === statusFilter)?.label}"`}
            </p>
          </div>
        )}

        {/* Pagination */}
        {reports && reports.total > reports.items.length && (
          <div className="p-4 border-t border-[#374151] flex justify-center">
            <button className="px-4 py-2 bg-[#374151] hover:bg-[#4B5563] text-[#E5E7EB] rounded-lg transition-colors">
              Загрузить еще
            </button>
          </div>
        )}
      </div>

      {/* Stats */}
      {reports && reports.total > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">Всего жалоб</p>
            <p className="text-2xl font-bold text-[#E5E7EB]">{reports.total}</p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">На рассмотрении</p>
            <p className="text-2xl font-bold text-[#F59E0B]">
              {reports.items.filter((r) => r.status === 'pending').length}
            </p>
          </div>
          <div className="bg-[#111827] rounded-xl p-4 shadow-xl">
            <p className="text-sm text-[#9CA3AF] mb-1">Одобрено</p>
            <p className="text-2xl font-bold text-[#10B981]">
              {reports.items.filter((r) => r.status === 'approved').length}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
