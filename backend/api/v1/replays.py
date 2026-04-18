"""Replay job management API."""
import asyncio
import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy import String, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from core.replay_context import infer_application_id_for_case_ids
from core.replay_executor import register_ws, unregister_ws
from core.security import require_editor, require_viewer
from database import async_session_factory, get_db
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from schemas.replay import ReplayJobCreate, ReplayJobOut, ReplayResultOut
from utils.failure_analyzer import analyze_failure

router = APIRouter(prefix="/replays", tags=["replays"])


def _load_jsonish(value):
    if value in (None, ""):
        return None
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


def _count_sub_call_nodes(value) -> int:
    parsed = _load_jsonish(value)
    if not isinstance(parsed, list):
        return 0

    total = 0
    for item in parsed:
        if not isinstance(item, dict):
            continue
        total += 1
        for key in ("children", "subCalls", "subInvocations", "sub_invocations", "items"):
            nested = item.get(key)
            if isinstance(nested, list) and nested:
                total += _count_sub_call_nodes(nested)
                break
    return total


async def _build_result_source_context(db: AsyncSession, result: ReplayResult) -> dict:
    context = {
        "use_sub_invocation_mocks": False,
        "source_recording_id": None,
        "source_recording_transaction_code": None,
        "source_recording_scene_key": None,
        "source_recording_sub_call_count": None,
    }

    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == result.job_id))
    job = job_result.scalar_one_or_none()
    if job:
        context["use_sub_invocation_mocks"] = bool(job.use_sub_invocation_mocks)

    if not result.test_case_id:
        return context

    case_result = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
    test_case = case_result.scalar_one_or_none()
    if not test_case:
        return context

    context["source_recording_id"] = test_case.source_recording_id

    if not test_case.source_recording_id:
        return context

    rec_result = await db.execute(select(Recording).where(Recording.id == test_case.source_recording_id))
    recording = rec_result.scalar_one_or_none()
    if not recording:
        return context

    context["source_recording_transaction_code"] = recording.transaction_code
    context["source_recording_scene_key"] = recording.scene_key
    context["source_recording_sub_call_count"] = _count_sub_call_nodes(recording.sub_calls)
    return context


