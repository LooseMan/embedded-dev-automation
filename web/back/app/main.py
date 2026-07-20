# FastAPIのエントリーポイント

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from app.model import Base
from app.schema import AddRequest, AddResponse
from app.service import calc_add
from app.dependencies import get_db, engine

# 3. FastAPI起動時にテーブルを自動生成する設定 (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリ起動時にテーブルがなければ自動作成する
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # アプリ終了時のクリーンアップ処理（必要あれば）

app = FastAPI(lifespan=lifespan)

# FastAPIであれば以下のデコレータでログ出力を共通化できます
# @app.middleware("http")
@app.post("/add", response_model=AddResponse)
# Dependsを使って、get_db関数からセッションを取得する
# 規定以外のパラメータは末尾に配置する必要があります
async def add(
    request: AddRequest,
    db: AsyncSession = Depends(get_db)
) -> AddResponse:
    return await calc_add(request, db)