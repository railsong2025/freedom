"""Checkpointed Markdown report assembly for Zeus intelligence tasks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_PARTS_DIRNAME = "03_zeus_intelligence_parts"
DEFAULT_OUTPUT_NAME = "03_zeus_intelligence.md"

REQUIRED_ZEUS_SECTIONS: tuple[str, ...] = (
    "输入与任务范围",
    "执行摘要",
    "情报问题清单",
    "请求/规划执行情况",
    "Python 工具调用记录",
    "市场与行情",
    "新闻、公告、文件与事件",
    "关键人物言论与市场影响",
    "关键事件捕捉与遗漏补查",
    "来源分层与覆盖度",
    "板块与宏观背景",
    "美股板块与行业代理覆盖",
    "行业、主题与供应链情报",
    "AI 产业链情报",
    "强周期波段量价证据",
    "上游工作流承接",
    "数据冲突与缺口",
    "关键发现",
    "来源清单",
)


@dataclass(frozen=True)
class CheckpointPart:
    index: int
    path: Path
    title: str
    char_count: int
    modified_at: str


@dataclass(frozen=True)
class MergeResult:
    output_path: Path
    manifest_path: Path
    part_count: int
    missing_sections: tuple[str, ...]
    complete: bool


def parts_dir_for(run_dir: Path, parts_dir: Path | None = None) -> Path:
    return parts_dir if parts_dir is not None else run_dir / DEFAULT_PARTS_DIRNAME


def discover_parts(run_dir: Path, parts_dir: Path | None = None) -> list[CheckpointPart]:
    directory = parts_dir_for(run_dir, parts_dir)
    if not directory.exists():
        return []
    parts: list[CheckpointPart] = []
    for path in sorted(directory.glob("*.md")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        title = _first_heading(text) or path.stem
        parts.append(
            CheckpointPart(
                index=len(parts) + 1,
                path=path,
                title=title,
                char_count=len(text),
                modified_at=datetime.fromtimestamp(path.stat().st_mtime).replace(microsecond=0).isoformat(),
            )
        )
    return parts


def merge_checkpoints(
    run_dir: Path,
    *,
    subject: str = "未命名主题",
    output_path: Path | None = None,
    parts_dir: Path | None = None,
    required_sections: tuple[str, ...] = REQUIRED_ZEUS_SECTIONS,
) -> MergeResult:
    run_dir.mkdir(parents=True, exist_ok=True)
    output = output_path or run_dir / DEFAULT_OUTPUT_NAME
    manifest_path = run_dir / "03_zeus_intelligence_manifest.json"
    parts = discover_parts(run_dir, parts_dir)

    body_chunks: list[str] = []
    for part in parts:
        text = part.path.read_text(encoding="utf-8").strip()
        body_chunks.append(f"<!-- checkpoint-part: {part.path.name} -->\n\n{text}")

    merged_body = "\n\n---\n\n".join(body_chunks)
    missing_sections = _missing_sections(merged_body, required_sections)
    complete = bool(parts) and not missing_sections
    status_text = "complete" if complete else "incomplete"
    generated_at = datetime.now().replace(microsecond=0).isoformat()

    manifest = {
        "run_dir": str(run_dir),
        "parts_dir": str(parts_dir_for(run_dir, parts_dir)),
        "output_path": str(output),
        "generated_at": generated_at,
        "status": status_text,
        "part_count": len(parts),
        "missing_sections": list(missing_sections),
        "parts": [
            {
                "index": part.index,
                "path": str(part.path),
                "title": part.title,
                "char_count": part.char_count,
                "modified_at": part.modified_at,
            }
            for part in parts
        ],
    }

    header = (
        f"# Zeus 情报报告 — {subject}\n\n"
        f"> Checkpoint merge status: `{status_text}`  \n"
        f"> Checkpoint count: `{len(parts)}`  \n"
        f"> Generated at: `{generated_at}`\n\n"
    )
    if missing_sections:
        header += (
            "> 注意：当前合并结果仍缺少必需章节，不能标记为 Zeus 完整交付；"
            "应继续补采并再次合并。\n\n"
        )

    footer = _merge_audit_section(parts, missing_sections)
    output.write_text(header + (merged_body + "\n\n" if merged_body else "") + footer, encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return MergeResult(
        output_path=output,
        manifest_path=manifest_path,
        part_count=len(parts),
        missing_sections=tuple(missing_sections),
        complete=complete,
    )


def checkpoint_status(run_dir: Path, parts_dir: Path | None = None) -> dict[str, object]:
    parts = discover_parts(run_dir, parts_dir)
    return {
        "run_dir": str(run_dir),
        "parts_dir": str(parts_dir_for(run_dir, parts_dir)),
        "part_count": len(parts),
        "parts": [
            {
                "index": part.index,
                "path": str(part.path),
                "title": part.title,
                "char_count": part.char_count,
                "modified_at": part.modified_at,
            }
            for part in parts
        ],
    }


def _first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def _missing_sections(text: str, required_sections: tuple[str, ...]) -> list[str]:
    missing: list[str] = []
    for section in required_sections:
        if f"## {section}" not in text:
            missing.append(section)
    return missing


def _merge_audit_section(parts: list[CheckpointPart], missing_sections: list[str]) -> str:
    lines = [
        "## Checkpoint 合并与缺口",
        "",
        "| 序号 | 分段文件 | 标题 | 字符数 | 更新时间 |",
        "|---:|---|---|---:|---|",
    ]
    if parts:
        for part in parts:
            lines.append(
                f"| {part.index} | `{part.path.name}` | {part.title} | {part.char_count} | {part.modified_at} |"
            )
    else:
        lines.append("| 0 | N/A | 尚无 checkpoint 分段 | 0 | N/A |")
    lines.extend(["", "### 合并缺口"])
    if missing_sections:
        for section in missing_sections:
            lines.append(f"- 缺少必需章节：`## {section}`")
    else:
        lines.append("- 无必需章节缺口。")
    lines.append("")
    return "\n".join(lines)
