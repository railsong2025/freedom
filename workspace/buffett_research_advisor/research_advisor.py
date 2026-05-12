#!/usr/bin/env python3
"""Manual Buffett US-equity research runner triggered by 'buffett开始'."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shlex
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TRIGGER_PHRASE = "buffett开始"
DEFAULT_REPORT_SLUG = "美股组合波段投研"
LEGACY_DEFAULT_REPORT_SLUG = "美股投研始"
REPORT_RECORD_PREFIX = "record"
CURRENT_CODEX_COMMAND = "current_codex"
CURRENT_CODEX_COMMANDS = {CURRENT_CODEX_COMMAND, "current-codex", "current_codex_flow"}
SQLITE_WRITE_DISABLED = "disabled"
REPORT_RECORD_RE = re.compile(r"^record_(\d{8}_\d{6})_(\d{3,})$")
LEGACY_REPORT_DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_.+")

REQUIRED_REPORT_FILES = (
    "00_metadata.md",
    "01_buffett_review.md",
    "02_buffett_plan.md",
    "03_zeus_intelligence.md",
    "04_poseidon_research.md",
    "05_hades_verification.md",
    "06_roundtable.md",
    "07_final_decision.md",
)

AI_CHAIN_FOCUS_SEGMENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("AI应用/云CAPEX/数据基础设施", ("MSFT", "AMZN", "GOOGL", "META", "ORCL", "PLTR", "SNOW", "DDOG")),
    ("GPU/ASIC/AI加速器", ("NVDA", "AMD", "AVGO", "MRVL", "ARM")),
    ("晶圆代工/半导体制造", ("TSM", "INTC")),
    ("存储/HBM/存储设备", ("MU", "WDC", "STX")),
    ("半导体设备/EDA/材料", ("ASML", "AMAT", "LRCX", "KLAC", "CDNS", "SNPS", "ENTG", "PLAB")),
    ("先进封装/测试", ("AMKR", "TSM")),
    ("光模块/网络", ("ANET", "CIEN", "COHR", "LITE")),
    ("AI服务器/ODM/EMS", ("DELL", "HPE", "SMCI", "FLEX", "JBL", "CLS", "SANM")),
    ("数据中心电力/散热/工程", ("VRT", "ETN", "PWR", "GEV")),
    ("PCB/CCL/电子制造", ("TTMI", "SANM", "FLEX", "JBL")),
    ("安全/数据基础设施", ("PANW", "CRWD", "NET", "SNOW", "DDOG")),
    ("链条ETF/篮子", ("SMH", "SOXX", "QQQ", "IGV", "AIQ")),
)

SPECIAL_WATCH_SYMBOLS: tuple[tuple[str, str], ...] = (
    ("AMD", "AMD/GPU-CPU加速器"),
    ("MU", "美光/存储-HBM"),
    ("FLEX", "伟创力/AI服务器EMS"),
    ("INTC", "英特尔/晶圆制造、AI PC与服务器CPU、美国半导体政策"),
    ("WDC", "西部数据/存储设备"),
    ("STX", "希捷/存储设备"),
    ("VRT", "Vertiv/数据中心电力散热"),
    ("ANET", "Arista/AI网络"),
    ("TSM", "台积电/晶圆代工"),
    ("NVDA", "英伟达/GPU与AI加速器"),
    ("SMH", "半导体ETF"),
    ("SOXX", "半导体ETF"),
    ("QQQ", "纳指100 ETF"),
)

MARKET_INDEX_PROXY_CONTRACT: tuple[dict[str, Any], ...] = (
    {
        "benchmark": "纳斯达克综合指数",
        "index_codes": ("IXIC",),
        "financebusiness_tool": "StockIndexList",
        "tradable_proxy": "QQQ",
        "action_rule": "指数只做市场 regime 和相对强弱背景；当前 BUY/SELL 只能使用 QQQ 等可交易 ETF 代理。",
    },
    {
        "benchmark": "标普 500",
        "index_codes": ("SPX", "GSPC", "INX", "SP500"),
        "financebusiness_tool": "StockIndexList",
        "tradable_proxy": "SPY",
        "action_rule": "若 financeBusiness 指数编码不可用，必须记录指数缺口；仍需用 SPY 作为可交易 ETF 代理进行审议。",
    },
)

DEFAULT_STRONG_CYCLE_FOCUS = tuple(
    dict.fromkeys(symbol for _, symbols in AI_CHAIN_FOCUS_SEGMENTS for symbol in symbols)
)

DEFAULT_CONFIG = {
    "project_root": "/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN",
    "base_short_path": "base_short.md",
    "timezone": "Asia/Shanghai",
    "primary_market": "US equities",
    "task_type": "portfolio_review",
    "subject": "us_equity_portfolio",
    "report_slug": DEFAULT_REPORT_SLUG,
    "prompt_language": "Chinese",
    "trade_deadline_beijing": "00:00",
    "per_trade_fee_usd": 5,
    "trading_profile": "swing_trading",
    "short_term_primary_horizon": "swing_days_to_weeks",
    "short_term_single_trade_risk_pct": 2.0,
    "strong_cycle_initial_position_pct_min": 5.0,
    "strong_cycle_initial_position_pct_max": 8.0,
    "short_term_stop_loss_pct_min": 3.0,
    "short_term_stop_loss_pct_max": 5.0,
    "strong_cycle_focus": list(DEFAULT_STRONG_CYCLE_FOCUS),
    "sqlite_write_mode": SQLITE_WRITE_DISABLED,
    "market_data_timeout_seconds": 8.0,
    "market_data_cache_dir": "workspace/buffett_research_advisor/data/market_data",
    "market_data_aktools_api_url": None,
    "market_data_http_api_url": None,
    "market_data_sources": [
        "financeBusiness_mcp",
    ],
    "execute_command": CURRENT_CODEX_COMMAND,
    "execute_timeout_seconds": 1800,
    "write_system_log": True,
    "system_log_path": "workspace/buffett_research_advisor/system_log.md",
}


@dataclass(frozen=True)
class ResearchConfig:
    project_root: Path
    base_short_path: Path
    timezone: ZoneInfo
    primary_market: str
    task_type: str
    subject: str
    report_slug: str
    prompt_language: str
    trade_deadline_beijing: str
    per_trade_fee_usd: float
    trading_profile: str
    short_term_primary_horizon: str
    short_term_single_trade_risk_pct: float
    strong_cycle_initial_position_pct_min: float
    strong_cycle_initial_position_pct_max: float
    short_term_stop_loss_pct_min: float
    short_term_stop_loss_pct_max: float
    strong_cycle_focus: tuple[str, ...]
    sqlite_write_mode: str
    market_data_timeout_seconds: float
    market_data_cache_dir: Path
    market_data_aktools_api_url: str | None
    market_data_http_api_url: str | None
    market_data_sources: tuple[str, ...]
    execute_command: str | None
    execute_timeout_seconds: int
    write_system_log: bool
    system_log_path: Path


def load_config(path: Path | None) -> ResearchConfig:
    data: dict[str, Any] = dict(DEFAULT_CONFIG)
    if path:
        data.update(json.loads(path.read_text(encoding="utf-8")))

    project_root = Path(data["project_root"]).expanduser().resolve()
    base_path = Path(data["base_short_path"])
    if not base_path.is_absolute():
        base_path = project_root / base_path
    system_log_path = Path(data["system_log_path"])
    if not system_log_path.is_absolute():
        system_log_path = project_root / system_log_path
    market_data_cache_dir = Path(data["market_data_cache_dir"])
    if not market_data_cache_dir.is_absolute():
        market_data_cache_dir = project_root / market_data_cache_dir

    return ResearchConfig(
        project_root=project_root,
        base_short_path=base_path,
        timezone=ZoneInfo(data["timezone"]),
        primary_market=str(data["primary_market"]),
        task_type=str(data["task_type"]),
        subject=str(data["subject"]),
        report_slug=str(data["report_slug"]),
        prompt_language=str(data["prompt_language"]),
        trade_deadline_beijing=str(data["trade_deadline_beijing"]),
        per_trade_fee_usd=float(data["per_trade_fee_usd"]),
        trading_profile=str(data.get("trading_profile", "swing_trading")),
        short_term_primary_horizon=str(data.get("short_term_primary_horizon", "swing_days_to_weeks")),
        short_term_single_trade_risk_pct=float(data.get("short_term_single_trade_risk_pct", 2.0)),
        strong_cycle_initial_position_pct_min=float(data.get("strong_cycle_initial_position_pct_min", 5.0)),
        strong_cycle_initial_position_pct_max=float(data.get("strong_cycle_initial_position_pct_max", 8.0)),
        short_term_stop_loss_pct_min=float(data.get("short_term_stop_loss_pct_min", 3.0)),
        short_term_stop_loss_pct_max=float(data.get("short_term_stop_loss_pct_max", 5.0)),
        strong_cycle_focus=tuple(str(item).upper() for item in data.get("strong_cycle_focus", DEFAULT_CONFIG["strong_cycle_focus"])),
        sqlite_write_mode=normalize_sqlite_write_mode(str(data.get("sqlite_write_mode", SQLITE_WRITE_DISABLED))),
        market_data_timeout_seconds=float(data.get("market_data_timeout_seconds", 8.0)),
        market_data_cache_dir=market_data_cache_dir,
        market_data_aktools_api_url=data.get("market_data_aktools_api_url"),
        market_data_http_api_url=data.get("market_data_http_api_url"),
        market_data_sources=tuple(str(item) for item in data.get("market_data_sources", DEFAULT_CONFIG["market_data_sources"])),
        execute_command=data.get("execute_command"),
        execute_timeout_seconds=int(data.get("execute_timeout_seconds", 1800)),
        write_system_log=bool(data.get("write_system_log", True)),
        system_log_path=system_log_path,
    )


def ensure_base_short(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Buffett 美股投研基础记录\n\n"
        "## 当前持仓\n\n"
        "- TODO：填写当前美股和美股 ETF 持仓。\n\n"
        "## 可用资金\n\n"
        "- TODO：填写可用于美股交易的现金或可换汇资金。\n\n"
        "## 操作记录\n\n"
        "<!--\n"
        "本节由用户手动填写真实美股交易记录。建议格式：\n\n"
        "### YYYY-MM-DD HH:MM 北京时间 - 买入/卖出/减仓/加仓\n\n"
        "- 标的：\n"
        "- 动作：\n"
        "- 数量：\n"
        "- 价格：\n"
        "- 参考的建议运行目录：\n"
        "- 执行原因：\n"
        "- 止损/止盈计划：\n"
        "-->\n",
        encoding="utf-8",
    )


def read_base_short(cfg: ResearchConfig) -> str:
    ensure_base_short(cfg.base_short_path)
    return cfg.base_short_path.read_text(encoding="utf-8")


def run_dir_for(timestamp: dt.datetime, cfg: ResearchConfig) -> Path:
    stamp = timestamp.astimezone(cfg.timezone).strftime("%Y%m%d_%H%M%S")
    return cfg.project_root / "workspace" / "buffett_research_advisor" / "runs" / stamp


def normalize_report_slug(slug: str | None, *, upgrade_legacy_default: bool = False) -> str:
    raw = (slug or "").strip()
    if upgrade_legacy_default and raw == LEGACY_DEFAULT_REPORT_SLUG:
        raw = DEFAULT_REPORT_SLUG
    if not raw:
        raw = DEFAULT_REPORT_SLUG
    cleaned = re.sub(r"[\\/:*?\"<>|]", "", raw)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned or DEFAULT_REPORT_SLUG


def report_dir_for(timestamp: dt.datetime, cfg: ResearchConfig, slug: str | None = None) -> Path:
    """Return the next local record folder path.

    The `slug` argument is kept for CLI/backward compatibility, but new Buffett
    report folders intentionally use only the record timestamp and sequence.
    """
    del slug
    report_root = cfg.project_root / "report"
    stamp = timestamp.astimezone(cfg.timezone).strftime("%Y%m%d_%H%M%S")
    sequence = next_report_sequence(report_root)
    return report_root / f"{REPORT_RECORD_PREFIX}_{stamp}_{sequence:03d}"


def next_report_sequence(report_root: Path) -> int:
    max_sequence = 0
    if not report_root.exists():
        return 1
    for child in report_root.iterdir():
        if not child.is_dir():
            continue
        match = REPORT_RECORD_RE.fullmatch(child.name)
        if not match:
            continue
        max_sequence = max(max_sequence, int(match.group(2)))
    return max_sequence + 1


def config_with_sqlite_write_mode(cfg: ResearchConfig, sqlite_write_mode: str) -> ResearchConfig:
    return ResearchConfig(
        project_root=cfg.project_root,
        base_short_path=cfg.base_short_path,
        timezone=cfg.timezone,
        primary_market=cfg.primary_market,
        task_type=cfg.task_type,
        subject=cfg.subject,
        report_slug=cfg.report_slug,
        prompt_language=cfg.prompt_language,
        trade_deadline_beijing=cfg.trade_deadline_beijing,
        per_trade_fee_usd=cfg.per_trade_fee_usd,
        trading_profile=cfg.trading_profile,
        short_term_primary_horizon=cfg.short_term_primary_horizon,
        short_term_single_trade_risk_pct=cfg.short_term_single_trade_risk_pct,
        strong_cycle_initial_position_pct_min=cfg.strong_cycle_initial_position_pct_min,
        strong_cycle_initial_position_pct_max=cfg.strong_cycle_initial_position_pct_max,
        short_term_stop_loss_pct_min=cfg.short_term_stop_loss_pct_min,
        short_term_stop_loss_pct_max=cfg.short_term_stop_loss_pct_max,
        strong_cycle_focus=cfg.strong_cycle_focus,
        sqlite_write_mode=normalize_sqlite_write_mode(sqlite_write_mode),
        market_data_timeout_seconds=cfg.market_data_timeout_seconds,
        market_data_cache_dir=cfg.market_data_cache_dir,
        market_data_aktools_api_url=cfg.market_data_aktools_api_url,
        market_data_http_api_url=cfg.market_data_http_api_url,
        market_data_sources=cfg.market_data_sources,
        execute_command=cfg.execute_command,
        execute_timeout_seconds=cfg.execute_timeout_seconds,
        write_system_log=cfg.write_system_log,
        system_log_path=cfg.system_log_path,
    )


def normalize_sqlite_write_mode(value: str | None) -> str:
    """Normalize legacy SQLite modes into the current no-write policy."""
    raw = (value or SQLITE_WRITE_DISABLED).strip().lower()
    if raw in {"disabled", "local_only", "read_only", "readonly", "off", "none", "false", "0"}:
        return SQLITE_WRITE_DISABLED
    if raw == "enabled":
        return SQLITE_WRITE_DISABLED
    return SQLITE_WRITE_DISABLED


def parse_prices_arg(value: str | None) -> dict[str, float]:
    prices: dict[str, float] = {}
    if not value:
        return prices
    for item in re.split(r"[,，;；\n]+", value):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"price item must use SYMBOL=PRICE, got {item!r}")
        symbol, price_text = item.split("=", 1)
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError(f"missing symbol in price item {item!r}")
        prices[symbol] = float(price_text.strip())
    return prices


def parse_timestamp_arg(value: str | None, cfg: ResearchConfig) -> dt.datetime | None:
    if not value:
        return None
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=cfg.timezone)
    return parsed.astimezone(cfg.timezone)


def stable_task_key(task_type: str, subject: str, symbols: str | None = None) -> str:
    normalized_type = task_type.strip().lower()
    normalized_subject = " ".join(subject.strip().lower().split())
    normalized_symbols = ""
    if symbols:
        normalized_symbols = ",".join(sorted({item.strip().upper() for item in symbols.split(",") if item.strip()}))
    raw = f"{normalized_type}|{normalized_subject}|{normalized_symbols}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{normalized_type}:{digest}"


def _decode_sqlite_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    for key in (
        "symbols_json",
        "recommendation_json",
        "expected_outcome_json",
        "source_doc_ids_json",
        "source_links_json",
        "actual_result_json",
    ):
        if key not in data:
            continue
        target = key.removesuffix("_json")
        raw = data.pop(key)
        try:
            data[target] = json.loads(raw or "null")
        except json.JSONDecodeError:
            data[target] = raw
    return data


def _read_previous_sqlite_decision(cfg: ResearchConfig) -> dict[str, Any]:
    db_path = cfg.project_root / "workspace" / "journal" / "decisions.sqlite3"
    task_key = stable_task_key(cfg.task_type, cfg.subject)
    lookup_command = (
        f"python3 workspace/journal/decision_db.py last --task-type {cfg.task_type} --subject {cfg.subject}"
    )
    result: dict[str, Any] = {
        "task_key": task_key,
        "db_path": str(db_path),
        "lookup_command": lookup_command,
        "status": "db_missing",
        "decision": None,
    }
    if not db_path.exists():
        return result
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            row = con.execute(
                "SELECT * FROM decisions WHERE task_key = ? ORDER BY created_at DESC LIMIT 1",
                (task_key,),
            ).fetchone()
        finally:
            con.close()
    except sqlite3.Error as exc:
        result["status"] = "read_error"
        result["error"] = str(exc)
        return result
    if row is None:
        result["status"] = "no_same_task_row"
        return result
    result["status"] = "found"
    result["decision"] = _decode_sqlite_row(row)
    return result


def _extract_metadata_value(text: str, key: str) -> str | None:
    patterns = (
        rf"\|\s*{re.escape(key)}\s*\|\s*`?([^`|\n]+?)`?\s*\|",
        rf"{re.escape(key)}\s*[:：]\s*`?([^`\n]+?)`?\s*$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None


def _read_optional_text(path: Path, *, limit: int | None = None) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    if limit is not None and len(text) > limit:
        return text[:limit] + "\n..."
    return text


def _metadata_for_report_dir(path: Path) -> dict[str, str | None]:
    text = _read_optional_text(path / "00_metadata.md", limit=24000)
    return {
        "task_type": _extract_metadata_value(text, "task_type"),
        "subject": _extract_metadata_value(text, "subject"),
        "market": _extract_metadata_value(text, "market"),
        "task_key": _extract_metadata_value(text, "task_key"),
        "run_time": _extract_metadata_value(text, "运行时间"),
        "task_folder": _extract_metadata_value(text, "任务目录"),
    }


def _history_exclusion_reason(info: dict[str, Any]) -> str | None:
    if info.get("folder_format") == "unknown":
        return "unsupported_report_folder"
    if not info.get("has_final_decision"):
        return "missing_final_decision"
    if info.get("missing_files"):
        return "missing_required_phase_files"
    if info.get("folder_format") == "record":
        if not info.get("has_local_result_snapshot"):
            return "missing_local_result_snapshot"
        if info.get("has_db_record"):
            return "contains_legacy_db_record"
    return None


def _report_dir_info(path: Path, cfg: ResearchConfig) -> dict[str, Any]:
    record_match = REPORT_RECORD_RE.fullmatch(path.name)
    legacy_match = LEGACY_REPORT_DIR_RE.fullmatch(path.name)
    folder_format = "record" if record_match else ("legacy_date_slug" if legacy_match else "unknown")
    timestamp_sort = ""
    sequence: int | None = None
    if record_match:
        timestamp_sort = record_match.group(1)
        sequence = int(record_match.group(2))
    elif legacy_match:
        timestamp_sort = legacy_match.group(1).replace("-", "")
    try:
        mtime = max((path / name).stat().st_mtime for name in REQUIRED_REPORT_FILES if (path / name).exists())
    except ValueError:
        mtime = path.stat().st_mtime
    files = {name: str(path / name) for name in REQUIRED_REPORT_FILES if (path / name).exists()}
    missing_files = [name for name in REQUIRED_REPORT_FILES if name not in files]
    metadata = _metadata_for_report_dir(path)
    final_excerpt = _read_optional_text(path / "07_final_decision.md", limit=2200)
    review_excerpt = _read_optional_text(path / "01_buffett_review.md", limit=1600)
    task_key = metadata.get("task_key") or stable_task_key(cfg.task_type, cfg.subject)
    info = {
        "path": str(path),
        "name": path.name,
        "folder_format": folder_format,
        "timestamp_sort": timestamp_sort,
        "sequence": sequence,
        "mtime": mtime,
        "metadata": metadata,
        "task_key": task_key,
        "task_type": metadata.get("task_type"),
        "subject": metadata.get("subject"),
        "market": metadata.get("market"),
        "has_final_decision": (path / "07_final_decision.md").exists(),
        "has_db_record": (path / "db_record.json").exists(),
        "has_local_result_snapshot": (path / "local_result_snapshot.json").exists(),
        "files": files,
        "missing_files": missing_files,
        "final_decision_excerpt": final_excerpt,
        "review_excerpt": review_excerpt,
    }
    info["history_exclusion_reason"] = _history_exclusion_reason(info)
    info["history_eligible"] = info["history_exclusion_reason"] is None
    return info


def list_local_report_records(cfg: ResearchConfig) -> list[dict[str, Any]]:
    report_root = cfg.project_root / "report"
    if not report_root.exists():
        return []
    records: list[dict[str, Any]] = []
    for child in report_root.iterdir():
        if not child.is_dir():
            continue
        info = _report_dir_info(child, cfg)
        if not info["history_eligible"]:
            continue
        metadata_task_type = info.get("task_type")
        metadata_subject = info.get("subject")
        if metadata_task_type and metadata_task_type != cfg.task_type:
            continue
        if metadata_subject and metadata_subject != cfg.subject:
            continue
        records.append(info)
    return records


def read_previous_history(cfg: ResearchConfig) -> dict[str, Any]:
    task_key = stable_task_key(cfg.task_type, cfg.subject)
    records = list_local_report_records(cfg)
    record_format_records = [record for record in records if record["folder_format"] == "record"]
    pool = record_format_records or records
    previous_record = None
    if pool:
        previous_record = max(
            pool,
            key=lambda item: (
                item.get("timestamp_sort") or "",
                item.get("sequence") or 0,
                item.get("mtime") or 0,
                item.get("name") or "",
            ),
        )
    if previous_record is None:
        status = "no_local_record_found"
    elif previous_record["folder_format"] == "record":
        status = "found_local_record"
    else:
        status = "found_legacy_local_report"
    sqlite_previous = _read_previous_sqlite_decision(cfg)
    return {
        "task_key": task_key,
        "history_source": "local_report_folder",
        "lookup_command": "local scan: report/record_* first, then legacy report/YYYY-MM-DD_* folders",
        "status": status,
        "record": previous_record,
        "records_scanned": len(records),
        "record_format_records_scanned": len(record_format_records),
        "sqlite": sqlite_previous,
    }


def _ensure_workspace_imports(cfg: ResearchConfig) -> None:
    candidates = [
        cfg.project_root / "workspace",
        Path(__file__).resolve().parents[1],
    ]
    for candidate in candidates:
        if candidate.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def _chinese_weekday(value: dt.date) -> str:
    names = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")
    return names[value.weekday()]


def _fmt_money(value: float | None, currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    prefix = "$" if currency == "USD" else f"{currency} "
    return f"{prefix}{value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def _ai_segment_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for segment, symbols in AI_CHAIN_FOCUS_SEGMENTS:
        for symbol in symbols:
            mapping.setdefault(symbol, segment)
    return mapping


def _special_watch_symbol_tuple() -> tuple[str, ...]:
    return tuple(symbol for symbol, _ in SPECIAL_WATCH_SYMBOLS)


def _special_watch_text() -> str:
    return "、".join(f"{symbol}（{label}）" for symbol, label in SPECIAL_WATCH_SYMBOLS)


def _effective_strong_cycle_focus(cfg: ResearchConfig) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*cfg.strong_cycle_focus, *_special_watch_symbol_tuple())))


def _ai_chain_markdown_table() -> str:
    lines = [
        "| 链条环节 | 必须覆盖的美股/ETF代表 |",
        "|---|---|",
    ]
    for segment, symbols in AI_CHAIN_FOCUS_SEGMENTS:
        lines.append(f"| {segment} | {'、'.join(symbols)} |")
    return "\n".join(lines)


def _market_index_proxy_markdown_table() -> str:
    lines = [
        "| 指数基准 | financeBusiness 指数通道 | 可交易代理 | 当前动作规则 |",
        "|---|---|---|---|",
    ]
    for item in MARKET_INDEX_PROXY_CONTRACT:
        codes = "/".join(item["index_codes"])
        lines.append(
            "| "
            f"{item['benchmark']} | {item['financebusiness_tool']}({codes}) | "
            f"{item['tradable_proxy']} | {item['action_rule']} |"
        )
    return "\n".join(lines)


def _pnl_chinese_table(pnl: Any) -> str:
    lines = [
        "| Ticker | 股数 | 成本价 | 当前价 | 当前市值 | 成本额 | 未实现盈亏 | 未实现盈亏率 | 数据状态 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for position in pnl.positions:
        data_status = "provided_price；待 Zeus 用 financeBusiness 内部核验" if position.current_price is not None else "缺当前价；不得用于交易"
        lines.append(
            "| "
            f"{position.symbol} | {position.shares} | {_fmt_money(position.avg_cost)} | "
            f"{_fmt_money(position.current_price)} | {_fmt_money(position.market_value)} | "
            f"{_fmt_money(position.cost_basis)} | {_fmt_money(position.unrealized_pnl)} | "
            f"{_fmt_pct(position.unrealized_pnl_pct)} | {data_status} |"
        )
    lines.append(
        "| **Total** |  |  |  | "
        f"{_fmt_money(pnl.total_market_value)} | {_fmt_money(pnl.total_cost_basis)} | "
        f"{_fmt_money(pnl.total_unrealized_pnl)} | {_fmt_pct(pnl.total_unrealized_pnl_pct)} | "
        "USD 持仓合计；现金另列 |"
    )
    return "\n".join(lines)


def _previous_decision_text(previous: dict[str, Any]) -> str:
    command = previous["lookup_command"]
    record = previous.get("record")
    sqlite_previous = previous.get("sqlite", {})
    sqlite_decision = sqlite_previous.get("decision")
    sqlite_status = sqlite_previous.get("status", "unknown")
    if record is None:
        status = previous["status"]
        return (
            f"- 本地扫描：`{command}`\n"
            f"- 扫描结果：未找到可复盘的本地完整 report 文件夹（status={status}，scanned={previous['records_scanned']}）。\n"
            f"- SQLite 只读交叉检查：status={sqlite_status}；"
            f"{'找到 id=' + str(sqlite_decision.get('id')) if sqlite_decision else '无可用同任务英文索引'}。\n"
            "- 处理原则：本项目从本轮起以本地 report/record_* 文件夹为复盘主索引；SQLite 只能作为英文索引和交叉检查，不能替代本地中文报告。"
        )
    source_docs = list(record.get("files", {}).values())
    sqlite_text = (
        f"SQLite 交叉检查找到 id={sqlite_decision.get('id')}，action={sqlite_decision.get('action')}，outcome_status={sqlite_decision.get('outcome_status')}。"
        if sqlite_decision
        else f"SQLite 交叉检查 status={sqlite_status}，无同任务英文索引。"
    )
    return (
        f"- 本地扫描：`{command}`\n"
        f"- 查询结果：找到上一轮本地报告文件夹 `{record['path']}`，格式={record['folder_format']}，"
        f"task_key={record.get('task_key')}。\n"
        f"- 上一轮本地中文报告路径：{source_docs or '未记录'}\n"
        f"- SQLite 只读交叉检查：{sqlite_text}\n"
        "- 处理原则：本轮复盘以该本地文件夹内 00/01/06/07 和 local_result_snapshot 为主；legacy 旧目录可读取既有 db_record。"
        "如 SQLite 与本地报告冲突，以本地中文 Markdown 为准并把冲突交给 Hades 审计。"
    )


def _missed_opportunity_ledger(previous: dict[str, Any]) -> str:
    required = _special_watch_symbol_tuple()
    symbols = tuple(dict.fromkeys((*required, *DEFAULT_STRONG_CYCLE_FOCUS)))
    segment_map = _ai_segment_map()
    no_previous = previous.get("record") is None
    lines = [
        "| Ticker | AI链条位置 | 上一轮建议/状态 | 当时 veto | 后续1日/5日涨跌 | 机会成本 | 本轮处理 |",
        "|---|---|---|---|---|---|---|",
    ]
    for symbol in symbols:
        segment = segment_map.get(symbol, "强周期补充/当前关注")
        if no_previous:
            prior = "无上一轮本地 record 文件夹"
            veto = "上一轮未覆盖/无当时 veto"
        else:
            prior = "待从上一轮本地中文报告核对"
            veto = "若旧报告未覆盖则标记：上一轮未覆盖/无当时 veto"
        lines.append(
            f"| {symbol} | {segment} | {prior} | {veto} | 待 Zeus 用最新行情补全 | "
            "待按买1股或5%-8% starter估算 | 纳入全链条初筛，禁止事后补造旧建议 |"
        )
    return "\n".join(lines)


def _top_loss_and_gain(pnl: Any) -> tuple[Any | None, Any | None]:
    priced = [position for position in pnl.positions if position.unrealized_pnl is not None]
    if not priced:
        return None, None
    return min(priced, key=lambda item: item.unrealized_pnl), max(priced, key=lambda item: item.unrealized_pnl)


def _buffett_self_reflection(previous: dict[str, Any], pnl: Any, prices: dict[str, float]) -> str:
    loss_position, gain_position = _top_loss_and_gain(pnl)
    missing_prices = sorted(position.symbol for position in pnl.positions if position.current_price is None)
    price_status = (
        f"本步已提供价格：{('、'.join(sorted(prices)) if prices else '无')}；"
        f"缺价格：{('、'.join(missing_prices) if missing_prices else '无')}；所有价格仍需 Zeus 用 financeBusiness 内部核验。"
    )
    record = previous.get("record")
    sqlite_decision = previous.get("sqlite", {}).get("decision")
    if record is None:
        history_evidence = (
            f"历史决策依据：本地 report 扫描状态为 `{previous['status']}`，task_key `{previous['task_key']}` 无可复盘的正式上一轮 record 文件夹；"
            "因此不能补造上一轮建议或 veto。SQLite 只可作英文索引交叉检查，不能替代本地中文报告。"
        )
    else:
        metadata = record.get("metadata", {})
        sqlite_note = (
            f"；SQLite 交叉检查 id={sqlite_decision.get('id')}，action={sqlite_decision.get('action')}"
            if sqlite_decision
            else "；SQLite 无同任务英文索引或未用于主复盘"
        )
        history_evidence = (
            "历史决策依据："
            f"上一轮本地文件夹 `{record['path']}`，格式={record['folder_format']}，"
            f"task_key={record.get('task_key')}，运行时间={metadata.get('run_time') or '待从 00_metadata.md 核对'}"
            f"{sqlite_note}；本轮必须用最新数据检验其成败和偏差。"
        )
    loss_text = (
        f"最大未实现亏损为 {loss_position.symbol}：{_fmt_money(loss_position.unrealized_pnl)}（{_fmt_pct(loss_position.unrealized_pnl_pct)}）。"
        if loss_position
        else "没有可计算的最大亏损持仓。"
    )
    gain_text = (
        f"最大未实现盈利为 {gain_position.symbol}：{_fmt_money(gain_position.unrealized_pnl)}（{_fmt_pct(gain_position.unrealized_pnl_pct)}）。"
        if gain_position
        else "没有可计算的最大盈利持仓。"
    )
    total_line = (
        f"最新数据依据：USD 持仓总市值 {_fmt_money(pnl.total_market_value)}，总成本 {_fmt_money(pnl.total_cost_basis)}，"
        f"总未实现盈亏 {_fmt_money(pnl.total_unrealized_pnl)}（{_fmt_pct(pnl.total_unrealized_pnl_pct)}）。"
    )
    return (
        "### 依据的最新数据\n\n"
        f"- {total_line}\n"
        f"- {loss_text}\n"
        f"- {gain_text}\n"
        f"- {price_status}\n\n"
        "### 依据的历史决策\n\n"
        f"- {history_evidence}\n"
        "- 错过机会账本仍待 Zeus/Poseidon 用最新 1日/5日涨跌和机会成本补齐；补齐前 Buffett 不得把未覆盖票事后改写为正确 veto。\n\n"
        "### 关键遗漏与分析错误复盘\n\n"
        "- 关键人物讲话遗漏：Buffett 必须检查上一轮是否遗漏 Fed/FOMC、财政部、白宫/总统、SEC/FTC/DOJ、商务部/BIS/USTR、当前持仓公司 CEO/CFO、AI 云厂商管理层、NVIDIA/AMD/TSMC/ASML/Broadcom/Arista/Micron/Vertiv 等核心供应链管理层的重要讲话；若本步没有最新讲话数据，必须责成 Zeus 补查并标记“待核验”，不能默认没有影响。\n"
        "- 关键事件未捕捉：Buffett 必须检查上一轮是否遗漏财报/指引、云 CAPEX、AI 订单、出口管制、宏观数据、利率路径、板块轮动、供应链涨价/缺货、监管/地缘事件、ETF/行业资金流和盘中量价突破；若未捕捉，必须归因为数据覆盖错误或事件影响链分析不足。\n"
        "- 关键分析错误：Buffett 必须检查是否把长期好公司误当当前波段好交易、是否把动能突破误判为一律追高、是否只因涨幅大否决、是否没有 financeBusiness 内部核验、是否没有费用后 R/R、是否没有硬止损/止盈、是否过度关注当前亏损而忽略更强机会、是否把数据缺口包装成确定结论。\n"
        "- 责任边界：这些错误先由 Buffett 承担流程责任；Zeus/Poseidon/Hades 负责补证和审计，但不能替 Buffett 背锅。\n\n"
        "### 反思结论\n\n"
        "- 历史责任：如果本地 record 文件夹缺失或报告不完整，Buffett 的第一责任是流程连续性和可审计性不足；如果本地文件夹存在，则必须用最新数据检验上一轮判断、仓位、止损、候选覆盖和 veto 是否正确。SQLite 只作英文索引，不作主复盘来源。\n"
        "- 覆盖责任：如果上一轮没有覆盖 MU、AMD、FLEX、INTC（英特尔）、WDC、STX、VRT、ANET、TSM、NVDA、SMH/SOXX/QQQ 或 AI 全链代表票，不能事后补造判断；必须承认覆盖不足，并把全链条初筛和特别观察范围写入本轮硬约束。\n"
        "- 信息责任：如果关键人物讲话或关键事件没有进入上一轮决策，Buffett 必须承认信息捕捉和影响链分析不足；本轮要把讲话、事件、价格反应、受益/受损对象和反证写成硬性数据表。\n"
        "- 执行责任：如果只给观察名单、只说不追高、只给小仓而没有确认加仓和移动止损路径，Buffett 必须承认这是防错过机制不足，而不是把责任推给市场波动。\n"
        "- 风控责任：亏损持仓必须先判断是否触发趋势破位或 thesis 恶化；盈利持仓必须判断利润保护；新增交易必须有费用后 R/R 和硬止损，否则 Hades 应否决。\n"
        "- 认知责任：Buffett 不得把“长期好公司”替代“当前波段好交易”，也不得把“涨得多”单独当作否决理由；本轮必须同时防 FOMO 和防过度保守。\n\n"
        "### 基于反思的新策略\n\n"
        "- 新策略一：先用 financeBusiness 最新价格、内部核验、量价和相对强弱重算当前持仓风险；亏损股不机械补仓，只有出现独立波段触发且费用后 R/R 合格才允许加仓或留仓。\n"
        "- 新策略二：先建立关键人物讲话和关键事件捕捉表；每条讲话/事件必须写人物或事件、时间、来源层级、影响链、受益/受损资产、可观察市场反应、置信度和反证。\n"
        "- 新策略三：AI 产业链采用“全链条初筛 + Top 8-12 深度计划”，不能只分析现有持仓或半导体单一环节；每个 Top 候选必须给出入场类型、止损、止盈和最长持有期。\n"
        "- 新策略四：防错过不再等于追高；当板块领先、成交量和相对强弱确认、止损可定义且第一/第二止盈覆盖费用和滑点时，允许小仓 starter 进入 Hades 三态审计。\n"
        "- 新策略五：starter 不是终局仓位；Poseidon 必须设计确认加仓、停止加仓、移动止损和利润保护路径，否则不得声称具备大幅盈利路径。\n"
        "- 新策略六：如果历史决策缺失、关键讲话/事件缺失或数据不足，本轮必须先建立可审计基线；最终只能输出当前可执行整股 BUY/SELL，或在证据不足时写 `本次不买入、不卖出`。"
    )


def _render_metadata_report(
    *,
    cfg: ResearchConfig,
    timestamp: dt.datetime,
    report_dir: Path,
    base_short_path: Path,
    previous: dict[str, Any],
    portfolio: Any,
    usd_symbols: list[str],
    prices: dict[str, float],
    market_data_manifest_path: Path | None,
) -> str:
    local_dt = timestamp.astimezone(cfg.timezone)
    deadline = next_trade_deadline(timestamp, cfg)
    planned_files = "\n".join(
        f"- `{report_dir / name}`"
        for name in (
            "00_metadata.md",
            "01_buffett_review.md",
            "02_buffett_plan.md",
            "03_zeus_intelligence.md",
            "04_poseidon_research.md",
            "05_hades_verification.md",
            "06_roundtable.md",
            "07_final_decision.md",
            "local_result_snapshot.json（legacy 旧目录可读取既有 db_record.json）",
        )
    )
    manifest_text = (
        f"`{market_data_manifest_path}`"
        if market_data_manifest_path
        else "本轮无预取数据包；禁止伪造 manifest，后续直接调用 financeBusiness MCP，不得 fallback。"
    )
    price_symbols = "、".join(sorted(prices)) if prices else "未提供；01 只能标注缺口"
    return f"""# 00_metadata

