"""Subprocess tests for project CLI contracts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


PORTFOLIO_TEXT = """# Test Portfolio

## record 1操作后持仓

- 微软：2 股，成本 100 美元

## 可用资金

- 10000 美元
"""


class TestCliContracts(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def with_portfolio(self):
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "portfolio.md"
        path.write_text(PORTFOLIO_TEXT, encoding="utf-8")
        return tmp, path

    def test_analysis_pnl_accepts_portfolio_file_and_colon_prices(self):
        tmp, path = self.with_portfolio()
        with tmp:
            result = self.run_cli(
                "workspace/analysis/cli.py",
                "pnl",
                "--portfolio-file",
                str(path),
                "--prices",
                "MSFT:110",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["positions"][0]["symbol"], "MSFT")
        self.assertAlmostEqual(payload["total_cost_basis"], 200.0)

    def test_analysis_post_trade_accepts_legacy_base_short_alias(self):
        tmp, path = self.with_portfolio()
        with tmp:
            result = self.run_cli(
                "workspace/analysis/cli.py",
                "post-trade",
                "--base-short",
                str(path),
                "--prices",
                "MSFT=110",
                "--trades",
                "MSFT:BUY:1:110",
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["total_fees"], 5.0)

    def test_hades_portfolio_file_supported_for_all_portfolio_commands(self):
        tmp, path = self.with_portfolio()
        commands = [
            (
                "audit-pnl",
                ["--portfolio-file", str(path), "--prices", "MSFT=110"],
            ),
            (
                "compliance",
                [
                    "--portfolio-file",
                    str(path),
                    "--prices",
                    "MSFT=110",
                    "--trades",
                    "MSFT:BUY:1:110",
                    "--stops",
                    "MSFT=105",
                    "--equity",
                    "10000",
                ],
            ),
            (
                "stress-test",
                ["--portfolio-file", str(path), "--prices", "MSFT=110"],
            ),
            (
                "audit-post-trade",
                [
                    "--portfolio-file",
                    str(path),
                    "--prices",
                    "MSFT=110",
                    "--trades",
                    "MSFT:BUY:1:110",
                ],
            ),
        ]
        with tmp:
            for command, args in commands:
                result = self.run_cli("workspace/verification/cli.py", command, *args)
                self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
                self.assertTrue(result.stdout.strip(), command)


if __name__ == "__main__":
    unittest.main()
