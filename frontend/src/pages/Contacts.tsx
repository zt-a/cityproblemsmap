import { Mail, Phone, MapPin, MessageSquare } from 'lucide-react';

export const Contacts = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
        <h1 className="text-3xl font-bold text-[#E5E7EB] mb-6">Контакты</h1>

        <div className="space-y-6">
          <section>
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-4">Свяжитесь с нами</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 bg-[#1F2937] rounded-lg">
                <Mail className="w-5 h-5 text-[#3B82F6] mt-1" />
                <div>
                  <p className="text-sm text-[#9CA3AF] mb-1">Email</p>
                  <a href="mailto:support@cityproblemmap.com" className="text-[#E5E7EB] hover:text-[#3B82F6] transition-colors">
                    support@cityproblemmap.com
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 bg-[#1F2937] rounded-lg">
                <Phone className="w-5 h-5 text-[#3B82F6] mt-1" />
                <div>
                  <p className="text-sm text-[#9CA3AF] mb-1">Телефон</p>
                  <a href="tel:+996555123456" className="text-[#E5E7EB] hover:text-[#3B82F6] transition-colors">
                    +996 555 123 456
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 bg-[#1F2937] rounded-lg">
                <MapPin className="w-5 h-5 text-[#3B82F6] mt-1" />
                <div>
                  <p className="text-sm text-[#9CA3AF] mb-1">Адрес</p>
                  <p className="text-[#E5E7EB]">г. Бишкек, Кыргызстан</p>
                </div>
              </div>

              <div className="flex items-start gap-4 p-4 bg-[#1F2937] rounded-lg">
                <MessageSquare className="w-5 h-5 text-[#3B82F6] mt-1" />
                <div>
                  <p className="text-sm text-[#9CA3AF] mb-1">Telegram</p>
                  <a href="https://t.me/cityproblemmap" target="_blank" rel="noopener noreferrer" className="text-[#E5E7EB] hover:text-[#3B82F6] transition-colors">
                    @cityproblemmap
                  </a>
                </div>
              </div>
            </div>
          </section>

          <section className="pt-6 border-t border-[#374151]">
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-4">Часы работы</h2>
            <div className="text-[#9CA3AF] space-y-2">
              <p>Понедельник - Пятница: 9:00 - 18:00</p>
              <p>Суббота: 10:00 - 14:00</p>
              <p>Воскресенье: Выходной</p>
            </div>
          </section>

          <section className="pt-6 border-t border-[#374151]">
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-4">Техническая поддержка</h2>
            <p className="text-[#9CA3AF] mb-4">
              Если у вас возникли технические проблемы с платформой, пожалуйста, опишите проблему
              и отправьте на tech@cityproblemmap.com. Мы ответим в течение 24 часов.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};
