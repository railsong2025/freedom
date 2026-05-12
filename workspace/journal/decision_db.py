#!/usr/bin/env python3
"""Local SQLite decision journal for Buffett workflows."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any


DEFAULT_DB = Path(__file__).with_name("decisions.sqlite3")
_CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def today() -> str:
    return dt.date.today().isoformat()


def _contains_cjk(value: str) -> bool:
    return bool(_CJK_RE.search(value))


def _validate_english_text(field: str, value: str | None) -> None:
    if value and _contains_cjk(value):
        raise SystemExit(f"{field} must be English-only")


def _validate_english_json_tree(field: str, value: Any, path: str = "") -> None:
    location = f"{field}{path}"
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise SystemExit(f"{location} must use string JSON keys")
            if _contains_cjk(key):
                raise SystemExit(f"{location} contains non-English key: {key}")
            _validate_english_json_tree(field, child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_english_json_tree(field, child, f"{path}[{index}]")
    elif isinstance(value, str) and _contains_cjk(value):
        raise SystemExit(f"{location} must be English-only")


def _validate_source_doc_paths(value: Any) -> None:
    if not isinstance(value, list):
        raise SystemExit("source_doc_ids_json must be a JSON list")
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("source_doc_ids_json entries must be strings")
        if "://" in item or item.startswith("/") or ".." in Path(item).parts:
            raise SystemExit(f"source_doc_ids_json must contain local report paths only: {item}")
        if not item.startswith("report/") or not item.endswith(".md"):
            raise SystemExit(f"source_doc_ids_json path must be under report/ and end with .md: {item}")


def parse_json(
    value: str | None,
    default: Any,
    *,
    english_only: bool = False,
    require_object: bool = False,
    source_docs_only: bool = False,
) -> str:
    if not value:
        data = default
    else:
        try:
            data = json.loads(value)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON: {exc}") from exc
    if require_object and not isinstance(data, dict):
        raise SystemExit("JSON field must be an object with stable English keys")
    if english_only:
        _validate_english_json_tree("JSON field", data)
    if source_docs_only:
        _validate_source_doc_paths(data)
    try:
        return json.dumps(data, ensure_ascii=False)
    except TypeError as exc:
        raise SystemExit(f"Invalid JSON value: {exc}") from exc


def normalize_symbols(symbols: str | None) -> list[str]:
    if not symbols:
        return []
    reader = csv.reader([symbols])
    return sorted({item.strip().upper() for item in next(reader) if item.strip()})


def make_task_key(task_type: str, subject: str, symbols: str | None = None) -> str:
    normalized_type = task_type.strip().lower()
    normalized_subject = " ".join(subject.strip().lower().split())
    normalized_symbols = ",".join(normalize_symbols(symbols))
    raw = f"{normalized_type}|{normalized_subject}|{normalized_symbols}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{normalized_type}:{digest}"


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            decision_date TEXT NOT NULL,
            task_key TEXT NOT NULL,
            task_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            market TEXT,
            symbols_json TEXT NOT NULL DEFAULT '[]',
            action TEXT NOT NULL,
            strategy_type TEXT,
            recommendation_json TEXT NOT NULL DEFAULT '{}',
            thesis TEXT,
            roundtable_summary TEXT,
            roundtable_english TEXT,
            final_decision_english TEXT,
            expected_outcome_json TEXT NOT NULL DEFAULT '{}',
            source_doc_ids_json TEXT NOT NULL DEFAULT '[]',
            source_links_json TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'open',
            outcome_status TEXT NOT NULL DEFAULT 'unreviewed',
            actual_result_json TEXT NOT NULL DEFAULT '{}',
            review_summary TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_decisions_task_key_created
            ON decisions(task_key, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_decisions_task_type_subject
            ON decisions(task_type, subject, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_decisions_outcome_status
            ON decisions(outcome_status);
        """
    )
    existing_columns = {
        row["name"] for row in con.execute("PRAGMA table_info(decisions)").fetchall()
    }
    migrations = {
        "roundtable_english": "ALTER TABLE decisions ADD COLUMN roundtable_english TEXT",
        "final_decision_english": "ALTER TABLE decisions ADD COLUMN final_decision_english TEXT",
    }
    for column, statement in migrations.items():
        if column not in existing_columns:
            con.execute(statement)
    con.commit()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    for key in (
        "symbols_json",
        "recommendation_json",
        "expected_outcome_json",
        "source_doc_ids_json",
        "source_links_json",
        "actual_result_json",
    ):
        data[key.removesuffix("_json")] = json.loads(data.pop(key) or "null")
    return data


def print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_init(args: argparse.Namespace) -> None:
    with connect(args.db) as con:
        init_db(con)
    print(f"initialized: {args.db}")


def cmd_key(args: argparse.Namespace) -> None:
    print(make_task_key(args.task_type, args.subject, args.symbols))


