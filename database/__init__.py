from config import settings
from database.base import Base
from database.session import Database
from database import models

# ✅ Создаем db только если не в контексте alembic
import sys
if 'alembic' not in sys.modules:
    db = Database(settings.get_database_url())
else:
    db = None

__all__ = ["db", "Base"]