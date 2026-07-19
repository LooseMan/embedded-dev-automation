from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from contextlib import asynccontextmanager

from app.db_logger import insert_api_log
from app.db_models import Base
from app.api_models import AddRequest, AddResponse
from app.stream_logger import log_function

# 1. データベースURLの設定 (asyncpgドライバを指定)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# 2. エンジンとセッションの作成
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

# 3. FastAPI起動時にテーブルを自動生成する設定 (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリ起動時にテーブルがなければ自動作成する
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # アプリ終了時のクリーンアップ処理（必要あれば）

# 4. FastAPIで使う依存関係（セッションの自動管理）
async def get_db():
    async with async_session() as session:
        yield session

app = FastAPI(lifespan=lifespan)

# FastAPIであれば以下のデコレータでログ出力を共通化できます
# @app.middleware("http")
@app.post("/add")
@log_function
# Dependsを使って、get_db関数からセッションを取得する
# 規定以外のパラメータは末尾に配置する必要があります
async def add(
    request: AddRequest,
    db: AsyncSession = Depends(get_db)
):
    result = request.a + request.b
    await insert_api_log(db, api="add", phase="post", result="success", message=f"Adding {request.a} and {request.b}")
    return AddResponse(result=result)
