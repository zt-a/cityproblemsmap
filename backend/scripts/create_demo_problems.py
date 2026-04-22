#!/usr/bin/env python3
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User
from app.models.problem import Problem, ProblemStatus, ProblemType, ProblemNature
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

PROBLEM_TITLES = {
    ProblemType.pothole: ['Большая яма на дороге', 'Опасная выбоина', 'Яма возле остановки'],
    ProblemType.garbage: ['Свалка мусора во дворе', 'Несанкционированная свалка', 'Куча строительного мусора'],
    ProblemType.flooding: ['Подтопление двора', 'Лужа на дороге', 'Не уходит вода'],
    ProblemType.lighting: ['Не работает уличный фонарь', 'Темный участок', 'Перегоревшие лампы'],
    ProblemType.traffic_light: ['Не работает светофор', 'Светофор мигает', 'Неправильный интервал'],
    ProblemType.road_work: ['Ремонт дороги', 'Вскрытое покрытие', 'Дорожные работы'],
    ProblemType.construction: ['Незаконченная стройка', 'Опасная стройка', 'Заброшенная стройка'],
    ProblemType.pollution: ['Загрязнение воздуха', 'Запах от предприятия', 'Дым из трубы'],
    ProblemType.infrastructure: ['Сломанная скамейка', 'Поврежденный забор', 'Аварийное состояние'],
    ProblemType.roads: ['Разбитая дорога', 'Нет асфальта', 'Колея'],
}

DISTRICTS = ['Центр', 'Первомайский', 'Сокулук', 'Ысык-Ата', 'Аламедин', 'Ленинский', 'Октябрьский']
ADDRESSES = ['ул. Киевская', 'ул. Логвиненко', 'ул. Панфилова', 'ул. Чуйкова', 'ул. Фрунзе', 'пр. Чингиза Айтматова']

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).filter(User.is_current == True).all()
user_ids = [u.entity_id for u in users]
print(f'Found {len(user_ids)} users')

for i in range(100):
    problem_type = random.choice(list(PROBLEM_TITLES.keys()))
    title = random.choice(PROBLEM_TITLES[problem_type])
    
    lat = 42.82 + random.uniform(-0.05, 0.05)
    lon = 74.55 + random.uniform(-0.05, 0.05)
    
    status = random.choice([ProblemStatus.pending, ProblemStatus.open, ProblemStatus.in_progress, ProblemStatus.solved, ProblemStatus.rejected])
    
    entity_id = Problem.next_entity_id(session)
    
    problem = Problem(
        entity_id=entity_id,
        version=1,
        is_current=True,
        author_entity_id=random.choice(user_ids),
        title=title,
        description='Прошу обратить внимание на эту проблему.',
        country='Kyrgyzstan',
        city='Bishkek',
        district=random.choice(DISTRICTS),
        address=f'{random.choice(ADDRESSES)}, {random.randint(1, 200)}',
        location=ST_SetSRID(ST_MakePoint(lon, lat), 4326),
        problem_type=problem_type,
        nature=random.choice([ProblemNature.temporary, ProblemNature.permanent]),
        status=status,
        vote_count=random.randint(0, 30),
        comment_count=random.randint(0, 10),
        truth_score=random.uniform(0.5, 1.0),
        urgency_score=random.uniform(0.3, 1.0),
        impact_score=random.uniform(0.4, 1.0),
        inconvenience_score=random.uniform(0.3, 0.9),
        priority_score=random.uniform(0.4, 0.95),
        tags=[problem_type.value],
    )
    
    if status == ProblemStatus.solved:
        problem.resolved_by_entity_id = random.choice(user_ids)
        problem.resolver_type = 'volunteer'
        problem.resolution_note = 'Проблема решена.'
    
    session.add(problem)
    
    if (i + 1) % 20 == 0:
        session.commit()
        print(f'Created {i + 1} problems...')

session.commit()
print('✅ Created 100 demo problems!')
session.close()