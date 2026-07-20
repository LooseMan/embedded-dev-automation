# APIの入出力を定義する

from pydantic import BaseModel

class AddRequest(BaseModel):
    a: int  # デフォルト値がないため必須
    b: int  # デフォルト値がないため必須
    
class AddResponse(BaseModel):
    result: int  # 計算結果を返すためのフィールド
