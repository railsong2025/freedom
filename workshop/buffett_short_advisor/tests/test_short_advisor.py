import datetime as dt
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

import short_advisor


class ShortAdvisorTest(unittest.TestCase):
    def make_config(self, root: Path) -> short_advisor.AdvisorConfig:
        return short_advisor.AdvisorConfig(
            project_root=root,
            base_short_path=root / "base_short.md",
            timezone=ZoneInfo("Asia/Shanghai"),
            primary_market="US equities",
            report_slug="美股短线议",
            prompt_language="Chinese",
            execute_command=None,
            write_system_log=True,
            system_log_path=root / "workshop" / "buffett_short_advisor" / "system_log.md",
        )

    def test_run_once_reads_base_writes_prompt_and_does_not_touch_user_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            original_base = "## 操作记录\n\n- 用户已有交易记录\n"
            cfg.base_short_path.write_text(original_base, encoding="utf-8")
            result = short_advisor.run_once(
                cfg,
                dry_run=True,
                timestamp=dt.datetime(2026, 5, 6, 21, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")
            self.assertIn("短线交易建议系统手动触发", prompt)
            self.assertIn("base_short.md 快照", prompt)
            self.assertIn("- 用户已有交易记录", prompt)
            self.assertIn("US equities", prompt)
            self.assertIn("必须启动完整 Buffett 本地流程", prompt)
            self.assertIn("上一次同类 SQLite 决策", prompt)
            self.assertIn("用户手工交易记录", prompt)
            self.assertIn("Zeus 情报", prompt)
            self.assertNotIn("每 30 分钟", prompt)
            self.assertNotIn("定时触发", prompt)
            self.assertEqual(original_base, cfg.base_short_path.read_text(encoding="utf-8"))
            self.assertIn("系统运行日志", cfg.system_log_path.read_text(encoding="utf-8"))

    def test_missing_base_file_is_created_in_chinese(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            text = short_advisor.read_base_short(cfg)
            self.assertIn("Buffett 短线交易基础记录", text)
            self.assertIn("## 当前持仓", text)
            self.assertIn("## 操作记录", text)
            self.assertIn("每次手动运行", text)
            self.assertNotIn("定时窗口", text)

    def test_cli_accepts_run_and_run_once_alias(self):
        parser = short_advisor.build_parser()
        self.assertEqual(parser.parse_args(["run", "--dry-run"]).command, "run")
        self.assertEqual(parser.parse_args(["run-once", "--dry-run"]).command, "run-once")

    def test_live_mode_requires_execute_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg.base_short_path.write_text("## 操作记录\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                short_advisor.run_once(
                    cfg,
                    dry_run=False,
                    timestamp=dt.datetime(2026, 5, 6, 21, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
                )


if __name__ == "__main__":
    unittest.main()
