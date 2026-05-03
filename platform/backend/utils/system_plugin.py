"""System plugin architecture for decoupling SUT-specific logic from the platform core.

Each System Under Test (SUT) implements a plugin subclass.
The platform calls plugin methods through the abstract interface only.
"""

import importlib
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class SystemPlugin(ABC):
    """Base class for all SUT (System Under Test) plugins.

    Each plugin encapsulates system-specific logic that was previously
    hardcoded in sessions.py, didi_sub_calls.py, nls_sub_calls.py, etc.
    """

    @property
    @abstractmethod
    def system_name(self) -> str:
        """System identifier, e.g. 'didi', 'nls', 'waimai', 'loan'."""
        ...

    def match_app_id(self, app_id: str) -> bool:
        """Return True if this plugin handles the given app_id.

        Default implementation: prefix match ``system_name + '-'`` or exact match.
        Override for custom matching logic.
        """
        normalized = (app_id or "").strip().lower()
        prefix = self.system_name.lower() + "-"
        return normalized.startswith(prefix) or normalized == self.system_name.lower()

    # ── Sub-call enrichment ──────────────────────────────────────────────

    async def fetch_extra_sub_calls(
        self,
        request_body: str | None,
        app_id: str,
        record_id: str | None,
        db: Any,
    ) -> list[dict]:
        """Return additional sub-calls reconstructed for this system.

        Default: returns empty list (no extra sub-calls).
        Override in subclasses that need to query SUT databases.
        """
        return []

    # ── Transaction code helpers ─────────────────────────────────────────

    def is_complex_transaction(self, txn_code: str) -> bool:
        """Return True if the transaction code requires sub-call reconstruction.

        Default: False.
        """
        return False

    def get_complex_transaction_codes(self) -> set[str]:
        """Return the set of complex transaction codes for this system."""
        return set()

    # ── Sibling HTTP sub-call matching ───────────────────────────────────────

    def should_fetch_sibling_http_sub_calls(
        self,
        request_body: str | None,
        correlation_tokens: set[str],
    ) -> bool:
        """Return True when sibling Servlet rows should be scanned."""
        return bool(correlation_tokens)

    def matches_sibling_http_sub_call(
        self,
        *,
        endpoint: str,
        query_params: dict[str, str],
        request_body: str | None,
        correlation_text: str,
        correlation_tokens: set[str],
    ) -> bool:
        """Return True when a sibling Servlet row belongs to the replay case."""
        return any(token and token in correlation_text for token in correlation_tokens)

    # ── XML / request body parsing ───────────────────────────────────────

    def extract_xml_params(self, request_body: str | None) -> dict[str, str]:
        """Extract business parameters from XML request body.

        Default: returns empty dict.
        """
        return {}

    # ── JDBC method → step / table mapping (for NLS-style systems) ─────

    def get_jdbc_method_table(self) -> dict[str, str]:
        """Return mapping: JDBC repository method name → database table name."""
        return {}

    def get_jdbc_method_param_key(self) -> dict[str, str]:
        """Return mapping: JDBC repository method name → XML parameter field name."""
        return {}

    def assign_jdbc_to_step(self, method_name: str, step_names: list[str]) -> str | None:
        """Map a JDBC method call to a business step name.

        Default: returns None (no mapping).
        """
        return None

    # ── Repository capture specs ─────────────────────────────────────────

    def get_repository_specs(self) -> list[dict]:
        """Return repository capture specs for this system.

        Each spec is a dict with keys:
            full_class_name, database, type, methods
        """
        return []


# ── Plugin registry ────────────────────────────────────────────────────────

_registry: list[SystemPlugin] = []
_loaded_plugin_modules: set[str] = set()


def register_plugin(plugin: SystemPlugin) -> None:
    """Register a system plugin."""
    for existing in _registry:
        if existing.system_name == plugin.system_name:
            return
    _registry.append(plugin)


def get_all_plugins() -> list[SystemPlugin]:
    """Return all registered plugins."""
    return list(_registry)


def get_plugin_for_app_id(app_id: str) -> SystemPlugin | None:
    """Return the plugin that handles the given app_id, or None."""
    for plugin in _registry:
        if plugin.match_app_id(app_id):
            return plugin
    return None


def get_plugin_by_name(system_name: str) -> SystemPlugin | None:
    """Return the plugin by system name, or None."""
    for plugin in _registry:
        if plugin.system_name == system_name:
            return plugin
    return None


def clear_registry() -> None:
    """Clear all registered plugins. Useful in tests."""
    _registry.clear()
    _loaded_plugin_modules.clear()


def discover_plugin_modules() -> list[str]:
    """Discover local plugin modules without hardcoding SUT names."""
    utils_dir = Path(__file__).resolve().parent
    modules: list[str] = []
    for item in pkgutil.iter_modules([str(utils_dir)]):
        if item.ispkg:
            continue
        name = item.name
        if not name.endswith("_plugin") or name == "system_plugin":
            continue
        modules.append(f"utils.{name}")
    return sorted(modules)


def load_plugins(module_names: list[str] | tuple[str, ...] | None = None) -> None:
    """Import plugin modules so they can self-register."""
    for module_name in module_names or discover_plugin_modules():
        if module_name in _loaded_plugin_modules:
            continue
        importlib.import_module(module_name)
        _loaded_plugin_modules.add(module_name)
