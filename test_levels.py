from app.core.database import SessionLocal
from app.models.models import Level

db = SessionLocal()
try:
    count = db.query(Level).count()
    print(f'Total levels in DB: {count}')
    levels = db.query(Level).all()
    print(f'Found {len(levels)} levels')
    for i, level in enumerate(levels):
        print(f'Level {i}: {level.name}')
        print(f'  ID: {level.id}')
        print(f'  Description: {level.description}')
finally:
    db.close()