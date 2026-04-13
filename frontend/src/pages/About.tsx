export const About = () => {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="bg-[#111827] rounded-xl p-8 shadow-xl">
        <h1 className="text-3xl font-bold text-[#E5E7EB] mb-6">О проекте CityProblemMap</h1>

        <div className="space-y-6 text-[#9CA3AF]">
          <section>
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-3">Что это?</h2>
            <p>
              CityProblemMap — это платформа для отслеживания и решения городских проблем.
              Мы создаем цифровой двойник города, где граждане могут сообщать о проблемах
              (ямы на дорогах, неработающее освещение, переполненные мусорные баки и т.д.),
              а городские службы — оперативно их решать.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-3">Наша миссия</h2>
            <p>
              Сделать города лучше через прозрачность, вовлеченность граждан и эффективное
              взаимодействие с городскими службами. Каждый житель может внести свой вклад
              в улучшение городской среды.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-3">Как это работает?</h2>
            <ul className="list-disc list-inside space-y-2">
              <li>Граждане сообщают о проблемах через карту или форму</li>
              <li>Модераторы проверяют и подтверждают проблемы</li>
              <li>Городские службы получают уведомления и берут проблемы в работу</li>
              <li>Все могут отслеживать статус решения проблем в реальном времени</li>
              <li>Система геймификации мотивирует активных участников</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-[#E5E7EB] mb-3">Технологии</h2>
            <p>
              Платформа построена на современных технологиях: FastAPI, PostgreSQL с PostGIS
              для работы с геоданными, React для интерактивного интерфейса, и Leaflet для
              визуализации проблем на карте.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};
