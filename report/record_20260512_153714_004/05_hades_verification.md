# 05_hades_verification

## 审计范围

Hades 已读取 00/01/02/03/04，并审计 P&L、数据质量、候选覆盖、费用后 R/R、止损、现金、单股 25% 上限、关键事件、指数代理和最终交易可执行性。

## Python 工具调用记录

| 工具 | 命令 | 结果 |
|---|---|---|
| P&L 审计 | `python3 workspace/verification/cli.py audit-pnl --portfolio-file base_short.md --prices ... --cash 21157.74` | `passed=true`；USD 持仓成本 19,976.83、市值 18,705.61。 |
| 压力测试 | `python3 workspace/verification/cli.py stress-test --portfolio-file base_short.md --prices ...` | 20 个场景；-20% 全组合冲击约 -3,741.12；半导体 -15% 冲击约 -765.64；科技 -15% 冲击约 -1,353.55；地缘半导体+科技 -20% 冲击约 -2,825.58。 |
| 合规检查 | `python3 workspace/verification/cli.py compliance --portfolio-file base_short.md --prices ... --cash 21157.74 --equity 39863.35` | 8/8 通过；最大单股 MSFT 18.63%，低于 25% 上限。 |
| 交易后审计 | `python3 workspace/verification/cli.py audit-post-trade --portfolio-file base_short.md --prices ... --cash 21157.74` | 无交易时 realized P&L=0、fees=0、remaining_cash=21,157.74；工具字段 `post_trade_equity` 只回传持仓市值 18,705.61，最终报告需手工加现金得 39,863.35。 |

## P&L 审计

| 项目 | 金额 |
|---|---:|
| 当前 USD 持仓市值 | $18,705.61 |
| 当前 USD 成本 | $19,976.83 |
| 当前未实现盈亏 | $-1,271.22 |
| 当前未实现盈亏率 | -6.36% |
| 背景现金折算 | $21,157.74 |
| 估算组合权益 | $39,863.35 |

审计意见：P&L 自洽。腾讯港股因 HKD 持仓不属于本轮美股操作，不进入 USD 当前交易 P&L；现金仅作背景可用资金，不生成港股建议。

## 数据质量审计

| 项目 | 状态 | 审计结论 |
|---|---|---|
| financeBusiness current | 持仓和重点候选可用 | 允许用于 P&L 和当前价格背景 |
| financeBusiness history | 当前持仓、INTC/MU/VRT/DELL/QQQ/SMH/SOXX 可用；WDC/STX 本轮只取当前价 | WDC/STX 不得成为当前交易 |
| IXIC 指数 | 可用 | 可用于纳指 regime |
| SPX 指数 | 返回 `{}` | 不能使用指数点位；只能用 SPY 代理 |
| SPY/QQQ 代理 | 当前和历史可用 | 修复有效；可作为 no-trade proof 的 fallback |
| Zeus CLI | 无预取时字段失败 | 不阻断直接 MCP，但降低当前交易置信度 |
| aiwebsearch/searchJumps | object URL 成功，字符串数组失败 | 工具 schema 与服务实现不一致，需记录 |

## 候选与 Hades 裁决

| 候选 | 上游分层 | 主要风险 | Hades 裁决 |
|---|---|---|---|
| NVDA | 核心/持仓 | 费用后 R/R 仅 marginal，未有开盘后量价确认 | 等待；不批准新增 |
| AMD | 核心/持仓 | 2% 风险预算会推高到超 25% 单股上限，当前 R/R marginal | 等待；不批准新增 |
| SMH | ETF fallback | 第二目标 marginal，当前无量价确认 | 等待 |
| SOXX | ETF fallback | 第二目标 marginal，当前无量价确认 | 等待 |
| QQQ | 纳指 fallback | 第二目标 marginal，当前无量价确认 | 等待 |
| SPY | 标普 fallback/持仓 | 已有持仓且 broad market 接近高位 | 等待 |
| FLEX | 持仓 | 费用后 R/R insufficient，已有仓位刚修复 | 否决加仓，保留 |
| MSFT | 持仓亏损 | 最大亏损，不能补仓摊成本 | 等待，不加仓 |
| TSM | 持仓 | 弱于半导体 ETF | 等待 |
| ANET | 持仓 | 单日 -3.77%，趋势转弱 | 等待 |
| INTC | 特别观察 | EPS/PE 为负、转型与政策兑现不确定，R/R insufficient | 当前买入否决 |
| MU/WDC/STX | 存储强势 | 单日涨幅大、追价风险、WDC/STX 历史未补齐 | 等待，不买 |
| VRT | 电力/散热 | 单日 +8.22%，估值/拥挤度高 | 等待，不买 |
| DELL | 服务器 | 单日 -5.15%，趋势分歧 | 不买 |

## 压力测试与风险

- 全组合 -20% 冲击约 -3,741.12 美元，会把当前未实现亏损扩大到约 -5,012.34 美元。
- 半导体 -15% 冲击约 -765.64 美元，说明已有 NVDA/AMD/TSM/ANET 暴露不低。
- 科技 -15% 冲击约 -1,353.55 美元，主要来自 MSFT。
- 地缘半导体+科技 -20% 冲击约 -2,825.58 美元，Hades 将其视为本轮最重要的宏观/地缘压力场景。

## 关键遗漏与错误修正审计

- 关键人物讲话：Zeus 已补 Microsoft、NVIDIA、Vertiv 官方证据；仍缺 Fed、BIS/USTR、TSMC/AMD/Arista/Micron 最新管理层逐条讲话，因此当前交易降权。
- 关键事件：已补 AI 云、Rubin、数据中心电力散热、存储强势新闻；仍缺完整 SEC/IR 文件列表，因此不得扩大到未取行情标的。
- 分析错误：Poseidon 已承认上一轮 AI 全链覆盖不足，也没有把“上涨多”作为唯一否决；本轮否决依据为交易窗口、R/R、开盘确认、数据闭环和仓位上限。

## 合规结论

- 单股 25% 上限通过：MSFT 18.63% 为最大。
- 当前无 BUY/SELL，交易费用为 0，现金不变。
- 若新增 AMD 27 股以匹配 2% 风险预算，会超过单股 25% 上限，因此禁止。
- 若最终报告输出任何 BUY/SELL，必须重新附 USD 5 费用、限价、整股、止损、止盈和交易后 P&L；当前上游没有合格交易。

## Hades 最终裁决

`本轮不批准当前 BUY/SELL`。批准保留现有仓位，批准下一次在北京时间 2026-05-12 22:30 以后重新刷新盘中数据。Hades 要求 06/07 写清 no-trade proof，并在 `交易后预计盈亏` 中手工修正组合权益为“持仓市值 + 现金”。
