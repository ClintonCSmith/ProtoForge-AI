import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_RAW_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://protoforge:protoforge@localhost:5432/protoforge"
)

# Managed Postgres providers (Neon, Supabase, ...) append libpq-only query
# parameters such as `sslmode` and `channel_binding`. asyncpg rejects both, so
# translate them: SSL intent becomes a connect_arg, and the libpq-only params
# are stripped from the async URL. psycopg2 (sync Celery engine) keeps sslmode.
def _normalize_url(url: str):
    parts = urlsplit(url)
    params = dict(parse_qsl(parts.query))
    sslmode = params.pop("sslmode", None)
    params.pop("channel_binding", None)

    scheme = parts.scheme
    if scheme in ("postgresql", "postgres"):
        scheme = "postgresql+asyncpg"
    async_url = urlunsplit((scheme, parts.netloc, parts.path, urlencode(params), parts.fragment))

    connect_args = {}
    if sslmode and sslmode != "disable":
        connect_args["ssl"] = sslmode

    sync_params = dict(params)
    if sslmode:
        sync_params["sslmode"] = sslmode
    sync_url = urlunsplit(("postgresql", parts.netloc, parts.path, urlencode(sync_params), parts.fragment))

    return async_url, connect_args, sync_url


DATABASE_URL, _ASYNC_CONNECT_ARGS, SYNC_DATABASE_URL = _normalize_url(_RAW_DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True, connect_args=_ASYNC_CONNECT_ARGS
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Synchronous session for Celery tasks
sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
