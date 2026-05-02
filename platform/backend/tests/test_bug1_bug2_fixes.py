"""
Bug 1 / Bug 2 回归测试

Bug 1: _execute_single 中 actual_response 永远存储 actual_body（未 mapping 的原始响应）
       因为 `status == "OK_GOT_RESPONSE"` 条件在此处永远为 False
       修复：直接使用 mapped_actual_body

Bug 2: fail_on_sub_call_diff 默认值被改为 True（破坏性变更）
       修复：恢复为 False，调用方若需要开启需显式传 True
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


# ─── Bug 2: fail_on_sub_call_diff 默认值 ───────────────────────────────────────

class TestFailOnSubCallDiffDefault:
    """fail_on_sub_call_diff 在 schema 中应默认为 False。"""

    def test_replay_job_create_default_is_false(self):
        """ReplayJobCreate 不显式传 fail_on_sub_call_diff 时应为 False。"""
        from schemas.replay import ReplayJobCreate

        job = ReplayJobCreate(case_ids=[1])
        assert job.fail_on_sub_call_diff is False, (
            "Default should be False; True would silently break all existing "
            "callers that do not set this field explicitly."
        )

    def test_replay_job_out_field_default_is_false(self):
        """ReplayJobOut schema 字段默认值应为 False。"""
        from schemas.replay import ReplayJobOut

        field = ReplayJobOut.model_fields["fail_on_sub_call_diff"]
        assert field.default is False, (
            f"ReplayJobOut.fail_on_sub_call_diff default should be False, got {field.default!r}"
        )


# ─── Bug 1: actual_response 应存储 mapped body ─────────────────────────────────

class TestActualResponseStoresMappedBody:
    """_execute_single 应将 transaction-mapped 响应体存入 actual_response。"""

    @pytest.mark.asyncio
    async def test_actual_response_is_mapped_not_raw(self, monkeypatch):
        """当 transaction mapping 转换了响应体时，actual_response 应为 mapped 版本。

        Before fix: `mapped_actual_body if status == "OK_GOT_RESPONSE" else actual_body`
                    status 在此处是 PASS/FAIL，条件永远 False → 存 actual_body（原始）
        After fix:  直接使用 mapped_actual_body（mapping 后的值）
        """
        import core.replay_executor as executor
        from unittest.mock import AsyncMock, MagicMock, patch

        RAW_BODY = '{"amount":100}'
        MAPPED_BODY = '{"loanAmount":100}'  # transaction mapping 改了字段名

        case = MagicMock()
        case.id = 7
        case.application_id = None
        case.transaction_code = "LOAN_QUERY"
        case.request_method = "POST"
        case.request_uri = "/api/loan/query"
        case.request_body = '{"id":"L001"}'
        case.request_headers = "{}"
        case.ignore_fields = None
        case.assert_rules = None
        case.expected_response = MAPPED_BODY   # 与 mapped_body 相同 → PASS
        case.expected_status = None
        case.source_recording_id = None

        saved: dict = {}

        async def capture_save(job_id, case_id, **kw):
            saved.update(kw)
            r = MagicMock()
            r.id = 99
            r.status = kw.get("status", "PASS")
            return r

        monkeypatch.setattr(executor, "_save_result", capture_save)
        monkeypatch.setattr(executor, "_append_replay_audit_log", AsyncMock())
        monkeypatch.setattr(executor, "_fetch_replay_sub_calls", AsyncMock(return_value=None))

        # response direction → MAPPED_BODY; request direction → 原样返回
        def fake_mapping(body, txn_code, mappings, direction):
            return MAPPED_BODY if direction == "response" else body

        monkeypatch.setattr(executor, "apply_transaction_mapping", fake_mapping)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = RAW_BODY
        mock_resp.headers = {}   # .get("arex-record-id") → None

        with patch("httpx.AsyncClient") as MockClient:
            mock_http = AsyncMock()
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_http.request = AsyncMock(return_value=mock_resp)

            await executor._execute_single(
                job_id=1,
                case_id=7,
                case=case,
                target_host="http://localhost:8080",
                arex_storage_url="http://arex:8090",
                timeout_ms=5000,
                diff_rules=[],
                base_ignore_fields=[],
                assertions_config=[],
                transaction_mappings=[],
                fail_on_sub_call_diff=False,
            )

        actual_response = saved.get("actual_response")
        assert actual_response == MAPPED_BODY, (
            f"actual_response should be the transaction-mapped body '{MAPPED_BODY}', "
            f"but got '{actual_response}'. "
            "This indicates the fix for `status == 'OK_GOT_RESPONSE'` dead-code "
            "condition was not applied."
        )

    @pytest.mark.asyncio
    async def test_actual_response_without_mapping_equals_raw(self, monkeypatch):
        """无 transaction mapping 时，actual_response 应等于原始响应体（行为不变）。"""
        import core.replay_executor as executor
        from unittest.mock import AsyncMock, MagicMock, patch

        RAW_BODY = '{"result":"ok"}'

        case = MagicMock()
        case.id = 8
        case.application_id = None
        case.transaction_code = None
        case.request_method = "GET"
        case.request_uri = "/api/ping"
        case.request_body = None
        case.request_headers = "{}"
        case.ignore_fields = None
        case.assert_rules = None
        case.expected_response = RAW_BODY
        case.expected_status = None
        case.source_recording_id = None

        saved: dict = {}

        async def capture_save(job_id, case_id, **kw):
            saved.update(kw)
            r = MagicMock()
            r.id = 100
            r.status = kw.get("status", "PASS")
            return r

        monkeypatch.setattr(executor, "_save_result", capture_save)
        monkeypatch.setattr(executor, "_append_replay_audit_log", AsyncMock())
        monkeypatch.setattr(executor, "_fetch_replay_sub_calls", AsyncMock(return_value=None))

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = RAW_BODY
        mock_resp.headers = {}

        with patch("httpx.AsyncClient") as MockClient:
            mock_http = AsyncMock()
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            mock_http.request = AsyncMock(return_value=mock_resp)

            await executor._execute_single(
                job_id=1,
                case_id=8,
                case=case,
                target_host="http://localhost:8080",
                arex_storage_url="http://arex:8090",
                timeout_ms=5000,
                diff_rules=[],
                base_ignore_fields=[],
                assertions_config=[],
                transaction_mappings=[],
                fail_on_sub_call_diff=False,
            )

        assert saved.get("actual_response") == RAW_BODY, (
            "Without mapping, actual_response should equal the raw HTTP response body."
        )
