"""Notification providers: DingTalk, WeCom, and extensible NotifyProvider interface."""
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class NotifyProvider(ABC):
    """Abstract notification provider. Implement to add new channels."""

    @abstractmethod
    async def send(self, title: str, content: str) -> bool:
        """Send notification. Returns True on success."""
        ...


class DingTalkNotify(NotifyProvider):
    """DingTalk robot webhook notification."""

    def __init__(self, webhook: str):
        self.webhook = webhook

    async def send(self, title: str, content: str) -> bool:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": f"## {title}\n\n{content}",
            },
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook, json=payload)
                data = resp.json()
                if data.get("errcode") == 0:
                    return True
                logger.warning(f"DingTalk send failed: {data}")
                return False
        except Exception as e:
            logger.error(f"DingTalk notify error: {e}")
            return False


class WeComNotify(NotifyProvider):
    """WeCom (企业微信) robot webhook notification."""

    def __init__(self, webhook: str):
        self.webhook = webhook

    async def send(self, title: str, content: str) -> bool:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"**{title}**\n{content}",
            },
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook, json=payload)
                data = resp.json()
                if data.get("errcode") == 0:
                    return True
                logger.warning(f"WeCom send failed: {data}")
                return False
        except Exception as e:
            logger.error(f"WeCom notify error: {e}")
            return False


def get_provider(notify_type: Optional[str], webhook: Optional[str]) -> Optional[NotifyProvider]:
    """Factory: get notification provider by type."""
    if not notify_type or not webhook:
        return None
    if notify_type == "dingtalk":
        return DingTalkNotify(webhook)
    elif notify_type == "wecom":
        return WeComNotify(webhook)
    return None


async def send_replay_report(
    notify_type: Optional[str],
    webhook: Optional[str],
    job_id: int,
    job_name: str,
    total: int,
    passed: int,
    failed: int,
    errored: int,
    report_url: Optional[str] = None,
) -> bool:
    """Send replay completion report via configured provider."""
    provider = get_provider(notify_type, webhook)
    if not provider:
        return False

    pass_rate = f"{(passed / total * 100):.1f}%" if total > 0 else "N/A"
    status_emoji = "✅" if failed == 0 and errored == 0 else "❌"

    content = (
        f"- **回放任务**: {job_name or f'Job #{job_id}'}\n"
        f"- **状态**: {status_emoji} {'全部通过' if failed == 0 and errored == 0 else '存在失败'}\n"
        f"- **通过率**: {pass_rate}\n"
        f"- **总数**: {total} | 通过: {passed} | 失败: {failed} | 错误: {errored}\n"
    )
    if report_url:
        content += f"- **报告链接**: [{report_url}]({report_url})\n"

    return await provider.send(f"AREX Recorder 回放完成 {status_emoji}", content)
