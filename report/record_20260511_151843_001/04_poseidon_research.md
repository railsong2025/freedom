# 04_poseidon_research

## 输入与任务范围

- 任务目录：`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001`。
- 已读取上游：`00_metadata.md`、`01_buffett_review.md`、`02_buffett_plan.md`、`03_zeus_intelligence.md`。
- 策略：美股强周期波段交易；默认数日至数周；当前操作只允许整股 BUY/SELL。
- 组合背景：USD 持仓市值 $17,178.14，成本 $18,405.81，未实现盈亏 -$1,227.67（-6.67%）；可换汇现金按 7.8293 折算约 $13,252.01；组合背景权益约 $30,430.15。

## Buffett 规划执行情况

| 要求 | 执行状态 | 研究结论 |
|---|---|---|
| 引用 P&L | 已执行 | MSFT 接近 25% 上限，不再加；AI 新仓必须小仓、低风险 |
| 先做板块地图 | 已执行 | 半导体/AI 基建 tactical overweight |
| AI 链条上中下游覆盖 | 已执行 | 存储/HBM、半导体、AI 服务器/ODM 最强 |
| 回应自我反思 | 已执行 | 不能因为涨幅大一律否决；必须给可审计 starter 或 no-trade proof |
| Python CLI | 已执行 | P&L、评分、R/R、sizing、veto、swing-verdict、post-trade 均已运行 |

## Python 工具调用记录

| 命令 | 退出码 | 关键输出 |
|---|---:|---|
| `python3 workspace/analysis/cli.py pnl --portfolio-file report/.../portfolio_usd_for_test.md --prices ...` | 0 | 总市值 $17,178.14，总成本 $18,405.81，未实现盈亏 -$1,227.67，总权益 $30,430.15。 |
| `python3 workspace/analysis/cli.py score-sector --sector AI_infrastructure --factors ...` | 0 | weighted_score=74.40，rating=`tactical_overweight`。 |
| `python3 workspace/analysis/cli.py score-stock --symbol FLEX --factors ...` | 0 | weighted_score=71.45，tier=`tactical`。 |
| `python3 workspace/analysis/cli.py score-short-term --symbol FLEX --factors ...` | 0 | weighted_score=77.40，action_bias=`tactical_only`。 |
| `python3 workspace/analysis/cli.py rr --symbol FLEX --entry 142.17 --stop 135.10 --target 154.00 --target-2 164.00 --shares 11` | 0 | target1 R/R=1.3394 marginal；target2 R/R=2.5771 positive_expectancy；break-even=143.0882。 |
| `python3 workspace/analysis/cli.py sizing --equity 30430.15 --entry 142.17 --stop 135.10 --risk-pct 2 --cash 13252.01` | 0 | 风险预算最大股数 83、现金足够；该工具按最大风险股数给 38.78% 仓位，研究采用 11 股以满足 5.14% starter 和 25% 上限。 |
| `python3 workspace/analysis/cli.py veto-check --symbol FLEX ...` | 0 | no triggered vetoes。 |
| `python3 workspace/analysis/cli.py swing-verdict --symbol FLEX ...` | 0 | verdict=`small_starter`，reason=`setup supports a starter but not a full current trade`。 |
| `python3 workspace/analysis/cli.py post-trade --portfolio-file report/.../portfolio_usd_for_test.md --trades FLEX:BUY:11:142.17 --markdown` | 0 | 交易后现金 $11,683.14，交易后持仓市值 $18,742.01，交易后权益 $30,425.15。 |

## 美股板块地图

| 板块/代理 | 证据 | 评分 | 结论 |
|---|---|---:|---|
| 半导体/AI 基建 | SMH +4.90%、SOXX +5.67%，五日约 +11.79%/+12.60% | 74.40 | tactical_overweight |
| 存储/HBM | MU +15.49%、WDC +3.47%、STX +2.11%；HBM/DRAM 事件强 | 82 | 最强，但高位风险大 |
| AI 服务器/ODM | DELL +13.11%、FLEX +6.89%；订单链催化 | 78 | 可小仓表达 |
| 云/应用 | MSFT -1.34%、AMZN +0.56%、PLTR +0.55% | 58 | 不是本轮最强波段 |
| 网络/光模块 | ANET +0.01% 但五日 -17.87% | 42 | 等待修复 |
| 防御消费 | KO 基本持平 | 45 | 保留，非新增方向 |

## AI 产业链机会漏斗

| 环节 | 代表 | 直接/间接受益 | 当前波段状态 | 研究处理 |
|---|---|---|---|---|
| 存储/HBM | MU/WDC/STX | 直接受益，供需和价格弹性最高 | MU 过热；WDC/STX 强 | 等待回撤，不当前追 |
| GPU/ASIC | NVDA/AMD/AVGO | 直接受益 | AMD/NVDA 强 | 已有 AMD/NVDA，避免追新仓 |
| 晶圆代工/制造 | TSM/INTC | TSM 直接；INTC 事件驱动 | TSM 弱，INTC 高波动 | TSM 持有；INTC 等待 |
| 服务器/ODM | DELL/FLEX/JBL/CLS | 订单链直接受益 | FLEX 放量突破且价位可控 | FLEX 小仓 starter |
| 电力散热 | VRT/ETN/PWR/GEV | CAPEX 直接受益 | VRT 回撤无量 | 等待 |
| 网络 | ANET/CIEN/COHR/LITE | AI networking 受益 | ANET 财报后弱 | 不加仓 |
| ETF/basket | SMH/SOXX/QQQ | 分散表达 | 强但 ETF 量比字段缺失 | 作为代理，不做当前 BUY |

