"""Tests for the local decision journal storage contract."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from journal import decision_db  # noqa: E402


class TestDecisionDbContracts(unittest.TestCase):
    def make_args(self, db: Path, **overrides):
        data = {
            "db": db,
            "task_key": None,
            "task_type": "portfolio_review",
            "subject": "us_equity_portfolio",
            "symbols": "MSFT,NVDA",
            "market": "US equities",
            "decision_date": "2026-05-10",
            "action": "NO_TRADE",
            "strategy_type": "swing",
            "recommendation_json": '{"action":"NO_TRADE"}',
            "thesis": "No trade until evidence improves.",
            "roundtable_summary": "Roundtable rejected weak evidence.",
            "roundtable_english": "Zeus, Poseidon, Hades, and Buffett discussed evidence gaps.",
            "final_decision_english": "No current buy or sell action.",
            "expected_outcome_json": '{"base_case":"capital preserved"}',
            "source_doc_ids_json": '["report/2026-05-10_test/07_final_decision.md"]',
            "source_links_json": '[]',
            "status": "open",
        }
        data.update(overrides)
        return argparse.Namespace(**data)

    def test_record_accepts_english_fields_and_local_report_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "decisions.sqlite3"
            decision_db.cmd_record(self.make_args(db))
            with sqlite3.connect(db) as con:
                row = con.execute("SELECT recommendation_json, source_doc_ids_json FROM decisions").fetchone()
            self.assertEqual({"action": "NO_TRADE"}, json.loads(row[0]))
            self.assertEqual(["report/2026-05-10_test/07_final_decision.md"], json.loads(row[1]))

    def test_record_rejects_chinese_in_english_text_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "decisions.sqlite3"
            with self.assertRaises(SystemExit):
                decision_db.cmd_record(self.make_args(db, thesis="本次不交易"))

    def test_record_rejects_chinese_json_and_external_doc_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "decisions.sqlite3"
            with self.assertRaises(SystemExit):
                decision_db.cmd_record(self.make_args(db, recommendation_json='{"action":"买入"}'))
            with self.assertRaises(SystemExit):
                decision_db.cmd_record(self.make_args(db, source_doc_ids_json='["https://example.com/doc"]'))

    def test_review_rejects_non_english_actual_result(self):
        args = argparse.Namespace(
            db=Path(":memory:"),
            id=1,
            status="reviewed",
            outcome_status="mixed",
            actual_result_json='{"summary":"失败"}',
            review_summary="Mixed result.",
        )
        with self.assertRaises(SystemExit):
            decision_db.cmd_review(args)


if __name__ == "__main__":
    unittest.main()
