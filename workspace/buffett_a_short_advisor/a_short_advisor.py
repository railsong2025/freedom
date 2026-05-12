#!/usr/bin/env python3
"""Manual runner for full Buffett A-share short-term advice."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


DEFAULT_CONFIG = {
    "project_root": "/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN",
    "base_short_path": "workspace/buffett_a_short_advisor/base_short_A.md",
    "timezone": "Asia/Shanghai",
    "primary_market": "China A-shares",
    "report_slug": "A股短线议",
    "prompt_language": "Chinese",
    "execute_command": None,
    "execute_timeout_seconds": 1800,
    "write_system_log": True,
    "system_log_path": "workspace/buffett_a_short_advisor/system_log.md",
}


@dataclass(frozen=True)
class AdvisorConfig:
    project_root: Path
    base_short_path: Path
    timezone: ZoneInfo
    primary_market: str
    report_slug: str
    prompt_language: str
    execute_command: str | None
    execute_timeout_seconds: int
    write_system_log: bool
    system_log_path: Path


def load_config(path: Path | None) -> AdvisorConfig:
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

    return AdvisorConfig(
        project_root=project_root,
        base_short_path=base_path,
        timezone=ZoneInfo(data["timezone"]),
        primary_market=str(data["primary_market"]),
        report_slug=str(data["report_slug"]),
        prompt_language=str(data["prompt_language"]),
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
        "# Buffett A股短线交易基础记录\n\n"
        "## 当前A股持仓\n\n"
        "- TODO：由用户填写当前 A 股持仓。\n\n"
        "## 可用资金\n\n"
        "- 50,000 元人民币，可投资 A 股。\n\n"
        "## A股短线交易规则\n\n"
        "- 主要目标市场：A 股。\n"
        "- 每次手动运行必须先阅读本文件中的持仓、可用资金和用户手动填写的“操作记录”，再读取上一次同类 SQLite 决策，然后启动 Buffett 完整本地流程生成交易建议。\n"
        "- “操作记录”只记录用户根据手动建议系统实际执行的人为股票交易，由用户手动填写。\n"
        "- 建议系统不得自动修改“操作记录”；系统运行记录另存于 `workspace/buffett_a_short_advisor/system_log.md` 和 `runs/` 目录。\n"
        "- A 股交易需遵守 100 股一手约束。\n"
        "- 所有建议仅作为投资研究记录，不是自动交易指令。\n\n"
        "## 操作记录\n\n"
        "<!--\n"
        "本节由用户手动填写真实 A 股交易记录。建议格式：\n\n"
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


def read_base_short(cfg: AdvisorConfig) -> str:
    ensure_base_short(cfg.base_short_path)
    return cfg.base_short_path.read_text(encoding="utf-8")


def run_dir_for(timestamp: dt.datetime, cfg: AdvisorConfig) -> Path:
    stamp = timestamp.astimezone(cfg.timezone).strftime("%Y%m%d_%H%M%S")
    return cfg.project_root / "workspace" / "buffett_a_short_advisor" / "runs" / stamp


def build_prompt(base_short: str, timestamp: dt.datetime, cfg: AdvisorConfig) -> str:
    local_ts = timestamp.astimezone(cfg.timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
    shared_base_path = cfg.base_short_path
    return f"""$buffett
本次是 A 股短线交易建议系统手动触发。

运行时间：{local_ts}
主交易市场：{cfg.primary_market}，重点是 A 股短线交易建议。
唯一共享操作记录文件：{shared_base_path}

