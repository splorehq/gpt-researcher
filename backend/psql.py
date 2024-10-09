import json
import contextlib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from aws_secret_manager import AWSecretsManager
from psycopg_pool import AsyncConnectionPool

Base = declarative_base()

class PSQLSessionMgr:
    def __init__(self, config: dict, secret_mgr: AWSecretsManager):
        self.config = config
        self.secret_mgr = secret_mgr
        secrets = self.secret_mgr.get_secret(self.config["secrets_key"])

        # Map secrets for connection
        if secrets:
            self.host = secrets.get("host", config["host"])
            self.dbname = secrets.get("dbname", config["dbname"])
            self.user = secrets.get("username", config["username"])
            self.password = secrets.get("password", config["password"])
            self.port = config["port"]

            # Create the engine and session maker
            self._engine = create_async_engine(
                f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}",
                pool_size=config["pool_size"],
                pool_pre_ping=config["pool_pre_ping"],
                pool_recycle=config["pool_recycle"],
            )
            self._sess_maker = async_sessionmaker(
                self._engine, autoflush=False, expire_on_commit=False
            )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncSession: # type: ignore
        async with self._sess_maker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sess_maker = None

class PSQLPoolCreator:
    def __init__(self, config: dict, secret_mgr: AWSecretsManager):
        self.config = config
        self.secret_mgr = secret_mgr

    def __call__(self) -> AsyncConnectionPool:
        secrets = self.secret_mgr.get_secret(self.config["secrets_key"])

        if secrets:
            host = secrets.get("host", self.config["host"])
            dbname = secrets.get("dbname", self.config["dbname"])
            user = secrets.get("username", self.config["username"])
            password = secrets.get("password", self.config["password"])
            port = self.config["port"]

            conninfo = f"host={host} dbname={dbname} user={user} password={password} port={port}"
            pool = AsyncConnectionPool(
                conninfo=conninfo,
                min_size=self.config.get("min_size", 1),
                max_size=self.config.get("max_size", 20),
                open=True,
                max_lifetime=self.config.get("max_lifetime", 3600),
                max_idle=self.config.get("max_idle", 300),
                reconnect_timeout=self.config.get("reconnect_timeout", 10),
            )
            return pool
        else:
            raise ValueError("Unable to retrieve secrets for PostgreSQL connection.")
