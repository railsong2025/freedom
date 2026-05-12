import datetime as dt
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import market_data
import replay_backtest
import research_advisor


class ResearchAdvisorTest(unittest.TestCase):
    def make_config(self, root: Path) -> research_advisor.ResearchConfig:
        return research_advisor.ResearchConfig(
            project_root=root,
            base_short_path=root / "base_short.md",
            timezone=ZoneInfo("Asia/Shanghai"),
            primary_market="US equities",
            task_type="portfolio_review",
            subject="us_equity_portfolio",
            report_slug=research_advisor.DEFAULT_REPORT_SLUG,
            prompt_language="Chinese",
            trade_deadline_beijing="00:00",
            per_trade_fee_usd=5,
            trading_profile="swing_trading",
            short_term_primary_horizon="swing_days_to_weeks",
            short_term_single_trade_risk_pct=2.0,
            strong_cycle_initial_position_pct_min=5.0,
            strong_cycle_initial_position_pct_max=8.0,
            short_term_stop_loss_pct_min=3.0,
            short_term_stop_loss_pct_max=5.0,
            strong_cycle_focus=tuple(research_advisor.DEFAULT_CONFIG["strong_cycle_focus"]),
            sqlite_write_mode="disabled",
            market_data_timeout_seconds=8.0,
            market_data_cache_dir=root / "workspace" / "buffett_research_advisor" / "data" / "market_data",
            market_data_aktools_api_url=None,
            market_data_http_api_url=None,
            market_data_sources=("financeBusiness_mcp",),
            execute_command=None,
            execute_timeout_seconds=1800,
            write_system_log=True,
            system_log_path=root / "workspace" / "buffett_research_advisor" / "system_log.md",
        )

    def test_report_dir_uses_record_timestamp_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            report_dir = research_advisor.report_dir_for(
                dt.datetime(2026, 5, 10, 22, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
                cfg,
            )
            self.assertEqual("record_20260510_220000_001", report_dir.name)

    def test_report_dir_increments_record_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            (root / "report" / "record_20260509_213000_001").mkdir(parents=True)
            report_dir = research_advisor.report_dir_for(
                dt.datetime(2026, 5, 10, 22, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
                cfg,
            )
            self.assertEqual("record_20260510_220000_002", report_dir.name)

    def test_report_dir_ignores_deprecated_custom_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            report_dir = research_advisor.report_dir_for(
                dt.datetime(2026, 5, 10, 22, 0, tzinfo=ZoneInfo("Asia/Shanghai")),
                cfg,
                "美股/强周期 复盘",
            )
            self.assertEqual("record_20260510_220000_001", report_dir.name)

    def test_special_watch_forces_intc_even_when_config_omits_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = replace(self.make_config(root), strong_cycle_focus=("MU",))
            timestamp = dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai"))

            prompt = research_advisor.build_prompt("# base\n", timestamp, cfg)
            symbols = research_advisor.prefetch_symbols_from_base("", cfg)

            self.assertIn("本轮配置优先跟踪 ticker：MU、AMD、FLEX、INTC", prompt)
            self.assertIn("特别观察范围（逐票完整核查", prompt)
            self.assertIn("INTC（英特尔/晶圆制造、AI PC与服务器CPU、美国半导体政策）", prompt)
            self.assertIn("INTC（英特尔）必须专项检查", prompt)
            self.assertIn("INTC", symbols)

    def test_previous_history_prefers_local_record_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            older = root / "report" / "2026-05-09_美股旧格式"
            older.mkdir(parents=True)
            (older / "00_metadata.md").write_text("| task_type | `portfolio_review` |\n| subject | `us_equity_portfolio` |\n", encoding="utf-8")
            (older / "07_final_decision.md").write_text("# old\n", encoding="utf-8")
            record = root / "report" / "record_20260510_220000_001"
            record.mkdir()
            (record / "00_metadata.md").write_text(
                "| task_type | `portfolio_review` |\n"
                "| subject | `us_equity_portfolio` |\n"
                "| task_key | `portfolio_review:993c7d93e383` |\n",
                encoding="utf-8",
            )
            (record / "01_buffett_review.md").write_text("# review\n", encoding="utf-8")
            (record / "02_buffett_plan.md").write_text("# plan\n", encoding="utf-8")
            (record / "03_zeus_intelligence.md").write_text("# zeus\n", encoding="utf-8")
            (record / "04_poseidon_research.md").write_text("# poseidon\n", encoding="utf-8")
            (record / "05_hades_verification.md").write_text("# hades\n", encoding="utf-8")
            (record / "06_roundtable.md").write_text("# roundtable\n", encoding="utf-8")
            (record / "07_final_decision.md").write_text("# final\n本次不买入、不卖出\n", encoding="utf-8")
            (record / "local_result_snapshot.json").write_text(
                json.dumps({"sqlite_write_status": "skipped_by_disabled_policy"}, ensure_ascii=False),
                encoding="utf-8",
            )

            history = research_advisor.read_previous_history(cfg)

            self.assertEqual("found_local_record", history["status"])
            self.assertEqual(str(record), history["record"]["path"])
            self.assertEqual("record", history["record"]["folder_format"])
            self.assertEqual(1, history["records_scanned"])
            self.assertEqual(1, history["record_format_records_scanned"])

    def test_previous_history_rejects_noncompliant_record_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            bad_record = root / "report" / "record_20260511_151843_001"
            bad_record.mkdir(parents=True)
            for name in research_advisor.REQUIRED_REPORT_FILES:
                (bad_record / name).write_text(f"# {name}\n", encoding="utf-8")
            (bad_record / "db_record.json").write_text("{}", encoding="utf-8")

            history = research_advisor.read_previous_history(cfg)

            self.assertEqual("no_local_record_found", history["status"])
            self.assertIsNone(history["record"])

    def test_prefetch_symbols_ignore_commented_operation_template_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            base_short = (
                "## 当前持仓\n\n"
                "- 可口可乐：30 股，成本 77.52 美元\n"
                "- 微软：18 股，成本 506.96 美元\n"
                "- 英伟达：7 股，成本 184.23 美元\n"
                "<!--\n"
                "### YYYY-MM-DD HH:MM 北京时间 - 买入/卖出\n"
                "- 标的：\n"
                "-->\n"
                "希望额外关注 MU、AMD、NATP、FLEX\n"
            )

            symbols = research_advisor.prefetch_symbols_from_base(base_short, cfg)

            self.assertIn("MU", symbols)
            self.assertIn("AMD", symbols)
            self.assertIn("NATP", symbols)
            self.assertNotIn("YYYY", symbols)
            self.assertNotIn("DD", symbols)
            self.assertNotIn("HH", symbols)
            self.assertNotIn("MM", symbols)

    def test_research_start_reads_base_writes_prompt_and_does_not_touch_operations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            original_base = (
                "# Buffett 短线交易基础记录\n\n"
                "## 当前持仓\n\n"
                "- 微软：53 股，成本 447.49 美元\n"
                "- 英伟达：6 股，成本 178.57 美元\n\n"
                "## 可用资金\n\n"
                "- 78,000 港元，可投资港股或美股\n\n"
                "## 操作记录\n\n"
                "- 2026-05-07 买入 NVDA 1 股\n"
            )
            cfg.base_short_path.write_text(original_base, encoding="utf-8")
            result = research_advisor.run_research(
                cfg,
                dry_run=True,
                timestamp=dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")

            self.assertIn("用户输入：buffett开始", prompt)
            self.assertIn("美股专用完整投研", prompt)
            self.assertIn("本轮建议 report 目录：", prompt)
            self.assertIn("record_20260508_214500_001", prompt)
            self.assertIn("复盘主索引：本地 report 文件夹", prompt)
            self.assertIn("不得把 SQLite 当作复盘主来源", prompt)
            self.assertIn("美股强周期波段交易 overlay", prompt)
            self.assertIn("所有策略遵从波段交易策略", prompt)
            self.assertIn("数日至数周的波段交易", prompt)
            self.assertIn("存储/HBM、半导体、AI 硬件", prompt)
            self.assertIn("技术面、量价关系、市场热点和严格止损", prompt)
            self.assertIn("波段策略 profile：`swing_trading`", prompt)
            self.assertIn("主要持有周期：`swing_days_to_weeks`", prompt)
            self.assertIn("本轮执行截止时间为北京时间 `2026-05-09 00:00:00 CST`", prompt)
            self.assertIn("只有最终决策生成或复核时间晚于该具体截止时间", prompt)
            self.assertIn("强周期/AI 产业链上中下游重点候选池", prompt)
            self.assertIn("AI应用/云CAPEX/数据基础设施（MSFT、AMZN、GOOGL、META、ORCL、PLTR、SNOW、DDOG）", prompt)
            self.assertIn("GPU/ASIC/AI加速器（NVDA、AMD、AVGO、MRVL、ARM）", prompt)
            self.assertIn("存储/HBM/存储设备（MU、WDC、STX）", prompt)
            self.assertIn("AI服务器/ODM/EMS（DELL、HPE、SMCI、FLEX、JBL、CLS、SANM）", prompt)
            self.assertIn("数据中心电力/散热/工程（VRT、ETN、PWR、GEV）", prompt)
            self.assertIn("PCB/CCL/电子制造（TTMI、SANM、FLEX、JBL）", prompt)
            self.assertIn("安全/数据基础设施（PANW、CRWD、NET、SNOW、DDOG）", prompt)
            self.assertIn("链条ETF/篮子（SMH、SOXX、QQQ、IGV、AIQ）", prompt)
            self.assertIn("本轮配置优先跟踪 ticker：MSFT、AMZN、GOOGL、META", prompt)
            self.assertIn("特别观察范围（逐票完整核查", prompt)
            self.assertIn("INTC（英特尔/晶圆制造、AI PC与服务器CPU、美国半导体政策）", prompt)
            self.assertIn("INTC（英特尔）必须专项检查", prompt)
            self.assertIn("Poseidon 候选动作对照表、Hades 裁决和 no-trade proof", prompt)
            self.assertIn("指数基准与可交易代理（必须分开处理）", prompt)
            self.assertIn("StockIndexList(IXIC)", prompt)
            self.assertIn("StockIndexList(SPX/GSPC/INX/SP500)", prompt)
            self.assertIn("指数本身不可进入 `本次当前操作`", prompt)
            self.assertIn("当前 BUY/SELL 只能落到 SPY/QQQ", prompt)
            self.assertIn("先对全链条候选做轻量广覆盖初筛", prompt)
            self.assertIn("筛出 Top 8-12 做深度波段计划", prompt)
            self.assertIn("不得要求 50+ 个 ticker 全部写成长篇个股深度报告", prompt)
            self.assertIn("行情数据源配置：`financeBusiness_mcp`", prompt)
            self.assertIn("Buffett 工作流结构化行情只允许 financeBusiness MCP", prompt)
            self.assertIn("market_data_aktools_api_url", (Path(result["run_dir"]) / "run.json").read_text(encoding="utf-8"))
            self.assertIn("本轮 financeBusiness 行情策略不生成本地行情 manifest", prompt)
            self.assertIn("不得假装读取不存在的 manifest", prompt)
            self.assertIn("本轮无 financeBusiness 预取数据包", prompt)
            self.assertIn("禁止使用本地 `market_data.py`", prompt)
            self.assertIn("不得作为这些结构化行情字段的 fallback", prompt)
            self.assertIn("新闻、公告、SEC/IR、宏观、政策、关键人物讲话、PDF 和反证必须使用 aiwebsearch", prompt)
            self.assertIn("单笔最大亏损约账户权益 2%", prompt)
            self.assertIn("强周期单票初始仓位通常为组合权益 5%-8%", prompt)
            self.assertIn("默认硬止损距离通常为入场价下方 3%-5%", prompt)
            self.assertIn("动能突破", prompt)
            self.assertIn("回撤承接", prompt)
            self.assertIn("超跌反弹", prompt)
            self.assertIn("第一止盈", prompt)
            self.assertIn("第二止盈", prompt)
            self.assertIn("移动止损", prompt)
            self.assertIn("最长持有期", prompt)
            self.assertIn("微软：53 股", prompt)
            self.assertIn("英伟达：6 股", prompt)
            self.assertIn("2026-05-07 买入 NVDA 1 股", prompt)
            self.assertIn("decision_db.py last --task-type portfolio_review --subject us_equity_portfolio", prompt)
            self.assertIn("只分析美股和美股 ETF", prompt)
            self.assertIn("不得生成港股或 A 股交易建议", prompt)
            self.assertIn("美股板块分析和 AI 产业链机会扫描", prompt)
            self.assertIn("AI 产业链机会漏斗", prompt)
            self.assertIn("AI 应用", prompt)
            self.assertIn("云 CAPEX", prompt)
            self.assertIn("GPU/ASIC", prompt)
            self.assertIn("存储/HBM", prompt)
            self.assertIn("光模块/网络", prompt)
            self.assertIn("数据中心/电力/散热", prompt)
            self.assertIn("核心候选 / 战术候选 / 观察名单 / 回避或否决", prompt)
            self.assertIn("当前持仓以外的新机会", prompt)
            self.assertIn("当前总盈亏和个股盈亏", prompt)
            self.assertIn("未实现盈亏金额", prompt)
            self.assertIn("总未实现盈亏率", prompt)
            self.assertIn("当前盈亏与仓位含义", prompt)
            self.assertIn("当前持仓盈亏复盘", prompt)
            self.assertIn("交易后预计盈亏", prompt)
            self.assertIn("错过机会账本", prompt)
            self.assertIn("Buffett 自我反思", prompt)
            self.assertIn("Buffett 必须根据最新数据和历史决策反思", prompt)
            self.assertIn("依据的最新数据", prompt)
            self.assertIn("依据的历史决策", prompt)
            self.assertIn("关键遗漏与分析错误复盘", prompt)
            self.assertIn("未关注到关键人物讲话", prompt)
            self.assertIn("关键事件未捕捉", prompt)
            self.assertIn("关键分析错误", prompt)
            self.assertIn("基于反思的新策略", prompt)
            self.assertIn("不能把责任推给 Zeus/Poseidon/Hades", prompt)
            self.assertIn("关键人物讲话补查", prompt)
            self.assertIn("上一轮未覆盖/无当时 veto", prompt)
            self.assertIn("不得补造当时建议或 veto 理由", prompt)
            self.assertIn("动能突破不是自动追高", prompt)
            self.assertIn("starter 不是终局仓位", prompt)
            self.assertIn("仓位升级阶梯", prompt)
            self.assertIn("确认加仓", prompt)
            self.assertIn("利润滚动", prompt)
            self.assertIn("大幅盈利路径", prompt)
            self.assertIn("批准当前交易", prompt)
            self.assertIn("批准小仓 starter", prompt)
            self.assertIn("workspace/analysis/cli.py swing-verdict", prompt)
            self.assertIn("current_trade", prompt)
            self.assertIn("small_starter", prompt)
            self.assertIn("hard_veto", prompt)
            self.assertIn("ETF/basket fallback", prompt)
            self.assertIn("no-trade proof", prompt)
            self.assertIn("批准加仓", prompt)
            self.assertIn("预计已实现盈亏", prompt)
            self.assertIn("交易后剩余持仓", prompt)
            self.assertIn("已实现+未实现合计盈亏", prompt)
            self.assertIn("平均成本法估算", prompt)
            self.assertIn("亏损股是否需要止损/减仓", prompt)
            self.assertIn("补仓摊低成本的陷阱", prompt)
            self.assertIn("Buffett 调度与验收要求", prompt)
            self.assertIn("派工合同", prompt)
            self.assertIn("验收失败条件", prompt)
            self.assertIn("关键人物言论与市场影响", prompt)
            self.assertIn("Fed/FOMC", prompt)
            self.assertIn("讲话前后可观察市场反应", prompt)
            self.assertIn("关键人物言论采纳与投资含义", prompt)
            self.assertIn("关键人物言论审计", prompt)
            self.assertIn("来源分层与覆盖度", prompt)
            self.assertIn("美股板块与行业代理覆盖", prompt)
            self.assertIn("上游报告完整性审计", prompt)
            self.assertIn("事实 -> 影响链条 -> 受益/受损对象 -> 置信度 -> 反证", prompt)
            self.assertIn("未来 1-5 个交易日和 2-6 周趋势预测", prompt)
            self.assertIn("强周期波段交易计划", prompt)
            self.assertIn("波段风控审计", prompt)
            self.assertIn("入场类型（动能突破/回撤承接/超跌反弹/止损卖出/止盈卖出/移动止损）", prompt)
            self.assertIn("mcp__financeBusiness__StockCurrentMarket", prompt)
            self.assertIn("mcp__financeBusiness__StockMarketList", prompt)
            self.assertIn("当前价、收盘、昨收、开盘、最高、最低、涨跌幅、涨跌额、振幅、成交量、成交额、量比、换手率、行情来源", prompt)
            self.assertIn("latestPri/lastestpri -> 当前价", prompt)
            self.assertIn("yesEndPri/formpri 或上一条 endPri -> 昨收", prompt)
            self.assertIn("volumeRatio -> 量比", prompt)
            self.assertIn("turnoverRate -> 换手率", prompt)
            self.assertIn("ZEUS_FIELD_FAILURE", prompt)
            self.assertIn("当前交易策略字段包", prompt)
            self.assertIn("ma5", prompt)
            self.assertIn("price_vs_ma20", prompt)
            self.assertIn("volatility_20d", prompt)
            self.assertIn("relative_strength_spy", prompt)
            self.assertIn("entry_trigger_price", prompt)
            self.assertIn("field_source_map", prompt)
            self.assertIn("usable_for_current_trade", prompt)
            self.assertIn("mcp__aiwebsearch__GoogleSearch", prompt)
            self.assertIn("mcp__aiwebsearch__searchJumps", prompt)
            self.assertIn("不要传纯字符串数组", prompt)
            self.assertIn("financebusiness_reconciliation_status", prompt)
            self.assertIn("financeBusiness 内部核验", prompt)
            self.assertIn("禁止泛泛分析", prompt)
            self.assertIn("USD 5", prompt)
            self.assertIn("买入现金占用 = 限价 * 整股数量 + 5", prompt)
            self.assertIn("卖出净回收 = 限价 * 整股数量 - 5", prompt)
            self.assertIn("不支持碎股交易", prompt)
            self.assertIn("本次当前操作", prompt)
            self.assertIn("不在当前本次范围要操作的股票", prompt)
            self.assertIn("下一次建议启动分析时间", prompt)
            self.assertIn("本轮执行截止时间", prompt)
            self.assertEqual(original_base, cfg.base_short_path.read_text(encoding="utf-8"))

            run_json = json.loads((Path(result["run_dir"]) / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("buffett开始", run_json["trigger_phrase"])
            self.assertTrue(run_json["suggested_report_dir"].endswith("record_20260508_214500_001"))
            self.assertEqual("local_report_folder", run_json["previous_history"]["history_source"])
            self.assertEqual("US equities", run_json["primary_market"])
            self.assertEqual("us_equity_portfolio", run_json["subject"])
            self.assertEqual(5, run_json["per_trade_fee_usd"])
            self.assertEqual("2026-05-09T00:00:00+08:00", run_json["trade_deadline_beijing_at"])
            self.assertEqual("swing_trading", run_json["trading_profile"])
            self.assertEqual("swing_days_to_weeks", run_json["short_term_primary_horizon"])
            self.assertEqual(2.0, run_json["short_term_single_trade_risk_pct"])
            self.assertEqual(5.0, run_json["strong_cycle_initial_position_pct_min"])
            self.assertEqual(8.0, run_json["strong_cycle_initial_position_pct_max"])
            self.assertEqual(3.0, run_json["short_term_stop_loss_pct_min"])
            self.assertEqual(5.0, run_json["short_term_stop_loss_pct_max"])
            self.assertIn("MU", run_json["strong_cycle_focus"])
            self.assertIn("SOXX", run_json["strong_cycle_focus"])
            self.assertIn("AMZN", run_json["strong_cycle_focus"])
            self.assertIn("AVGO", run_json["strong_cycle_focus"])
            self.assertIn("ASML", run_json["strong_cycle_focus"])
            self.assertIn("DELL", run_json["strong_cycle_focus"])
            self.assertIn("ETN", run_json["strong_cycle_focus"])
            self.assertIn("TTMI", run_json["strong_cycle_focus"])
            self.assertIn("PANW", run_json["strong_cycle_focus"])
            self.assertIn("AIQ", run_json["strong_cycle_focus"])
            self.assertIn("INTC", run_json["effective_strong_cycle_focus"])
            self.assertIn("INTC", run_json["special_watch_symbols"])
            self.assertIn("QQQ", run_json["special_watch_symbols"])
            self.assertEqual("IXIC", run_json["market_index_proxy_contract"][0]["index_codes"][0])
            self.assertEqual("QQQ", run_json["market_index_proxy_contract"][0]["tradable_proxy"])
            self.assertEqual("SPY", run_json["market_index_proxy_contract"][1]["tradable_proxy"])
            self.assertEqual("disabled", run_json["sqlite_write_mode"])
            self.assertEqual("skipped_dry_run", run_json["artifact_validation"]["status"])
            self.assertEqual(8.0, run_json["market_data_timeout_seconds"])
            self.assertEqual("financeBusiness_mcp", run_json["market_data_sources"][0])
            self.assertEqual(["financeBusiness_mcp"], run_json["market_data_sources"])

    def test_missing_base_file_is_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = self.make_config(Path(tmp))
            text = research_advisor.read_base_short(cfg)
            self.assertIn("Buffett 美股投研基础记录", text)
            self.assertIn("## 当前持仓", text)
            self.assertIn("## 操作记录", text)

    def test_cli_accepts_chinese_trigger_phrase(self):
        parser = research_advisor.build_parser()
        args = parser.parse_args(["buffett开始", "--dry-run", "--local-only"])
        self.assertEqual("buffett开始", args.command)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.local_only)

    def test_cli_accepts_prepare_step2(self):
        parser = research_advisor.build_parser()
        args = parser.parse_args(["prepare-step2", "--local-only", "--prices", "MSFT=1"])
        self.assertEqual("prepare-step2", args.command)
        self.assertTrue(args.local_only)
        self.assertEqual({"MSFT": 1.0}, research_advisor.parse_prices_arg(args.prices))

    def test_default_config_uses_current_codex_handoff(self):
        cfg = research_advisor.load_config(None)

        self.assertEqual("current_codex", cfg.execute_command)
        self.assertEqual("current_codex", research_advisor.DEFAULT_CONFIG["execute_command"])

    def test_prepare_step2_reports_writes_complete_metadata_review_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg = research_advisor.config_with_sqlite_write_mode(cfg, "local_only")
            cfg.base_short_path.write_text(
                "# Buffett 短线交易基础记录\n\n"
                "## 初始持仓\n\n"
                "- 微软：53 股，成本 447.49 美元\n"
                "- 特斯拉：5 股，成本 667 美元\n\n"
                "## record 17操作后持仓\n\n"
                "- 可口可乐：30 股，成本 77.52 美元\n"
                "- 微软：18 股，成本 506.96 美元\n"
                "- 英伟达：7 股，成本 184.23 美元\n"
                "- 标普 500 ETF：3 股，成本 679.31 美元\n"
                "- 超威半导体：1股，成本 413.23美元\n"
                "- 台积电：6股，成本 416.71美元\n"
                "- ANET：5股，成本 142.78美元\n\n"
                "## 可用资金\n\n"
                "- 103754 港元，可投资港股或美股\n\n"
                "## 操作记录\n\n"
                "1、按record 15建议，卖出MSFT 35股，成交价417美元。\n",
                encoding="utf-8",
            )

            result = research_advisor.prepare_step2_reports(
                cfg,
                prices={
                    "KO": 79.23,
                    "MSFT": 413.96,
                    "NVDA": 214.93,
                    "SPY": 737.62,
                    "AMD": 408.46,
                    "TSM": 414.15,
                    "ANET": 147.06,
                },
                hkd_usd_rate=7.8322,
                timestamp=dt.datetime(2026, 5, 10, 17, 25, tzinfo=ZoneInfo("Asia/Shanghai")),
            )

            metadata = Path(result["files"]["metadata"]).read_text(encoding="utf-8")
            review = Path(result["files"]["review"]).read_text(encoding="utf-8")
            plan = Path(result["files"]["plan"]).read_text(encoding="utf-8")
            audit = json.loads(Path(result["files"]["audit"]).read_text(encoding="utf-8"))

            self.assertTrue(Path(result["report_dir"]).name.startswith("record_20260510_172500_"))
            self.assertIn("task_key | `portfolio_review:993c7d93e383`", metadata)
            self.assertIn("Why this task_key", metadata)
            self.assertIn("buffett开始", metadata)
            self.assertIn("report 命名 | `record_YYYYMMDD_HHMMSS_序号`", metadata)
            self.assertIn("复盘主索引 | `local_report_folder`", metadata)
            self.assertIn("所有策略遵从波段交易策略", metadata)
            self.assertIn("AI应用/云CAPEX/数据基础设施", metadata)
            self.assertIn("Top 8-12", metadata)
            self.assertIn("本轮无预取数据包", metadata)
            self.assertIn("未找到可复盘的本地完整 report 文件夹", review)
            self.assertIn("local scan: report/record_* first", review)
            self.assertIn("| MSFT | 18 |", review)
            self.assertNotIn("| MSFT | 53 |", review)
            self.assertNotIn("| TSLA |", review)
            self.assertIn("错过机会账本", review)
            self.assertIn("Buffett 自我反思", review)
            self.assertIn("依据的最新数据", review)
            self.assertIn("依据的历史决策", review)
            self.assertIn("关键遗漏与分析错误复盘", review)
            self.assertIn("关键人物讲话遗漏", review)
            self.assertIn("关键事件未捕捉", review)
            self.assertIn("关键分析错误", review)
            self.assertIn("Fed/FOMC", review)
            self.assertIn("反思结论", review)
            self.assertIn("基于反思的新策略", review)
            self.assertIn("USD 持仓总市值 $17,174.21", review)
            self.assertIn("最大未实现亏损为 MSFT", review)
            self.assertIn("历史决策依据：本地 report 扫描状态为 `no_local_record_found`", review)
            self.assertIn("新策略一", review)
            self.assertIn("新策略二", review)
            self.assertIn("不能只评价股票涨跌", review)
            self.assertIn("本地 record 文件夹缺失或报告不完整", review)
            self.assertIn("新策略六", review)
            self.assertIn("上一轮未覆盖/无当时 veto", review)
            self.assertIn("AI 应用、云 CAPEX、GPU/ASIC", review)
            self.assertIn("Zeus 派工合同", plan)
            self.assertIn("Poseidon 派工合同", plan)
            self.assertIn("Hades 派工合同", plan)
            self.assertIn("Buffett 自我反思和新策略必须贯穿 03-06", plan)
            self.assertIn("关键遗漏与分析错误复盘必须贯穿 03-06", plan)
            self.assertIn("关键人物讲话遗漏、关键事件未捕捉、关键分析错误", plan)
            self.assertIn("验证 `基于反思的新策略` 是否可执行", plan)
            self.assertIn("不得忽略 Buffett 自我反思和新策略", plan)
            self.assertIn("Buffett 自我反思是否成立", plan)
            self.assertIn("新策略是否被最新数据支持", plan)
            self.assertIn("关键人物讲话遗漏/关键事件未捕捉/关键分析错误是否被修正", plan)
            self.assertIn("本轮无预取数据包", plan)
            self.assertIn("Top 8-12", plan)
            self.assertIn("当前 USD 持仓总市值", plan)
            self.assertEqual("portfolio_review:993c7d93e383", audit["task_key"])
            self.assertEqual("local_report_folder", audit["previous_decision"]["history_source"])
            self.assertFalse(audit["previous_decision"]["has_local_record"])
            self.assertEqual(["AMD", "ANET", "KO", "MSFT", "NVDA", "SPY", "TSM"], audit["usd_symbols"])

    def test_default_prompt_forbids_sqlite_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg = research_advisor.ResearchConfig(
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
                sqlite_write_mode="enabled",
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
            cfg.base_short_path.write_text("## 操作记录\n", encoding="utf-8")
            result = research_advisor.run_research(
                cfg,
                dry_run=True,
                timestamp=dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")
            self.assertIn("SQLite 写入模式：disabled", prompt)
            self.assertIn("复盘主来源仍是上一轮本地 report/record 文件夹", prompt)
            self.assertIn("SQLite 只允许只读 legacy 交叉检查", prompt)
            self.assertIn("禁止运行 `decision_db.py review`", prompt)
            self.assertIn("禁止运行 `decision_db.py review`、`decision_db.py record`", prompt)
            self.assertIn("禁止修改 `workspace/journal/decisions.sqlite3`", prompt)
            self.assertIn("local_result_snapshot.json", prompt)
            self.assertIn("新流程不得创建 `db_record.json`", prompt)
            self.assertIn("SQLite 写入：skipped_by_disabled_policy", prompt)
            run_json = json.loads((Path(result["run_dir"]) / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("disabled", run_json["sqlite_write_mode"])

    def test_live_mode_requires_execute_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg.base_short_path.write_text("## 操作记录\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                research_advisor.run_research(
                    cfg,
                    dry_run=False,
                    timestamp=dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
                )

    def test_current_codex_handoff_writes_prompt_without_child_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            run_dir.mkdir()
            prompt_file = run_dir / "prompt.md"
            prompt_file.write_text("$buffett\n本地组合 prompt\n", encoding="utf-8")
            cfg = self.make_config(root)

            result = research_advisor.execute_command(
                "current_codex",
                prompt_file,
                run_dir,
                dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
                cfg,
            )

            self.assertEqual(0, result["returncode"])
            self.assertFalse(result["timed_out"])
            self.assertEqual("current_codex", result["command"])
            self.assertEqual("current_codex", result["handoff_mode"])
            self.assertEqual(prompt_file.read_text(encoding="utf-8"), (run_dir / "stdout.txt").read_text(encoding="utf-8"))
            self.assertEqual("", (run_dir / "stderr.txt").read_text(encoding="utf-8"))
            handoff = json.loads((run_dir / "current_codex_handoff.json").read_text(encoding="utf-8"))
            self.assertEqual("current_codex", handoff["mode"])
            self.assertEqual(str(prompt_file), handoff["prompt_file"])
            self.assertIn("No child Codex subprocess is started", handoff["note"])

    def test_final_artifact_validation_rejects_db_record_without_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp) / "report" / "record_20260511_151843_001"
            report_dir.mkdir(parents=True)
            for name in research_advisor.REQUIRED_REPORT_FILES:
                (report_dir / name).write_text(f"# {name}\n", encoding="utf-8")
            (report_dir / "db_record.json").write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "missing_local_result_snapshot.json"):
                research_advisor.validate_final_artifacts(report_dir)

    def test_market_data_client_falls_back_after_provider_failure(self):
        class FailingProvider:
            name = "broken_source"

            def daily_bars(self, symbol, start, end):
                raise market_data.MarketDataError("source unavailable")

        class WorkingProvider:
            name = "working_source"

            def daily_bars(self, symbol, start, end):
                return [
                    market_data.DailyBar(symbol, "2026-05-04", 10, 11, 9, 10, 1000, self.name, {}),
                    market_data.DailyBar(symbol, "2026-05-08", 12, 13, 11, 12, 2000, self.name, {}),
                ]

        client = market_data.CompositeMarketDataClient(
            [FailingProvider(), WorkingProvider()],
            timeout_seconds=0,
        )
        result = client.daily_bars("MU", dt.date(2026, 5, 4), dt.date(2026, 5, 8))

        self.assertTrue(result.ok)
        self.assertEqual("working_source", result.source)
        self.assertEqual(2, len(result.attempts))
        self.assertFalse(result.attempts[0].ok)
        self.assertTrue(result.attempts[1].ok)
        self.assertAlmostEqual(20.0, market_data.five_day_return(result))

    def test_market_data_batch_deduplicates_and_keeps_partial_failures(self):
        class SelectiveProvider:
            name = "selective_source"

            def daily_bars(self, symbol, start, end):
                if symbol == "BAD":
                    raise market_data.MarketDataError("bad symbol")
                return [
                    market_data.DailyBar(symbol, "2026-05-04", 10, 11, 9, 10, 1000, self.name, {}),
                    market_data.DailyBar(symbol, "2026-05-08", 12, 13, 11, 12, 2000, self.name, {}),
                ]

        client = market_data.CompositeMarketDataClient([SelectiveProvider()], timeout_seconds=0)
        results = client.daily_bars_batch(["MU", "mu", "BAD"], dt.date(2026, 5, 4), dt.date(2026, 5, 8))
        summary = market_data.batch_summary(results)

        self.assertEqual(["MU", "BAD"], list(results.keys()))
        self.assertTrue(results["MU"].ok)
        self.assertFalse(results["BAD"].ok)
        self.assertEqual("bad symbol", results["BAD"].attempts[0].error)
        self.assertEqual(2, len(summary))
        self.assertAlmostEqual(20.0, summary[0]["period_return_pct"])

    def test_market_data_client_rejects_stale_provider_and_falls_back(self):
        class StaleProvider:
            name = "stale_source"

            def daily_bars(self, symbol, start, end):
                # Latest bar is 2026-05-03, which is 5 days before end (2026-05-08),
                # exceeding the 3-day staleness tolerance.
                return [
                    market_data.DailyBar(symbol, "2026-05-02", 10, 11, 9, 10, 1000, self.name, {}),
                    market_data.DailyBar(symbol, "2026-05-03", 12, 13, 11, 12, 2000, self.name, {}),
                ]

        class FreshProvider:
            name = "fresh_source"

            def daily_bars(self, symbol, start, end):
                return [
                    market_data.DailyBar(symbol, "2026-05-08", 13, 14, 12, 13, 3000, self.name, {}),
                ]

        client = market_data.CompositeMarketDataClient(
            [StaleProvider(), FreshProvider()],
            timeout_seconds=0,
        )
        result = client.daily_bars("AMD", dt.date(2026, 5, 1), dt.date(2026, 5, 8))

        self.assertTrue(result.ok)
        self.assertEqual("fresh_source", result.source)
        self.assertFalse(result.attempts[0].ok)
        self.assertIn("stale latest date 2026-05-03", result.attempts[0].error)
        self.assertTrue(result.attempts[1].ok)

    def test_csv_market_data_provider_reads_local_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            (cache_dir / "AMD.csv").write_text(
                "date,open,high,low,close,volume\n"
                "2026-05-04,360,362,338,341.54,42000244\n"
                "2026-05-08,418,456,418,455.19,58134868\n",
                encoding="utf-8",
            )
            provider = market_data.CsvMarketDataProvider(cache_dir)
            bars = provider.daily_bars("AMD", dt.date(2026, 5, 4), dt.date(2026, 5, 8))

            self.assertEqual(2, len(bars))
            self.assertEqual("csv_cache", bars[0].source)
            self.assertEqual(455.19, bars[-1].close)

    def test_write_csv_cache_persists_manifest_and_symbol_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_dir = Path(tmp)
            result = market_data.MarketDataResult(
                symbol="AMD",
                bars=[
                    market_data.DailyBar("AMD", "2026-05-08", 418.59, 456.29, 418.29, 455.19, 58134868, "stooq", {}),
                ],
                source="stooq",
                attempts=[market_data.SourceAttempt("stooq", True, rows=1)],
            )

            manifest = market_data.write_csv_cache({"AMD": result}, cache_dir)

            self.assertTrue((cache_dir / "AMD.csv").exists())
            self.assertTrue((cache_dir / "manifest.json").exists())
            self.assertEqual([str(cache_dir / "AMD.csv")], manifest["written_files"])
            provider = market_data.CsvMarketDataProvider(cache_dir)
            bars = provider.daily_bars("AMD", dt.date(2026, 5, 8), dt.date(2026, 5, 8))
            self.assertEqual(455.19, bars[0].close)

    def test_stooq_provider_parses_daily_csv(self):
        payload = (
            "Date,Open,High,Low,Close,Volume\n"
            "2026-05-07,417.07,421.71,401.08,408.46,44885481\n"
            "2026-05-08,418.59,456.29,418.29,455.19,58134868\n"
        )

        class _Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return payload.encode("utf-8")

        with patch("urllib.request.urlopen", return_value=_Response()):
            provider = market_data.StooqMarketDataProvider()
            bars = provider.daily_bars("AMD", dt.date(2026, 5, 7), dt.date(2026, 5, 8))

        self.assertEqual(2, len(bars))
        self.assertEqual("stooq", bars[0].source)
        self.assertEqual(455.19, bars[-1].close)

    def test_default_market_data_client_keeps_yfinance_as_last_resort(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"FREEDOM_AKTOOLS_API_URL": "", "AKTOOLS_API_URL": ""}):
            client = market_data.default_client(
                cache_dir=Path(tmp),
                http_api_url="https://example.com/{symbol}?start={start}&end={end}",
                timeout_seconds=0,
            )

        self.assertEqual(
            ["akshare", "http_api", "stooq", "csv_cache", "yfinance_last_resort"],
            [provider.name for provider in client.providers],
        )

    def test_default_market_data_client_can_use_aktools_http_between_akshare_and_http_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = market_data.default_client(
                cache_dir=Path(tmp),
                aktools_api_url="http://127.0.0.1:8080",
                http_api_url="https://example.com/{symbol}?start={start}&end={end}",
                timeout_seconds=0,
            )

        self.assertEqual(
            ["akshare", "aktools_http", "http_api", "stooq", "csv_cache", "yfinance_last_resort"],
            [provider.name for provider in client.providers],
        )

    def test_default_market_data_client_can_disable_yfinance(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"FREEDOM_DISABLE_YFINANCE": "true"}):
            client = market_data.default_client(cache_dir=Path(tmp), timeout_seconds=0)

        self.assertNotIn("yfinance", [provider.name for provider in client.providers])
        self.assertEqual("akshare", client.providers[0].name)

    def test_previous_us_weekday_moves_weekend_to_friday(self):
        self.assertEqual(
            dt.date(2026, 5, 8),
            research_advisor.previous_us_weekday(dt.date(2026, 5, 9)),
        )
        self.assertEqual(
            dt.date(2026, 5, 8),
            research_advisor.previous_us_weekday(dt.date(2026, 5, 10)),
        )
        self.assertEqual(
            dt.date(2026, 5, 11),
            research_advisor.previous_us_weekday(dt.date(2026, 5, 11)),
        )

    def test_live_run_prefetches_market_data_pack_before_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = self.make_config(root)
            cfg = research_advisor.ResearchConfig(
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
                sqlite_write_mode="local_only",
                market_data_timeout_seconds=cfg.market_data_timeout_seconds,
                market_data_cache_dir=cfg.market_data_cache_dir,
                market_data_aktools_api_url=cfg.market_data_aktools_api_url,
                market_data_http_api_url=cfg.market_data_http_api_url,
                market_data_sources=cfg.market_data_sources,
                execute_command="codex-placeholder",
                execute_timeout_seconds=cfg.execute_timeout_seconds,
                write_system_log=False,
                system_log_path=cfg.system_log_path,
            )
            cfg.base_short_path.write_text("持仓 AMD 1股，关注 MU、FLEX。\n", encoding="utf-8")
            fake_pack = {
                "cache_dir": str(root / "pack"),
                "written_files": [],
                "summary": [],
            }

            fake_command = {
                "command": "codex-placeholder",
                "returncode": 0,
                "timed_out": False,
                "stdout_file": str(root / "stdout.txt"),
                "stderr_file": str(root / "stderr.txt"),
            }
            def fake_execute_command(*args, **kwargs):
                report_dir = root / "report" / "record_20260508_214500_001"
                report_dir.mkdir(parents=True)
                for name in research_advisor.REQUIRED_REPORT_FILES:
                    (report_dir / name).write_text(f"# {name}\n", encoding="utf-8")
                (report_dir / "local_result_snapshot.json").write_text(
                    json.dumps(
                        {
                            "sqlite_write_mode": "disabled",
                            "sqlite_write_status": "skipped_by_disabled_policy",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return fake_command

            with patch("research_advisor.prefetch_market_data_pack", return_value=fake_pack) as mock_prefetch, \
                 patch("research_advisor.execute_command", side_effect=fake_execute_command):
                result = research_advisor.run_research(
                    cfg,
                    dry_run=False,
                    timestamp=dt.datetime(2026, 5, 8, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
                )

            mock_prefetch.assert_called_once()
            self.assertEqual(0, result["command_result"]["returncode"])
            self.assertEqual("passed", result["artifact_validation"]["status"])
            self.assertEqual(fake_pack, result["market_data_pack_summary"])
            self.assertIsNone(result["market_data_pack_manifest"])
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")
            self.assertIn("行情数据规则：本轮未提供预取 manifest", prompt)
            self.assertIn("不得回退到在线、本地、CSV 或任何非 financeBusiness 数据源", prompt)
            self.assertNotIn("行情数据必须优先从本轮预取数据包消费", prompt)

    def test_early_week_strong_cycle_data_requires_momentum_starter_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_dir = root / "market_data"
            cache_dir.mkdir()
            fixtures = {
                "SPY": [
                    ("2026-05-04", 720.070, 722.120, 714.990, 718.010, 51950559),
                    ("2026-05-05", 721.770, 725.040, 721.490, 723.770, 36933226),
                    ("2026-05-06", 728.160, 734.590, 727.820, 733.830, 53288941),
                ],
                "SMH": [
                    ("2026-05-04", 512.470, 513.150, 501.150, 506.790, 6867462),
                    ("2026-05-05", 515.380, 526.200, 514.120, 522.690, 8624609),
                    ("2026-05-06", 537.770, 549.880, 532.350, 549.760, 15262913),
                ],
                "MU": [
                    ("2026-05-04", 560.600, 592.799, 557.760, 576.450, 46043705),
                    ("2026-05-05", 609.775, 651.740, 605.470, 640.200, 64268503),
                    ("2026-05-06", 660.370, 667.670, 627.580, 666.590, 55725836),
                ],
                "AMD": [
                    ("2026-05-04", 360.310, 361.850, 338.700, 341.540, 42000244),
                    ("2026-05-05", 351.510, 359.572, 344.880, 355.260, 64235117),
                    ("2026-05-06", 409.490, 430.600, 402.040, 421.390, 87732167),
                ],
                "FLEX": [
                    ("2026-05-04", 92.405, 93.000, 90.850, 91.840, 2613069),
                    ("2026-05-05", 93.090, 96.580, 92.630, 96.450, 9450372),
                    ("2026-05-06", 119.850, 134.990, 119.000, 134.730, 18828629),
                ],
                "INTC": [
                    ("2026-05-04", 99.180, 99.820, 95.600, 95.780, 119294030),
                    ("2026-05-05", 100.505, 110.480, 100.080, 108.150, 198481960),
                    ("2026-05-06", 110.975, 113.500, 106.580, 113.010, 157320080),
                ],
            }
            for symbol, rows in fixtures.items():
                text = "date,open,high,low,close,volume\n" + "".join(
                    f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n"
                    for row in rows
                )
                (cache_dir / f"{symbol}.csv").write_text(text, encoding="utf-8")

            client = market_data.CompositeMarketDataClient(
                [market_data.CsvMarketDataProvider(cache_dir)],
                timeout_seconds=0,
            )
            start = dt.date(2026, 5, 4)
            end = dt.date(2026, 5, 6)
            returns = {
                symbol: market_data.five_day_return(client.daily_bars(symbol, start, end))
                for symbol in fixtures
            }
            spy_return = returns["SPY"]
            smh_return = returns["SMH"]
            leaders = {
                symbol
                for symbol in ("MU", "AMD", "FLEX", "INTC")
                if returns[symbol] is not None
                and smh_return is not None
                and spy_return is not None
                and returns[symbol] > smh_return
                and returns[symbol] - spy_return > 10
            }

            self.assertAlmostEqual(2.20, spy_return, places=2)
            self.assertAlmostEqual(8.48, smh_return, places=2)
            self.assertEqual({"MU", "AMD", "FLEX", "INTC"}, leaders)

            cfg = self.make_config(root)
            cfg = research_advisor.ResearchConfig(
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
                sqlite_write_mode="local_only",
                market_data_timeout_seconds=cfg.market_data_timeout_seconds,
                market_data_cache_dir=cache_dir,
                market_data_aktools_api_url=cfg.market_data_aktools_api_url,
                market_data_http_api_url=cfg.market_data_http_api_url,
                market_data_sources=cfg.market_data_sources,
                execute_command=cfg.execute_command,
                execute_timeout_seconds=cfg.execute_timeout_seconds,
                write_system_log=cfg.write_system_log,
                system_log_path=cfg.system_log_path,
            )
            cfg.base_short_path.write_text(
                "# Buffett 短线交易基础记录\n\n"
                "## 当前持仓\n\n"
                "- 英伟达：6 股，成本 178.57 美元\n\n"
                "## 可用资金\n\n"
                "- 78,000 港元，可投资港股或美股\n\n"
                "## 操作记录\n\n"
                "- 本周前期回放测试\n",
                encoding="utf-8",
            )
            result = research_advisor.run_research(
                cfg,
                dry_run=True,
                timestamp=dt.datetime(2026, 5, 6, 22, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
            )
            prompt = Path(result["prompt_file"]).read_text(encoding="utf-8")

            self.assertIn("错过机会账本", prompt)
            self.assertIn("动能突破不是自动追高", prompt)
            self.assertIn("至少提供一个可执行小仓 starter 方案", prompt)
            self.assertIn("仓位升级阶梯与大幅盈利路径", prompt)
            self.assertIn("批准小仓 starter", prompt)
            self.assertIn("workspace/analysis/cli.py swing-verdict", prompt)
            self.assertIn("ETF/basket fallback", prompt)
            self.assertIn("no-trade proof", prompt)
            self.assertIn("INTC/英特尔", prompt)
            self.assertIn("SMH/SOXX/QQQ", prompt)
            self.assertNotIn(str(cache_dir), prompt)
            self.assertIn("Buffett 工作流结构化行情只允许 financeBusiness MCP", prompt)
            self.assertIn("SQLite 写入：skipped_by_disabled_policy", prompt)

    def test_may_6_replay_selected_leaders_were_not_profitable_on_may_7(self):
        cache_dir = Path(__file__).resolve().parent / "fixtures" / "market_data_2026w19"
        client = market_data.CompositeMarketDataClient(
            [market_data.CsvMarketDataProvider(cache_dir)],
            timeout_seconds=0,
        )
        report = replay_backtest.replay_strong_cycle_starter(
            client=client,
            symbols=["MU", "AMD", "FLEX", "INTC"],
            lookback_start=dt.date(2026, 5, 4),
            decision_date=dt.date(2026, 5, 6),
            exit_date=dt.date(2026, 5, 7),
            shares=1,
            fee_usd=5.0,
        )

        self.assertEqual(["MU", "AMD", "FLEX", "INTC"], report.selected_symbols)
        self.assertFalse(report.profitable)
        self.assertAlmostEqual(-78.0, report.net_pnl_usd)
        self.assertTrue(all(trade.verdict == "not_profitable" for trade in report.trades))

    def test_may_6_replay_became_profitable_if_held_to_may_8_with_five_pct_starters(self):
        cache_dir = Path(__file__).resolve().parent / "fixtures" / "market_data_2026w19"
        client = market_data.CompositeMarketDataClient(
            [market_data.CsvMarketDataProvider(cache_dir)],
            timeout_seconds=0,
        )
        report = replay_backtest.replay_strong_cycle_starter(
            client=client,
            symbols=["MU", "AMD", "FLEX", "INTC"],
            lookback_start=dt.date(2026, 5, 4),
            decision_date=dt.date(2026, 5, 6),
            exit_date=dt.date(2026, 5, 8),
            equity_usd=30447.51,
            position_pct=5.0,
            fee_usd=5.0,
        )

        self.assertEqual(["MU", "AMD", "FLEX", "INTC"], report.selected_symbols)
        self.assertTrue(report.profitable)
        self.assertAlmostEqual(458.51, report.net_pnl_usd)


if __name__ == "__main__":
    unittest.main()