硬性要求：
1. 先读取唯一共享源文件 `{shared_base_path}`，并引用其中的 A 股持仓、可用资金和用户手动填写的“操作记录”。
2. 在 Buffett 复盘阶段必须读取上一次同类 SQLite 决策；不得跳过历史决策读取。
3. `01_buffett_review.md` 必须同时复盘两类信息：用户手工 A 股交易记录的执行结果、上一条同类 SQLite 决策的成败/待验证状态。
4. 必须启动完整 Buffett 本地流程，不允许只输出轻量盘中检查。
5. 完整流程必须按项目 buffett skill 执行：Buffett 复盘、Buffett 规划、Zeus 情报、Poseidon 研究、Hades 验证、Buffett 圆桌会议、最终决策。
6. 后续所有阶段必须读取前置文件，尤其是 `01_buffett_review.md` 和 `02_buffett_plan.md`，并在计划遵循表中说明如何吸收交易记录和上次决策教训。
7. 每个阶段都要写入中文本地 Markdown；不要创建 `.zh.md` 备份；把英文版圆桌会议全文和英文版最终决策全文写入本地 SQLite。
8. 根据当前 A 股价格、盘中走势、板块/题材/政策催化、用户实际操作记录和上一次决策复盘，给出短线交易建议。
9. 建议必须区分：立即可执行、等待触发、止损/止盈、禁止追高、继续观察。
10. 必须考虑 A 股 100 股一手、涨跌停、午间休市、T+1 约束和人民币 50,000 元资金上限。
11. 不要自动下单。所有输出都是投资研究建议。
12. 不要改写 `{shared_base_path}` 的“操作记录”；该区域只由用户手动填写真实交易。
13. `runs/` 目录中的 `base_short_A_snapshot.md` 只是本次运行时的只读审计快照，不是新的操作记录文件，不得把它当作记录来源。

共享 base_short_A.md 当前内容如下：

```markdown
{base_short}
```
"""


def append_system_log(log_path: Path, timestamp: dt.datetime, run_dir: Path, dry_run: bool, command_result: dict[str, Any] | None) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if log_path.exists():
        text = log_path.read_text(encoding="utf-8")
    else:
        text = "# Buffett A股短线建议系统运行记录\n\n"
    mode = "dry-run" if dry_run else "executed"
    command_status = "not configured" if command_result is None else f"returncode={command_result['returncode']}"
    entry = (
        f"\n### {timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')} - 手动 Buffett A股短线检查\n\n"
        f"- 模式：{mode}\n"
        f"- 运行目录：`{run_dir}`\n"
        "- 市场重点：A 股\n"
        f"- 外部执行：{command_status}\n"
        "- 说明：本记录是系统运行日志，不是用户交易操作记录。\n"
    )
    log_path.write_text(text.rstrip() + "\n" + entry + "\n", encoding="utf-8")


def execute_command(command_template: str, prompt_file: Path, run_dir: Path, timestamp: dt.datetime, cfg: AdvisorConfig) -> dict[str, Any]:
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


def run_once(cfg: AdvisorConfig, *, dry_run: bool, timestamp: dt.datetime | None = None) -> dict[str, Any]:
    ts = (timestamp or dt.datetime.now(cfg.timezone)).astimezone(cfg.timezone)
    base_short = read_base_short(cfg)
    run_dir = run_dir_for(ts, cfg)
    run_dir.mkdir(parents=True, exist_ok=True)

    snapshot = run_dir / "base_short_A_snapshot.md"
    prompt_file = run_dir / "prompt.md"
    snapshot.write_text(base_short, encoding="utf-8")
    prompt_file.write_text(build_prompt(base_short, ts, cfg), encoding="utf-8")

    command_result: dict[str, Any] | None = None
    if not dry_run and not cfg.execute_command:
        raise SystemExit(
            "execute_command is required for non-dry-run mode because live runs must start the full Buffett workflow"
        )
    if not dry_run and cfg.execute_command:
        command_result = execute_command(cfg.execute_command, prompt_file, run_dir, ts, cfg)

    if cfg.write_system_log:
        append_system_log(cfg.system_log_path, ts, run_dir, dry_run or not cfg.execute_command, command_result)

    metadata = {
        "timestamp": ts.isoformat(),
        "timezone": str(cfg.timezone),
        "primary_market": cfg.primary_market,
        "shared_base_short_path": str(cfg.base_short_path),
        "system_log_path": str(cfg.system_log_path),
        "run_dir": str(run_dir),
        "prompt_file": str(prompt_file),
        "audit_snapshot_file": str(snapshot),
        "dry_run": dry_run,
        "command_result": command_result,
    }
    (run_dir / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Optional JSON config path.")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", aliases=["run-once"], help="Run one manual full Buffett prompt.")
    run_parser.add_argument("--dry-run", action="store_true", help="Do not execute configured external command.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(args.config)

    if args.command in ("run", "run-once"):
        print(json.dumps(run_once(cfg, dry_run=args.dry_run), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
