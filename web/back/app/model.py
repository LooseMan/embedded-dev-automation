# DBテーブルを定義する

import datetime

from sqlalchemy import String, Text, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class APILog(Base):
    __tablename__ = "api_log"

    # プライマリキー（自動連番）が必要な場合は追加
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(255))
    phase: Mapped[str] = mapped_column(String(50))
    result: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text, nullable=True)
    # 💡 タイムスタンプカラムを追加（DB側で自動生成）
    # server_default=text("CURRENT_TIMESTAMP") でレコード作成時の日時が自動で入ります
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=text("CURRENT_TIMESTAMP")
    )