## 任务身份

| 项目 | 内容 |
|---|---|
| 用户触发 | `{TRIGGER_PHRASE}` |
| 运行时间 | {local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}（{_chinese_weekday(local_dt.date())}） |
| 交易截止 | {deadline.strftime('%Y-%m-%d %H:%M:%S %Z')} |
| 任务目录 | `{report_dir}` |
| 输入文件 | `{base_short_path}` |
| task_type | `{cfg.task_type}` |
| subject | `{cfg.subject}` |
| market | `{cfg.primary_market}` |
| task_key | `{previous['task_key']}` |
| report 命名 | `record_YYYYMMDD_HHMMSS_序号` |
| 复盘主索引 | `local_report_folder` |
| 上一轮本地记录 | `{previous.get('record', {}).get('path') if previous.get('record') else previous['status']}` |
| SQLite 模式 | `{cfg.sqlite_write_mode}` |

Why this task_key：`{TRIGGER_PHRASE}` 是固定的美股组合复盘与本轮操作任务，身份必须稳定为 `task_type=portfolio_review`、`subject=us_equity_portfolio`、`market=US equities`；本轮不把候选股列表写入 task_key，避免同一组合复盘因候选池变化而失去历史连续性。

复盘主规则：本轮起复盘按本地 report 文件夹进行，优先读取 `report/record_*` 中上一轮同任务完整报告；若没有 record 新格式，才允许读取旧 `report/YYYY-MM-DD_*` 完整报告作为 legacy 背景。SQLite 只作为可选只读英文索引交叉检查，不得替代本地中文 Markdown 复盘，也不得写入本轮结果。

