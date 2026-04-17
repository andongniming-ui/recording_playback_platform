"""Unit tests for _fetch_nls_sub_calls — N-LS sub-call enrichment logic."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# XML 请求体模板（A0201D012 还款，含 account_no / loan_no）
_REQ_REPAY = """<REQUEST>
  <SYS_EVT_TRACE_ID>TRACE-001</SYS_EVT_TRACE_ID>
  <account_no>ACC-001</account_no>
  <loan_no>LOAN-001</loan_no>
  <repayment_amount>500.00</repayment_amount>
</REQUEST>"""

# XML 请求体模板（A0201D014，XML 中无 loan_no，需从响应反查）
_REQ_NO_LOAN = """<REQUEST>
  <SYS_EVT_TRACE_ID>TRACE-002</SYS_EVT_TRACE_ID>
  <account_no>ACC-002</account_no>
</REQUEST>"""


def _make_conn_mock(side_effects: list):
    """构造 aiomysql 连接 mock，cursor 的 execute/fetchone/fetchall 按顺序返回。"""
    cursor = AsyncMock()
    cursor.description = []  # 默认空，各测试自行覆盖

    # fetchone / fetchall 按调用顺序消费 side_effects
    cursor.fetchone = AsyncMock(side_effect=[
        se for se in side_effects if not isinstance(se, list)
    ])
    cursor.fetchall = AsyncMock(side_effect=[
        se for se in side_effects if isinstance(se, list)
    ])
    cursor.execute = AsyncMock()

    conn = AsyncMock()
    conn.cursor = AsyncMock(return_value=cursor)
    conn.close = MagicMock()
    return conn, cursor


# ---------------------------------------------------------------------------
# 辅助：构建完整的 aiomysql.connect mock，返回两次连接（conn / conn2）
# ---------------------------------------------------------------------------

def _mock_connect(conn1, conn2):
    """patch aiomysql.connect，第一次返回 conn1，第二次返回 conn2。"""
    return AsyncMock(side_effect=[conn1, conn2])


# ---------------------------------------------------------------------------
# 测试 1：bank_account UPDATE 子节点被添加（有 account_no）
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_bank_account_child_appended():
    from api.v1.sessions import _fetch_nls_sub_calls

    # conn1：查 bank_transaction_log → tx_log_id=1；查 bank_sub_call_log → 1 步骤
    cursor1 = AsyncMock()
    cursor1.execute = AsyncMock()
    cursor1.fetchone = AsyncMock(side_effect=[(1,)])       # tx_log_id
    cursor1.fetchall = AsyncMock(return_value=[
        ("repay", "db", "repay detail", 120, "SUCCESS"),
    ])
    conn1 = AsyncMock()
    conn1.cursor = AsyncMock(return_value=cursor1)
    conn1.close = MagicMock()

    # conn2：bank_transaction_log写入、bank_statement_line写入、
    #         bank_account UPDATE、bank_loan UPDATE（无 loan_no，跳过）
    acct_row = ("ACC-001", "1000.00", "ACTIVE", "2026-01-01")
    cursor2 = AsyncMock()
    cursor2.execute = AsyncMock()
    # fetchone: txlog → acct_row（按 execute 顺序）
    cursor2.fetchone = AsyncMock(side_effect=[
        ("TX-001", "A0201D012", "还款", "ACC-001", None, "SUCCESS", "2026-01-01"),  # txlog
        acct_row,   # bank_account
        None,       # bank_loan（loan_no 为空，execute 不会被调 — 但防御性加一个 None）
    ])
    cursor2.fetchall = AsyncMock(return_value=[])  # bank_statement_line 无流水
    # description for bank_account SELECT *
    cursor2.description = [
        ("account_no",), ("balance",), ("status",), ("updated_at",)
    ]
    conn2 = AsyncMock()
    conn2.cursor = AsyncMock(return_value=cursor2)
    conn2.close = MagicMock()

    with patch("api.v1.sessions.settings") as mock_settings, \
         patch("aiomysql.connect", AsyncMock(side_effect=[conn1, conn2])):
        mock_settings.nls_mysql_host = "127.0.0.1"
        mock_settings.nls_mysql_port = 3306
        mock_settings.nls_mysql_user = "root"
        mock_settings.nls_mysql_password = "pass"

        result = await _fetch_nls_sub_calls(_REQ_REPAY, "nls-sat")

    assert len(result) == 1
    repay = result[0]
    assert repay["operation"] == "repay"

    children = repay.get("children", [])
    ops = [c["operation"] for c in children]
    assert "UPDATE bank_account" in ops, f"bank_account UPDATE missing, got: {ops}"

    acct_child = next(c for c in children if c["operation"] == "UPDATE bank_account")
    assert acct_child["table"] == "bank_account"
    assert acct_child["status"] == "WRITE"
    assert acct_child["request"] == {"account_no": "ACC-001"}
    assert acct_child["response"]["account_no"] == "ACC-001"
    assert acct_child["response"]["balance"] == "1000.00"


# ---------------------------------------------------------------------------
# 测试 2：bank_loan UPDATE 子节点被添加（loan_no 直接来自 XML）
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_bank_loan_child_appended():
    from api.v1.sessions import _fetch_nls_sub_calls

    cursor1 = AsyncMock()
    cursor1.execute = AsyncMock()
    cursor1.fetchone = AsyncMock(side_effect=[(1,)])
    cursor1.fetchall = AsyncMock(return_value=[
        ("repay", "db", "repay detail", 100, "SUCCESS"),
    ])
    conn1 = AsyncMock()
    conn1.cursor = AsyncMock(return_value=cursor1)
    conn1.close = MagicMock()

    loan_row = ("LOAN-001", "9500.00", "ACTIVE", "2026-01-01")
    # description 随 execute 的 SQL 内容切换
    _desc_by_table = {
        "bank_account": [("account_no",), ("balance",), ("status",), ("updated_at",)],
        "bank_loan":    [("loan_no",), ("principal_balance",), ("status",), ("updated_at",)],
    }
    cursor2 = AsyncMock()
    cursor2.description = []

    async def _execute2(sql, params=None):
        for tbl, desc in _desc_by_table.items():
            if tbl in sql:
                cursor2.description = desc
                return

    cursor2.execute = _execute2
    cursor2.fetchone = AsyncMock(side_effect=[
        ("TX-002", "A0201D012", "还款", "ACC-001", "LOAN-001", "SUCCESS", "2026-01-01"),  # txlog
        ("ACC-001", "500.00", "ACTIVE", "2026-01-01"),  # bank_account
        loan_row,                                        # bank_loan
    ])
    cursor2.fetchall = AsyncMock(return_value=[])

    conn2 = AsyncMock()
    conn2.cursor = AsyncMock(return_value=cursor2)
    conn2.close = MagicMock()

    with patch("api.v1.sessions.settings") as mock_settings, \
         patch("aiomysql.connect", AsyncMock(side_effect=[conn1, conn2])):
        mock_settings.nls_mysql_host = "127.0.0.1"
        mock_settings.nls_mysql_port = 3306
        mock_settings.nls_mysql_user = "root"
        mock_settings.nls_mysql_password = "pass"

        result = await _fetch_nls_sub_calls(_REQ_REPAY, "nls-sat")

    assert len(result) == 1
    children = result[0].get("children", [])
    ops = [c["operation"] for c in children]
    assert "UPDATE bank_loan" in ops, f"bank_loan UPDATE missing, got: {ops}"

    loan_child = next(c for c in children if c["operation"] == "UPDATE bank_loan")
    assert loan_child["table"] == "bank_loan"
    assert loan_child["request"] == {"loan_no": "LOAN-001"}
    assert loan_child["response"]["loan_no"] == "LOAN-001"


# ---------------------------------------------------------------------------
# 测试 3：无 loan_no 时从 step_children 响应反查（A0201D014 场景）
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_loan_no_fallback_from_arex_mocker_response():
    """XML 中无 loan_no，但 arex_mocker 里 findLoanByNo 响应包含 loan_no。"""
    from api.v1.sessions import _fetch_nls_sub_calls
    from models.arex_mocker import ArexMocker
    import json

    cursor1 = AsyncMock()
    cursor1.execute = AsyncMock()
    cursor1.fetchone = AsyncMock(side_effect=[(1,)])
    cursor1.fetchall = AsyncMock(return_value=[
        ("loan-load", "db", "loan detail", 80, "SUCCESS"),
        ("repay", "db", "repay detail", 150, "SUCCESS"),
    ])
    conn1 = AsyncMock()
    conn1.cursor = AsyncMock(return_value=cursor1)
    conn1.close = MagicMock()

    # conn2：txlog 无数据，statement 无数据，account 无 account_no（XML 中没有）
    # _REQ_NO_LOAN 含 account_no=ACC-002，所以 bank_account 查询也会触发
    # fetchone 顺序：txlog → None，bank_account → None（忽略），bank_loan → loan_row
    loan_row = ("LOAN-999", "8000.00", "ACTIVE", "2026-01-01")
    _desc_by_table3 = {
        "bank_loan": [("loan_no",), ("principal_balance",), ("status",), ("updated_at",)],
    }
    cursor2 = AsyncMock()
    cursor2.description = []

    async def _execute3(sql, params=None):
        for tbl, desc in _desc_by_table3.items():
            if tbl in sql:
                cursor2.description = desc
                return

    cursor2.execute = _execute3
    cursor2.fetchone = AsyncMock(side_effect=[
        None,       # txlog（无记录）
        None,       # bank_account（有 account_no 但返回空，测试忽略）
        loan_row,   # bank_loan
    ])
    cursor2.fetchall = AsyncMock(return_value=[])
    conn2 = AsyncMock()
    conn2.cursor = AsyncMock(return_value=cursor2)
    conn2.close = MagicMock()

    # arex_mocker 行：findLoanByNo 响应含 loan_no
    mocker_row = MagicMock()
    mocker_row.record_id = "REC-002"
    mocker_row.is_entry_point = False
    mocker_row.category_name = "DynamicClass"
    mocker_row.created_at_ms = 1000
    mocker_row.mocker_data = json.dumps({
        "operationName": "com.example.BankJdbcRepository.findLoanByNo",
        "targetResponse": {"body": json.dumps({"loan_no": "LOAN-999", "principal_balance": 8000})},
    })

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mocker_row]
    mock_db.execute = AsyncMock(return_value=mock_result)

    with patch("api.v1.sessions.settings") as mock_settings, \
         patch("aiomysql.connect", AsyncMock(side_effect=[conn1, conn2])):
        mock_settings.nls_mysql_host = "127.0.0.1"
        mock_settings.nls_mysql_port = 3306
        mock_settings.nls_mysql_user = "root"
        mock_settings.nls_mysql_password = "pass"

        result = await _fetch_nls_sub_calls(
            _REQ_NO_LOAN, "nls-sat", record_id="REC-002", db=mock_db
        )

    assert len(result) == 2
    repay = next((s for s in result if s["operation"] == "repay"), None)
    assert repay is not None, "repay step not found"
    children = repay.get("children", [])
    ops = [c["operation"] for c in children]
    assert "UPDATE bank_loan" in ops, f"bank_loan UPDATE missing when loan_no fallback: {ops}"

    loan_child = next(c for c in children if c["operation"] == "UPDATE bank_loan")
    assert loan_child["request"] == {"loan_no": "LOAN-999"}


# ---------------------------------------------------------------------------
# 测试 4：N-LS 连不上时整体降级为空列表（不抛异常）
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_nls_connection_failure_returns_empty():
    from api.v1.sessions import _fetch_nls_sub_calls

    with patch("api.v1.sessions.settings") as mock_settings, \
         patch("aiomysql.connect", AsyncMock(side_effect=OSError("connection refused"))):
        mock_settings.nls_mysql_host = "127.0.0.1"
        mock_settings.nls_mysql_port = 3306
        mock_settings.nls_mysql_user = "root"
        mock_settings.nls_mysql_password = "pass"

        result = await _fetch_nls_sub_calls(_REQ_REPAY, "nls-sat")

    assert result == []