## 当前盈亏与仓位含义

- MSFT 市值 $7,472.16，占背景权益约 24.56%，且亏损 -18.12%；当前不追加 MSFT，也不机械止损，先用后续财报/趋势确认。
- NVDA、AMD 已有盈利，代表 GPU/AI beta；若继续加 AMD/MU，组合强周期波动会快速上升。
- ANET 和 TSM 小幅亏损，不因亏损补仓；ANET 财报后相对弱，必须等待修复。
- 可换汇现金约 $13,252.01，足以做 5%-8% starter；小仓的目的不是保证盈利，而是把“错过强周期”的风险转化为可控试错。

## 关键人物言论采纳与投资含义

- Fed/Powell 与利率路径：属于估值背景变量，不是买入催化；若利率预期转鹰，应降低科技 beta。
- AMD management/IR：Q1 revenue $10.3B 与 AI demand 相关催化支持 AI accelerator 链，但 AMD 当日 +11.44%，不追加新仓。
- ANET management：收入增长强但市场反应弱，说明利润率/指引担忧压过 AI networking 叙事。
- Dell/AI server guide：订单链催化支撑 DELL/FLEX；DELL 跳空更大，FLEX 以小仓 starter 表达更合理。

## 强周期波段交易计划

| 候选 | 入场类型 | 限价 | 止损 | 第一止盈 | 第二止盈 | 移动止损 | 最长持有期 | 股数 | 风险金额 | 费用后 R/R |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---|
| FLEX | 动能突破后的轻回撤/收盘确认 starter | 142.17 | 135.10 | 154.00 | 164.00 | 触及 154 后止损抬至 143.10；若回落破 10日线或 135.10 立即退出 | 10 个交易日 | 11 | $88.87 | 1.34 / 2.58 |
| AMD | 动能突破 | 不追 | 428 下方 | 480 | 510 | 已有 1 股跟踪 | 5-10 日 | 0 | N/A | 等待回撤 |
| MU | 动能突破 | 不追 | 690 下方 | 800 | 860 | 等待 1-2 日消化 | 5-10 日 | 0 | N/A | 过热 |
| DELL | 动能突破 | 不追 | 242 下方 | 280 | 300 | 等待回撤承接 | 5-10 日 | 0 | N/A | 跳空过大 |
| VRT | 回撤承接 | 不当前 | 330 下方 | 360 | 375 | 缺量确认 | 10 日 | 0 | N/A | 等待 |

## 错过机会修正与当前 starter 方案

上一轮本地 record 不存在，不能归因“当时为何没买”。但当前流程必须修正潜在过度保守：强周期 leadership 明确时，不能因个股已上涨就全部否决。FLEX starter 的作用是用 5.14% 背景权益暴露换取 AI server/ODM 链参与权；若判断错误，硬止损把风险控制在约 $88.87，约组合权益 0.29%。

## 仓位升级阶梯与大幅盈利路径

| 档位 | 触发条件 | 仓位 | 风险控制 |
|---|---|---:|---|
| 第一档 starter | FLEX 限价 142.17 成交；不高于 break-even 143.09 追价 | 11 股，约 5.14% 权益 | 止损 135.10 |
| 第二档确认加仓 | FLEX 收盘站稳 154 且成交量继续高于 20日均量，止损抬至 143.10 | 可再评估加至 8%-10% 单票 | 新增风险由浮盈垫吸收 |
| 第三档利润滚动 | 触及 164 后仍强于 SMH/SOXX，且组合已有浮盈 | 只用浮盈滚动，不新增无保护风险 | 移动止损跟随 5日线/前低 |

## 候选动作对照表

| 候选 | 短线分数 | 入场类型 | 限价 | 止损 | 第一/第二目标 | 数据质量 | Hades 预期 | swing verdict | 最终动作 |
|---|---:|---|---:|---:|---|---|---|---|---|
| FLEX | 77.40 | 动能突破 starter | 142.17 | 135.10 | 154/164 | MCP 字段完整，独立价格源缺 | 有条件批准 | small_starter | BUY 11 |
| AMD | 82 估算 | 动能突破 | N/A | N/A | N/A | 完整 | 等待 | wait | 不加仓 |
| MU | 85 估算 | 动能突破 | N/A | N/A | N/A | 完整 | 等待 | wait | 不追 |
| DELL | 81 估算 | 动能突破 | N/A | N/A | N/A | 完整 | 等待 | wait | 不追 |
| SMH/SOXX | 78 估算 | ETF basket | N/A | N/A | N/A | 量比缺失 | 不作为当前 BUY | wait | 仅代理观察 |

## 趋势预测

- 1-5 个交易日：半导体/AI server 仍可能强于 SPY；但高位跳空股回撤概率上升。FLEX 若守住 135.10 并继续站上 142 附近，倾向延续到 154。
- 2-6 周：AI capex、存储/HBM 和服务器链仍是正预期主线，但估值和拥挤度要求分阶段暴露。
- 失效条件：FLEX 跌破 135.10、成交量萎缩且回到 133.01 下方、AI server/semiconductor ETF 同步破位、或 Fed/宏观导致科技 beta 快速去风险。

## 研究结论

Poseidon 建议本轮执行一个小仓 starter：`BUY FLEX 11 股，限价 142.17，USD 5 费用，止损 135.10，第一止盈 154，第二止盈 164`。这不是满仓追高，而是用可审计的费用后正期望和硬止损，修正“强周期永远无有效建议”的问题。