@router.post("", response_model=ReplayJobOut, status_code=201)
async def create_replay_job(
    body: ReplayJobCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Create and start a replay job."""
    if not body.case_ids:
        raise HTTPException(status_code=400, detail="case_ids must not be empty")

    from sqlalchemy import func

    count_result = await db.execute(
        select(func.count()).select_from(TestCase).where(TestCase.id.in_(body.case_ids))
    )
    found_count = count_result.scalar()
    if found_count != len(body.case_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Some case_ids do not exist: expected {len(body.case_ids)}, found {found_count}",
        )

    try:
        inferred_application_id = await infer_application_id_for_case_ids(db, body.case_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    application_id = body.application_id
    if inferred_application_id is not None:
        if application_id is not None and application_id != inferred_application_id:
            raise HTTPException(
                status_code=400,
                detail="application_id does not match the selected test cases",
            )
        application_id = inferred_application_id

    job = ReplayJob(
        name=body.name,
        application_id=application_id,
        status="PENDING",
        concurrency=body.concurrency,
        timeout_ms=body.timeout_ms,
        delay_ms=body.delay_ms,
        total=len(body.case_ids),
        use_sub_invocation_mocks=body.use_sub_invocation_mocks,
        ignore_fields=json.dumps(body.ignore_fields, ensure_ascii=False) if body.ignore_fields else None,
        diff_rules=json.dumps([rule.model_dump(exclude_none=True) for rule in body.diff_rules], ensure_ascii=False) if body.diff_rules else None,
        assertions=json.dumps([rule.model_dump(exclude_none=True) for rule in body.assertions], ensure_ascii=False) if body.assertions else None,
        header_transforms=json.dumps([item.model_dump(exclude_none=True) for item in body.header_transforms], ensure_ascii=False) if body.header_transforms else None,
        perf_threshold_ms=body.perf_threshold_ms,
        webhook_url=body.webhook_url,
        notify_type=body.notify_type,
        smart_noise_reduction=body.smart_noise_reduction,
        retry_count=body.retry_count,
        repeat_count=body.repeat_count,
        target_host=body.target_host,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in body.case_ids:
        db.add(
            ReplayResult(
                job_id=job.id,
                test_case_id=case_id,
                status="PENDING",
                is_pass=False,
            )
        )
    await db.commit()

    import core.replay_executor as replay_executor

    asyncio.create_task(replay_executor.run_replay_job(job.id))
    return job


@router.get("", response_model=list[ReplayJobOut])
async def list_replay_jobs(
    application_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(ReplayJob)
    if application_id:
        stmt = stmt.where(ReplayJob.application_id == application_id)
    if status:
        stmt = stmt.where(ReplayJob.status == status)
    if search:
        stmt = stmt.where(
            or_(
                ReplayJob.name.contains(search),
                ReplayJob.id.cast(String).contains(search),
            )
        )
    if created_after:
        stmt = stmt.where(ReplayJob.created_at >= created_after)
    if created_before:
        stmt = stmt.where(ReplayJob.created_at <= created_before)
    stmt = stmt.order_by(ReplayJob.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{job_id}", response_model=ReplayJobOut)
async def get_replay_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")
    return job


@router.get("/results/{result_id}", response_model=ReplayResultOut)
async def get_replay_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    replay_result = result.scalar_one_or_none()
    if not replay_result:
        raise HTTPException(status_code=404, detail="Replay result not found")
    out = ReplayResultOut.model_validate(replay_result)
    tx_result = await db.execute(
        select(TestCase.transaction_code).where(TestCase.id == replay_result.test_case_id)
    )
    out.transaction_code = tx_result.scalar_one_or_none()
    context = await _build_result_source_context(db, replay_result)
    for key, value in context.items():
        setattr(out, key, value)
    return out


def _pair_sub_calls(recorded: list, replayed: list) -> list:
    """Pair recorded and replayed sub-calls by sequential index."""
    max_len = max(len(recorded), len(replayed)) if (recorded or replayed) else 0
    pairs = []
    for i in range(max_len):
        rec = recorded[i] if i < len(recorded) else None
        rep = replayed[i] if i < len(replayed) else None
        if rec and rep:
            side = "both"
            try:
                response_matched = (
                    json.dumps(rec.get("response"), sort_keys=True)
                    == json.dumps(rep.get("response"), sort_keys=True)
                )
            except Exception:
                response_matched = False
        elif rec:
            side = "recorded_only"
            response_matched = None
        else:
            side = "replayed_only"
            response_matched = None
        pairs.append({
            "index": i + 1,
            "type": (rec or rep or {}).get("type") or "",
            "recorded": rec,
            "replayed": rep,
            "side": side,
            "response_matched": response_matched,
        })
    return pairs


@router.get("/results/{result_id}/sub-call-diff")
async def get_sub_call_diff(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Return paired sub-calls for a replay result: recorded vs replayed."""
    result_row = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    result = result_row.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Replay result not found")

    # Load recorded sub-calls from source recording
    recorded_raw = []
    if result.test_case_id:
        case_row = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
        test_case = case_row.scalar_one_or_none()
        if test_case and test_case.source_recording_id:
            rec_row = await db.execute(
                select(Recording).where(Recording.id == test_case.source_recording_id)
            )
            recording = rec_row.scalar_one_or_none()
            if recording and recording.sub_calls:
                try:
                    recorded_raw = json.loads(recording.sub_calls)
                    if not isinstance(recorded_raw, list):
                        recorded_raw = []
                except Exception:
                    recorded_raw = []

    # Load replayed sub-calls stored during replay execution
    replayed_raw = []
    if result.actual_sub_calls:
        try:
            replayed_raw = json.loads(result.actual_sub_calls)
            if not isinstance(replayed_raw, list):
                replayed_raw = []
        except Exception:
            replayed_raw = []

    pairs = _pair_sub_calls(recorded_raw, replayed_raw)
    return {
        "recorded": recorded_raw,
        "replayed": replayed_raw,
        "pairs": pairs,
    }


@router.get("/{job_id}/results", response_model=list[ReplayResultOut])
async def list_results(
    job_id: int,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    from sqlalchemy.orm import aliased
    stmt = (
        select(ReplayResult, TestCase.transaction_code)
        .outerjoin(TestCase, TestCase.id == ReplayResult.test_case_id)
        .where(ReplayResult.job_id == job_id)
    )
    if status:
        stmt = stmt.where(ReplayResult.status == status)
    stmt = stmt.order_by(ReplayResult.id).offset(skip).limit(limit)
    rows = (await db.execute(stmt)).all()
    results = []
    for rr, tx_code in rows:
        out = ReplayResultOut.model_validate(rr)
        out.transaction_code = tx_code
        context = await _build_result_source_context(db, rr)
        for key, value in context.items():
            setattr(out, key, value)
        results.append(out)
    return results


@router.get("/{job_id}/report")
async def get_html_report(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Generate a detailed downloadable HTML report for a replay job."""
    from fastapi.responses import Response as FastAPIResponse
    from models.application import Application

    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results_query = await db.execute(
        select(ReplayResult).where(ReplayResult.job_id == job_id).order_by(ReplayResult.id)
    )
    results = results_query.scalars().all()

    # 获取应用名称
    app_name = "-"
    if job.application_id:
        app_res = await db.execute(select(Application).where(Application.id == job.application_id))
        app = app_res.scalar_one_or_none()
        if app:
            app_name = app.name

    # 获取测试用例 request_body / transaction_code
    case_ids = [r.test_case_id for r in results if r.test_case_id]
    case_map: dict[int, any] = {}
    if case_ids:
        cases_res = await db.execute(select(TestCase).where(TestCase.id.in_(case_ids)))
        for tc in cases_res.scalars().all():
            case_map[tc.id] = tc

    source_recording_map: dict[int, dict] = {}
    for tc in case_map.values():
        if not tc.source_recording_id or tc.source_recording_id in source_recording_map:
            continue
        rec_res = await db.execute(select(Recording).where(Recording.id == tc.source_recording_id))
        recording = rec_res.scalar_one_or_none()
        if recording:
            source_recording_map[tc.source_recording_id] = {
                "transaction_code": recording.transaction_code,
                "scene_key": recording.scene_key,
                "sub_call_count": _count_sub_call_nodes(recording.sub_calls),
            }

    import html as html_lib

    def esc(s: str) -> str:
        return html_lib.escape(str(s)) if s else ""

    pass_rate_num = (job.passed / job.total * 100) if job.total > 0 else 0
    pass_rate_str = f"{pass_rate_num:.1f}%"
    pass_color = "#18a058" if pass_rate_num >= 90 else "#f0a020" if pass_rate_num >= 60 else "#d03050"

    status_label_map = {"PENDING": "待执行", "RUNNING": "运行中", "DONE": "已完成", "FAILED": "失败", "CANCELLED": "已取消"}

    # 忽略字段 / 差异规则 / 断言规则
    ignore_fields_list: list[str] = []
    if job.ignore_fields:
        try:
            ignore_fields_list = json.loads(job.ignore_fields)
        except Exception:
            pass
    diff_rules_str = "无"
    if job.diff_rules:
        try:
            rules = json.loads(job.diff_rules)
            diff_rules_str = ", ".join(r.get("type", "") for r in rules) if rules else "无"
        except Exception:
            pass
    assertions_str = "无"
    if job.assertions:
        try:
            assts = json.loads(job.assertions)
            assertions_str = ", ".join(a.get("type", "") for a in assts) if assts else "无"
        except Exception:
            pass
    mock_mode_str = "开启" if job.use_sub_invocation_mocks else "关闭"

    # 失败原因分析
    from utils.failure_analyzer import analyze_failure
    category_counts: dict[str, int] = {"ENVIRONMENT": 0, "DATA_ISSUE": 0, "BUG": 0, "PERFORMANCE": 0, "UNKNOWN": 0}
    fail_results = [r for r in results if not r.is_pass]
    for rr in fail_results:
        assertion_list = None
        if rr.assertion_results:
            try:
                assertion_list = json.loads(rr.assertion_results)
            except Exception:
                pass
        category, _ = analyze_failure(
            error_message=rr.failure_reason if rr.status in ("ERROR", "TIMEOUT") else None,
            diff_json=rr.diff_result, diff_score=rr.diff_score,
            replayed_status_code=rr.actual_status_code, assertion_results=assertion_list,
        )
        if category in category_counts:
            category_counts[category] += 1

    total_fail_cnt = len(fail_results) or 1
    analysis_cells = ""
    category_defs = [
        ("ENVIRONMENT", "🌐", "环境问题", "#f0a020"),
        ("DATA_ISSUE",  "📝", "数据问题", "#2080f0"),
        ("BUG",         "🐛", "代码缺陷", "#d03050"),
        ("PERFORMANCE", "⚡", "性能问题", "#8a2be2"),
        ("UNKNOWN",     "❓", "未知",     "#999"),
    ]
    for key, icon, label, color in category_defs:
        cnt = category_counts.get(key, 0)
        pct = cnt / total_fail_cnt * 100
        analysis_cells += f"""<td class="analysis-cell">
            <div class="a-icon">{icon}</div>
            <div class="a-label">{label}</div>
            <div class="a-count" style="color:{color}">{cnt}</div>
            <div class="a-bar-bg"><div class="a-bar" style="width:{pct:.0f}%;background:{color}"></div></div>
            <div class="a-pct">{pct:.0f}%</div>
        </td>"""

    # 逐条结果
    rows_html = ""
    for i, result in enumerate(results):
        tc = case_map.get(result.test_case_id) if result.test_case_id else None
        tx_code = tc.transaction_code if tc else ""
        req_body = tc.request_body if tc else ""
        source_recording = source_recording_map.get(tc.source_recording_id) if tc and tc.source_recording_id else None

        status_cls = "pass" if result.is_pass else ("error" if result.status in ("ERROR", "TIMEOUT") else "fail")
        status_txt = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERROR", "TIMEOUT": "TIMEOUT"}.get(result.status, result.status)
        latency = f"{result.latency_ms}" if result.latency_ms is not None else "-"
        source_summary = "-"
        if source_recording:
            source_summary = f"录制 #{tc.source_recording_id} / 子调用 {source_recording['sub_call_count']}"

        # Diff score + diff count
        diff_count = 0
        diff_details_html = ""
        if result.diff_result:
            try:
                diff_obj = json.loads(result.diff_result)
                if isinstance(diff_obj, dict):
                    diff_count = len(diff_obj)
                    for path, detail in list(diff_obj.items())[:20]:
                        detail_str = json.dumps(detail, ensure_ascii=False) if not isinstance(detail, str) else detail
                        diff_details_html += f"<div class='diff-item'><span class='diff-path'>{esc(path)}</span><div class='diff-val'>{esc(detail_str)}</div></div>"
            except Exception:
                pass
        diff_score_str = f"score={result.diff_score:.3f}，{diff_count} 处差异" if result.diff_score is not None else "-"
        diff_color = "#18a058" if (result.diff_score or 0) <= 0.1 else "#f0a020" if (result.diff_score or 0) <= 0.5 else "#d03050"

        # 请求体
        req_body_disp = esc(req_body[:4000]) if req_body else "(无)"
        # 响应（原始/回放）
        expected_raw = result.expected_response or ""
        actual_raw = result.actual_response or ""
        # 不做 JSON 格式化（XML 等原样展示）
        expected_disp = esc(expected_raw[:4000])
        actual_disp = esc(actual_raw[:4000])

        detail_id = f"d{i}"
        detail_block = ""
        if not result.is_pass:
            detail_block = f"""<tr id="{detail_id}" class="detail-row" style="display:none">
  <td colspan="7">
    <div class="detail-grid">
      <div class="detail-section">
        <div class="detail-title">📤 请求体（录制时）</div>
        <pre class="code-pre">{req_body_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">🔗 来源录制</div>
        <pre class="code-pre">{esc(source_summary)}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">📥 原始响应（录制时）</div>
        <pre class="code-pre">{expected_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">🔄 回放响应</div>
        <pre class="code-pre">{actual_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">📋 差异明细</div>
        <div class="diff-details">{diff_details_html if diff_details_html else '<span style="color:#999">无差异明细</span>'}</div>
      </div>
    </div>
  </td>
</tr>"""

        click_attr = f'onclick="toggle(\'{detail_id}\')" style="cursor:pointer"' if not result.is_pass else ""
        interface_label = f"{esc(result.request_uri or '')}"
        if tx_code:
            interface_label += f'<br><span class="tx-code">{esc(tx_code)}</span>'
        time_str = result.created_at.strftime("%Y-%m-%d %H:%M:%S") if result.created_at else "-"
        rows_html += f"""<tr class="result-row" data-status="{result.status}" {click_attr}>
  <td class="uri-cell">{interface_label}</td>
  <td><span class="badge {status_cls}">{status_txt}</span></td>
  <td style="color:{diff_color};font-size:12px">{esc(diff_score_str)}</td>
  <td>{result.actual_status_code or '-'}</td>
  <td>{latency}</td>
  <td class="time-cell">{time_str}</td>
</tr>{detail_block}"""

    ignore_meta = "、".join(ignore_fields_list) if ignore_fields_list else "无"
    started = job.started_at.strftime("%Y-%m-%d %H:%M:%S") if job.started_at else "-"
    ended = job.finished_at.strftime("%Y-%m-%d %H:%M:%S") if job.finished_at else "-"
    job_name = esc(job.name or f"任务 #{job_id}")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>录制回放测试报告 - {job_name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#222;font-size:14px}}
.page{{max-width:1280px;margin:0 auto;padding:20px}}
/* 顶部标题栏 */
.top-bar{{background:#1a1a2e;color:#fff;padding:14px 24px;border-radius:10px 10px 0 0;display:flex;align-items:center;gap:10px}}
.top-bar h1{{font-size:16px;font-weight:600}}
/* 信息条 */
.meta-bar{{background:#fff;border:1px solid #e8e8e8;border-top:none;padding:12px 24px;font-size:12px;color:#666;line-height:2;border-radius:0 0 10px 10px;margin-bottom:16px}}
.meta-bar span{{margin-right:16px}}
.meta-bar b{{color:#333}}
/* 统计卡片 */
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px}}
.stat{{background:#fff;border-radius:10px;padding:18px 12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.stat .num{{font-size:36px;font-weight:700;line-height:1.1}}
.stat .lbl{{font-size:12px;color:#888;margin-top:4px}}
.stat.total .num{{color:#333}}
.stat.pass .num{{color:#18a058}}
.stat.fail .num{{color:#d03050}}
.stat.err .num{{color:#f0a020}}
.stat.rate .num{{color:{pass_color}}}
/* 分析卡片 */
.card{{background:#fff;border-radius:10px;padding:18px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.card-title{{font-size:14px;font-weight:600;color:#444;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid #f0f0f0}}
.analysis-table{{width:100%;border-collapse:collapse}}
.analysis-cell{{text-align:center;padding:16px 8px;border:1px solid #f5f5f5}}
.a-icon{{font-size:22px;margin-bottom:4px}}
.a-label{{font-size:12px;color:#666;margin-bottom:6px}}
.a-count{{font-size:26px;font-weight:700;margin-bottom:6px}}
.a-bar-bg{{background:#f0f0f0;border-radius:4px;height:6px;margin:4px 8px}}
.a-bar{{height:6px;border-radius:4px}}
.a-pct{{font-size:12px;color:#999;margin-top:4px}}
/* 筛选条 */
.filter-bar{{display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap}}
.tab-btn{{padding:5px 14px;border-radius:20px;border:1px solid #ddd;background:#fff;cursor:pointer;font-size:13px;color:#666}}
.tab-btn.active,.tab-btn:hover{{background:#1a1a2e;color:#fff;border-color:#1a1a2e}}
.search-box{{margin-left:auto;padding:5px 12px;border:1px solid #ddd;border-radius:20px;font-size:13px;width:220px;outline:none}}
.count-info{{font-size:12px;color:#999}}
/* 结果表格 */
table.result-table{{width:100%;border-collapse:collapse;font-size:13px}}
table.result-table th{{background:#fafafa;padding:10px 12px;text-align:left;border-bottom:2px solid #eee;color:#555;font-weight:600}}
table.result-table td{{padding:10px 12px;border-bottom:1px solid #f5f5f5;vertical-align:middle}}
.result-row:hover td{{background:#fafbfc}}
.uri-cell{{font-family:monospace;font-size:12px;max-width:320px;word-break:break-all}}
.tx-code{{display:inline-block;background:#e8f0fe;color:#1a73e8;border-radius:4px;padding:1px 6px;font-size:11px;margin-top:2px;font-family:sans-serif}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600}}
.badge.pass{{background:#e8f5e9;color:#18a058}}
.badge.fail{{background:#fce4e4;color:#d03050}}
.badge.error{{background:#fff3e0;color:#f0a020}}
.time-cell{{font-size:11px;color:#999;white-space:nowrap}}
/* 详情展开 */
.detail-row td{{padding:0;background:#fffdf5;border-bottom:1px solid #fde}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0;padding:16px 20px;gap:16px}}
.detail-section{{}}
.detail-title{{font-size:13px;font-weight:600;color:#555;margin-bottom:8px}}
.code-pre{{background:#f8f8f8;border:1px solid #eee;border-radius:6px;padding:10px;font-size:11px;font-family:'Courier New',monospace;white-space:pre-wrap;word-break:break-all;max-height:280px;overflow-y:auto;line-height:1.5}}
.diff-details{{background:#fff9e6;border:1px solid #ffe58f;border-radius:6px;padding:10px}}
.diff-item{{padding:6px 0;border-bottom:1px solid #ffd;font-size:12px}}
.diff-item:last-child{{border-bottom:none}}
.diff-path{{color:#d03050;font-weight:600;font-family:monospace;font-size:11px}}
.diff-val{{margin-top:3px;font-family:monospace;font-size:11px;color:#666;word-break:break-all}}
</style>
</head>
<body>
<div class="page">

<div class="top-bar">
  <span>🖥</span>
  <h1>录制回放测试报告</h1>
  <span style="color:#aaa;margin:0 6px">›</span>
  <span style="opacity:.8">{esc(app_name)}</span>
  <span style="color:#aaa;margin:0 6px">›</span>
  <span style="opacity:.8">📋 {job_name}</span>
</div>

<div class="meta-bar">
  <span>任务 ID: <b>#{job_id}</b></span>
  <span>状态: <b>{status_label_map.get(job.status, job.status)}</b></span>
  <span>开始: <b>{started}</b></span>
  <span>结束: <b>{ended}</b></span>
  <span>并发: <b>{job.concurrency}</b></span>
  <span>超时: <b>{job.timeout_ms}ms</b></span>
  <span>忽略字段: <b>{esc(ignore_meta)}</b></span>
  <span>差异规则: <b>{esc(diff_rules_str)}</b></span>
  <span>断言规则: <b>{esc(assertions_str)}</b></span>
  <span>子调用 Mock: <b>{mock_mode_str}</b></span>
</div>

<div class="stats">
  <div class="stat total"><div class="num">{job.total}</div><div class="lbl">已执行</div></div>
  <div class="stat pass"><div class="num">{job.passed}</div><div class="lbl">通过 PASS</div></div>
  <div class="stat fail"><div class="num">{job.failed}</div><div class="lbl">失败 FAIL</div></div>
  <div class="stat err"><div class="num">{job.errored}</div><div class="lbl">错误 ERROR</div></div>
  <div class="stat rate"><div class="num">{pass_rate_str}</div><div class="lbl">通过率</div></div>
</div>

<div class="card">
  <div class="card-title">失败原因分析</div>
  <table class="analysis-table"><tr>{analysis_cells}</tr></table>
</div>

<div class="card">
  <div class="card-title">逐条结果</div>
  <div class="filter-bar">
    <button class="tab-btn active" onclick="filterStatus('ALL', event)">全部 ({job.total})</button>
    <button class="tab-btn" onclick="filterStatus('PASS', event)">✅ PASS ({job.passed})</button>
    <button class="tab-btn" onclick="filterStatus('FAIL', event)">❌ FAIL ({job.failed})</button>
    <button class="tab-btn" onclick="filterStatus('ERROR', event)">⚠️ ERROR ({job.errored})</button>
    <input class="search-box" type="text" placeholder="搜索接口路径…" oninput="doSearch(this.value)" />
    <span class="count-info" id="countInfo">共 {job.total} 条</span>
  </div>
  <table class="result-table">
    <thead><tr><th>接口</th><th>状态</th><th>差异</th><th>状态码</th><th>耗时(ms)</th><th>回放时间</th></tr></thead>
    <tbody id="tbody">{rows_html}</tbody>
  </table>
</div>

</div>
<script>
var currentStatus='ALL', currentSearch='';
function toggle(id){{
  var el=document.getElementById(id);
  if(el) el.style.display=el.style.display==='none'?'table-row':'none';
}}
function filterStatus(s, ev){{
  currentStatus=s;
  document.querySelectorAll('.tab-btn').forEach(function(b){{b.classList.remove('active')}});
  if(ev && ev.target) ev.target.classList.add('active');
  applyFilter();
}}
function doSearch(v){{currentSearch=v.toLowerCase();applyFilter();}}
function applyFilter(){{
  var rows=document.querySelectorAll('#tbody .result-row');
  var visible=0;
  rows.forEach(function(row){{
    var st=row.getAttribute('data-status');
    var txt=row.textContent.toLowerCase();
    var show=(currentStatus==='ALL'||st===currentStatus)&&(!currentSearch||txt.includes(currentSearch));
    row.style.display=show?'':'none';
    if(show) visible++;
    // 隐藏详情行
    var did=row.getAttribute('onclick')||'';
    var m=did.match(/toggle\('(d\d+)'\)/);
    if(m){{var det=document.getElementById(m[1]);if(det&&!show) det.style.display='none';}}
  }});
  document.getElementById('countInfo').textContent='共 '+visible+' 条';
}}
</script>
</body>
</html>"""

    filename = f"replay_report_{job_id}.html"
    return FastAPIResponse(
        content=html.encode("utf-8"),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{job_id}/analysis")
async def get_failure_analysis(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    对回放任务的失败结果做 5 类自动归因分析。

    返回:
        {
            "job_id": int,
            "total_failures": int,
            "categories": {
                "ENVIRONMENT": {"count": int, "percentage": float, "results": [...]},
                "DATA_ISSUE":  {"count": int, "percentage": float, "results": [...]},
                "BUG":         {"count": int, "percentage": float, "results": [...]},
                "PERFORMANCE": {"count": int, "percentage": float, "results": [...]},
                "UNKNOWN":     {"count": int, "percentage": float, "results": [...]},
            }
        }
    """
    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")

    stmt = (
        select(ReplayResult)
        .where(ReplayResult.job_id == job_id)
        .where(ReplayResult.status.in_(["FAIL", "ERROR", "TIMEOUT"]))
        .order_by(ReplayResult.id)
    )
    fail_results = (await db.execute(stmt)).scalars().all()

    categories: dict = {
        "ENVIRONMENT": {"count": 0, "percentage": 0.0, "results": []},
        "DATA_ISSUE":  {"count": 0, "percentage": 0.0, "results": []},
        "BUG":         {"count": 0, "percentage": 0.0, "results": []},
        "PERFORMANCE": {"count": 0, "percentage": 0.0, "results": []},
        "UNKNOWN":     {"count": 0, "percentage": 0.0, "results": []},
    }

    for rr in fail_results:
        # 解析断言结果
        assertion_list = None
        if rr.assertion_results:
            try:
                assertion_list = json.loads(rr.assertion_results)
            except Exception:
                pass

        # 用 analyze_failure 重新归因（不改动已存储的 failure_category）
        category, reason = analyze_failure(
            error_message=rr.failure_reason if rr.status in ("ERROR", "TIMEOUT") else None,
            diff_json=rr.diff_result,
            diff_score=rr.diff_score,
            replayed_status_code=rr.actual_status_code,
            assertion_results=assertion_list,
        )

        if category not in categories:
            category = "UNKNOWN"

        categories[category]["count"] += 1
        categories[category]["results"].append({
            "id": rr.id,
            "test_case_id": rr.test_case_id,
            "request_method": rr.request_method,
            "request_uri": rr.request_uri,
            "status": rr.status,
            "actual_status_code": rr.actual_status_code,
            "diff_score": rr.diff_score,
            "failure_category": rr.failure_category,
            "failure_reason": rr.failure_reason,
            "analysis_reason": reason,
            "latency_ms": rr.latency_ms,
        })

    total_failures = len(fail_results)
    if total_failures > 0:
        for cat in categories:
            categories[cat]["percentage"] = round(
                categories[cat]["count"] / total_failures * 100, 1
            )

    return {
        "job_id": job_id,
        "total_failures": total_failures,
        "categories": categories,
    }


@router.websocket("/{job_id}/ws")
async def replay_progress_ws(job_id: int, websocket: WebSocket):
    """WebSocket endpoint for real-time replay progress."""
    await websocket.accept()
    register_ws(job_id, websocket)
    try:
        async with async_session_factory() as db:
            result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                await websocket.send_json(
                    {
                        "job_id": job_id,
                        "done": job.passed + job.failed + job.errored,
                        "total": job.total,
                        "passed": job.passed,
                        "failed": job.failed,
                        "errored": job.errored,
                        "finished": job.status in ("DONE", "FAILED", "CANCELLED"),
                    }
                )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        unregister_ws(job_id, websocket)
