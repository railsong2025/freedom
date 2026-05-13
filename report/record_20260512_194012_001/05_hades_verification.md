# Hades 验证报告 — 美股组合当前操作审计

## 输入与审计范围

已读取 `00_metadata.md` 至 `04_poseidon_research.md`，并审计 `base_short.md` 与衍生 `portfolio_usd_working.md`。审计范围包括数据质量、P&L、压力测试、合规、费用、现金、整股、限价、止损、交易后P&L与遗漏修正。

## 审计结论

顶层结论：`有条件同意`。当前交易结论：`批准小仓 starter` 买入 VRT 2 股，同时批准卖出 ANET 5 股作为弱项风控。条件是：必须在 2026-05-13 00:00:00 北京时间前，按限价或更优成交；VRT 不得上调限价追买；ANET 不得向下追卖。

## 请求/规划执行情况


| 计划项        | 审计状态   | 说明                                                                  |
| --------------- | ------------ | ----------------------------------------------------------------------- |
| 上游完整性    | 通过       | 00-04 文件存在且相互引用                                              |
| P&L使用       | 通过       | Poseidon 用 MSFT/ANET/MU/WDC 等盈亏区分卖出、持有和不追买             |
| 关键人物/事件 | 有条件通过 | Intel/White House/AI CAPEX覆盖；Fed与其他公司管理层覆盖不够细，已降权 |
| 当前交易      | 有条件通过 | VRT是小仓 starter，ANET为弱项退出                                     |
| post-trade    | 通过       | 工具审计通过                                                          |

## Python 工具调用记录


| 命令                                                                                   | exit | 关键输出                                                                              |
| ---------------------------------------------------------------------------------------- | -----: | --------------------------------------------------------------------------------------- |
| `verification/cli.py audit-pnl --portfolio-file portfolio_usd_working.md --prices ...` |    0 | passed=true；total_cost_basis 40,149.92；total_market_value 38,993.91                 |
| `verification/cli.py stress-test --portfolio-file ...`                                 |    0 | 半导体 -15% 冲击约 -3,808.88；地缘半导体+科技 -20% 冲击约 -6,883.24                   |
| `verification/cli.py compliance ... ANET SELL 5 / VRT BUY 2 --stops VRT:349`           |    0 | 18/20 通过；2项失败均为仓位小于5%初始区间                                             |
| `verification/cli.py audit-post-trade ...`                                             |    0 | fee audit passed；pnl audit passed；realized_pnl -38.90；fees 10.00；post_cash 923.29 |

## 上游报告完整性审计

Zeus 有完整情报表和来源清单，但本地 indicators/quality 未拿到 CSV 数据；该缺口不能用来否定 financeBusiness MCP 当前/历史行情，但会降低 MA/ATR/自动相对强弱的精度。Poseidon 没有把工具缺口隐藏成精确技术指标，处理合格。

## 数据质量审计


| 项目      | 结论                                                           |
| ----------- | ---------------------------------------------------------------- |
| price/P&L | financeBusiness 当前价与历史最新收盘一致，可用                 |
| ETF量比   | SPY/SMH/SOXX source volumeRatio 缺失，非阻断                   |
| 新闻/公告 | Intel与White House为高等级来源；AI CAPEX新闻和二级媒体为中等级 |
| 本地工具  | indicators/quality 输出 no_local_data，必须在最终文件中披露    |

## 当前盈亏审计

P&L 数学通过。当前美股市值 38,993.91，成本 40,149.92，未实现亏损 -1,156.01，亏损率 -2.88%。MSFT 最大亏损但仓位未超限；ANET亏损小但相对弱势；MU/WDC接近成本且波动过强，不适合补仓追涨。

## 压力测试


| 情景                 |  组合影响 | 审计含义                              |
| ---------------------- | ----------: | --------------------------------------- |
| 全组合 -10%          | -3,899.39 | 可承受但现金垫薄                      |
| 全组合 -20%          | -7,798.78 | 半导体暴露会放大回撤                  |
| 半导体 -15%          | -3,808.88 | 主要风险来自 MU/AMD/WDC/INTC/NVDA/TSM |
| 科技 -15%            | -1,353.55 | MSFT是主要贡献                        |
| 地缘半导体+科技 -20% | -6,883.24 | 出口管制/台湾/关税是组合核心尾部风险  |

## 合规与仓位审计


| 项目           | 结果               | 处理                                           |
| ---------------- | -------------------- | ------------------------------------------------ |
| 整股           | 通过               | ANET 5 股，VRT 2 股                            |
| 单股25%上限    | 通过               | MU约19.89%，MSFT约18.58%，均未超限             |
| VRT止损        | 通过               | 365入场、349止损，距离4.38%，风险约42.20美元   |
| 现金           | 通过               | 卖ANET后可用现金1658.29，买VRT需735.00         |
| 小仓低于5%     | 工具失败但审计豁免 | 这是现金受限、风险受限的 starter，不是风险放大 |
| ANET sell stop | 不适用             | 卖出弱项不需要买入式止损；无向下追卖           |

## 否决条件检查


| 条件                            | VRT                              | ANET     |
| --------------------------------- | ---------------------------------- | ---------- |
| single_source_critical_data     | 未触发                           | 未触发   |
| stale_data                      | 未触发                           | 未触发   |
| narrative_only_beneficiary      | 未触发                           | 未触发   |
| valuation_assumes_best_case     | 未触发，但降权                   | 不适用   |
| fomo_justified                  | 未触发，因限价低于当前价且有止损 | 不适用   |
| inadequate_liquidity            | 未触发                           | 未触发   |
| sanctions/export risk           | 间接风险，非硬否决               | 间接风险 |
| stress_loss_exceeds_risk_budget | 未触发                           | 未触发   |

## 波段风控审计

VRT 的 `swing-verdict` 为 `small_starter`，而非 `current_trade`。Hades认可这个分级：价格强、量比1.42、链条直接，但单日涨幅大且估值贵，必须小仓、限价、硬止损。ANET 的 `swing-verdict` 为 `hard_veto`，原因是相对强弱和费用后R/R不足，卖出弱项合理。

## 交易后预计盈亏审计

`audit-post-trade` 通过。若 ANET 以 136.00 卖出、VRT 以 365.00 买入，费用合计 10.00，预计已实现 P&L -38.90，交易后现金 923.29，交易后组合权益约 39,965.05。采用平均成本法。

## 最终验证意见

批准：

1. SELL ANET 5 @ 136.00 limit，USD 5 fee。
2. BUY VRT 2 @ 365.00 limit，USD 5 fee，stop 349.00，target 399.00/420.00。

否决/限制：

1. 不追买 MU/WDC/STX/AMD/SMH/SOXX/QQQ，因为组合已有高 AI链暴露且价格过热。
2. 不补 MSFT，因为亏损未等于安全边际，且趋势未确认。
3. 超过截止时间或限价无法成交，当前操作自动失效。