## 输入与资产范围

- 当前解析出的 USD 持仓：{('、'.join(usd_symbols) if usd_symbols else '无可解析 USD 持仓')}。
- 组合背景现金：{portfolio.cash:,.2f} {portfolio.cash_currency}。港股和港币资金只作为背景或可换汇约束，不生成港股/A股交易建议。
- 本轮提供的价格字段：{price_symbols}。
- 交易费用：每笔 BUY/SELL 固定 USD {cfg.per_trade_fee_usd:g}。
- 交易单位：整股；禁止碎股、百分比股数或只写金额下单。

## 策略边界

- 所有策略遵从波段交易策略：本轮买入、卖出、加仓、止盈、止损、等待和复盘，都以数日至数周为默认目标。
- 长期基本面只作为候选质量、估值和事件风险过滤器；当前 BUY/SELL 必须由波段 setup、量价、相对强弱、费用后 R/R、止损和交易窗口共同支持。
- 不承诺盈利；“需要利润”在本系统中等价于费用后正期望、明确下行、分阶段暴露、确认加仓、止盈保护和可复盘退出。

## 本轮 AI 产业链候选池

重点候选池必须覆盖 AI 产业链上中下游。Zeus 和 Poseidon 先做全链条轻量初筛，再筛出 Top 8-12 做深度波段计划。

{_ai_chain_markdown_table()}

## 特别观察范围

{_special_watch_text()}

- INTC（英特尔）必须作为独立特别观察标的，而不是只并入半导体行业概括；Zeus、Poseidon、Hades 和圆桌都要给出独立结论。

## 指数基准与可交易代理

纳斯达克和标普必须先作为市场 regime / 风险偏好基准处理，再映射到可交易 ETF 代理；指数本身不得进入 `本次当前操作`。

{_market_index_proxy_markdown_table()}

## 数据源计划

- 行情数据源：`{' -> '.join(cfg.market_data_sources)}`；Buffett 工作流结构化行情只允许 financeBusiness MCP。
- 本地适配层：公共 `workspace/interface/market_data.py` 不得用于本轮 Buffett 行情补源；旧 `workspace/buffett_research_advisor/market_data.py` 仅作历史兼容。
- manifest：{manifest_text}
- 价格只做 financeBusiness 内部核验：`StockCurrentMarket` 对 `StockMarketList` 最新历史；不能使用外部核验源。
- 新闻、公告、SEC/IR、宏观和政策：恢复使用 aiwebsearch、官方网页、兼容 WebSearch 和 PDF 抽取；financeBusiness 只负责行情、价格、成交量、FX、P&L 和估值价格输入。

## 评分、分层与否决

- 板块评分：market regime、板块相对强弱、催化新鲜度、利润池归属、估值/拥挤度、技术结构、政策/地缘风险。
- 股票分层：核心候选 / 战术候选 / 观察名单 / 回避或否决。
- 波段 setup：动能突破 / 回撤承接 / 超跌反弹 / 止损卖出 / 止盈卖出 / 移动止损。
- Hades veto：financeBusiness 缺字段或内部冲突、数据过期、止损缺失、费用后 R/R 不足、FOMO 追价、仓位超过风险预算、单股超过 25%、把波段失败票拖成长线。
- 强周期三态/四态裁决：必须使用 `workspace/analysis/cli.py swing-verdict`
  或等价逻辑，把候选标记为 `current_trade`、`small_starter`、`wait`
  或 `hard_veto`。上涨多本身不是 FOMO；只有 R/R、止损、量价、跳空或
  仓位约束失败时才是硬否决。若个股数据不足，必须先审计 SMH/SOXX/QQQ
  等 ETF/basket fallback 后才能给整体 no-trade。

## 计划文件

{planned_files}
"""


def _render_review_report(
    *,
    cfg: ResearchConfig,
    timestamp: dt.datetime,
    report_dir: Path,
    previous: dict[str, Any],
    pnl: Any,
    portfolio: Any,
    usd_cash: float | None,
    hkd_usd_rate: float | None,
    prices: dict[str, float],
    base_short_path: Path,
) -> str:
    local_dt = timestamp.astimezone(cfg.timezone)
    cash_text = (
        f"{portfolio.cash:,.2f} HKD / {hkd_usd_rate:g} = 约 {_fmt_money(usd_cash)}"
        if portfolio.cash_currency == "HKD" and usd_cash is not None and hkd_usd_rate
        else (
            f"{_fmt_money(portfolio.cash)}"
            if portfolio.cash_currency == "USD"
            else f"{portfolio.cash:,.2f} {portfolio.cash_currency}，本步未换算为 USD"
        )
    )
    sold_lines = []
    base_text = base_short_path.read_text(encoding="utf-8") if base_short_path.exists() else ""
    for line in base_text.splitlines():
        if "卖出" in line:
            sold_lines.append(line.strip())
    realized_text = (
        "；".join(sold_lines)
        if sold_lines
        else "base_short.md 操作记录未发现可解析卖出。"
    )
    if sold_lines:
        realized_text += "。已成交卖出存在，但 exact lots/税费/成交费用和成本归集不足；本步不把已实现盈亏写成精确值，后续若需要只能声明平均成本法估算。"
    return f"""# 01_buffett_review

## 复盘范围

- 复盘时间：{local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}（{_chinese_weekday(local_dt.date())}）。
- 输入源：`{base_short_path}`。
- 任务目录：`{report_dir}`。
- 本轮固定身份：`{cfg.task_type}` / `{cfg.subject}` / `{cfg.primary_market}`。
- 策略边界：所有策略遵从波段交易策略；当前动作只允许美股和美股 ETF，港股/A股不出交易建议。

## 上一次本地 record 复盘

{_previous_decision_text(previous)}

## 当前持仓盈亏复盘

本表只计算当前最新持仓 section 中的 USD 股票/ETF；初始持仓和已卖出标的不得重复计入。当前价来自本轮传入价格或后续 financeBusiness 数据，仍需 Zeus 做 financeBusiness 内部核验。

{_pnl_chinese_table(pnl)}

