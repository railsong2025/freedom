# Hades 验证报告

## 输入与审计范围

已读取 `00_metadata.md` 至 `04_poseidon_research.md`，并审计 `base_short.md`、`portfolio_usd_working.md`、financeBusiness 行情、aiwebsearch 来源、Python 工具输出、拟定交易和交易后 P&L。

## 顶层审计结论

`有条件同意`：允许 ANET 5股以 139.50 或更优卖出，允许 VRT 2股以 350.00 或更优买入。VRT 是 `small_starter`，不是 full current_trade；小仓低于5%是现金受限与风险控制下的豁免，不是风险放大。若价格不能达到，不能追。

## 计划执行情况

| 审计项 | 状态 | 说明 |
|---|---|---|
| 上游完整性 | 通过 | 00-04 文件存在且引用路径明确 |
| P&L使用 | 通过 | 亏损扩大后没有追买 MU/WDC/AMD，也没有机械卖 MSFT |
| 关键人物/事件 | 有条件通过 | Intel/White House/Goldman/Vertiv/Arista/Micron 覆盖；Fed和其他公司管理层覆盖仍需下轮加强 |
| 数据质量 | 有条件通过 | financeBusiness 当前行情可用；本地 indicators CLI 无 CSV，不允许伪装成精确 MA/ATR |
| 当前交易 | 有条件通过 | 只批准 ANET 反弹卖出与 VRT 低限价 starter |

## Python 工具调用记录

| 命令 | exit | 关键输出 |
|---|---:|---|
| `verification/cli.py audit-pnl --portfolio-file portfolio_usd_working.md --prices ...` | 0 | passed=true；total_cost_basis 40,149.92；total_market_value 38,106.54 |
| `verification/cli.py stress-test --portfolio-file portfolio_usd_working.md --prices ...` | 0 | 半导体 -15% 冲击约 -3,700.08；地缘半导体+科技 -20% 冲击约 -6,707.28 |
| `verification/cli.py compliance ... ANET SELL 5 / VRT BUY 2 --stops VRT:338` | 0 | 18/20 通过；2项失败均为 VRT 低于5% starter |
| `verification/cli.py audit-post-trade ...` | 0 | fee audit passed；pnl audit passed；realized_pnl -21.40；fees 10.00；post_cash 970.79；overall_passed=true |

## P&L 审计

P&L 数学通过。当前美股持仓市值约 38,106.53，成本 40,149.92，未实现亏损 -2,043.39，亏损率 -5.09%。亏损主要来自 MSFT、MU、WDC、TSM；ANET亏损金额小但相对强弱差。Hades 确认 Poseidon 没有把亏损当作自动补仓理由。

## 压力测试摘要

| 情景 | 组合影响 | 审计含义 |
|---|---:|---|
| 全组合 -10% | -3,810.65 | 可承受但现金垫薄 |
| 全组合 -20% | -7,621.31 | 不应再堆高相关AI链 |
| 半导体 -15% | -3,700.08 | MU/AMD/WDC/INTC/NVDA/TSM 是主要风险源 |
| 科技 -15% | -1,330.38 | MSFT与FLEX风险仍在 |
| 地缘半导体+科技 -20% | -6,707.28 | 出口管制、台湾、关税是核心尾部风险 |

## 合规与费用审计

| 项目 | 结果 | 处理 |
|---|---|---|
| 整股 | 通过 | ANET 5 股，VRT 2 股 |
| 25%单股上限 | 通过 | MU约19.57%，MSFT约18.82%，均未超限 |
| VRT止损距离 | 通过 | 350入场、338止损，距离3.43% |
| 风险预算 | 通过 | VRT风险约34.20美元，约0.09%权益 |
| 现金 | 通过 | 卖ANET后可用现金 1,675.79，买VRT需 705.00 |
| 小仓低于5% | 工具失败但审计豁免 | starter 低于常规初始仓位是现金/风险受限结果 |
| 费用 | 通过 | 每笔 USD 5；ANET费用占成交额0.717%，VRT 0.714% |

## 否决条件

| 条件 | VRT | ANET |
|---|---|---|
| single_source_critical_data | 未触发 | 未触发 |
| stale_data | 未触发；当前价为 22:08 | 未触发；当前价为 22:07 |
| narrative_only_beneficiary | 未触发 | 不适用，卖出弱项 |
| valuation_assumes_best_case | 降权但未硬否决 | 不适用 |
| fomo_justified | 未触发，限价显著低于当前价 | 未触发 |
| inadequate_liquidity | 未触发 | 未触发 |
| sanctions_export_risk | 间接风险 | 间接风险 |
| stress_loss_exceeds_risk_budget | 未触发 | 未触发 |

## Post-trade 审计

若两单均成交：已实现 P&L -21.40，交易费用合计 10.00，交易后现金 970.79，交易后组合权益约 39,078.92。交易后剩余未实现 P&L 约 -2,032.89，已实现加未实现合计 -2,054.29。采用平均成本法；精确税务 lot 不可得。

## Hades 最终意见

批准执行，但只在价格边界内执行：

1. SELL ANET 5 @139.50 limit 或更优；低于 139.50 不追卖。
2. BUY VRT 2 @350.00 limit 或更优；成交后硬止损 338.00；不提高限价。
3. 不批准追买 MU/WDC/STX/AMD/SMH/SOXX/QQQ；不批准补 MSFT；不批准买入 INTC/FLEX。

