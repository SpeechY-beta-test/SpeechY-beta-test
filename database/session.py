from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Database:
    def __init__(self, url: str):
        self.engine = create_async_engine(
            url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def close(self):
        await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        return self.session_maker()
