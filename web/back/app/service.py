# APIの処理を定義する

from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import insert_api_log
from app.schema import AddRequest, AddResponse
from app.stream_logger import log_function

@log_function
async def calc_add(
    request: AddRequest,
    db: AsyncSession
) -> AddResponse:
    result = request.a + request.b
    await insert_api_log(db, api="add", phase="post", result="success", message=f"Adding {request.a} and {request.b}")
    return AddResponse(result=result)
