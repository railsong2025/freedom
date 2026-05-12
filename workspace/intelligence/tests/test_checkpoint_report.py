"""Tests for Zeus checkpointed report assembly."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from intelligence.checkpoint_report import (  # noqa: E402
    DEFAULT_PARTS_DIRNAME,
    checkpoint_status,
    merge_checkpoints,
)


class TestCheckpointReport(unittest.TestCase):
    def test_merge_checkpoints_writes_output_manifest_and_missing_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            parts_dir = run_dir / DEFAULT_PARTS_DIRNAME
            parts_dir.mkdir()
            (parts_dir / "010_scope.md").write_text(
                "## 输入与任务范围\n\n范围已确认。\n\n## 情报问题清单\n\n| 情报问题 | 覆盖状态 |\n|---|---|\n",
                encoding="utf-8",
            )

            result = merge_checkpoints(run_dir, subject="AI chain")
            output = result.output_path.read_text(encoding="utf-8")
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

            self.assertFalse(result.complete)
            self.assertEqual(1, result.part_count)
            self.assertIn("Checkpoint merge status: `incomplete`", output)
            self.assertIn("010_scope.md", output)
            self.assertIn("缺少必需章节", output)
            self.assertEqual("incomplete", manifest["status"])

    def test_merge_complete_when_required_sections_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            parts_dir = run_dir / DEFAULT_PARTS_DIRNAME
            parts_dir.mkdir()
            sections = [
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
            ]
            (parts_dir / "010_full.md").write_text(
                "\n\n".join(f"## {section}\n\n测试内容。" for section in sections),
                encoding="utf-8",
            )

            result = merge_checkpoints(run_dir, subject="complete")

            self.assertTrue(result.complete)
            self.assertEqual((), result.missing_sections)
            self.assertIn("Checkpoint merge status: `complete`", result.output_path.read_text(encoding="utf-8"))

    def test_checkpoint_status_lists_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            parts_dir = run_dir / DEFAULT_PARTS_DIRNAME
            parts_dir.mkdir()
            (parts_dir / "020_events.md").write_text("## 新闻、公告、文件与事件\n\n内容。", encoding="utf-8")

            status = checkpoint_status(run_dir)

            self.assertEqual(1, status["part_count"])
            self.assertEqual("新闻、公告、文件与事件", status["parts"][0]["title"])


if __name__ == "__main__":
    unittest.main()
