from fastapi import FastAPI

from web.back.app.logger import write_log

app = FastAPI()


@app.post("/device/start")
async def root():
    # return {"message": "Hello World"}
    write_log("/device/start", "START", "-", "API開始")

    try:

        #
        # デバイス処理
        #

        write_log("/device/start", "END", "OK", "正常終了")

        return {"result": "OK"}

    except Exception as e:

        write_log("/device/start", "END", "NG", str(e))

        raise