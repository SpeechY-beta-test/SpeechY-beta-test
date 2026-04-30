from config import settings
from database.base import Base
from database.session import Database
from database import models

db = Database(settings.get_database_url())

__all__ = ["db", "Base"]
