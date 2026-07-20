# 4. FastAPIで使う依存関係（セッションの自動管理）

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# 1. データベースURLの設定 (asyncpgドライバを指定)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# 2. エンジンとセッションの作成
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# 4. FastAPIで使う依存関係（セッションの自動管理）
async def get_db():
    async with async_session() as session:
        yield session
