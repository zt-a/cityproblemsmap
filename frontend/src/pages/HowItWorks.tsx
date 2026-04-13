import { MapPin, CheckCircle, Users, Award } from 'lucide-react';

export const HowItWorks = () => {
  const steps = [
    {
      icon: MapPin,
      title: 'Сообщите о проблеме',
      description: 'Найдите проблему на карте или создайте новую. Добавьте фото, описание и точное местоположение.',
      color: '#3B82F6'
    },
    {
      icon: CheckCircle,
      title: 'Модерация',
      description: 'Модераторы проверяют проблему на достоверность и подтверждают её.',
      color: '#F59E0B'
    },
    {
      icon: Users,
      title: 'Решение',
      description: 'Городские службы получают уведомление, берут проблему в работу и решают её.',
      color: '#10B981'
    },
    {
      icon: Award,
      title: 'Награды',
      description: 'Активные участники получают репутацию, достижения и поднимаются в рейтинге.',
      color: '#EF4444'
    }
  ];

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-[#E5E7EB] mb-4">Как это работает?</h1>
        <p className="text-[#9CA3AF] text-lg">Простой процесс от проблемы до решения</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={index} className="bg-[#111827] rounded-xl p-6 shadow-xl">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center mb-4"
                style={{ backgroundColor: `${step.color}20` }}
              >
                <Icon className="w-6 h-6" style={{ color: step.color }} />
              </div>
              <div className="text-sm text-[#9CA3AF] mb-2">Шаг {index + 1}</div>
              <h3 className="text-xl font-semibold text-[#E5E7EB] mb-3">{step.title}</h3>
              <p className="text-[#9CA3AF]">{step.description}</p>
            </div>
          );
        })}
      </div>

      <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
        <h2 className="text-2xl font-bold text-[#E5E7EB] mb-6">Роли пользователей</h2>

        <div className="space-y-4">
          <div className="border-l-4 border-[#6B7280] pl-4">
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Пользователь</h3>
            <p className="text-[#9CA3AF]">Может создавать проблемы, комментировать, голосовать и отслеживать статус.</p>
          </div>

          <div className="border-l-4 border-[#10B981] pl-4">
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Волонтёр</h3>
            <p className="text-[#9CA3AF]">Помогает решать проблемы, организует субботники и мероприятия.</p>
          </div>

          <div className="border-l-4 border-[#F59E0B] pl-4">
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Модератор</h3>
            <p className="text-[#9CA3AF]">Проверяет и подтверждает проблемы, модерирует комментарии.</p>
          </div>

          <div className="border-l-4 border-[#3B82F6] pl-4">
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Официальное лицо</h3>
            <p className="text-[#9CA3AF]">Представитель городских служб, берет проблемы в работу и решает их.</p>
          </div>

          <div className="border-l-4 border-[#EF4444] pl-4">
            <h3 className="text-lg font-semibold text-[#E5E7EB] mb-2">Администратор</h3>
            <p className="text-[#9CA3AF]">Полный доступ к системе, управление пользователями и настройками.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
