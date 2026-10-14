"""可配置的重试装饰器模块"""

import functools
import time
import logging
from typing import Type, Tuple

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """可配置的重试装饰器

    Args:
        max_attempts: 最大重试次数，默认3次
        delay: 每次重试间隔秒数，默认1秒
        exceptions: 需要捕获并重试的异常类型元组，默认捕获所有异常

    Returns:
        装饰器函数

    Example:
        @retry(max_attempts=3, delay=2.0, exceptions=(TimeoutError, ConnectionError))
        def fetch_data():
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"{func.__name__} 第{attempt}次执行失败，"
                            f"{delay}s后重试: {e}"
                        )
                        time.sleep(delay)
            raise last_exception  # type: ignore[misc]

        return wrapper

    return decorator