- USD 持仓总市值：{_fmt_money(pnl.total_market_value)}。
- USD 持仓总成本：{_fmt_money(pnl.total_cost_basis)}。
- USD 持仓总未实现盈亏：{_fmt_money(pnl.total_unrealized_pnl)}（{_fmt_pct(pnl.total_unrealized_pnl_pct)}）。
- 可换汇/背景现金：{cash_text}。
- 估算组合背景权益：{_fmt_money((pnl.total_market_value or 0) + usd_cash) if usd_cash is not None and pnl.total_market_value is not None else 'N/A，现金未可靠换算'}。
- 数据状态：价格字段 {('、'.join(sorted(prices)) if prices else '未提供')}；financeBusiness 内部核验和时间戳必须在 Zeus 阶段补齐。

## 已实现盈亏可靠性

{realized_text}

结论：第二步只确认“能否可靠计算”。若最终阶段提出 SELL，`交易后预计盈亏` 必须默认使用平均成本法并明确声明；若平均成本也不可靠，禁止把该 SELL 的盈亏当精确值。

## 当前 P&L 对本轮风险的含义

- 亏损持仓要区分可恢复的估值/时点亏损与基本面或趋势恶化；不得因为亏损机械补仓，也不得因为亏损逃避止损。
- 盈利持仓要判断是否需要移动止损、分批止盈或继续持有；盈利不是自动加仓理由。
- 新增 AI 强周期仓位必须先看现金、费用、单股 25% 上限、已有 AI 暴露和单笔约 {cfg.short_term_single_trade_risk_pct:g}% 风险预算。
- 当前 P&L 信息必须被 02-06 全阶段引用，尤其用于 MSFT/TSM/ANET/NVDA/AMD 的仓位风险、止损和再部署判断。

## 错过机会账本

若上一轮没有覆盖新增 AI 代表票，必须写“上一轮未覆盖/无当时 veto”，不得补造当时建议或 veto 理由。涨跌和机会成本在 Zeus/Poseidon 获取 1日/5日价格后补齐。

特别观察范围必须逐票复盘：{_special_watch_text()}。INTC（英特尔）不得被省略，也不得只用半导体 ETF 或 TSM 代替。

{_missed_opportunity_ledger(previous)}

## Buffett 自我反思

复盘后 Buffett 必须先审视自己的流程、覆盖、仓位和风控错误，不能只评价股票涨跌或把问题交给下游部门。

{_buffett_self_reflection(previous, pnl, prices)}

## 复盘结论

- 第二步不能直接给买卖结论，只能把历史、P&L、错过机会、Buffett 自我反思和数据缺口转化为本轮派工要求。
- 当前最重要的修正是：不能只围绕现有持仓；必须覆盖 AI 应用、云 CAPEX、GPU/ASIC、半导体、存储/HBM、设备/材料、先进封装、光模块/网络、服务器/ODM、电力散热、PCB/CCL、安全和数据基础设施。
- 本轮若找不到费用后正期望 setup，最终必须写 `本次不买入、不卖出`；若找到，必须是整股、限价、USD {cfg.per_trade_fee_usd:g} 费用、止损、止盈和最长持有期齐全的波段交易。
"""


def _render_plan_report(
    *,
    cfg: ResearchConfig,
    timestamp: dt.datetime,
    report_dir: Path,
    previous: dict[str, Any],
    pnl: Any,
    market_data_manifest_path: Path | None,
) -> str:
    local_dt = timestamp.astimezone(cfg.timezone)
    manifest_line = (
        f"本轮 manifest：`{market_data_manifest_path}`；仅当其明确为 financeBusiness 生成时才可用于本轮。"
        if market_data_manifest_path
        else "本轮无预取数据包；Zeus 不得假装读取 manifest，必须直接调用 financeBusiness MCP，且不得使用任何非 financeBusiness fallback。"
    )
    upstream = (
        f"`{report_dir / '00_metadata.md'}`、"
        f"`{report_dir / '01_buffett_review.md'}`、"
        f"`{report_dir / '02_buffett_plan.md'}`"
    )
    return f"""# 02_buffett_plan

## 本轮目标

- 计划时间：{local_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}（{_chinese_weekday(local_dt.date())}）。
- 固定触发：`{TRIGGER_PHRASE}`。
- 固定身份：`task_type={cfg.task_type}`，`subject={cfg.subject}`，`task_key={previous['task_key']}`。
- 任务目录命名：本轮和后续报告目录必须使用 `record_YYYYMMDD_HHMMSS_序号`。
- 复盘主索引：按本地 report 文件夹复盘，优先上一轮 `report/record_*` 完整报告；SQLite 只作英文索引交叉检查。
- 目标：在完整复盘当前 USD 持仓 P&L 后，先做美股板块地图和 AI 产业链机会漏斗，再决定当前会话是否执行整股 BUY/SELL，或写 `本次不买入、不卖出`。
- 策略：所有策略遵从波段交易策略；默认持有数日至数周，禁止把失败波段拖成长线。

## 从 01 继承的约束

- 当前 USD 持仓总市值：{_fmt_money(pnl.total_market_value)}；总成本：{_fmt_money(pnl.total_cost_basis)}；未实现盈亏：{_fmt_money(pnl.total_unrealized_pnl)}（{_fmt_pct(pnl.total_unrealized_pnl_pct)}）。
- 上一轮本地复盘状态：{previous['status']}；本地扫描规则必须写入报告：`{previous['lookup_command']}`。
- 错过机会账本必须贯穿 03-06：MU、AMD、FLEX、INTC、WDC、STX、VRT、ANET、TSM、SMH、SOXX 和全 AI 链代表票都要复盘覆盖/未覆盖、涨跌、机会成本和是否过度保守。
- 特别观察范围必须贯穿 03-06：{_special_watch_text()}。INTC（英特尔）必须被独立核查行情字段、相对强弱、催化、风险、swing verdict、Hades 裁决和 no-trade proof。
- Buffett 自我反思和新策略必须贯穿 03-06：下游部门必须基于最新数据和历史决策，回应 Buffett 在历史连续性、候选覆盖、仓位执行、防错过、防追高、止损/止盈和费用后 R/R 上的流程责任，并验证 `基于反思的新策略` 是否可执行。
- 关键遗漏与分析错误复盘必须贯穿 03-06：关键人物讲话遗漏、关键事件未捕捉、关键分析错误必须被 Zeus 补证、Poseidon 归因、Hades 审计，并在圆桌中确认是否改变当前策略。
- 当前价和 P&L 仍需 Zeus 用 financeBusiness `StockCurrentMarket` 与 `StockMarketList` 内部核验；未经核验的价格只能作为临时计算。

## 数据刷新计划

{manifest_line}

- 结构化行情：只使用 financeBusiness MCP；失败、空值、字段不足或时间戳过旧时写缺口，不得用公共 `workspace/interface/market_data.py` 或其他行情源补齐。
- 指数基准与代理：纳斯达克/标普指数用 financeBusiness `StockIndexList` 做市场 regime；`SPY/QQQ` 用 `StockCurrentMarket` + `StockMarketList` 做可交易 ETF 代理审议。指数不可直接下单，ETF 代理必须进入 no-trade proof。
- 新闻/公告/宏观/人物言论：使用 aiwebsearch 优先，官方网页、兼容 WebSearch 和 PDF 抽取作为 fallback；不得用这些来源补齐 financeBusiness 缺失的行情字段。
- 核验：所有关键价格、涨跌幅、成交量、催化和估值只能通过 financeBusiness 内部字段/历史核验；不得外部核验。
- 数据缺口：任何缺口要写入 `## 数据冲突与缺口`，并说明对波段交易是否降权或否决。

{_market_index_proxy_markdown_table()}

## AI 产业链两阶段漏斗

第一阶段：全链条轻量广覆盖初筛，覆盖下表所有环节，字段至少包括最新价/涨跌、量价状态、催化、追高风险、是否有可定义止损、初步 veto。

{_ai_chain_markdown_table()}

第二阶段：筛出 Top 8-12 做深度波段计划。筛选依据：板块强弱、催化新鲜度、利润池归属、订单/业绩能见度、费用后 R/R、成交量确认、相对 SPY/QQQ/SMH/SOXX 强弱、现金和组合风险约束。

## Zeus 派工合同

- 必须读取：{upstream}。
- 必须写入：`{report_dir / '03_zeus_intelligence.md'}`。
- 必须运行 Python CLI：`workspace/intelligence/cli.py indicators`、`quality`、`sector-map`，并把命令和输出写入 `## Python 工具调用记录`。
- 必须覆盖：当前持仓、SPY/QQQ/SMH/SOXX、行业 ETF、宏观风险、关键人物言论，以及 AI 应用/云、GPU/ASIC、晶圆代工、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、服务器/ODM、数据中心电力散热、PCB/CCL、安全/数据基础设施。
- 必须覆盖指数：用 `mcp__financeBusiness__StockIndexList` 获取纳斯达克综合指数 `IXIC`；标普 500 依次尝试 `SPX/GSPC/INX/SP500`，若 financeBusiness 不覆盖则写明指数缺口；无论指数缺口如何，必须继续用 `SPY` 和 `QQQ` 作为可交易 ETF 代理完成当前交易审议。
- 必须补查：上一轮可能未关注到的关键人物讲话和关键事件，至少覆盖讲话/事件时间、来源层级、影响链、受影响资产、讲话或事件前后市场反应、反证和数据缺口。
- 必须专项覆盖：特别观察范围内每个 ticker 的完整行情字段与当前交易策略字段包；INTC（英特尔）必须单独检查公司催化、美国半导体政策/补贴、代工转型、AI PC/服务器 CPU 需求、毛利/资本开支压力和相对 SMH/SOXX 强弱。
- 最低报告门槛：financeBusiness 来源状态、内部核验差异、数据时间戳、事实影响链、反证、数据缺口、波段量价字段。
- 禁止事项：不得只复盘现有持仓；不得伪造 manifest；不得用单一未核验来源支撑交易；不得忽略 Buffett 自我反思和新策略中提出的覆盖缺口。

## Poseidon 派工合同

- 必须读取：00/01/02 和 03 Zeus 报告。
- 必须写入：`{report_dir / '04_poseidon_research.md'}`。
- 必须运行 Python CLI：`workspace/analysis/cli.py pnl`、`score`、`rr`、`swing-verdict` 或同等本地分析命令，并把输出写入 `## Python 工具调用记录`。
- 必须输出：`## 美股板块地图`、`## AI 产业链机会漏斗`、`## 当前盈亏与仓位含义`、`## 强周期波段交易计划`、`## 错过机会修正与当前 starter 方案`、`## 仓位升级阶梯与大幅盈利路径`。
- 必须归因：上一轮关键分析错误，包括长期 thesis 替代波段 setup、动能突破被误判为一律追高、只因涨幅大否决、缺 financeBusiness 内部核验、缺费用后 R/R、缺硬止损/止盈、忽略关键讲话/事件、或把数据缺口当确定结论。
- 候选分层：核心候选 / 战术候选 / 观察名单 / 回避或否决。
- 特别观察：`候选动作对照表` 必须纳入特别观察范围全部 ticker；INTC（英特尔）必须单独列行并给出 `current_trade`、`small_starter`、`wait` 或 `hard_veto`。
- 可执行 BUY 至少包含：入场类型、技术触发、限价、整股数量、硬止损、第一/第二止盈、移动止损、最长持有期、单笔风险金额、费用后 R/R。
- 必须输出 `候选动作对照表`：候选、短线分数、入场类型、限价、止损、第一/第二目标、费用后 R/R、数据质量、Hades 预期状态、swing verdict、最终动作。
- 若所有单股候选都不是 `current_trade` 或 `small_starter`，必须评估 SMH/SOXX/QQQ 或更合适的 basket/ETF fallback；整体 no-trade 必须证明每个候选和 fallback 均失败。
- 禁止事项：不得只说“上涨多所以不买”；不得只给小仓而没有确认加仓或利润保护路径；不得保证盈利；不得回避 Buffett 自我反思和新策略中指出的过度保守或防错过机制不足。

## Hades 派工合同

- 必须读取：00/01/02/03/04。
- 必须写入：`{report_dir / '05_hades_verification.md'}`。
- 必须运行 Python CLI：`workspace/verification/cli.py audit-pnl --portfolio-file base_short.md`、`stress-test --portfolio-file base_short.md`、`compliance --portfolio-file base_short.md`、`audit-post-trade --portfolio-file base_short.md` 或同等审计命令，并把输出写入 `## Python 工具调用记录`。
- 必须审计：上游报告完整性、P&L 自洽性、数据质量、financeBusiness 覆盖和内部核验、费用后 R/R、止损/止盈、单股 25% 上限、现金、AI 链条遗漏、关键人物言论是否过度解读。
- 必须审计：关键人物讲话遗漏、关键事件未捕捉和关键分析错误是否被 Zeus/Poseidon 充分补证与修正；若没有，Hades 必须降权、要求补查或否决。
- 必须审计：特别观察范围是否逐票得到行情、字段包、swing verdict 和 no-trade proof；INTC（英特尔）缺独立结论时必须判定上游不完整。
- 三态/四态裁决：`批准当前交易`、`批准小仓 starter`、`等待`、`否决`；确认加仓另给 `批准加仓`、`仅保留 starter` 或 `减仓/止盈`。
- 若单股因数据质量被否决但存在 ETF/basket fallback，Hades 必须要求 fallback 审议，不得直接接受整体 no-trade。
- 禁止事项：不得笼统说“不追高”；只能用交易窗口、数据源、止损、R/R、仓位/现金/25% 上限等可审计硬条件否决；必须审计 Buffett 自我反思和新策略是否已经转化为硬约束。

## Roundtable 与 Buffett 最终验收

- Buffett 只有在 03/04/05 均存在并通过最低门槛后，才能写 `06_roundtable.md`。
- 圆桌必须讨论：上一轮成功/失败/混合/待验证原因、Buffett 自我反思是否成立、关键人物讲话遗漏/关键事件未捕捉/关键分析错误是否被修正、新策略是否被最新数据支持、当前 P&L 对买卖的影响、错过机会修正、AI 链条 Top 8-12、Hades veto、是否当前下单。
- `07_final_decision.md` 必须包含 `## 当前持仓盈亏复盘`、`## 本次当前操作`、`## 交易后预计盈亏`、`## 下一次建议启动分析时间（北京时间）`。
- `本次当前操作` 只能列当前立即执行的 BUY/SELL；观察名单、未来条件单和非行动候选不得混入。
- 若交易窗口内最终仍是 `本次不买入、不卖出`，`06_roundtable.md` 和
  `07_final_decision.md` 必须写出 no-trade proof：每个核心/战术候选及
  SMH/SOXX/QQQ fallback 的 swing verdict、硬否决原因或等待原因。
- 若最终决策或复核晚于本轮具体交易截止时间，最终只能写 `本次不买入、不卖出`。

## 第二步验收门槛

