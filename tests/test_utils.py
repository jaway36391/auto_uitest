"""utils 模块单元测试"""

import time

import pytest

from utils.retry import retry
from utils.timing import timed, timing


class TestRetryDecorator:
    """重试装饰器测试"""

    def test_success_on_first_attempt(self):
        """首次执行成功时不重试"""
        call_count = 0

        @retry(max_attempts=3, delay=0)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_success_after_retries(self):
        """失败后重试成功"""
        call_count = 0

        @retry(max_attempts=3, delay=0)
        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fail_then_succeed()
        assert result == "ok"
        assert call_count == 3

    def test_raises_after_max_attempts(self):
        """达到最大重试次数后抛出最后一次异常"""

        @retry(max_attempts=3, delay=0)
        def always_fail():
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError, match="always fails"):
            always_fail()

    def test_only_catches_specified_exceptions(self):
        """仅捕获指定的异常类型"""
        call_count = 0

        @retry(max_attempts=3, delay=0, exceptions=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raise_type_error()
        # TypeError 不在 exceptions 中，不应重试
        assert call_count == 1

    def test_respects_max_attempts(self):
        """尊重 max_attempts 参数"""
        call_count = 0

        @retry(max_attempts=5, delay=0)
        def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fail()
        assert call_count == 5

    def test_preserves_function_metadata(self):
        """保留被装饰函数的元数据"""

        @retry(max_attempts=2, delay=0)
        def my_function():
            """My docstring"""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring"


class TestTimingContextManager:
    """耗时记录上下文管理器测试"""

    def test_records_elapsed_time(self):
        """记录执行耗时"""
        with timing("test") as t:
            time.sleep(0.05)
        assert t.elapsed >= 0.04  # 允许少量误差

    def test_elapsed_is_zero_before_exit(self):
        """进入上下文时 elapsed 为 0"""
        with timing("test") as t:
            assert t.elapsed == 0.0

    def test_works_without_label(self):
        """不传 label 也能正常工作"""
        with timing() as t:
            pass
        assert t.elapsed >= 0.0

    def test_records_time_even_on_exception(self):
        """异常时也记录耗时"""
        result = None
        with pytest.raises(ValueError):
            with timing("error_test") as result:
                time.sleep(0.02)
                raise ValueError("oops")
        assert result is not None
        assert result.elapsed >= 0.01


class TestTimedDecorator:
    """耗时记录装饰器测试"""

    def test_timed_without_args(self):
        """@timed 无参数使用"""

        @timed
        def fast_func():
            return 42

        assert fast_func() == 42

    def test_timed_with_label(self):
        """@timed(label=...) 带参数使用"""

        @timed(label="custom")
        def fast_func():
            return "hello"

        assert fast_func() == "hello"

    def test_preserves_function_metadata(self):
        """保留被装饰函数的元数据"""

        @timed
        def my_func():
            """My doc"""
            pass

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My doc"

    def test_propagates_exceptions(self):
        """异常正常传播"""

        @timed
        def raise_error():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            raise_error()
