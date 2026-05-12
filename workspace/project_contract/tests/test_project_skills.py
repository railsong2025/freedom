"""Tests for project-local Codex skill contracts."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class TestZeusSkillContract(unittest.TestCase):
    def setUp(self):
        self.skill = (ROOT / ".codex" / "skills" / "zeus" / "SKILL.md").read_text(encoding="utf-8")
        self.agent = (ROOT / ".codex" / "agents" / "zeus.toml").read_text(encoding="utf-8")

    def test_zeus_skill_has_executable_symbol_universe_contract(self):
        self.assertIn("## Run Directory And Symbol Universe", self.skill)
        self.assertIn("Set `run_dir` to the current Zeus report folder", self.skill)
        self.assertIn("Build one deterministic comma-separated symbol universe", self.skill)
        self.assertNotIn("{symbols}", self.skill)
        self.assertNotIn("{run_dir}", self.skill)

    def test_zeus_skill_has_timeout_safe_checkpoint_contract(self):
        self.assertIn("## Timeout-Safe Checkpoint Workflow", self.skill)
        self.assertIn("03_zeus_intelligence_parts", self.skill)
        self.assertIn("checkpoint-status", self.skill)
        self.assertIn("merge-checkpoints", self.skill)
        self.assertIn("03_zeus_intelligence_manifest.json", self.skill)
        self.assertIn("broad or long-running tasks used checkpoint parts", self.skill)

    def test_zeus_skill_supports_standalone_explicit_trigger(self):
        self.assertIn("public intelligence collection module", self.skill)
        self.assertIn("user or any project workflow", self.skill)
        self.assertIn("public intelligence request contract", self.skill)
        self.assertIn("Storage location is caller-controlled", self.skill)
        self.assertIn("must ask for", self.skill)
        self.assertIn("Do not invent a default", self.skill)
        self.assertNotIn("report/YYYY-MM-DD_zeus_10字以内摘要/", self.skill)
        self.assertIn("workflow-driven tasks are not marked complete unless", self.skill)
        self.assertIn("情报问题清单", self.skill)
        self.assertNotIn("receives tasks only through", self.skill)
        self.assertNotIn("If any required file is missing, stop", self.skill)
        self.assertIn("Buffett workflows and financeBusiness-only market-data requests", self.skill)
        self.assertIn("standalone tasks", self.skill)
        self.assertNotIn("巴菲特", self.skill)

    def test_zeus_skill_preserves_ai_chain_minimum_universe(self):
        required_symbols = [
            "MSFT",
            "NVDA",
            "AVGO",
            "TSM",
            "INTC",
            "MU",
            "ASML",
            "AMKR",
            "ANET",
            "DELL",
            "VRT",
            "TTMI",
            "PANW",
            "SMH",
            "SOXX",
            "AIQ",
        ]
        self.assertIn("Canonical AI-chain universe", self.skill)
        for symbol in required_symbols:
            self.assertIn(symbol, self.skill)

    def test_zeus_skill_requires_complete_financebusiness_market_tape(self):
        self.assertIn("must come from financeBusiness MCP only", self.skill)
        self.assertIn("mcp__financeBusiness__StockCurrentMarket", self.skill)
        self.assertIn("mcp__financeBusiness__StockMarketList", self.skill)
        self.assertIn("ZEUS_FIELD_FAILURE", self.skill)
        for field in [
            "current_price",
            "close",
            "previous_close",
            "open",
            "high",
            "low",
            "pct_change",
            "change_amount",
            "amplitude",
            "volume",
            "amount",
            "volume_ratio",
            "turnover_rate",
            "market_source",
        ]:
            self.assertIn(field, self.skill)
        for financebusiness_field in [
            "latestPri",
            "yesEndPri",
            "startPri",
            "maxPri",
            "minPri",
            "increasePer",
            "increasePri",
            "stockAmplitude",
            "tradingVolume",
            "turnover",
            "volumeRatio",
            "turnoverRate",
            "traAmount",
            "traNumber",
            "update_time",
        ]:
            self.assertIn(financebusiness_field, self.skill)

    def test_zeus_skill_requires_current_strategy_field_pack(self):
        self.assertIn("current-strategy field pack", self.skill)
        self.assertIn("当前交易策略字段包", self.skill)
        for field in [
            "ticker",
            "name",
            "quote_time",
            "trade_status",
            "ma5",
            "ma10",
            "ma20",
            "price_vs_ma5",
            "price_vs_ma10",
            "price_vs_ma20",
            "high_20d",
            "low_20d",
            "range_position_20d",
            "return_1d",
            "return_5d",
            "return_10d",
            "return_20d",
            "atr_14",
            "volatility_20d",
            "relative_strength_spy",
            "relative_strength_qqq",
            "relative_strength_smh",
            "relative_strength_soxx",
            "entry_type",
            "entry_trigger_price",
            "suggested_limit_price",
            "stop_loss_price",
            "take_profit_1",
            "take_profit_2",
            "trailing_stop_rule",
            "max_holding_days",
            "next_review_time_bj",
            "fee_adjusted_rr_tp1",
            "fee_adjusted_rr_tp2",
            "field_source_map",
            "field_timestamp_map",
            "zeus_field_status",
            "usable_for_current_trade",
        ]:
            self.assertIn(field, self.skill)

    def test_zeus_agent_delegates_report_contract_to_skill(self):
        self.assertIn(".codex/skills/zeus/SKILL.md", self.agent)
        self.assertIn("本 agent 文件只定义角色身份", self.agent)
        self.assertIn("项目级公共情报收集模块", self.agent)
        self.assertIn("任意项目工作流明确提出的 Zeus/宙斯/情报部/情报收集任务", self.agent)
        self.assertIn("03_zeus_intelligence_parts", self.agent)
        self.assertIn("merge-checkpoints", self.agent)
        self.assertIn("必须由请求方提供", self.agent)
        self.assertIn("先询问存储位置", self.agent)
        self.assertNotIn("只通过 Buffett 接收任务", self.agent)
        self.assertNotIn("Buffett", self.agent)
        self.assertNotIn("buffett", self.agent)
        self.assertNotIn("巴菲特", self.agent)
        self.assertNotIn("## 03_zeus_intelligence.md 格式", self.agent)
        self.assertNotIn("默认重点候选必须覆盖", self.agent)


class TestPublicResearchModuleContracts(unittest.TestCase):
    def setUp(self):
        self.poseidon_skill = (ROOT / ".codex" / "skills" / "poseidon" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.hades_skill = (ROOT / ".codex" / "skills" / "hades" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.poseidon_agent = (ROOT / ".codex" / "agents" / "poseidon.toml").read_text(
            encoding="utf-8"
        )
        self.hades_agent = (ROOT / ".codex" / "agents" / "hades.toml").read_text(
            encoding="utf-8"
        )
        self.buffett_skill = (ROOT / ".codex" / "skills" / "buffett" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.buffett_agent = (ROOT / ".codex" / "agents" / "buffett-leader.toml").read_text(
            encoding="utf-8"
        )
        self.buffett_workflow = (
            ROOT / ".codex" / "skills" / "buffett" / "references" / "full-workflow.md"
        ).read_text(encoding="utf-8")
        self.buffett_sector_playbook = (
            ROOT / ".codex" / "skills" / "buffett" / "references" / "sector-stock-playbook.md"
        ).read_text(encoding="utf-8")
        self.claude_buffett_skill = (ROOT / ".claude" / "skills" / "buffett" / "SKILL.md").read_text(
            encoding="utf-8"
        )

    def assert_public_module_independent(self, text):
        self.assertIn("standalone_user", text)
        self.assertIn("workflow", text)
        self.assertIn("workflow-driven tasks are not marked complete unless", text)
        self.assertNotIn("只通过 Buffett", text)
        self.assertNotIn("receives work through Buffett", text)
        self.assertNotIn("If any required file is missing, stop and ask Buffett", text)
        self.assertNotIn("01_buffett_review.md", text)
        self.assertNotIn("02_buffett_plan.md", text)
        self.assertNotIn("Buffett 自我反思", text)

    def test_poseidon_is_public_research_module(self):
        self.assertIn("public investment research module", self.poseidon_skill)
        self.assertIn("04_poseidon_research.md", self.poseidon_skill)
        self.assertIn("Storage location is caller-controlled", self.poseidon_skill)
        self.assertIn("must ask for", self.poseidon_skill)
        self.assertNotIn("report/YYYY-MM-DD_poseidon_10字以内摘要/", self.poseidon_skill)
        self.assertIn("候选股票评分与分层", self.poseidon_skill)
        self.assertIn("强周期波段交易计划", self.poseidon_skill)
        self.assert_public_module_independent(self.poseidon_skill)

        self.assertIn(".codex/skills/poseidon/SKILL.md", self.poseidon_agent)
        self.assertIn("项目级公共投资研究模块", self.poseidon_agent)
        self.assertIn("必须由请求方提供", self.poseidon_agent)
        self.assertIn("先询问存储位置", self.poseidon_agent)
        self.assertNotIn("只通过 Buffett", self.poseidon_agent)
        self.assertNotIn("01_buffett_review.md", self.poseidon_agent)

    def test_hades_is_public_verification_module(self):
        self.assertIn("public verification and audit module", self.hades_skill)
        self.assertIn("05_hades_verification.md", self.hades_skill)
        self.assertIn("Storage location is caller-controlled", self.hades_skill)
        self.assertIn("must ask for", self.hades_skill)
        self.assertNotIn("report/YYYY-MM-DD_hades_10字以内摘要/", self.hades_skill)
        self.assertIn("同意 / 有条件同意 / 不同意", self.hades_skill)
        self.assertIn("波段风控审计", self.hades_skill)
        self.assert_public_module_independent(self.hades_skill)

        self.assertIn(".codex/skills/hades/SKILL.md", self.hades_agent)
        self.assertIn("项目级公共验证与审计模块", self.hades_agent)
        self.assertIn("必须由请求方提供", self.hades_agent)
        self.assertIn("先询问存储位置", self.hades_agent)
        self.assertNotIn("只通过 Buffett", self.hades_agent)
        self.assertNotIn("01_buffett_review.md", self.hades_agent)

    def test_buffett_remains_orchestrator_for_full_workflow(self):
        for filename in [
            "00_metadata.md",
            "01_buffett_review.md",
            "02_buffett_plan.md",
            "03_zeus_intelligence.md",
            "04_poseidon_research.md",
            "05_hades_verification.md",
            "06_roundtable.md",
            "07_final_decision.md",
        ]:
            self.assertIn(filename, self.buffett_skill + self.buffett_workflow)

        self.assertIn("Zeus is a public module", self.buffett_skill)
        self.assertIn("Poseidon is a public module", self.buffett_skill)
        self.assertIn("Hades is a public module", self.buffett_skill)
        self.assertIn("public `zeus` skill", self.buffett_workflow)
        self.assertIn("public `poseidon` skill", self.buffett_workflow)
        self.assertIn("public `hades` skill", self.buffett_workflow)
        self.assertIn("subject=us_equity_portfolio", self.buffett_workflow)
        self.assertIn("market=US equities", self.buffett_workflow)
        self.assertIn("buffett开始", self.buffett_skill)
        self.assertNotIn("buffett投研开始", self.buffett_skill)
        self.assertNotIn("buffett投研开始", self.buffett_workflow)
        self.assertNotIn("buffett投研开始", self.buffett_agent)
        for text in [self.buffett_skill, self.buffett_workflow, self.buffett_agent, self.claude_buffett_skill]:
            self.assertIn("local_result_snapshot.json", text)
            self.assertIn("skipped_by_disabled_policy", text)
            self.assertIn("INTC", text)
            self.assertNotIn("python3 workspace/journal/decision_db.py record", text)
            self.assertNotIn("SQLite journal", text)
            self.assertNotIn("if at or past 00:00", text)
            self.assertNotIn("Read base_short.md + SQLite", text)
        self.assertIn("Special watch scope", self.buffett_skill)
        self.assertIn("INTC/Intel", self.buffett_skill)
        self.assertIn("INTC/Intel", self.buffett_workflow)
        self.assertIn("INTC/英特尔", self.buffett_agent)
        self.assertIn("INTC,ANET", self.claude_buffett_skill)
        self.assertIn("local result snapshot", self.buffett_sector_playbook)
        self.assertNotIn("SQLite record", self.buffett_sector_playbook)
        for text in [self.buffett_skill, self.buffett_workflow, self.buffett_agent]:
            self.assertIn("mcp__financeBusiness__StockCurrentMarket", text)
            self.assertIn("mcp__financeBusiness__StockMarketList", text)
            self.assertIn("ZEUS_FIELD_FAILURE", text)
            self.assertIn("current-strategy field pack", text)
            self.assertIn("field_source_map", text)
            self.assertIn("usable_for_current_trade", text)


class TestAuxiliarySkillBoundaries(unittest.TestCase):
    def test_legacy_analysis_skills_are_auxiliary_to_buffett_decisions(self):
        for skill_name in ["us-stock-analysis", "portfolio-manager", "sector-analyst"]:
            text = (ROOT / ".codex" / "skills" / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("auxiliary", text)
            self.assertIn("Buffett", text)
            self.assertIn("do not bypass Buffett", text)
            self.assertIn("buffett开始", text)

    def test_market_and_technical_skills_are_auxiliary_inside_project(self):
        for skill_name in ["market-environment-analysis", "technical-analyst"]:
            text = (ROOT / ".codex" / "skills" / skill_name / "SKILL.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("Freedom_Multi_EN Boundary", text)
            self.assertIn("auxiliary", text)
            self.assertIn("buffett开始", text)
            self.assertIn("must not", text)

    def test_portfolio_manager_does_not_issue_final_trade_actions(self):
        text = (ROOT / ".codex" / "skills" / "portfolio-manager" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("rebalancing evidence", text)
        self.assertIn("Final Action:** Defer to Buffett", text)
        self.assertNotIn("**Recommendation:** [HOLD / ADD / TRIM / SELL]", text)
        self.assertNotIn("Specific quantities (sell XX shares, add $X,XXX)", text)

    def test_poseidon_cannot_bypass_buffett_for_final_portfolio_decisions(self):
        poseidon = (ROOT / ".codex" / "skills" / "poseidon" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("final current", poseidon)
        self.assertIn("must be\nescalated to Buffett", poseidon)
        self.assertNotIn("unless the user explicitly asks for a standalone research recommendation", poseidon)


class TestPublicToolingContracts(unittest.TestCase):
    def test_zeus_cli_uses_public_market_data_module(self):
        cli = (ROOT / "workspace" / "intelligence" / "cli.py").read_text(encoding="utf-8")
        public_market_data = (ROOT / "workspace" / "interface" / "market_data.py").read_text(
            encoding="utf-8"
        )
        compatibility_wrapper = (
            ROOT / "workspace" / "buffett_research_advisor" / "market_data.py"
        ).read_text(encoding="utf-8")

        self.assertIn("from interface.market_data import DailyBar", cli)
        self.assertIn("financeBusiness_mcp_required", cli)
        self.assertIn("ZEUS_FIELD_FAILURE", cli)
        self.assertNotIn("from interface.market_data import default_client", cli)
        self.assertNotIn("--aktools-api-url", cli)
        self.assertIn("merge-checkpoints", cli)
        self.assertIn("checkpoint-status", cli)
        self.assertNotIn("buffett_research_advisor.market_data", cli)
        self.assertIn("Public market data adapters", public_market_data)
        self.assertIn("AkToolsMarketDataProvider", public_market_data)
        self.assertIn("FREEDOM_AKTOOLS_API_URL", public_market_data)
        self.assertIn("workspace/interface/market_data.py", compatibility_wrapper)
        self.assertIn("AkToolsMarketDataProvider", compatibility_wrapper)

    def test_portfolio_clis_expose_public_portfolio_file_argument(self):
        analysis_cli = (ROOT / "workspace" / "analysis" / "cli.py").read_text(encoding="utf-8")
        verification_cli = (ROOT / "workspace" / "verification" / "cli.py").read_text(
            encoding="utf-8"
        )

        for text in [analysis_cli, verification_cli]:
            self.assertIn("--portfolio-file", text)
            self.assertIn("Legacy alias for --portfolio-file", text)
            self.assertNotIn('required=True, help="Path to base_short.md"', text)

    def test_buffett_mandatory_tool_examples_are_templates(self):
        buffett_skill = (ROOT / ".codex" / "skills" / "buffett" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("--portfolio-file <portfolio_file>", buffett_skill)
        self.assertIn("<comma_separated_symbol_universe>", buffett_skill)
        self.assertIn("<SYMBOL:PRICE> ...", buffett_skill)
        self.assertIn("--symbol <candidate_symbol>", buffett_skill)
        self.assertIn("<evidence_based_sector_factor_scores>", buffett_skill)
        self.assertIn("<evidence_based_stock_factor_scores>", buffett_skill)
        self.assertIn("<evidence_based_swing_factor_scores>", buffett_skill)
        self.assertIn("--symbol {candidate_symbol}", (ROOT / ".codex" / "skills" / "buffett" / "references" / "full-workflow.md").read_text(encoding="utf-8"))
        for stale_literal in ["KO=78.42", "MSFT=415.12", "NVDA=215.20", "MU:BUY:2:600"]:
            self.assertNotIn(stale_literal, buffett_skill)
            self.assertNotIn(
                stale_literal,
                (ROOT / ".codex" / "skills" / "buffett" / "references" / "full-workflow.md").read_text(encoding="utf-8"),
            )

    def test_buffett_runner_defaults_to_current_codex_handoff(self):
        config = json.loads(
            (ROOT / "workspace" / "buffett_research_advisor" / "config.example.json").read_text(
                encoding="utf-8"
            )
        )
        live_config = json.loads(
            (ROOT / "workspace" / "buffett_research_advisor" / "config.live.example.json").read_text(
                encoding="utf-8"
            )
        )
        readme = (ROOT / "workspace" / "buffett_research_advisor" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual("current_codex", config["execute_command"])
        self.assertEqual("current_codex", live_config["execute_command"])
        self.assertIn("current_codex_handoff.json", readme)
        self.assertIn("不再启动子 Codex", readme)
        self.assertNotIn("/usr/local/bin/codex", json.dumps(config, ensure_ascii=False))
        self.assertNotIn("/usr/local/bin/codex", json.dumps(live_config, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