- 00 已明确 task_key、`record_YYYYMMDD_HHMMSS_序号` 任务目录、源文件、数据源计划、AI 全链候选池、波段策略边界和文件计划。
- 01 已读取/说明上一轮本地 report/record 文件夹历史，使用最新 record 持仓计算 USD P&L，未重复计入初始持仓或已卖出 TSLA/MSFT 股数，建立错过机会账本，并基于最新数据和历史决策写出 Buffett 自我反思与新策略。
- 02 已把 P&L、历史状态、Buffett 自我反思、新策略、AI 全链覆盖、三部门派工合同、Python 工具调用、Hades veto 和最终报告格式写成可执行要求。
"""


def prepare_step2_reports(
    cfg: ResearchConfig,
    *,
    prices: dict[str, float] | None = None,
    hkd_usd_rate: float | None = None,
    report_slug: str | None = None,
    market_data_manifest_path: Path | None = None,
    timestamp: dt.datetime | None = None,
) -> dict[str, Any]:
    cfg = config_with_sqlite_write_mode(cfg, cfg.sqlite_write_mode)
    _ensure_workspace_imports(cfg)
    from analysis.portfolio_tracker import compute_portfolio_pnl, parse_base_short_positions
    from interface.models import Portfolio

    ts = (timestamp or dt.datetime.now(cfg.timezone)).astimezone(cfg.timezone)
    price_map = {symbol.upper(): price for symbol, price in (prices or {}).items()}
    base_short = read_base_short(cfg)
    portfolio = parse_base_short_positions(base_short)
    usd_positions = tuple(
        position
        for position in portfolio.positions
        if position.currency == "USD" and not position.symbol.upper().endswith(".HK")
    )
    usd_cash: float | None
    if portfolio.cash_currency == "USD":
        usd_cash = portfolio.cash
    elif portfolio.cash_currency == "HKD" and hkd_usd_rate:
        usd_cash = round(portfolio.cash / hkd_usd_rate, 2)
    else:
        usd_cash = None
    pnl_cash = usd_cash if usd_cash is not None else 0.0
    usd_portfolio = Portfolio(positions=usd_positions, cash=pnl_cash, cash_currency="USD")
    pnl = compute_portfolio_pnl(usd_portfolio, price_map)
    previous = read_previous_history(cfg)
    report_dir = report_dir_for(ts, cfg, report_slug)
    report_dir.mkdir(parents=True, exist_ok=True)
    usd_symbols = sorted(position.symbol for position in usd_positions)

    metadata_path = report_dir / "00_metadata.md"
    review_path = report_dir / "01_buffett_review.md"
    plan_path = report_dir / "02_buffett_plan.md"
    metadata_path.write_text(
        _render_metadata_report(
            cfg=cfg,
            timestamp=ts,
            report_dir=report_dir,
            base_short_path=cfg.base_short_path,
            previous=previous,
            portfolio=portfolio,
            usd_symbols=usd_symbols,
            prices=price_map,
            market_data_manifest_path=market_data_manifest_path,
        ),
        encoding="utf-8",
    )
    review_path.write_text(
        _render_review_report(
            cfg=cfg,
            timestamp=ts,
            report_dir=report_dir,
            previous=previous,
            pnl=pnl,
            portfolio=portfolio,
            usd_cash=usd_cash,
            hkd_usd_rate=hkd_usd_rate,
            prices=price_map,
            base_short_path=cfg.base_short_path,
        ),
        encoding="utf-8",
    )
    plan_path.write_text(
        _render_plan_report(
            cfg=cfg,
            timestamp=ts,
            report_dir=report_dir,
            previous=previous,
            pnl=pnl,
            market_data_manifest_path=market_data_manifest_path,
        ),
        encoding="utf-8",
    )

    audit = {
        "timestamp": ts.isoformat(),
        "trigger_phrase": TRIGGER_PHRASE,
        "task_key": previous["task_key"],
        "task_type": cfg.task_type,
        "subject": cfg.subject,
        "market": cfg.primary_market,
        "report_dir": str(report_dir),
        "files": {
            "metadata": str(metadata_path),
            "review": str(review_path),
            "plan": str(plan_path),
        },
        "base_short_path": str(cfg.base_short_path),
        "usd_symbols": usd_symbols,
        "prices": price_map,
        "hkd_usd_rate": hkd_usd_rate,
        "estimated_usd_cash": usd_cash,
        "pnl": {
            "total_market_value": pnl.total_market_value,
            "total_cost_basis": pnl.total_cost_basis,
            "total_unrealized_pnl": pnl.total_unrealized_pnl,
            "total_unrealized_pnl_pct": pnl.total_unrealized_pnl_pct,
        },
        "previous_decision": {
            "status": previous["status"],
            "task_key": previous["task_key"],
            "lookup_command": previous["lookup_command"],
            "history_source": previous["history_source"],
            "has_local_record": previous["record"] is not None,
            "local_record_path": previous["record"]["path"] if previous["record"] else None,
            "sqlite_status": previous["sqlite"]["status"],
            "has_sqlite_decision": previous["sqlite"]["decision"] is not None,
        },
        "sqlite_write_mode": cfg.sqlite_write_mode,
        "market_data_manifest_path": str(market_data_manifest_path) if market_data_manifest_path else None,
    }
    audit_path = report_dir / "step2_audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    audit["files"]["audit"] = str(audit_path)
    return audit


def sqlite_mode_instructions(sqlite_write_mode: str) -> str:
    normalized = normalize_sqlite_write_mode(sqlite_write_mode)
    if normalized == SQLITE_WRITE_DISABLED:
        return (
            "SQLite 写入模式：disabled（Buffett 不再写入 SQLite）。\n"
            "- 复盘主来源仍是上一轮本地 report/record 文件夹；SQLite 只允许只读 legacy 交叉检查，不得作为主复盘来源。\n"
            "- 允许的 SQLite 命令仅限 `decision_db.py last` 这类只读查询；禁止运行 `decision_db.py review`、`decision_db.py record` 或任何直接 SQL 写入。\n"
            "- 禁止修改 `workspace/journal/decisions.sqlite3`。\n"
            "- 最终结果只写本地 Markdown 和本地 JSON 文件。\n"
            "- 用本地 `local_result_snapshot.json` 记录任务目录、中文报告路径、最终决策摘要和 SQLite 写入已跳过；新流程不得创建 `db_record.json`。\n"
            "- `07_final_decision.md` 必须写明：`SQLite 写入：skipped_by_disabled_policy`。\n"
        )
    return (
        "SQLite 写入模式：disabled（未知配置已按禁写处理）。\n"
        "- 禁止运行 `decision_db.py review`、`decision_db.py record` 或任何直接 SQL 写入。\n"
        "- 最终结果只写本地 Markdown 和 `local_result_snapshot.json`。\n"
    )


def next_trade_deadline(timestamp: dt.datetime, cfg: ResearchConfig) -> dt.datetime:
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", cfg.trade_deadline_beijing)
    if not match:
        raise ValueError(f"trade_deadline_beijing must be HH:MM, got {cfg.trade_deadline_beijing!r}")
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23 or minute > 59:
        raise ValueError(f"trade_deadline_beijing must be a valid HH:MM, got {cfg.trade_deadline_beijing!r}")

    local_ts = timestamp.astimezone(cfg.timezone)
    deadline = local_ts.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if local_ts >= deadline:
        deadline += dt.timedelta(days=1)
    return deadline


def build_prompt(
    base_short: str,
    timestamp: dt.datetime,
    cfg: ResearchConfig,
    *,
    market_data_manifest_path: Path | None = None,
) -> str:
    local_dt = timestamp.astimezone(cfg.timezone)
    local_ts = local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    deadline_dt = next_trade_deadline(timestamp, cfg)
    deadline_text = deadline_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    fee_text = f"{cfg.per_trade_fee_usd:g}"
    effective_focus = _effective_strong_cycle_focus(cfg)
    focus_text = "、".join(effective_focus)
    special_watch_text = _special_watch_text()
    ai_chain_focus_text = "；".join(
        f"{segment}（{'、'.join(symbols)}）" for segment, symbols in AI_CHAIN_FOCUS_SEGMENTS
    )
    market_source_text = " -> ".join(cfg.market_data_sources)
    suggested_report_dir = report_dir_for(timestamp, cfg)
    previous_history = read_previous_history(cfg)
    previous_record = previous_history.get("record")
    previous_record_text = (
        f"上一轮本地复盘文件夹：`{previous_record['path']}`（format={previous_record['folder_format']}，task_key={previous_record.get('task_key')}）。"
        if previous_record
        else f"上一轮本地复盘文件夹：未找到（status={previous_history['status']}，scanned={previous_history['records_scanned']}）。"
    )
    if market_data_manifest_path is None:
        data_pack_text = (
            "本轮行情预取数据包：本轮 financeBusiness 行情策略不生成本地行情 manifest。Zeus 不得假装读取不存在的 manifest；"
            "必须在报告中记录预取数据包缺口，并直接调用 financeBusiness MCP。禁止使用本地 `market_data.py`、AkShare、HTTP/API、Stooq、CSV/cache、yfinance 或任何其他 fallback。"
        )
        data_pack_rule_text = (
            "行情数据规则：本轮未提供预取 manifest 时，Zeus 不得要求或伪造 `manifest.json`；必须把“本轮无 financeBusiness 预取数据包”写入 `## Python 工具调用记录` 和 `## 数据冲突与缺口`，然后直接调用 `mcp__financeBusiness__StockCurrentMarket` 与 `mcp__financeBusiness__StockMarketList`。若 financeBusiness 字段缺失、过旧或内部冲突，写 `ZEUS_FIELD_FAILURE`，不得回退到在线、本地、CSV 或任何非 financeBusiness 数据源。"
        )
    else:
        data_pack_text = (
            f"本轮行情预取数据包：`{market_data_manifest_path}`。Zeus 必须先读取该 manifest 和对应 CSV；"
            "仅当 manifest 明确显示数据由 financeBusiness 在本轮生成时，CSV 才可作为 financeBusiness 内部缓存读取；不得作为外部核验源、字段补齐或故障 fallback。"
        )
        data_pack_rule_text = (
            "行情数据规则：行情数据必须只用 `financeBusiness` MCP。即使本轮存在预取 manifest，Zeus 也必须对每个美股持仓、核心候选、Top 候选和 ETF/basket fallback 调用 `mcp__financeBusiness__StockCurrentMarket` 与 `mcp__financeBusiness__StockMarketList`，并只在 manifest 确认为本轮 financeBusiness 缓存时读取 CSV 做内部复核。若 MCP 字段缺失，不得用 CSV/本地 fallback 补齐；必须写 `ZEUS_FIELD_FAILURE`。"
        )
    return f"""$buffett
用户输入：{TRIGGER_PHRASE}

本次是 Buffett 美股专用完整投研启动，不是泛泛市场点评，也不是轻量盘中检查。
本次必须启用美股强周期波段交易 overlay。所有策略遵从波段交易策略：买入、卖出、加仓、止盈、止损、等待和复盘，都必须以数日至数周的波段交易为默认目标。日内量价、VWAP、开盘 15 分钟结构、成交量和相对强弱只作为波段入场、风控、确认加仓或退出的证据，不得把纯日内冲动交易作为默认策略。
核心目标是在 AI 产业链上中下游强周期中，重点包括存储/HBM、半导体、AI 硬件、云 CAPEX、AI 服务器、数据中心电力冷却、光模块/网络、PCB/CCL、安全和数据基础设施等高 beta 方向，用技术面、量价关系、市场热点和严格止损捕捉数日至数周的波段利润；长期基本面只作为候选质量和事件风险过滤器，不能替代波段入场/退出信号。

运行时间：{local_ts}
主交易市场：{cfg.primary_market}
canonical task_type：{cfg.task_type}
canonical subject：{cfg.subject}
canonical task_key：{previous_history['task_key']}。该 key 仅用于本地 report 历史连续性和只读 legacy SQLite 交叉检查；最终禁止写 SQLite，不得运行 `decision_db.py record`。
唯一输入源文件：{cfg.base_short_path}
本轮建议 report 目录：`{suggested_report_dir}`。必须使用 `report/record_YYYYMMDD_HHMMSS_序号/` 命名，不再使用 `YYYY-MM-DD_摘要` 命名。
复盘主索引：本地 report 文件夹。{previous_record_text} SQLite 只能作为只读 legacy 英文索引交叉检查，不得替代本地中文报告复盘，也不得写入本轮结果。
交易时间约束：用户只会在本轮执行截止时间前执行本次美股交易建议；本轮执行截止时间为北京时间 `{deadline_text}`，即本轮运行时间之后最近的 `{cfg.trade_deadline_beijing}`。只有最终决策生成或复核时间晚于该具体截止时间，才因交易窗口关闭而写 `本次不买入、不卖出`。
交易费用约束：每一笔美股买入或卖出都固定额外产生 USD {fee_text} 费用。
碎股约束：不支持碎股交易，只能建议整数股，禁止美元金额下单、0.x 股、fractional share 或百分比股数。
波段策略 profile：`{cfg.trading_profile}`。
主要持有周期：`{cfg.short_term_primary_horizon}`，默认数日至数周；禁止把波段失败票拖成长线被套。
强周期/AI 产业链上中下游重点候选池（必须覆盖并分层评估）：{ai_chain_focus_text}。
本轮配置优先跟踪 ticker：{focus_text}。若配置候选缺少某个 AI 链条环节，Zeus/Poseidon 必须从上中下游覆盖模板补充可交易美股/ETF 代表标的并说明理由；不得只分析当前持仓、旧候选或单一半导体环节。
特别观察范围（逐票完整核查，不得只作为广覆盖候选略过）：{special_watch_text}。其中 INTC（英特尔）必须专项检查晶圆制造/代工转型、AI PC 与服务器 CPU、美国政策/补贴、资本开支和毛利压力、相对 SMH/SOXX 强弱；即使没有进入 Top 8-12，也必须在 Zeus 字段包、Poseidon 候选动作对照表、Hades 裁决和 no-trade proof 中给出结论。
指数基准与可交易代理（必须分开处理）：纳斯达克/标普指数只用于市场 regime、风险偏好和相对强弱背景；指数本身不可进入 `本次当前操作`，当前 BUY/SELL 只能落到 SPY/QQQ 等可交易 ETF 或具体股票。

{_market_index_proxy_markdown_table()}

候选池执行方式：先对全链条候选做轻量广覆盖初筛（链条环节、最新量价、催化、流动性、数据质量、明显 veto），再按板块强弱、催化新鲜度、费用后 R/R、止损可定义性和组合约束筛出 Top 8-12 做深度波段计划；不得要求 50+ 个 ticker 全部写成长篇个股深度报告。
波段交易默认风控：单笔最大亏损约账户权益 {cfg.short_term_single_trade_risk_pct:g}%；强周期单票初始仓位通常为组合权益 {cfg.strong_cycle_initial_position_pct_min:g}%-{cfg.strong_cycle_initial_position_pct_max:g}%；默认硬止损距离通常为入场价下方 {cfg.short_term_stop_loss_pct_min:g}%-{cfg.short_term_stop_loss_pct_max:g}%，但必须结合支撑位、ATR/波动率和费用后盈亏比校准。
行情数据源配置：`{market_source_text}`。本轮 Buffett 工作流结构化行情只允许 financeBusiness MCP；行情、估值价格、P&L、成交量、FX 和当前交易数值都属于结构化行情字段。本地公共数据适配层、AkShare、AKTools、HTTP/API、Stooq、CSV/cache、Yahoo/yfinance、搜索和网页来源都不得作为这些结构化行情字段的 fallback、补齐或外部核验源。新闻、公告、SEC/IR、宏观、政策、关键人物讲话、PDF 和反证必须使用 aiwebsearch、官方网页、兼容 WebSearch/PDF 抽取补齐事件链。
{data_pack_text}
{sqlite_mode_instructions(cfg.sqlite_write_mode)}

