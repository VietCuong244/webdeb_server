from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

# postgresql+asyncpg:// thay vì postgresql://
engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # tránh lỗi khi access object sau commit
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()