def cmd_record(args: argparse.Namespace) -> None:
    _validate_english_text("thesis", args.thesis)
    _validate_english_text("roundtable_summary", args.roundtable_summary)
    _validate_english_text("roundtable_english", args.roundtable_english)
    _validate_english_text("final_decision_english", args.final_decision_english)
    with connect(args.db) as con:
        init_db(con)
        task_key = args.task_key or make_task_key(args.task_type, args.subject, args.symbols)
        symbols_json = json.dumps(normalize_symbols(args.symbols), ensure_ascii=False)
        cur = con.execute(
            """
            INSERT INTO decisions (
                created_at, updated_at, decision_date, task_key, task_type, subject,
                market, symbols_json, action, strategy_type, recommendation_json,
                thesis, roundtable_summary, roundtable_english, final_decision_english,
                expected_outcome_json, source_doc_ids_json, source_links_json, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_iso(),
                now_iso(),
                args.decision_date or today(),
                task_key,
                args.task_type,
                args.subject,
                args.market,
                symbols_json,
                args.action,
                args.strategy_type,
                parse_json(args.recommendation_json, {}, english_only=True, require_object=True),
                args.thesis,
                args.roundtable_summary,
                args.roundtable_english,
                args.final_decision_english,
                parse_json(args.expected_outcome_json, {}, english_only=True, require_object=True),
                parse_json(args.source_doc_ids_json, [], source_docs_only=True),
                parse_json(args.source_links_json, []),
                args.status,
            ),
        )
        con.commit()
        print_json({"id": cur.lastrowid, "task_key": task_key, "db": str(args.db)})


def cmd_last(args: argparse.Namespace) -> None:
    with connect(args.db) as con:
        init_db(con)
        task_key = args.task_key or make_task_key(args.task_type, args.subject, args.symbols)
        row = con.execute(
            "SELECT * FROM decisions WHERE task_key = ? ORDER BY created_at DESC LIMIT 1",
            (task_key,),
        ).fetchone()
    print_json(row_to_dict(row) if row else {"task_key": task_key, "decision": None})


def cmd_list(args: argparse.Namespace) -> None:
    with connect(args.db) as con:
        init_db(con)
        if args.task_key:
            rows = con.execute(
                "SELECT * FROM decisions WHERE task_key = ? ORDER BY created_at DESC LIMIT ?",
                (args.task_key, args.limit),
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?",
                (args.limit,),
            ).fetchall()
    print_json([row_to_dict(row) for row in rows])


def cmd_review(args: argparse.Namespace) -> None:
    _validate_english_text("review_summary", args.review_summary)
    with connect(args.db) as con:
        init_db(con)
        cur = con.execute(
            """
            UPDATE decisions
            SET updated_at = ?,
                status = ?,
                outcome_status = ?,
                actual_result_json = ?,
                review_summary = ?
            WHERE id = ?
            """,
            (
                now_iso(),
                args.status,
                args.outcome_status,
                parse_json(args.actual_result_json, {}, english_only=True, require_object=True),
                args.review_summary,
                args.id,
            ),
        )
        con.commit()
    if cur.rowcount == 0:
        raise SystemExit(f"decision id not found: {args.id}")
    print_json({"id": args.id, "updated": True})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(required=True)

    init = sub.add_parser("init", help="Create or migrate the local decision database.")
    init.set_defaults(func=cmd_init)

    key = sub.add_parser("key", help="Generate a stable same-task key.")
    key.add_argument("--task-type", required=True)
    key.add_argument("--subject", required=True)
    key.add_argument("--symbols")
    key.set_defaults(func=cmd_key)

    record = sub.add_parser("record", help="Record a Buffett decision.")
    record.add_argument("--task-key")
    record.add_argument("--task-type", required=True)
    record.add_argument("--subject", required=True)
    record.add_argument("--symbols")
    record.add_argument("--market")
    record.add_argument("--decision-date")
    record.add_argument("--action", required=True)
    record.add_argument("--strategy-type")
    record.add_argument("--recommendation-json")
    record.add_argument("--thesis")
    record.add_argument("--roundtable-summary")
    record.add_argument("--roundtable-english")
    record.add_argument("--final-decision-english")
    record.add_argument("--expected-outcome-json")
    record.add_argument("--source-doc-ids-json")
    record.add_argument("--source-links-json")
    record.add_argument("--status", default="open")
    record.set_defaults(func=cmd_record)

    last = sub.add_parser("last", help="Read the previous decision for the same task.")
    last.add_argument("--task-key")
    last.add_argument("--task-type", required=True)
    last.add_argument("--subject", required=True)
    last.add_argument("--symbols")
    last.set_defaults(func=cmd_last)

    list_cmd = sub.add_parser("list", help="List recent decisions.")
    list_cmd.add_argument("--task-key")
    list_cmd.add_argument("--limit", type=int, default=10)
    list_cmd.set_defaults(func=cmd_list)

    review = sub.add_parser("review", help="Attach an outcome review to a decision.")
    review.add_argument("--id", type=int, required=True)
    review.add_argument(
        "--outcome-status",
        choices=("success", "failure", "mixed", "unreviewed"),
        required=True,
    )
    review.add_argument("--actual-result-json")
    review.add_argument("--review-summary")
    review.add_argument("--status", default="reviewed")
    review.set_defaults(func=cmd_review)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