硬性执行要求：
1. 先创建本轮唯一任务目录 `{suggested_report_dir}`；目录名必须保持 `record_YYYYMMDD_HHMMSS_序号`，不得改回 `YYYY-MM-DD_摘要`。
2. 先读取并引用 `{cfg.base_short_path}` 中的美股/美股 ETF 持仓、可用于美股的资金、用户手动填写的”操作记录”。港股和 A 股资产只能作为组合背景或资金约束，不得生成港股或 A 股交易建议。
3. 按本地文件夹复盘上一轮同任务：优先扫描 `report/record_*` 中包含完整 00-07 阶段文件且存在 `local_result_snapshot.json`、不存在 `db_record.json` 的合规文件夹；若没有合规 record 新格式，才可读取旧 `report/YYYY-MM-DD_*` 完整文件夹作为 legacy 背景。缺少 `local_result_snapshot.json` 或含 `db_record.json` 的新格式 record 目录不得作为主历史，只能在必要时作为 legacy 风险提示。至少读取上一轮的 `00_metadata.md`、`01_buffett_review.md`、`06_roundtable.md`、`07_final_decision.md`，以及存在时的 `local_result_snapshot.json` 或 legacy `db_record.json`。不得把 SQLite 当作复盘主来源；如需要，可用 `python3 workspace/journal/decision_db.py last --task-type {cfg.task_type} --subject {cfg.subject}` 做只读英文索引交叉检查并记录冲突。
3a. 最终禁止写 SQLite：不得运行 `decision_db.py review`、`decision_db.py record` 或任何直接 SQL 写入；不得修改 `workspace/journal/decisions.sqlite3`。最终必须创建 `local_result_snapshot.json`，记录本轮 task_key、中文报告路径、最终动作、关键英文摘要、推荐 JSON、预期结果 JSON、SQLite 写入跳过原因 `skipped_by_disabled_policy`。
4. 必须启动完整 Buffett 本地流程：00_metadata、01_buffett_review、02_buffett_plan、03_zeus_intelligence、04_poseidon_research、05_hades_verification、06_roundtable、07_final_decision。
4a. 每个阶段（Zeus/Poseidon/Hades）必须运行对应的 Python CLI 工具，并将输出写入报告的 `## Python 工具调用记录` 章节。具体命令见 `.codex/skills/buffett/SKILL.md` 中的 `Mandatory Python Tool Calls` 章节。不得跳过 CLI 调用而纯手动估算技术指标、P&L、评分、R/R、仓位、压力测试或审计。
{data_pack_rule_text}
5. 每个阶段都必须写完整中文 Markdown 报告；不得创建 `.zh.md` 备份。
6. 只分析美股和美股 ETF；不得进行 A 股、港股、外汇、加密货币或商品交易建议。
7. 分析必须全面、丰富、老道、干练，体现顶级投资专家判断。禁止泛泛分析、标题堆砌、只给结论不写证据、只复述新闻、无数据链路的主观判断。
8. 所有买卖动作必须能从“证据链 -> 趋势预测 -> 费用后期望值 -> 仓位约束 -> Hades 审计”追溯。
9. 必须先做美股板块分析和 AI 产业链机会扫描，再决定组合交易；不得只围绕现有持仓复盘。AI 机会扫描必须覆盖 AI 应用、云 CAPEX、GPU/ASIC、半导体、存储/HBM、先进封装、光模块/网络、AI 服务器、数据中心/电力/散热、PCB/CCL、设备、材料、安全和数据基础设施中相关环节，并寻找可交易机会。
10. `01_buffett_review.md` 必须计算当前总盈亏和个股盈亏：每个美股/ETF 持仓的当前价、持股数、成本价、当前市值、成本额、未实现盈亏金额、未实现盈亏率；同时给出美股持仓总市值、总成本、总未实现盈亏金额、总未实现盈亏率，以及纳入可转换美股现金后的组合背景。若“操作记录”含已成交卖出且数据足够，补充已实现盈亏；若不足，明确标注无法可靠计算。
11. `02_buffett_plan.md`、`03_zeus_intelligence.md`、`04_poseidon_research.md`、`05_hades_verification.md`、`06_roundtable.md` 必须持续引用并充分考虑第 10 条盈亏复盘信息，特别是亏损股是否需要止损/减仓、盈利股是否需要保护利润、亏损是否由基本面恶化还是估值/时点造成、是否存在补仓摊低成本的陷阱、卖出是否会锁定亏损但降低更大风险。
12. 必须新增 `错过机会账本`：复盘上一轮本地 report 文件夹中所有强周期特别观察候选（至少 AMD、MU、FLEX、INTC/英特尔、WDC、STX、VRT、ANET、TSM、NVDA、SMH、SOXX、QQQ），并从本轮 AI 产业链上中下游重点候选池补充 AI 应用/云、GPU/ASIC、设备/材料、光模块/网络、服务器/ODM、电力散热、PCB/CCL、安全/数据基础设施等代表票；记录当时建议、veto 理由、后续 1 日/5 日涨跌、若买 1 股或按 5%-8% starter 的机会成本、是否属于正确不买/过度保守/交易窗口限制/数据不足/已执行但仓位偏小。若上一轮没有覆盖某个新增代表票，必须标记“上一轮未覆盖/无当时 veto”，不得补造当时建议或 veto 理由。这个账本必须进入 `01_buffett_review.md`，并被 `02-06` 阶段引用。
12a. `01_buffett_review.md` 在复盘后必须新增 `Buffett 自我反思`：Buffett 必须根据最新数据和历史决策反思自己的任务定义、候选覆盖、数据连续性、仓位执行、防错过机制、防追高机制、止损/止盈和费用后 R/R 纪律。该章节必须明确写出 `依据的最新数据`、`依据的历史决策`、`关键遗漏与分析错误复盘`、`反思结论` 和 `基于反思的新策略`。其中 `关键遗漏与分析错误复盘` 必须覆盖未关注到关键人物讲话、关键事件未捕捉、关键分析错误。反思不能只评价股票涨跌，也不能把责任推给 Zeus/Poseidon/Hades；必须写明本轮要修正的流程动作和新策略，并由 `02_buffett_plan.md` 转成 Zeus/Poseidon/Hades 派工要求。`03-06` 必须逐项回应 Buffett 自我反思和新策略，否则验收失败。
13. 本轮波段交易必须优先判断三类入场：`动能突破`、`回撤承接`、`超跌反弹`。每个可执行 BUY 必须归入其中一类，并写明触发 K 线/分时结构、成交量确认、相对强弱、关键支撑/阻力、止损价、第一止盈、第二止盈、移动止损、最长持有期和复盘时间。若无法给出这些要素，Hades 必须否决 BUY。
14. `动能突破不是自动追高`：当板块/ETF 处于本周或当日领先、个股相对 SPY/QQQ/SMH/SOXX 放量走强、突破位或 VWAP/均线结构明确、硬止损和第一/第二止盈明确、费用后 R/R 合格时，必须允许小仓 starter 或当前 BUY 审议；不得仅因个股当日已上涨或 5 日涨幅较大而一票否决。只有当价格脱离买区导致 R/R 转负、量能无法验证、跳空无法设止损、或仓位/现金/时间窗口不合格时，才能定义为 FOMO 追高。
15. starter 不是终局仓位。若 starter 后出现确认信号，必须评估 `仓位升级阶梯`：第一档 starter 5%-8% 单票或 10%-20% basket；第二档确认加仓把最强 1-2 只或 ETF/basket 提升到组合 15%-25% 总强周期暴露；第三档只在已有浮盈垫、止损抬至成本或盈利保护位后，用利润滚动而非新增无保护风险扩大到 25%-35% 总强周期暴露。任何单股仍不得超过 25% 上限。
16. 大幅盈利路径必须来自 `加大正确仓位 + 留住趋势利润`，而不是永远小仓。Poseidon 必须为可执行候选写出：starter 条件、确认加仓条件、停止加仓条件、止盈/移动止损、预计组合层面上行贡献和错判最大亏损；若只建议小仓且没有加仓路径，必须说明为什么本轮只能做试错而不适合追求大收益。
17. Poseidon 必须使用 `python3 workspace/analysis/cli.py swing-verdict` 或等价本地逻辑，把每个强周期候选和特别观察候选标记为 `current_trade`、`small_starter`、`wait` 或 `hard_veto`，其中 INTC/英特尔不得缺席。必须至少给出一个可执行小仓 starter 方案，或明确证明全部候选和 SMH/SOXX/QQQ 等 ETF/basket fallback 在费用、滑点、止损和目标后为负期望。Hades 审计结论必须是四态之一：`批准当前交易`、`批准小仓 starter`、`等待`、`否决`；对于确认加仓，还必须给出 `批准加仓`、`仅保留 starter` 或 `减仓/止盈`。不得只写笼统“不追高”。
18. 波段卖出也必须技术化：盈利股要判断是否分批止盈、移动止损或继续持有；亏损股要判断是否触发硬止损、趋势破位或仍在原入场逻辑内。严禁因为亏损而补仓摊低，除非出现新的独立波段触发且重新计算风险预算。
19. 对强周期标的，波段收益目标必须覆盖 USD {fee_text} 费用、预估滑点和止损风险；若第一止盈空间小于止损距离或费用后盈亏比不足，必须等待，不得为了参与热点而下单。
20. 若交易窗口内最终仍建议 no-trade，必须写出 `no-trade proof`：逐项列明 AMD、MU、FLEX、INTC/英特尔、WDC、STX、VRT、ANET、TSM、NVDA、SMH、SOXX、QQQ 及其他 Top 候选的 swing verdict、硬否决/等待原因、是否已审计 ETF/basket fallback。缺少该证明时，Buffett 不得验收 `本次不买入、不卖出`。

Buffett 调度与验收要求：
1. 调度 Zeus、Poseidon、Hades 时，必须分别发送明确的派工合同，包含任务目录、必须读取的上游 Markdown、必须写入的输出文件、从 `02_buffett_plan.md` 抽取的逐项任务清单、最低报告门槛、禁止事项和完成后只返回路径/缺口的要求。
2. 每个部长完成后，Buffett 必须读取对应 Markdown 并验收；报告不完整时必须要求同一部长补写或重写原文件，不得直接进入下一阶段。
3. 通用验收失败条件包括：缺少 `Buffett 规划执行情况` 逐项表、缺少输入路径、来源清单、financeBusiness 数据时间戳、financeBusiness 内部核验、数据冲突/缺口、当前 P&L 使用说明、反证、候选分层、费用/现金/整股约束。
3a. 第二步之后的通用验收失败条件还包括：缺少 `Buffett 自我反思`、`关键遗漏与分析错误复盘` 和 `基于反思的新策略` 回应，或没有把 Buffett 自我反思中的流程责任和新策略转化为数据覆盖、关键人物讲话补查、关键事件补查、分析错误归因、候选筛选、仓位、止损、止盈、确认加仓、防错过和 Hades veto 约束。
4. Zeus 验收失败条件包括：只复盘现有持仓、不覆盖当前持仓之外 AI 机会、不覆盖主要行业 ETF/宏观变量、不覆盖 financeBusiness 可得的关键人物言论与市场影响、不覆盖 AI 应用/云 CAPEX/GPU/ASIC/半导体/存储 HBM/先进封装/光模块网络/AI 服务器/数据中心电力散热/PCB CCL/设备/材料/安全数据基础设施、不写 financeBusiness 来源状态和内部核验差异。
5. Poseidon 验收失败条件包括：未先做市场 regime 和板块评分、未做 `美股板块地图` 和 `AI 产业链机会漏斗`、未把 Zeus 缺口或关键人物言论映射为降权/等待/否决、未给候选分层、未给波段执行建议、未运行或等价执行 swing verdict、未审计 ETF/basket fallback、未给 no-trade proof、长期背景判断和 Hades 潜在否决点。
6. Hades 验收失败条件包括：未做 `上游报告完整性审计`、未标出 Zeus/Poseidon 缺口、未审计关键人物言论是否被过度解读、未对不完整情报降权或否决、未复核费用后盈亏、现金、单股 25% 上限和交易后预计盈亏、未审计每个候选的四态裁决和 ETF/basket fallback。

