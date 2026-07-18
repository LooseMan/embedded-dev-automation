from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models import APILog

async def insert_api_log(db: AsyncSession, api: str, phase: str, result: str, message: str):
    # データをオブジェクトとして作成（SQLの文字列結合をしないので安全）
    new_log = APILog(
        api_name=api,
        phase=phase,
        result=result,
        message=message
    )
    
    # セッションに追加してコミット
    db.add(new_log)
    await db.commit()
