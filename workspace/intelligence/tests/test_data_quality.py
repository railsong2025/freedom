"""Tests for data_quality module."""

import sys
import unittest
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from intelligence.data_quality import (
    cross_source_agreement,
    detect_missing_bars,
    detect_outliers,
    detect_staleness,
    validate_data_quality,
)


@dataclass
class FakeBar:
    symbol: str
    date: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    source: str = "test"
    raw: dict = None

    def __post_init__(self):
        if self.raw is None:
            self.raw = {}


@dataclass
class FakeResult:
    symbol: str
    bars: list
    source: str | None
    attempts: list

    @property
    def ok(self):
        return bool(self.bars)


class TestDetectStaleness(unittest.TestCase):
    def test_fresh_data(self):
        bars = [FakeBar("TEST", date.today().isoformat(), 100, 101, 99, 100, 1000)]
        is_stale, days = detect_staleness(bars, max_staleness_days=2)
        self.assertFalse(is_stale)
        self.assertEqual(days, 0)

    def test_stale_data(self):
        old_date = (date.today() - __import__("datetime").timedelta(days=5)).isoformat()
        bars = [FakeBar("TEST", old_date, 100, 101, 99, 100, 1000)]
        is_stale, days = detect_staleness(bars, max_staleness_days=2)
        self.assertTrue(is_stale)
        self.assertEqual(days, 5)

    def test_empty_bars(self):
        is_stale, days = detect_staleness([], max_staleness_days=2)
        self.assertTrue(is_stale)
        self.assertIsNone(days)


class TestDetectMissingBars(unittest.TestCase):
    def test_no_missing(self):
        bars = [
            FakeBar("TEST", "2026-04-06", 100, 101, 99, 100, 1000),
            FakeBar("TEST", "2026-04-07", 101, 102, 100, 101, 1100),
        ]
        missing = detect_missing_bars(bars, date(2026, 4, 6), date(2026, 4, 7))
        # 2026-04-06 is Sunday, 04-07 is Monday -> only Monday is a trading day
        self.assertEqual(len(missing), 0)

    def test_with_missing(self):
        bars = [
            FakeBar("TEST", "2026-04-06", 100, 101, 99, 100, 1000),
            # Missing 04-08
            FakeBar("TEST", "2026-04-09", 102, 103, 101, 102, 1200),
        ]
        missing = detect_missing_bars(bars, date(2026, 4, 6), date(2026, 4, 9), exclude_weekends=True)
        # Trading days: 04-06 (Sun), 04-07 (Mon), 04-08 (Tue), 04-09 (Wed)
        # With exclude_weekends: 04-07, 04-08, 04-09
        self.assertIn("2026-04-08", missing)

    def test_empty_bars(self):
        missing = detect_missing_bars([], date(2026, 4, 6), date(2026, 4, 10))
        self.assertEqual(len(missing), 0)


class TestDetectOutliers(unittest.TestCase):
    def test_no_outliers(self):
        bars = [FakeBar("TEST", f"2026-04-{i+1:02d}", 100+i, 101+i, 99+i, 100+i, 1000) for i in range(20)]
        outliers = detect_outliers(bars, z_threshold=4.0)
        self.assertEqual(len(outliers), 0)

    def test_with_outlier(self):
        bars = [FakeBar("TEST", f"2026-04-{i+1:02d}", 100, 101, 99, 100, 1000) for i in range(20)]
        # Add a massive jump
        bars.append(FakeBar("TEST", "2026-04-21", 200, 201, 199, 200, 5000))
        outliers = detect_outliers(bars, z_threshold=3.0)
        self.assertGreater(len(outliers), 0)

    def test_too_few_bars(self):
        bars = [FakeBar("TEST", "2026-04-01", 100, 101, 99, 100, 1000)]
        outliers = detect_outliers(bars, z_threshold=3.0)
        self.assertEqual(len(outliers), 0)


class TestCrossSourceAgreement(unittest.TestCase):
    def test_agreeing_sources(self):
        r1 = FakeResult("MU", [FakeBar("MU", "2026-05-08", 130, 131, 129, 130.5, 1000)], "source1", [])
        r2 = FakeResult("MU", [FakeBar("MU", "2026-05-08", 130, 131, 129, 130.0, 1000)], "source2", [])
        score = cross_source_agreement([r1, r2], tolerance_pct=1.0)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.9)

    def test_disagreeing_sources(self):
        r1 = FakeResult("MU", [FakeBar("MU", "2026-05-08", 130, 131, 129, 130.0, 1000)], "source1", [])
        r2 = FakeResult("MU", [FakeBar("MU", "2026-05-08", 140, 141, 139, 140.0, 1000)], "source2", [])
        score = cross_source_agreement([r1, r2], tolerance_pct=1.0)
        self.assertIsNotNone(score)
        self.assertLess(score, 0.5)

    def test_single_source(self):
        r1 = FakeResult("MU", [FakeBar("MU", "2026-05-08", 130, 131, 129, 130.0, 1000)], "source1", [])
        self.assertIsNone(cross_source_agreement([r1]))


class TestValidateDataQuality(unittest.TestCase):
    def test_good_data(self):
        today = date.today()
        bars = [FakeBar("TEST", (today - __import__("datetime").timedelta(days=i)).isoformat(),
                         100, 101, 99, 100 + i * 0.1, 1000) for i in range(20)]
        report = validate_data_quality(bars, today - __import__("datetime").timedelta(days=20), today, "TEST")
        self.assertGreater(report.quality_score, 0.5)

    def test_stale_data(self):
        old = date(2026, 1, 1)
        bars = [FakeBar("TEST", old.isoformat(), 100, 101, 99, 100, 1000)]
        report = validate_data_quality(bars, old, old, "TEST")
        self.assertTrue(report.is_stale)
        self.assertLess(report.quality_score, 0.8)


if __name__ == "__main__":
    unittest.main()