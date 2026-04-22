#!/usr/bin/env python3
import random
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User
from app.models.problem import Problem
from app.models.media import ProblemMedia, MediaType, MediaCategory

IMAGES = [
    "1705803311114062047.jpg", "2-9058239.jpg", "316a6c7eaae9814290ac18bd652bd9969956ea21.jpg",
    "5b13b5b1dde224450b853f3ffe5fd66bbbb33050.jpg", "6834487_49_2595882_1289321915.jpg",
    "69f4f7es-960.jpg", "702d6ffc4eca81840584e0d0d1f0d76118096b82.jpg",
    "a-choked-urban-drain-filled-with-trash-causing-water-logging-and-urban-flooding_1045156-29488.jpg",
    "b5ad556f2dbff26dee5177be1862928f.jpg", "bc1c656s-1920.jpg",
    "dlya-voditelej-popavshix-v-yamu-1.jpg", "DSC03605.jpg",
    "e837e8a3d9246b4dc82c35fdfa678aaefe35b28b.jpg", "hq720_2.jpg",
    "jama-musor-svalka-min.jpg", "maxresdefault.jpg", "N0F1VoVuj-w.jpg",
    "obrashchenie.jpg", "plenar4.jpg", "problemy-vyvoza-musora-v-novyh-zhk.jpg",
    "TQtE1UwjvIc.jpg", "voronki-na-dorogakh-02.jpg",
    "waste-dump-concept-pile-of-garbage-garbage-dump-environmental-problems-pollution_667565-1579.jpg",
]

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).filter(User.is_current == True).all()
user_ids = [u.entity_id for u in users]
print(f'Found {len(user_ids)} users')

problems = session.query(Problem).filter(Problem.is_current == True).all()
print(f'Found {len(problems)} problems')

media_count = 0
for problem in problems:
    num_images = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]
    
    for i in range(num_images):
        image_file = random.choice(IMAGES)
        
        entity_id = ProblemMedia.next_entity_id(session)
        
        media = ProblemMedia(
            entity_id=entity_id,
            version=1,
            is_current=True,
            problem_entity_id=problem.entity_id,
            uploader_entity_id=problem.author_entity_id,
            media_type=MediaType.photo,
            media_category=MediaCategory.problem,
            url=f"/media/{image_file}",
            display_order=i,
        )
        session.add(media)
        media_count += 1
    
    if media_count % 20 == 0:
        session.commit()
        print(f'Added {media_count} media records...')

session.commit()
print(f'✅ Added {media_count} media records to problems!')
session.close()