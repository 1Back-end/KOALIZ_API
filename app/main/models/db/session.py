from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.main.core.config import Config


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URL,
    echo=False,  # To generate logs
    poolclass=QueuePool,
    pool_size=Config.SQLALCHEMY_POOL_SIZE,
    max_overflow=Config.SQLALCHEMY_MAX_OVERFLOW,
    pool_recycle=Config.SQLALCHEMY_POOL_RECYCLE,
    pool_timeout=Config.SQLALCHEMY_POOL_TIMEOUT,
    pool_pre_ping=Config.SQLALCHEMY_POOL_PRE_PING,
    connect_args={"connect_timeout": 60},
    isolation_level="READ UNCOMMITTED",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