Zeus 情报与工具要求：
1. 行情数据必须只使用本地 `financeBusiness` MCP，不得先用 CSV、AkShare 或任何本地/网页/搜索源。对每个美股持仓、核心候选、Top 候选和 ETF/basket fallback，Zeus 必须同时调用 `mcp__financeBusiness__StockCurrentMarket`（实时/最新 tape）和 `mcp__financeBusiness__StockMarketList`（历史日线/收盘校验）。每个标的的行情字段一个不能少：当前价、收盘、昨收、开盘、最高、最低、涨跌幅、涨跌额、振幅、成交量、成交额、量比、换手率、行情来源。字段映射必须写入 `03_zeus_intelligence.md`：`latestPri/lastestpri -> 当前价`，`endPri/latestPri -> 收盘`，`yesEndPri/formpri 或上一条 endPri -> 昨收`，`startPri/openpri -> 开盘`，`maxPri/maxpri -> 最高`，`minPri/minpri -> 最低`，`increasePer/limit -> 涨跌幅`，`increasePri/uppic -> 涨跌额`，`stockAmplitude/amplitude -> 振幅`，`tradingVolume/traNumber -> 成交量`，`turnover/traAmount -> 成交额`，`volumeRatio -> 量比`，`turnoverRate -> 换手率`，`financeBusiness_mcp + 工具名 + update_time/date -> 行情来源`。若 MCP 任一字段为空、过旧或内部冲突，不得补齐；必须在 Zeus 和 Hades 写 `ZEUS_FIELD_FAILURE`，不能把该标的用于最终当前 BUY/SELL。
2. 用 financeBusiness 拉取指数基准与 ETF 代理数据，形成相对强弱和板块 leadership 证据：纳斯达克综合指数必须调用 `mcp__financeBusiness__StockIndexList(stock_index_code=IXIC)`；标普 500 指数依次尝试 `SPX/GSPC/INX/SP500` 并记录覆盖缺口；SPY/QQQ/SMH/SOXX 必须作为美股 ETF 代理调用 `StockCurrentMarket` 和 `StockMarketList`。指数只做 regime，不可下单；SPY/QQQ 代理必须进入候选动作表和 no-trade proof。
3. 最新新闻、财报、公告、宏观、板块催化、关键人物讲话和反证必须用 `mcp__aiwebsearch__GoogleSearch` 搜索；对官方 IR、SEC/Fed/BLS、交易所、监管机构、公司公告、主流财经媒体等关键 URL，必须用 `mcp__aiwebsearch__searchJumps` 抽取网页正文，调用格式为 URL 对象数组，例如 `{{"cache": false, "urls": [{{"url": "https://example.com"}}]}}`，不要传纯字符串数组；aiwebsearch 不足时用官方网页、兼容 WebSearch 和 PDF 抽取 fallback。
4. 关键价格、估值价格、P&L、成交量、FX、行情字段和当前交易 sizing 只能做 financeBusiness 内部核验；不得用 aiwebsearch、searchJumps、内置 WebSearch、官方网页抓取、PDF 提取或兼容网页源补齐这些结构化行情字段。
5. 若新闻/网页源也无法覆盖关键人物/事件/公告证据，必须记录缺口、降置信度，并说明是否触发等待或 `本次不买入、不卖出`。
6. 必须为 AI 产业链至少抓取或核验代表性美股/ETF证据：AI 应用、云平台、GPU/ASIC、半导体设备、存储/HBM、先进封装、网络/光模块、服务器/ODM、数据中心电力散热、PCB/CCL、材料、安全/数据基础设施。特别观察范围 AMD、MU、FLEX、INTC/英特尔、WDC、STX、VRT、ANET、TSM、NVDA、SMH、SOXX、QQQ 必须逐票给出完整行情字段和当前交易策略字段包；若某环节缺少美股直接标的，必须说明可替代表达或暂不交易原因。
7. 必须输出数据时间戳、financeBusiness 工具名/来源字段、内部核验差异和不能核验的数据缺口。
8. `03_zeus_intelligence.md` 必须包含 `## 来源分层与覆盖度`、`## 美股板块与行业代理覆盖`、`## 数据冲突与缺口` 和完整 `## 来源清单`。
9. 每个投资关键事实必须写出“事实 -> 影响链条 -> 受益/受损对象 -> 置信度 -> 反证”，不能只列新闻标题。
10. 必须包含独立章节 `## 关键人物言论与市场影响`。覆盖 Fed/FOMC、财政部、白宫/总统、SEC/FTC/DOJ/商务部/BIS/USTR 等监管政策人物，当前持仓公司 CEO/CFO，AI 超大规模云厂商管理层，NVIDIA/AMD/TSMC/ASML/Broadcom/Arista/Micron/Vertiv 等核心 AI 供应链公司管理层，以及足以影响风险偏好的地缘政治人物。
11. 每条重要言论必须记录：人物/职务、时间、场合/来源、来源层级、核心表述、影响链条、受影响资产/板块、讲话前后可观察市场反应、方向、强度/置信度、反证或降权原因。无法量化市场反应时必须明确写“无法量化”并降低置信度；社媒或分析师言论只能作为情绪补充，不能单独支撑交易。
12. 必须为波段交易提供量价原始数据：当前价、收盘、昨收、开盘、最高、最低、涨跌幅、涨跌额、振幅、成交量、成交额、量比、换手率、行情来源、5/10/20 日均线位置、20 日高低点、近 5 日涨跌、盘中是否放量突破或回踩承接、相对 SPY/QQQ/SMH/SOXX 强弱。若成交额或量比来自 OHLCV 推导而不是源字段，必须标注估算；无法取得的字段必须标记缺口，并说明对波段结论的影响。
13. 必须新增 `## 当前交易策略字段包`。对每个当前持仓、核心候选、Top 候选、特别观察候选和 ETF/basket fallback，Zeus 必须输出字段：`ticker`、`name`、`current_price`、`close`、`previous_close`、`open`、`high`、`low`、`pct_change`、`change_amount`、`amplitude`、`volume`、`amount`、`volume_ratio`、`turnover_rate`、`market_source`、`quote_time`、`trade_status`、`ma5`、`ma10`、`ma20`、`price_vs_ma5`、`price_vs_ma10`、`price_vs_ma20`、`high_20d`、`low_20d`、`range_position_20d`、`return_1d`、`return_5d`、`return_10d`、`return_20d`、`atr_14`、`volatility_20d`、`relative_strength_spy`、`relative_strength_qqq`、`relative_strength_smh`、`relative_strength_soxx`、`entry_type`、`entry_trigger_price`、`suggested_limit_price`、`stop_loss_price`、`take_profit_1`、`take_profit_2`、`trailing_stop_rule`、`max_holding_days`、`next_review_time_bj`、`risk_per_share`、`reward_to_tp1`、`reward_to_tp2`、`fee_adjusted_rr_tp1`、`fee_adjusted_rr_tp2`、`max_loss_usd`、`cash_required_or_released`、`fee_usd`、`fee_pct`、`whole_share_count`、`primary_source_status`、`financebusiness_reconciliation_status`、`missing_fields`、`estimated_fields`、`field_source_map`、`field_timestamp_map`、`data_conflicts`、`confidence`、`zeus_field_status`、`usable_for_current_trade`。其中执行字段只能作为证据交接或写 `待 Poseidon/Buffett 裁决`，不得被 Zeus 包装成最终 BUY/SELL；INTC/英特尔的字段包不得省略或用半导体行业均值替代。
14. 对 AI 产业链上中下游重点候选必须按环节覆盖，而不是只覆盖存储/HBM 或当前持仓；至少覆盖 AI 应用/云、GPU/ASIC、晶圆代工、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、AI 服务器/ODM/EMS、数据中心电力/散热、PCB/CCL、安全/数据基础设施和链条 ETF/篮子。全链条初筛表中每个候选至少给出热点催化、量价状态、追高风险、动能突破是否成立、是否适合当前交易窗口；深度波段计划只要求覆盖初筛后的 Top 8-12。

Poseidon 研究与趋势预测要求：
1. 必须做美股市场 regime、板块轮动、利润池归属、盈利修正、估值水位、技术趋势、资金约束、费用拖累和风险预算分析。
2. `04_poseidon_research.md` 必须包含独立章节 `## 美股板块地图` 和 `## AI 产业链机会漏斗`。AI 漏斗必须按环节评分，列出直接/间接受益、利润池归属、定价权、订单能见度、估值/拥挤度、关键催化、代表性美股 ticker/ETF、波段机会、长期背景、Hades 潜在否决点。
3. 必须把候选分为 `核心候选 / 战术候选 / 观察名单 / 回避或否决`，并解释为什么可执行或不可执行。候选池可以包括当前持仓以外的新机会，但必须专注美股可交易标的。
4. 必须包含独立章节 `## 当前盈亏与仓位含义`，把总盈亏、个股盈亏、持仓集中度和 AI 机会放在同一个风险预算框架里分析。本轮买卖理由必须解释该动作如何改变总盈亏风险、单股亏损暴露、盈利保护或再部署能力。
5. 必须包含 `## 关键人物言论采纳与投资含义`，把 Zeus 记录的讲话分类为政策信号、公司基本面信号、产业链订单/供给信号、监管/地缘信号或市场情绪噪音，并说明是否改变估值、仓位、交易窗口、失效条件或不改变操作。
6. 必须给出未来 1-5 个交易日和 2-6 周趋势预测：方向、概率、关键驱动、关键价位、失效条件。
7. 必须允许并优先使用本地 Python/表格/计算代码来辅助判断，例如计算趋势评分、相对强弱、均线位置、成交量、波动率、近期回撤、板块动量、新闻/财报催化、关键人物言论影响、宏观压力、费用后期望值、总盈亏和个股盈亏。
8. 不得承诺盈利；趋势预测用于提高本次下单质量，必须同时写出错判下行和失效条件。
9. 必须新增 `## 强周期波段交易计划`：按 `动能突破 / 回撤承接 / 超跌反弹` 三类列出候选，给出技术触发、限价、止损、第一止盈、第二止盈、移动止损、最长持有期、仓位、单笔风险金额和费用后盈亏比。
10. 必须新增 `## 错过机会修正与当前 starter 方案`：逐项解释上一轮未买强势股的错误类型，并给出本轮是否采用小仓 starter、确认加仓、ETF/basket 替代、等待回撤或继续否决。至少提供一个可执行小仓 starter 方案；若没有，必须用数据证明所有候选费用后负期望。
11. 必须新增 `## 仓位升级阶梯与大幅盈利路径`：说明如何从 starter 升级到确认加仓和利润滚动，给出每档仓位、触发条件、最大组合强周期暴露、单股上限、浮盈保护、预计组合层面收益贡献和错判下行。不能只说小仓参与。
12. 强周期波段候选的默认仓位和风险必须按 `{cfg.trading_profile}` 执行：单笔最大亏损约账户 {cfg.short_term_single_trade_risk_pct:g}%，初始仓位 {cfg.strong_cycle_initial_position_pct_min:g}%-{cfg.strong_cycle_initial_position_pct_max:g}%，硬止损通常 {cfg.short_term_stop_loss_pct_min:g}%-{cfg.short_term_stop_loss_pct_max:g}%。若偏离，必须解释是因为波动率、流动性、现金、仓位集中或数据质量；确认加仓时，新增风险必须由抬高止损或已有浮盈垫吸收，不能简单扩大无保护亏损。
13. 必须新增 `## 候选动作对照表`：候选、短线分数、入场类型、限价、止损、第一/第二目标、费用后 R/R、数据质量、Hades 预期状态、swing verdict、最终动作。特别观察候选必须全部入表，INTC/英特尔必须单独列行并说明是否为 `current_trade`、`small_starter`、`wait` 或 `hard_veto`。若个股数据不足，必须在同表或相邻表中审计 SMH/SOXX/QQQ 或更合适 basket fallback。

Hades 审计要求：
1. 审计趋势预测是否过度自信、是否依赖单一来源、是否被 USD {fee_text} 费用和滑点吞噬。
2. 审计每个潜在交易的费用后期望值：买入现金占用 = 限价 * 整股数量 + {fee_text}；卖出净回收 = 限价 * 整股数量 - {fee_text}。
3. 必须审计 AI 产业链机会漏斗：是否把主题暴露误当利润池，是否遗漏上游/下游更优机会，是否忽略客户集中、库存、出口管制、技术替代、估值拥挤和事件风险。
4. 必须审计当前总盈亏和个股盈亏计算是否自洽，且审计研究是否正确使用盈亏信息。不得因为亏损就机械卖出，也不得因为亏损就补仓摊低成本；必须区分“可恢复的估值/时点亏损”和“基本面/风险预算恶化的亏损”。
5. 必须审计 `07_final_decision.md` 的 `## 交易后预计盈亏`：每笔 SELL 是否按限价、整股数量、成本价和 USD {fee_text} 费用计算预计已实现盈亏；每笔 BUY 是否把 USD {fee_text} 费用计入现金占用和建仓后成本；交易后剩余持仓的股数、成本额、市值、未实现盈亏、现金和组合权益是否自洽。
6. 若预期收益不能覆盖费用、滑点和风险预算，必须否决交易。
7. 若最终决策生成或复核时间已经晚于本轮执行截止时间 `{deadline_text}`，必须否决本次买入/卖出，并要求最终写“本次不买入、不卖出”；不得把“当前时间的小时数大于 00:00”误读为窗口已关闭。
8. `05_hades_verification.md` 必须包含 `## 上游报告完整性审计`，逐项审计 Zeus/Poseidon 是否满足输入文件、规划执行表、来源清单、financeBusiness 内部核验、P&L 使用、AI 链条覆盖、候选分层、反证和数据缺口要求。
9. 如果 Zeus 情报不完整或 Poseidon 使用不完整情报仍给可执行建议，Hades 必须写 `🔴 不同意` 或 `🟡 有条件同意`，并要求圆桌补查、降权、等待或否决。
10. `05_hades_verification.md` 必须包含 `## 关键人物言论审计`，检查来源是否可靠、讲话人权重是否足够、市场反应是否可量化、Poseidon 是否过度加权言论、是否把情绪噪音误当基本面信号。
11. 必须新增 `## 波段风控审计`：逐笔审计入场类型是否成立、止损是否硬、止盈/移动止损是否明确、单笔风险是否不超过账户约 {cfg.short_term_single_trade_risk_pct:g}%、初始仓位是否在 {cfg.strong_cycle_initial_position_pct_min:g}%-{cfg.strong_cycle_initial_position_pct_max:g}% 合理区间、费用后盈亏比是否足够、是否存在把波段失败交易拖成长线的风险。
12. 必须新增 `## 防错过审计与三态裁决`：对每个强周期候选和特别观察候选给出 `批准当前交易`、`批准小仓 starter`、`等待` 或 `否决`。INTC/英特尔必须有独立裁决，不能被合并进“半导体整体”。若否决，只能使用可审计硬条件：交易窗口关闭、数据源不足、止损无法定义、费用后 R/R 不合格、仓位/现金/25% 上限冲突、或跳空追价导致第一目标不足；不得把“上涨多”单独作为否决理由。若否决原因只是个股数据质量，必须要求 ETF/basket fallback 审计。
13. 必须新增 `## 仓位升级审计`：审计 starter 是否只是试错、是否有确认加仓路径、加仓后组合强周期总暴露是否合理、单股是否低于 25%、新增风险是否被浮盈垫或移动止损覆盖、以及是否具备组合层面大幅盈利的数学路径。若没有加仓路径，必须要求圆桌承认“本轮只能小赚或试错，不能期待大幅盈利”。
14. 必须新增 `## No-trade proof 审计`：当最终候选为不交易时，逐项核验核心/战术候选和 ETF/basket fallback 的 swing verdict 是否足以支持 no-trade；缺失则 Hades 不得同意最终 no-trade。

最终决策硬格式：
1. `07_final_decision.md` 必须包含独立章节 `## 当前持仓盈亏复盘`，列出美股持仓总市值、总成本、总未实现盈亏金额、总未实现盈亏率，以及每个美股/ETF 的当前价、成本价、持股数、当前市值、成本额、未实现盈亏金额、未实现盈亏率。
2. `当前持仓盈亏复盘` 后必须写明这些盈亏信息如何影响本次决策，例如：为什么对亏损中的 MSFT/TSLA 不机械补仓，为什么对盈利中的 NVDA/SPY 不盲目追加，为什么卖出某标的是锁定亏损但降低组合尾部风险，或为什么不卖是保留恢复路径。
3. `07_final_decision.md` 必须包含独立章节 `## 本次当前操作`。
4. `本次当前操作` 只列当前本次要立刻执行的 BUY / SELL；不在当前本次范围要操作的股票、观察名单、未来条件单、候选池、等待触发、泛泛建议一律不要列出。
5. 如果当前无交易，必须只写：`本次不买入、不卖出`，并简述费用后期望值或时间窗口导致不交易的原因。
6. 每条 BUY / SELL 必须包含：ticker、动作、整股数量、限价、USD {fee_text} 费用、总现金占用或卖出净回收、费用占交易额比例、趋势预测依据、下单理由、无效条件。
6a. 每条 BUY / SELL 还必须包含波段执行字段：入场类型（动能突破/回撤承接/超跌反弹/止损卖出/止盈卖出/移动止损）、技术触发、止损价、第一止盈价、第二止盈价、移动止损规则、最长持有期、下一次盘中复盘时间。若这些字段不完整，不得进入 `本次当前操作`。
7. `07_final_decision.md` 必须在 `## 本次当前操作` 之后包含独立章节 `## 交易后预计盈亏`。该章节必须假设本次 BUY/SELL 均按限价成交且每笔收取 USD {fee_text} 费用，列出：交易前可用美股现金、每笔交易现金变化、交易后可用美股现金、每笔 SELL 的卖出成本基础、预计已实现盈亏金额和费用后已实现盈亏、每笔 BUY 的现金占用和费用后初始成本、交易后每个剩余美股/ETF 持仓的股数、成本额、估算市值、未实现盈亏金额、未实现盈亏率，以及交易后剩余持仓合计未实现盈亏、当次已实现盈亏、已实现+未实现合计盈亏、交易后组合权益估算。
8. 若卖出成本基础无法从操作记录可靠识别，必须明确写出采用平均成本法估算；若连平均成本也不可得，必须标注无法可靠计算并禁止把该项当作精确盈亏。
9. 必须写出交易后剩余可用美股资金；如果现金不足买入至少 1 股并支付 USD {fee_text} 费用，必须不买。
10. 卖出必须给出整数股数，不能只写“减仓 20%”。
11. 必须包含独立章节 `## 下一次建议启动分析时间（北京时间）`，给出下一次用户应该输入 `{TRIGGER_PHRASE}` 的具体北京时间和原因。
12. 其他 AI 产业链机会、候选、观察名单和未来条件必须留在 `04_poseidon_research.md`、`05_hades_verification.md`、`06_roundtable.md`，不得混入 `## 本次当前操作`；若其中有费用后正期望且适合当前窗口执行，才可作为当前 BUY/SELL 进入最终操作表。

