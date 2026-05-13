# Buffett 新一轮任务计划 — 美股组合

## 决策目标

在 2026-05-13 00:00:00 北京时间前，基于当前美股组合、P&L、AI链行情、现金和费用，给出仅限本次可执行的整股 BUY/SELL，或明确 `本次不买入、不卖出`。

## 规划执行总表

| 阶段 | 负责人 | 必须完成 | 验收标准 |
|---|---|---|---|
| Zeus | 情报数据部 | financeBusiness 当前/历史行情、指数/ETF代理、AI CAPEX、管理层/政策/宏观事件、AI链漏斗 | 覆盖持仓、特殊关注、SMH/SOXX/QQQ；列出来源时间、置信度、反证和缺口 |
| Poseidon | 投资研究部 | 市场/板块评分、AI链分层、候选评分、VRT/ANET/MU等 swing verdict、仓位与R/R | 先板块后个股；必须使用当前 P&L；当前交易必须有整股、限价、止损、止盈、费用 |
| Hades | 决策验证部 | P&L审计、压力测试、合规、费用、现金、整股、交易后P&L、遗漏修正审计 | 明确批准/有条件批准/否决；不能只因上涨否决，也不能忽略小仓费用 |
| Roundtable | Buffett + 三部负责人 | 讨论分歧并形成当前操作 | 最终行动区只列本次当前 BUY/SELL，不列观察名单或未来条件单 |

## Zeus 任务合同

| 情报问题 | 交付要求 |
|---|---|
| 当前行情 | 对 AMD, ANET, FLEX, INTC, KO, MSFT, MU, NVDA, SPY, TSM, WDC, STX, VRT, SMH, SOXX, QQQ, AVGO, ASML, AMAT, MRVL 运行 `StockCurrentMarket` 与 `StockMarketList` 或记录覆盖缺口 |
| 市场背景 | IXIC 用 `StockIndexList`；SPX/GSPC/INX/SP500 若返回空则记录缺口，并用 SPY 作可交易代理 |
| AI链 | 覆盖 AI应用/云CAPEX、GPU/ASIC、半导体、存储/HBM、先进封装、光/网络、AI服务器、数据中心电力/散热、PCB/CCL、设备、材料、安全/数据基础设施 |
| 关键人物/事件 | Fed/FOMC、白宫/商务部、Intel CEO/CFO、NVIDIA/AMD/MU/TSM/云厂商管理层；记录来源、时间、影响链、反证 |
| Python工具 | 运行 `indicators`, `quality`, `sector-map`，即使本地 CSV 不完整也必须记录输出和限制 |

## Poseidon 任务合同

| 研究问题 | 交付要求 |
|---|---|
| P&L如何影响仓位 | 区分 MSFT 大额浮亏、NVDA盈利、ANET弱势小亏、MU/WDC接近成本但波动大 |
| 哪个板块最适合当前表达 | 给出 sector score、rating、直接/间接受益、估值与拥挤 |
| 哪些候选可交易 | 对 VRT、MU、WDC、STX、AMD、INTC、ANET、SMH/SOXX/QQQ 给出 tier 或 no-trade proof |
| 当前交易草案 | 每笔必须整股、限价、USD 5 fee、fee%、现金影响、止损、目标、移动止损、最大持有期 |
| Python工具 | 运行 P&L、sector score、stock score、short-term score、R/R、sizing、veto、swing-verdict、post-trade |

## Hades 任务合同

| 审计问题 | 交付要求 |
|---|---|
| 数据质量 | 审计 financeBusiness 当前/历史一致性、aiwebsearch来源层级、本地 CLI 缺口 |
| 数学正确性 | 审计当前 P&L、交易费用、现金、交易后 P&L |
| 风控 | 审计 25% 单股上限、2%风险预算、VRT stop、ANET sell、强周期集中度 |
| 压力测试 | 运行组合、半导体、地缘/政策压力情景 |
| 最终意见 | 对每笔交易给出批准/小仓starter/等待/否决，并列出硬性失效条件 |

## 当前硬约束

| 约束 | 内容 |
|---|---|
| 交易截止 | 2026-05-13 00:00:00 北京时间 |
| 手续费 | 每笔 USD 5 |
| 股数 | 禁止碎股 |
| 单股上限 | 不超过组合权益 25% |
| 当前现金 | 7700 港元，按 HKD/USD 0.1277 折约 983.29 美元 |
| SQLite | 只读交叉检查；不得写入 |
