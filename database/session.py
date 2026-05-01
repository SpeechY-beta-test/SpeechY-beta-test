from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class Database:
    def __init__(self, url: str):
        if url is None:
            self.engine = None
            self.session_maker = None
        else:
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
        if self.engine:
            await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        if not self.session_maker:
            raise RuntimeError("Database not initialized")
        return self.session_maker()