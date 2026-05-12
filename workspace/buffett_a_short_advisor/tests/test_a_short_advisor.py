import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

import a_short_advisor


class AShortAdvisorTest(unittest.TestCase):
    def make_config(self, root: Path) -> a_short_advisor.AdvisorConfig:
        return a_short_advisor.AdvisorConfig(
            project_root=root,
            base_short_path=root / "workspace" / "buffett_a_short_advisor" / "base_short_A.md",
            timezone=ZoneInfo("Asia/Shanghai"),
            primary_market="China A-shares",
            report_slug="A股短线议",
            prompt_language="Chinese",
            execute_command=None,
            write_system_log=True,
            system_log_path=root / "workspace" / "buffett_a_short_advisor" / "system_log.md",
        )

    def test_run_once_reads_base_writes_prompt_and_does_not_touch_user_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg.base_short_path.parent.mkdir(parents=True)
            original_base = "## 操作记录\n\n- 用户已有A股交易记录\n"
            cfg.base_short_path.write_text(original_base, encoding="utf-8")
            result = a_short_advisor.run_once(
                cfg,
                dry_run=True,
                timestamp=dt.datetime(2026, 5, 6, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")
            self.assertIn("A 股短线交易建议系统手动触发", prompt)
            self.assertIn("唯一共享源文件", prompt)
            self.assertIn(str(cfg.base_short_path), prompt)
            self.assertIn("- 用户已有A股交易记录", prompt)
            self.assertIn("China A-shares", prompt)
            self.assertIn("上一次同类 SQLite 决策", prompt)
            self.assertIn("用户手工 A 股交易记录", prompt)
            self.assertIn("100 股一手", prompt)
            self.assertIn("只读审计快照", prompt)
            self.assertIn("午间休市", prompt)
            self.assertIn("T+1", prompt)
            self.assertNotIn("每 30 分钟", prompt)
            self.assertNotIn("定时触发", prompt)
            self.assertEqual(original_base, cfg.base_short_path.read_text(encoding="utf-8"))
            self.assertIn("系统运行日志", cfg.system_log_path.read_text(encoding="utf-8"))
            run_json = json.loads((Path(result["run_dir"]) / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(str(cfg.base_short_path), run_json["shared_base_short_path"])

    def test_missing_base_file_is_created_in_chinese(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self.make_config(Path(tmp))
            text = a_short_advisor.read_base_short(cfg)
            self.assertIn("Buffett A股短线交易基础记录", text)
            self.assertIn("## 当前A股持仓", text)
            self.assertIn("## 操作记录", text)
            self.assertIn("每次手动运行", text)
            self.assertNotIn("触发频率", text)

    def test_cli_accepts_run_and_run_once_alias(self):
        parser = a_short_advisor.build_parser()
        self.assertEqual(parser.parse_args(["run", "--dry-run"]).command, "run")
        self.assertEqual(parser.parse_args(["run-once", "--dry-run"]).command, "run-once")

    def test_live_mode_requires_execute_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg.base_short_path.parent.mkdir(parents=True)
            cfg.base_short_path.write_text("## 操作记录\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                a_short_advisor.run_once(
                    cfg,
                    dry_run=False,
                    timestamp=dt.datetime(2026, 5, 6, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
                )


if __name__ == "__main__":
    unittest.main()
