"""
P0 修复测试

P0-1: 日志落盘 - _configure_app_logging() 需要支持 RotatingFileHandler
P0-2: 子调用比对噪声过滤 - _sub_calls_have_diff() 需要支持 smart_noise_reduction / ignore_fields
"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from logging.handlers import RotatingFileHandler


# ─── P0-1: 日志落盘 ────────────────────────────────────────────────────────────

class TestFileLogging:
    """_configure_app_logging() 应当在配置了 log_file 时添加 RotatingFileHandler。"""

    def _collect_file_handlers(self):
        root = logging.getLogger()
        return [h for h in root.handlers if isinstance(h, (logging.FileHandler, RotatingFileHandler))]

    def _cleanup(self, handlers):
        root = logging.getLogger()
        for h in handlers:
            h.flush()
            h.close()
            root.removeHandler(h)

    def test_adds_rotating_file_handler_when_log_file_given(self, tmp_path):
        from main import _configure_app_logging

        log_file = str(tmp_path / "app.log")
        before = self._collect_file_handlers()

        _configure_app_logging(log_file=log_file)

        after = self._collect_file_handlers()
        new_handlers = [h for h in after if h not in before]
        self._cleanup(new_handlers)

        assert len(new_handlers) >= 1, "应当添加至少一个文件 handler"
        assert any(isinstance(h, RotatingFileHandler) for h in new_handlers), \
            "文件 handler 应当是 RotatingFileHandler"

    def test_log_messages_written_to_file(self, tmp_path):
        from main import _configure_app_logging

        log_file = str(tmp_path / "app.log")
        before = self._collect_file_handlers()

        _configure_app_logging(log_file=log_file)

        # 触发一条日志
        logging.getLogger("api").info("p0-test-marker-abc123")
        for h in logging.getLogger().handlers:
            h.flush()

        after = self._collect_file_handlers()
        new_handlers = [h for h in after if h not in before]
        self._cleanup(new_handlers)

        content = (tmp_path / "app.log").read_text(encoding="utf-8")
        assert "p0-test-marker-abc123" in content, "日志内容应写入文件"

    def test_no_file_handler_when_log_file_not_given(self):
        """不传 log_file 时不应新增任何 FileHandler。"""
        from main import _configure_app_logging

        before = self._collect_file_handlers()
        _configure_app_logging()  # 不传 log_file
        after = self._collect_file_handlers()
        new_handlers = [h for h in after if h not in before]

        assert len(new_handlers) == 0, "未配置 log_file 时不应添加文件 handler"

    def test_log_file_setting_used_when_no_param_given(self, tmp_path, monkeypatch):
        """当 settings.log_file 有值时，不传参数也应落盘。"""
        from main import _configure_app_logging
        import config

        log_file = str(tmp_path / "settings_driven.log")
        monkeypatch.setattr(config.settings, "log_file", log_file, raising=False)

        before = self._collect_file_handlers()
        _configure_app_logging()
        after = self._collect_file_handlers()
        new_handlers = [h for h in after if h not in before]
        self._cleanup(new_handlers)

        assert len(new_handlers) >= 1, "settings.log_file 有值时应自动落盘"


# ─── P0-2: 子调用比对噪声过滤 ─────────────────────────────────────────────────

class TestSubCallNoiseReduction:
    """_sub_calls_have_diff() 应当支持 smart_noise_reduction 和 ignore_fields 参数。"""

    # helpers
    @staticmethod
    def _make_calls(response_dict, call_type="MySQL", operation="LoanRepository.findAll"):
        return json.dumps([{
            "type": call_type,
            "operation": operation,
            "request": "{}",
            "response": json.dumps(response_dict),
        }])

    def test_baseline_detects_any_change_without_noise_reduction(self):
        """无噪声过滤时，任何响应字段变化都算差异（基准行为不变）。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls({"createdAt": "2024-01-01", "status": "approved"})
        actual   = self._make_calls({"createdAt": "2024-06-15", "status": "approved"})

        assert _sub_calls_have_diff(expected, actual) is True

    def test_smart_noise_reduction_ignores_timestamp_only_diff(self):
        """smart_noise_reduction=True 时，仅 createdAt 变化不应判为差异。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls({"createdAt": "2024-01-01", "status": "approved"})
        actual   = self._make_calls({"createdAt": "2024-06-15", "status": "approved"})

        assert _sub_calls_have_diff(expected, actual, smart_noise_reduction=True) is False

    def test_smart_noise_reduction_still_catches_real_content_diff(self):
        """smart_noise_reduction=True 时，真实字段差异（status 变化）仍应被检出。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls({"createdAt": "2024-01-01", "status": "approved"})
        actual   = self._make_calls({"createdAt": "2024-06-15", "status": "rejected"})

        assert _sub_calls_have_diff(expected, actual, smart_noise_reduction=True) is True

    def test_ignore_fields_excludes_specified_field(self):
        """ignore_fields 中的字段变化不应判为差异。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls(
            {"balance": 1000, "lastLoginIp": "192.168.1.1"},
            call_type="HttpClient", operation="/api/balance",
        )
        actual = self._make_calls(
            {"balance": 1000, "lastLoginIp": "10.0.0.1"},  # IP 变了
            call_type="HttpClient", operation="/api/balance",
        )

        assert _sub_calls_have_diff(expected, actual) is True, "不加 ignore_fields 应检出差异"
        assert _sub_calls_have_diff(expected, actual, ignore_fields=["lastLoginIp"]) is False, \
            "ignore_fields 包含 lastLoginIp 时不应检出差异"

    def test_ignore_fields_does_not_suppress_unrelated_diff(self):
        """ignore_fields 只忽略指定字段，其他差异仍应被检出。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls(
            {"balance": 1000, "lastLoginIp": "192.168.1.1"},
            call_type="HttpClient", operation="/api/balance",
        )
        actual = self._make_calls(
            {"balance": 9999, "lastLoginIp": "10.0.0.1"},  # balance 也变了
            call_type="HttpClient", operation="/api/balance",
        )

        assert _sub_calls_have_diff(expected, actual, ignore_fields=["lastLoginIp"]) is True, \
            "balance 变化不应被 ignore_fields=['lastLoginIp'] 掩盖"

    def test_noise_reduction_on_http_sub_call_requestid(self):
        """HTTP 子调用中 requestId 字段变化（在内置噪声列表中）不应判为差异。"""
        from core.replay_executor import _sub_calls_have_diff

        expected = self._make_calls(
            {"requestId": "abc-111", "data": "ok"},
            call_type="HttpClient", operation="/api/query",
        )
        actual = self._make_calls(
            {"requestId": "xyz-999", "data": "ok"},
            call_type="HttpClient", operation="/api/query",
        )

        assert _sub_calls_have_diff(expected, actual) is True, "无噪声过滤时应检出 requestId 变化"
        assert _sub_calls_have_diff(expected, actual, smart_noise_reduction=True) is False, \
            "smart_noise_reduction 应忽略 requestId 变化"
