import { useState } from 'react';
import { X, AlertTriangle, Flag } from 'lucide-react';
import { ReportsService } from '../api/generated/services/ReportsService';
import type { ReportCreate } from '../api/generated/models/ReportCreate';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  targetType: 'problem' | 'comment' | 'user';
  targetEntityId: number;
  targetTitle?: string;
}

const reasonOptions = [
  { value: 'spam', label: 'Спам', description: 'Нежелательная реклама или повторяющийся контент' },
  { value: 'offensive', label: 'Оскорбительный контент', description: 'Содержит оскорбления или ненормативную лексику' },
  { value: 'inappropriate', label: 'Неуместный контент', description: 'Не соответствует теме или правилам' },
  { value: 'false_info', label: 'Ложная информация', description: 'Содержит недостоверные данные' },
  { value: 'duplicate', label: 'Дубликат', description: 'Повторяет существующий контент' },
  { value: 'other', label: 'Другое', description: 'Другая причина' },
];

const targetTypeLabels = {
  problem: 'проблему',
  comment: 'комментарий',
  user: 'пользователя',
};

export const ReportModal = ({ isOpen, onClose, targetType, targetEntityId, targetTitle }: ReportModalProps) => {
  const [selectedReason, setSelectedReason] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedReason) {
      setError('Выберите причину жалобы');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const reportData: ReportCreate = {
        target_type: targetType,
        target_entity_id: targetEntityId,
        reason: selectedReason,
        description: description.trim() || null,
      };

      await ReportsService.createReportApiV1ReportsPost(reportData);
      setSuccess(true);

      setTimeout(() => {
        onClose();
        setSuccess(false);
        setSelectedReason('');
        setDescription('');
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Не удалось отправить жалобу');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      onClose();
      setSelectedReason('');
      setDescription('');
      setError('');
      setSuccess(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-[#111827] rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-[#374151]">
        {/* Header */}
        <div className="sticky top-0 bg-[#111827] border-b border-[#374151] p-6 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#F59E0B]/10 rounded-lg">
              <Flag className="w-6 h-6 text-[#F59E0B]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-[#E5E7EB]">Пожаловаться</h2>
              <p className="text-sm text-[#9CA3AF]">
                Пожаловаться на {targetTypeLabels[targetType]}
                {targetTitle && `: "${targetTitle}"`}
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-[#9CA3AF] hover:text-[#E5E7EB] transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {success ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-[#10B981]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Flag className="w-8 h-8 text-[#10B981]" />
              </div>
              <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Жалоба отправлена</h3>
              <p className="text-sm text-[#9CA3AF]">
                Спасибо за вашу бдительность. Модераторы рассмотрят жалобу в ближайшее время.
              </p>
            </div>
          ) : (
            <>
              {/* Warning */}
              <div className="mb-6 p-4 bg-[#F59E0B]/10 border border-[#F59E0B]/20 rounded-lg flex gap-3">
                <AlertTriangle className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
                <div className="text-sm text-[#E5E7EB]">
                  <p className="font-medium mb-1">Важно</p>
                  <p className="text-[#9CA3AF]">
                    Ложные жалобы могут привести к снижению вашей репутации.
                    Пожалуйста, используйте эту функцию ответственно.
                  </p>
                </div>
              </div>

              {/* Reason Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-[#E5E7EB] mb-3">
                  Причина жалобы <span className="text-[#EF4444]">*</span>
                </label>
                <div className="space-y-2">
                  {reasonOptions.map((option) => (
                    <label
                      key={option.value}
                      className={`block p-4 rounded-lg border cursor-pointer transition-all ${
                        selectedReason === option.value
                          ? 'border-[#3B82F6] bg-[#3B82F6]/10'
                          : 'border-[#374151] hover:border-[#4B5563] bg-[#1F2937]'
                      }`}
                    >
                      <input
                        type="radio"
                        name="reason"
                        value={option.value}
                        checked={selectedReason === option.value}
                        onChange={(e) => setSelectedReason(e.target.value)}
                        className="sr-only"
                      />
                      <div className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                          selectedReason === option.value
                            ? 'border-[#3B82F6] bg-[#3B82F6]'
                            : 'border-[#6B7280]'
                        }`}>
                          {selectedReason === option.value && (
                            <div className="w-2 h-2 bg-white rounded-full" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium text-[#E5E7EB]">{option.label}</p>
                          <p className="text-sm text-[#9CA3AF] mt-1">{option.description}</p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Description */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-[#E5E7EB] mb-2">
                  Дополнительная информация (необязательно)
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Опишите подробнее, что не так с этим контентом..."
                  rows={4}
                  className="w-full px-4 py-3 bg-[#1F2937] border border-[#374151] rounded-lg text-[#E5E7EB] placeholder-[#6B7280] focus:outline-none focus:border-[#3B82F6] transition-colors resize-none"
                  maxLength={500}
                />
                <p className="text-xs text-[#6B7280] mt-2">
                  {description.length}/500 символов
                </p>
              </div>

              {/* Error */}
              {error && (
                <div className="mb-6 p-4 bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-lg">
                  <p className="text-sm text-[#EF4444]">{error}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={isSubmitting}
                  className="flex-1 px-4 py-3 bg-[#374151] hover:bg-[#4B5563] text-[#E5E7EB] rounded-lg transition-colors disabled:opacity-50"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={!selectedReason || isSubmitting}
                  className={`flex-1 px-4 py-3 rounded-lg transition-colors ${
                    selectedReason && !isSubmitting
                      ? 'bg-[#F59E0B] hover:bg-[#D97706] text-white'
                      : 'bg-[#374151] text-[#6B7280] cursor-not-allowed'
                  }`}
                >
                  {isSubmitting ? 'Отправка...' : 'Отправить жалобу'}
                </button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  );
};
