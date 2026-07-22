import os
import glob
from app.config import settings
from app.database import engine
print('DATABASE_URL=', settings.DATABASE_URL)
print('ENGINE_URL=', str(engine.url))
print('CWD=', os.getcwd())
print('DB_FILES=')
for path in sorted(glob.glob('**/*.db', recursive=True)):
    print(path)
