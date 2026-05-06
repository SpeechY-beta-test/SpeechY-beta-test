"""retell

Revision ID: 042f735f0f7b
Revises: 971633f3f957
Create Date: 2026-05-06 10:14:32.420361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# revision identifiers, used by Alembic.
revision: str = '042f735f0f7b'
down_revision: Union[str, Sequence[str], None] = '971633f3f957'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


async def upgrade_async() -> None:
    """Асинхронное обновление данных."""
    from config import settings
    from database.services.data_seeder import DataSeeder
    from sqlalchemy.ext.asyncio import AsyncSession

    # Создаем асинхронное подключение
    database_url = settings.get_database_url()
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        seeder = DataSeeder(session)
        await seeder.update_seed_data()


def upgrade() -> None:
    """Точка входа для Alembic."""
    import asyncio
    asyncio.run(upgrade_async())


def downgrade() -> None:
    """Откат (опционально)."""
    pass