base_short.md 当前快照如下：

```markdown
{base_short}
```
"""


def append_system_log(
    log_path: Path,
    timestamp: dt.datetime,
    run_dir: Path,
    dry_run: bool,
    command_result: dict[str, Any] | None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        text = log_path.read_text(encoding="utf-8")
    else:
        text = "# Buffett 美股投研运行记录\n\n"
    mode = "dry-run" if dry_run else "executed"
    command_status = "not configured" if command_result is None else f"returncode={command_result['returncode']}"
    entry = (
        f"\n### {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')} - {TRIGGER_PHRASE}\n\n"
        f"- 模式：{mode}\n"
        f"- 运行目录：`{run_dir}`\n"
        "- 市场重点：美股\n"
        f"- 执行状态：{command_status}\n"
        "- 说明：本记录是系统运行日志，不是用户交易操作记录。\n"
    )
    log_path.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")


def execute_command(command_template: str, prompt_file: Path, run_dir: Path, timestamp: dt.datetime, cfg: ResearchConfig) -> dict[str, Any]:
    if command_template.strip().lower() in CURRENT_CODEX_COMMANDS:
        prompt_text = prompt_file.read_text(encoding="utf-8")
        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"
        handoff_path = run_dir / "current_codex_handoff.json"
        stdout_path.write_text(prompt_text, encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        handoff = {
            "mode": CURRENT_CODEX_COMMAND,
            "prompt_file": str(prompt_file),
            "stdout_file": str(stdout_path),
            "stderr_file": str(stderr_path),
            "run_dir": str(run_dir),
            "timestamp": timestamp.isoformat(),
            "note": "Prompt is handed to the current Codex workflow. No child Codex subprocess is started.",
        }
        handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "command": CURRENT_CODEX_COMMAND,
            "returncode": 0,
            "timed_out": False,
            "stdout_file": str(stdout_path),
            "stderr_file": str(stderr_path),
            "handoff_file": str(handoff_path),
            "handoff_mode": CURRENT_CODEX_COMMAND,
        }

    command = command_template.format(
        prompt_file=str(prompt_file),
        run_dir=str(run_dir),
        timestamp=timestamp.isoformat(),
        base_short_path=str(cfg.base_short_path),
    )
    try:
        proc = subprocess.run(
            shlex.split(command),
            cwd=cfg.project_root,
            text=True,
            input=prompt_file.read_text(encoding="utf-8"),
            capture_output=True,
            check=False,
            timeout=cfg.execute_timeout_seconds,
        )
        stdout = proc.stdout
        stderr = proc.stderr
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stderr = (
            stderr.rstrip()
            + f"\nCommand timed out after {cfg.execute_timeout_seconds} seconds.\n"
        )
        returncode = 124
        timed_out = True

    (run_dir / "stdout.txt").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.txt").write_text(stderr, encoding="utf-8")
    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "stdout_file": str(run_dir / "stdout.txt"),
        "stderr_file": str(run_dir / "stderr.txt"),
    }


def validate_final_artifacts(report_dir: Path) -> dict[str, Any]:
    missing_files = [name for name in REQUIRED_REPORT_FILES if not (report_dir / name).exists()]
    snapshot_path = report_dir / "local_result_snapshot.json"
    db_record_path = report_dir / "db_record.json"
    errors: list[str] = []

    if not report_dir.exists():
        errors.append(f"report_dir_missing:{report_dir}")
    if missing_files:
        errors.append(f"missing_required_phase_files:{','.join(missing_files)}")
    if not snapshot_path.exists():
        errors.append("missing_local_result_snapshot.json")
    else:
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid_local_result_snapshot_json:{exc}")
        else:
            if not isinstance(snapshot, dict):
                errors.append("local_result_snapshot_json_not_object")
            else:
                if snapshot.get("sqlite_write_status") != "skipped_by_disabled_policy":
                    errors.append("sqlite_write_status_not_skipped_by_disabled_policy")
                sqlite_mode = snapshot.get("sqlite_write_mode")
                if sqlite_mode is not None and sqlite_mode != SQLITE_WRITE_DISABLED:
                    errors.append("sqlite_write_mode_not_disabled")
    if db_record_path.exists():
        errors.append("db_record.json_created")

    result = {
        "status": "passed" if not errors else "failed",
        "report_dir": str(report_dir),
        "required_files": list(REQUIRED_REPORT_FILES),
        "missing_files": missing_files,
        "local_result_snapshot": str(snapshot_path),
        "db_record_path": str(db_record_path),
        "errors": errors,
    }
    if errors:
        raise RuntimeError("final Buffett artifact validation failed: " + "; ".join(errors))
    return result


US_EQUITY_DEFAULT_PREFETCH_SYMBOLS = (
    "KO",
    "MSFT",
    "NVDA",
    "SPY",
    "TSLA",
    "AMD",
    "TSM",
    "ANET",
    "QQQ",
    "DIA",
    "SMH",
    "SOXX",
    "XLK",
    "XLC",
    "XLY",
    "XLI",
    "XLU",
    "XLF",
    "XLV",
    "XLP",
    "XLE",
    "XLB",
    "XLRE",
    "MU",
    "WDC",
    "STX",
    "VRT",
    "FLEX",
    "INTC",
    "PLAB",
    "JBL",
    "CLS",
)


def prefetch_symbols_from_base(base_short: str, cfg: ResearchConfig) -> list[str]:
    symbols = {symbol.upper() for symbol in US_EQUITY_DEFAULT_PREFETCH_SYMBOLS}
    symbols.update(symbol.upper() for symbol in _effective_strong_cycle_focus(cfg))
    visible_text = re.sub(r"<!--.*?-->", "", base_short, flags=re.DOTALL)
    for match in re.findall(r"\b[A-Z]{1,5}(?:\.[A-Z])?\b", visible_text):
        token = match.upper()
        if token in {"ETF", "USD", "HKD", "AI"}:
            continue
        symbols.add(token)
    return sorted(symbols)


def previous_us_weekday(value: dt.date) -> dt.date:
    while value.weekday() >= 5:
        value -= dt.timedelta(days=1)
    return value


def prefetch_market_data_pack(
    cfg: ResearchConfig,
    base_short: str,
    run_dir: Path,
    timestamp: dt.datetime,
) -> dict[str, Any]:
    """Do not prefetch market data outside financeBusiness.

    Buffett workflows now require Zeus to call financeBusiness MCP directly.
    This helper remains for backwards-compatible callers, but it no longer
    invokes local adapters or writes a CSV manifest.
    """
    symbols = prefetch_symbols_from_base(base_short, cfg)
    return {
        "status": "skipped_financebusiness_only_policy",
        "generated_at": timestamp.isoformat(),
        "symbols": symbols,
        "source_order": ["financeBusiness_mcp"],
        "note": "No local market-data pack generated; Zeus must call financeBusiness MCP directly.",
    }


def run_research(cfg: ResearchConfig, *, dry_run: bool, timestamp: dt.datetime | None = None) -> dict[str, Any]:
    cfg = config_with_sqlite_write_mode(cfg, cfg.sqlite_write_mode)
    ts = (timestamp or dt.datetime.now(cfg.timezone)).astimezone(cfg.timezone)
    base_short = read_base_short(cfg)
    run_dir = run_dir_for(ts, cfg)
    run_dir.mkdir(parents=True, exist_ok=True)

    command_result: dict[str, Any] | None = None
    if not dry_run and not cfg.execute_command:
        raise SystemExit(
            "execute_command is required for non-dry-run mode because live Buffett research must start the full workflow"
        )

    market_data_pack: dict[str, Any] | None = None
    if not dry_run:
        market_data_pack = prefetch_market_data_pack(cfg, base_short, run_dir, ts)

    snapshot = run_dir / "base_short_snapshot.md"
    prompt_file = run_dir / "prompt.md"
    snapshot.write_text(base_short, encoding="utf-8")
    market_data_manifest_path = None
    suggested_report_dir = report_dir_for(ts, cfg)
    previous_history = read_previous_history(cfg)
    prompt_file.write_text(
        build_prompt(
            base_short,
            ts,
            cfg,
            market_data_manifest_path=market_data_manifest_path,
        ),
        encoding="utf-8",
    )

    if not dry_run and cfg.execute_command:
        command_result = execute_command(cfg.execute_command, prompt_file, run_dir, ts, cfg)

    artifact_validation: dict[str, Any]
    if dry_run:
        artifact_validation = {
            "status": "skipped_dry_run",
            "reason": "dry-run only writes prompt/run metadata; final reports are not executed",
            "report_dir": str(suggested_report_dir),
        }
    elif command_result and command_result.get("returncode") != 0:
        artifact_validation = {
            "status": "skipped_failed_command",
            "reason": f"command_returncode={command_result.get('returncode')}",
            "report_dir": str(suggested_report_dir),
        }
    elif command_result and command_result.get("handoff_mode") == CURRENT_CODEX_COMMAND:
        artifact_validation = {
            "status": "skipped_current_codex_handoff",
            "reason": "current_codex mode only hands the prompt to the active Codex workflow; final artifacts are validated by the active workflow after it runs",
            "report_dir": str(suggested_report_dir),
        }
    else:
        artifact_validation = validate_final_artifacts(suggested_report_dir)

    if cfg.write_system_log:
        append_system_log(cfg.system_log_path, ts, run_dir, dry_run or not cfg.execute_command, command_result)

    metadata = {
        "timestamp": ts.isoformat(),
        "timezone": str(cfg.timezone),
        "trigger_phrase": TRIGGER_PHRASE,
        "primary_market": cfg.primary_market,
        "task_type": cfg.task_type,
        "subject": cfg.subject,
        "base_short_path": str(cfg.base_short_path),
        "system_log_path": str(cfg.system_log_path),
        "run_dir": str(run_dir),
        "suggested_report_dir": str(suggested_report_dir),
        "prompt_file": str(prompt_file),
        "snapshot_file": str(snapshot),
        "trade_deadline_beijing": cfg.trade_deadline_beijing,
        "trade_deadline_beijing_at": next_trade_deadline(ts, cfg).isoformat(),
        "per_trade_fee_usd": cfg.per_trade_fee_usd,
        "trading_profile": cfg.trading_profile,
        "short_term_primary_horizon": cfg.short_term_primary_horizon,
        "short_term_single_trade_risk_pct": cfg.short_term_single_trade_risk_pct,
        "strong_cycle_initial_position_pct_min": cfg.strong_cycle_initial_position_pct_min,
        "strong_cycle_initial_position_pct_max": cfg.strong_cycle_initial_position_pct_max,
        "short_term_stop_loss_pct_min": cfg.short_term_stop_loss_pct_min,
        "short_term_stop_loss_pct_max": cfg.short_term_stop_loss_pct_max,
        "strong_cycle_focus": list(cfg.strong_cycle_focus),
        "effective_strong_cycle_focus": list(_effective_strong_cycle_focus(cfg)),
        "special_watch_symbols": list(_special_watch_symbol_tuple()),
        "market_index_proxy_contract": [
            {
                **item,
                "index_codes": list(item["index_codes"]),
            }
            for item in MARKET_INDEX_PROXY_CONTRACT
        ],
        "sqlite_write_mode": cfg.sqlite_write_mode,
        "market_data_timeout_seconds": cfg.market_data_timeout_seconds,
        "market_data_cache_dir": str(cfg.market_data_cache_dir),
        "market_data_aktools_api_url": cfg.market_data_aktools_api_url,
        "market_data_http_api_url": cfg.market_data_http_api_url,
        "market_data_sources": list(cfg.market_data_sources),
        "market_data_pack_manifest": str(market_data_manifest_path) if market_data_manifest_path is not None else None,
        "market_data_pack_summary": market_data_pack,
        "previous_history": {
            "history_source": previous_history["history_source"],
            "status": previous_history["status"],
            "local_record_path": previous_history["record"]["path"] if previous_history["record"] else None,
            "records_scanned": previous_history["records_scanned"],
            "record_format_records_scanned": previous_history["record_format_records_scanned"],
            "sqlite_status": previous_history["sqlite"]["status"],
            "has_sqlite_decision": previous_history["sqlite"]["decision"] is not None,
        },
        "artifact_validation": artifact_validation,
        "dry_run": dry_run,
        "command_result": command_result,
    }
    (run_dir / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    if command_result and command_result["returncode"] != 0:
        raise SystemExit(
            f"external Buffett workflow failed with returncode={command_result['returncode']}; "
            f"see {command_result['stderr_file']}"
        )
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Optional JSON config path.")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser(TRIGGER_PHRASE, help="Start today's full Buffett US-equity research workflow.")
    run_parser.add_argument("--dry-run", action="store_true", help="Do not execute configured external command.")
    run_parser.add_argument(
        "--local-only",
        action="store_true",
        help="Legacy alias for the default no-SQLite-write mode; write final results only to local files.",
    )

    step2_parser = sub.add_parser(
        "prepare-step2",
        help="Generate and validate 00_metadata, 01_buffett_review, and 02_buffett_plan locally.",
    )
    step2_parser.add_argument(
        "--local-only",
        action="store_true",
        help="Legacy alias for the default no-SQLite-write mode.",
    )
    step2_parser.add_argument(
        "--prices",
        help="Comma-separated current prices, format <SYMBOL=PRICE,...>.",
    )
    step2_parser.add_argument("--hkd-usd-rate", type=float, help="HKD per USD rate for cash background conversion.")
    step2_parser.add_argument("--report-slug", help="Deprecated; record_YYYYMMDD_HHMMSS_序号 naming ignores this value.")
    step2_parser.add_argument("--timestamp", help="ISO timestamp. Naive timestamps use the configured timezone.")
    step2_parser.add_argument("--market-data-manifest", type=Path, help="Optional prefetch manifest path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(args.config)

    if args.command == TRIGGER_PHRASE:
        if args.local_only:
            cfg = config_with_sqlite_write_mode(cfg, "local_only")
        print(json.dumps(run_research(cfg, dry_run=args.dry_run), ensure_ascii=False, indent=2))
        return

    if args.command == "prepare-step2":
        if args.local_only:
            cfg = config_with_sqlite_write_mode(cfg, "local_only")
        result = prepare_step2_reports(
            cfg,
            prices=parse_prices_arg(args.prices),
            hkd_usd_rate=args.hkd_usd_rate,
            report_slug=args.report_slug,
            market_data_manifest_path=args.market_data_manifest,
            timestamp=parse_timestamp_arg(args.timestamp, cfg),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
