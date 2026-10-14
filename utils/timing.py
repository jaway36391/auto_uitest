"""耗时记录工具模块

支持作为装饰器和上下文管理器两种使用方式。
"""

import functools
import logging
import time
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


class TimingResult:
    """耗时记录结果"""

    def __init__(self):
        self.elapsed: float = 0.0

    def __repr__(self) -> str:
        return f"TimingResult(elapsed={self.elapsed:.4f}s)"


@contextmanager
def timing(label: Optional[str] = None):
    """耗时记录上下文管理器

    Args:
        label: 可选的标签名称，用于日志输出

    Yields:
        TimingResult 实例，退出上下文后 elapsed 字段包含耗时秒数

    Example:
        with timing("数据加载") as t:
            load_data()
        print(f"耗时: {t.elapsed:.2f}s")
    """
    result = TimingResult()
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed = time.perf_counter() - start
        display_label = label or "操作"
        logger.info(f"{display_label} 耗时: {result.elapsed:.4f}s")


def timed(func=None, *, label: Optional[str] = None):
    """耗时记录装饰器

    可直接使用或带参数使用：
        @timed
        def my_func(): ...

        @timed(label="自定义标签")
        def my_func(): ...

    Args:
        func: 被装饰的函数（直接使用时自动传入）
        label: 可选的标签名称，默认使用函数名

    Returns:
        装饰后的函数，执行时自动记录耗时日志
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            display_label = label or fn.__name__
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                logger.info(f"{display_label} 耗时: {elapsed:.4f}s")

        return wrapper

    if func is not None:
        # @timed 无括号直接使用
        return decorator(func)
    # @timed(...) 带参数使用
    return decorator
