import logging

# ログの基本設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)

from functools import wraps

def log_function(func):
    """関数の開始・終了を自動ログ出力するデコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # func.__name__ で実行中の関数名を自動取得
        func_name = func.__name__
        
        logger.info(f"{func_name}() start.")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func_name}() end.")
            return result
        except Exception as e:
            logger.error(f"{func_name}() error.")
            raise
    return wrapper

# @log_function
# def hallo():
#     logger.info("Hello from stream_logger.py")
#     raise Exception("This is a test exception in hallo()")

# hallo()
