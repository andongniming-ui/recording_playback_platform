"""
P1/P2 修复测试

P1-1: 子调用比对无 diff 详情 - _build_sub_call_diff_pairs() 返回每对的 diff 细节
P1-2: AREX flush 无确认机制 - 支持重试配置，空结果时自动重试
P2-1: 录制逐条操作日志 (纯日志，无需测试)
P2-2: SQL 原文提取 - normalize_repository_sub_call() 追加 sql_text 字段
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


# ─── P1-1: 子调用比对 diff 详情 ────────────────────────────────────────────────

class TestSubCallDiffDetail:
    """_build_sub_call_diff_pairs() 应返回每对子调用的结构化比对结果。"""

    def test_matched_identical_pair_has_no_diff(self):
        from core.replay_executor import _build_sub_call_diff_pairs

        data = json.dumps([{
            "type": "MySQL", "operation": "SELECT customer",
            "request": {}, "response": {"name": "Alice", "status": "active"},
        }])
        pairs = _build_sub_call_diff_pairs(data, data)

        assert len(pairs) == 1
        assert pairs[0]["matched"] is True
        assert pairs[0]["has_diff"] is False
        assert pairs[0]["diff_result"] is None

    def test_matched_pair_with_response_diff_shows_detail(self):
        from core.replay_executor import _build_sub_call_diff_pairs

        expected = json.dumps([{
            "type": "MySQL", "operation": "SELECT customer",
            "request": {}, "response": {"status": "approved"},
        }])
        actual = json.dumps([{
            "type": "MySQL", "operation": "SELECT customer",
            "request": {}, "response": {"status": "rejected"},
        }])
        pairs = _build_sub_call_diff_pairs(expected, actual)

        assert len(pairs) == 1
        assert pairs[0]["has_diff"] is True
        assert pairs[0]["matched"] is True
        assert pairs[0]["diff_result"] is not None, "应包含 DeepDiff JSON"
        # diff_result 里应提到 status 字段
        assert "status" in pairs[0]["diff_result"]

    def test_unmatched_recorded_call_marked_missing(self):
        """录制存在但回放没有的子调用，应标记 matched=False。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        expected = json.dumps([{
            "type": "MySQL", "operation": "SELECT product",
            "request": {}, "response": {},
        }])
        pairs = _build_sub_call_diff_pairs(expected, json.dumps([]))

        assert len(pairs) == 1
        assert pairs[0]["matched"] is False
        assert pairs[0]["has_diff"] is True

    def test_extra_actual_call_appended_as_unmatched(self):
        """回放多出的子调用（录制不存在）应追加到结果中，标记为 matched=False。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        actual = json.dumps([{
            "type": "HttpClient", "operation": "/api/extra",
            "request": {}, "response": {},
        }])
        pairs = _build_sub_call_diff_pairs(json.dumps([]), actual)

        assert len(pairs) == 1
        assert pairs[0]["matched"] is False
        assert pairs[0]["has_diff"] is True

    def test_returns_empty_list_for_null_inputs(self):
        from core.replay_executor import _build_sub_call_diff_pairs

        assert _build_sub_call_diff_pairs(None, None) == []

    def test_pair_includes_expected_and_actual_response(self):
        """每对结果都应包含 expected_response 和 actual_response 字段，便于前端展示。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        expected = json.dumps([{
            "type": "MySQL", "operation": "SELECT blacklist",
            "request": {}, "response": {"blocked": False},
        }])
        actual = json.dumps([{
            "type": "MySQL", "operation": "SELECT blacklist",
            "request": {}, "response": {"blocked": True},
        }])
        pairs = _build_sub_call_diff_pairs(expected, actual)

        assert "expected_response" in pairs[0]
        assert "actual_response" in pairs[0]

    def test_diff_pairs_stored_in_replay_result_schema(self):
        """ReplayResultOut schema 应包含 sub_call_diff_detail 字段。"""
        from schemas.replay import ReplayResultOut
        assert "sub_call_diff_detail" in ReplayResultOut.model_fields

    def test_diff_pairs_supports_noise_reduction(self):
        """噪声过滤参数应透传到 diff 细节计算中。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        expected = json.dumps([{
            "type": "MySQL", "operation": "SELECT customer",
            "request": {}, "response": {"createdAt": "2024-01-01", "name": "Bob"},
        }])
        actual = json.dumps([{
            "type": "MySQL", "operation": "SELECT customer",
            "request": {}, "response": {"createdAt": "2024-12-31", "name": "Bob"},
        }])
        # 无噪声：有 diff
        pairs_without = _build_sub_call_diff_pairs(expected, actual)
        assert pairs_without[0]["has_diff"] is True

        # 有噪声：createdAt 被忽略，无 diff
        pairs_with = _build_sub_call_diff_pairs(expected, actual, smart_noise_reduction=True)
        assert pairs_with[0]["has_diff"] is False

    def test_diff_pairs_treat_json_encoded_xml_string_as_same_response(self):
        """AREX 可能把同一段 XML 响应保存成原文或 JSON 字符串字面量。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        xml = "<BookVo><idcard>440203198709237790</idcard><opendate>2026-04-27</opendate></BookVo>"
        expected = json.dumps([{
            "type": "HttpClient",
            "operation": "/order/search",
            "request": {},
            "response": xml,
        }], ensure_ascii=False)
        actual = json.dumps([{
            "type": "HttpClient",
            "operation": "/order/search",
            "request": {},
            "response": json.dumps(xml, ensure_ascii=False),
        }], ensure_ascii=False)

        pairs = _build_sub_call_diff_pairs(expected, actual, smart_noise_reduction=True)

        assert len(pairs) == 1
        assert pairs[0]["matched"] is True
        assert pairs[0]["has_diff"] is False

    def test_diff_pairs_treat_sibling_http_body_wrapper_as_same_response(self):
        """回放侧 sibling Servlet 兜底会把 HttpClient 响应包成 {httpStatus, body}。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        xml = "<BookVo><dinner>白切鸡、冬瓜</dinner></BookVo>"
        expected = json.dumps([{
            "type": "HttpClient",
            "operation": "/order/query",
            "request": {"responseType": "java.lang.String"},
            "response": xml,
        }], ensure_ascii=False)
        actual = json.dumps([{
            "type": "HttpClient",
            "operation": "/order/query",
            "request": {"responseType": "java.lang.String"},
            "response": {"httpStatus": 200, "body": xml},
        }], ensure_ascii=False)

        pairs = _build_sub_call_diff_pairs(expected, actual)

        assert len(pairs) == 1
        assert pairs[0]["matched"] is True
        assert pairs[0]["has_diff"] is False

    def test_diff_pairs_prefers_matching_sql_params_for_duplicate_operations(self):
        """同一 operation 重复出现时，应优先按 SQL 参数匹配，避免错配。"""
        from core.replay_executor import _build_sub_call_diff_pairs

        expected = json.dumps([
            {
                "type": "Database",
                "operation": "query",
                "sql": "select * from cust_info where idcard=?",
                "params": ["A"],
                "response": [{"idcard": "A", "name": "Alice"}],
            },
            {
                "type": "Database",
                "operation": "query",
                "sql": "select * from cust_info where idcard=?",
                "params": ["B"],
                "response": [{"idcard": "B", "name": "Bob"}],
            },
        ], ensure_ascii=False)
        actual = json.dumps([
            {
                "type": "Database",
                "operation": "query",
                "sql": "select * from cust_info where idcard=?",
                "params": ["B"],
                "response": [{"idcard": "B", "name": "Bob"}],
            },
            {
                "type": "Database",
                "operation": "query",
                "sql": "select * from cust_info where idcard=?",
                "params": ["A"],
                "response": [{"idcard": "A", "name": "Alice"}],
            },
        ], ensure_ascii=False)

        pairs = _build_sub_call_diff_pairs(expected, actual)

        assert len(pairs) == 2
        assert all(pair["matched"] for pair in pairs)
        assert all(not pair["has_diff"] for pair in pairs)


# ─── P1-2: AREX flush 重试机制 ──────────────────────────────────────────────────

class TestArexFlushRetry:
    """AREX agent flush 后空结果时，应按配置自动重试。"""

    def test_settings_has_flush_max_retries(self):
        from config import settings
        assert hasattr(settings, "arex_flush_max_retries"), \
            "settings 应有 arex_flush_max_retries 字段"
        assert isinstance(settings.arex_flush_max_retries, int)
        assert settings.arex_flush_max_retries >= 1

    def test_settings_has_flush_retry_interval(self):
        from config import settings
        assert hasattr(settings, "arex_flush_retry_interval_s"), \
            "settings 应有 arex_flush_retry_interval_s 字段"
        assert isinstance(settings.arex_flush_retry_interval_s, float)
        assert settings.arex_flush_retry_interval_s > 0

    @pytest.mark.asyncio
    async def test_fetch_sub_calls_retries_when_empty_then_succeeds(self, monkeypatch):
        """首次查询返回空时，应重试直到有结果或达到上限。"""
        import asyncio
        import core.replay_executor as executor
        from unittest.mock import AsyncMock, MagicMock, patch

        # 模拟第1次返回空，第2次返回结果
        call_count = [0]

        class FakeRow:
            record_id = "r1"
            app_id = "app1"
            category_name = "DynamicClass"
            is_entry_point = False
            id = 1
            mocker_data = json.dumps({
                "operationName": "com.example.Repo.findAll",
                "categoryType": {"name": "DynamicClass"},
                "targetRequest": {"body": "{}"},
                "targetResponse": {"body": "{}"},
            })

        async def fake_execute(stmt):
            call_count[0] += 1
            fake_result = MagicMock()
            if call_count[0] < 2:
                fake_result.scalars.return_value.all.return_value = []
            else:
                fake_result.scalars.return_value.all.return_value = [FakeRow()]
            return fake_result

        sleep_calls = []
        async def fake_sleep(seconds):
            sleep_calls.append(seconds)

        # Patch settings to use 2 retries with fast interval
        monkeypatch.setattr(executor.settings, "arex_flush_max_retries", 2, raising=False)
        monkeypatch.setattr(executor.settings, "arex_flush_retry_interval_s", 0.01, raising=False)
        monkeypatch.setattr(executor.settings, "arex_flush_delay_s", 0.0, raising=False)
        monkeypatch.setattr(executor, "_AREX_AGENT_FLUSH_DELAY_S", 0.0)

        with patch("asyncio.sleep", side_effect=fake_sleep):
            with patch("database.async_session_factory") as mock_factory:
                mock_session = AsyncMock()
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=False)
                mock_session.execute = fake_execute
                mock_factory.return_value = mock_session

                result = await executor._fetch_replay_sub_calls("test-record-id")

        # Should have retried at least once (call_count > 1)
        assert call_count[0] >= 2, f"应至少重试一次，实际调用 {call_count[0]} 次"

    @pytest.mark.asyncio
    async def test_fetch_sub_calls_stops_after_max_retries(self, monkeypatch):
        """达到最大重试次数后应停止，即使仍为空。"""
        import core.replay_executor as executor
        from unittest.mock import AsyncMock, MagicMock, patch

        call_count = [0]

        async def fake_execute(stmt):
            call_count[0] += 1
            fake_result = MagicMock()
            fake_result.scalars.return_value.all.return_value = []  # 始终为空
            return fake_result

        monkeypatch.setattr(executor.settings, "arex_flush_max_retries", 2, raising=False)
        monkeypatch.setattr(executor.settings, "arex_flush_retry_interval_s", 0.01, raising=False)
        monkeypatch.setattr(executor.settings, "arex_flush_delay_s", 0.0, raising=False)
        monkeypatch.setattr(executor, "_AREX_AGENT_FLUSH_DELAY_S", 0.0)

        async def fake_sleep(seconds):
            pass

        with patch("asyncio.sleep", side_effect=fake_sleep):
            with patch("database.async_session_factory") as mock_factory:
                mock_session = AsyncMock()
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=False)
                mock_session.execute = fake_execute
                mock_factory.return_value = mock_session

                result = await executor._fetch_replay_sub_calls("test-record-id")

        # Should stop after initial + max_retries attempts
        max_calls = 1 + executor.settings.arex_flush_max_retries
        assert call_count[0] <= max_calls, \
            f"最多查询 {max_calls} 次，实际 {call_count[0]} 次"
        assert result is None, "全部为空时应返回 None"


# ─── P2-2: SQL 原文 / sql_text 字段 ────────────────────────────────────────────

class TestSqlTextExtraction:
    """normalize_repository_sub_call() 应在 sub_call 中追加可读的 sql_text 字段。"""

    def test_select_method_includes_sql_text(self):
        from utils.repository_capture import normalize_repository_sub_call

        mocker = {
            "operationName": "com.arex.demo.loan.repository.LoanDataRepository.findCustomer",
            "targetRequest": {"body": json.dumps(["C001"])},
            "targetResponse": {"body": json.dumps({"name": "Alice", "score": 750})},
        }
        result = normalize_repository_sub_call(mocker, "DynamicClass")

        assert result is not None
        assert "sql_text" in result, "应包含 sql_text 字段"
        assert "customer" in result["sql_text"].lower(), "sql_text 应含表名"

    def test_select_sql_text_contains_param_value(self):
        """SELECT 类操作的 sql_text 应包含参数值，便于定位具体查询。"""
        from utils.repository_capture import normalize_repository_sub_call

        mocker = {
            "operationName": "com.arex.demo.loan.repository.LoanDataRepository.findCustomer",
            "targetRequest": {"body": json.dumps(["CUST-42"])},
            "targetResponse": {"body": "{}"},
        }
        result = normalize_repository_sub_call(mocker, "DynamicClass")

        assert result is not None
        assert "CUST-42" in result["sql_text"], "sql_text 应包含入参值"

    def test_insert_method_includes_sql_text_with_insert_keyword(self):
        from utils.repository_capture import normalize_repository_sub_call

        mocker = {
            "operationName": "com.arex.demo.waimai.repository.WaimaiDataRepository.insertOrder",
            "targetRequest": {"body": json.dumps(["O001", "customer_1", "merchant_1", "PENDING"])},
            "targetResponse": {"body": "null"},
        }
        result = normalize_repository_sub_call(mocker, "DynamicClass")

        assert result is not None
        assert "sql_text" in result
        assert "INSERT" in result["sql_text"].upper()
        assert "orders" in result["sql_text"].lower()

    def test_update_method_includes_sql_text_with_update_keyword(self):
        from utils.repository_capture import normalize_repository_sub_call

        mocker = {
            "operationName": "com.arex.demo.waimai.repository.WaimaiDataRepository.updateOrderStatus",
            "targetRequest": {"body": json.dumps(["O001", "DELIVERED"])},
            "targetResponse": {"body": "null"},
        }
        result = normalize_repository_sub_call(mocker, "DynamicClass")

        assert result is not None
        assert "sql_text" in result
        assert "UPDATE" in result["sql_text"].upper()

    def test_unknown_method_does_not_crash(self):
        """未知方法不应影响主流程，sql_text 可以缺失但不能抛异常。"""
        from utils.repository_capture import normalize_repository_sub_call

        mocker = {
            "operationName": "com.example.Unknown.unknownMethod",
            "targetRequest": {"body": "{}"},
            "targetResponse": {"body": "{}"},
        }
        # 未知方法应返回 None（lookup 失败），不抛异常
        result = normalize_repository_sub_call(mocker, "DynamicClass")
        assert result is None or isinstance(result, dict)

    def test_generic_jdbc_mocker_is_normalized_to_database_sub_call(self):
        from utils.repository_capture import normalize_generic_database_sub_call

        mocker = {
            "operationName": "SELECT * FROM account WHERE id = ?",
            "targetRequest": {
                "attributes": {"Database": "bank", "Table": "account"},
                "body": json.dumps({"sql": "SELECT * FROM account WHERE id = ?", "params": [1]}),
            },
            "targetResponse": {"body": json.dumps({"rows": [{"id": 1, "balance": 100}]})},
        }
        result = normalize_generic_database_sub_call(mocker, "JDBC")

        assert result is not None
        assert result["type"] == "MySQL"
        assert result["database"] == "bank"
        assert result["table"] == "account"
        assert result["sql_text"] == "SELECT * FROM account WHERE id = ?"
