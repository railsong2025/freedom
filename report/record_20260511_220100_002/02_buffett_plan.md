# 02_buffett_plan

## 新一轮目标

在 2026-05-12 00:00:00 CST 前完成美股组合复盘、AI/强周期机会漏斗、P&L 风险审计和当前动作裁决。当前动作必须只包含可立即执行的整股 BUY/SELL，或明确写 `本次不买入、不卖出`。本轮优先判断已持 FLEX 是否继续持有、止损、止盈或不加仓；新增买入必须比持有 FLEX 或 ETF fallback 有更好的费用后正期望。

## 必须承接的复盘教训

| 复盘教训 | 本轮硬要求 |
|---|---|
| 上一轮文件夹非合规 | 本轮只写本地 Markdown 和 `local_result_snapshot.json`；禁止写 SQLite 和 `db_record.json` |
| FLEX 已进入持仓 | Poseidon/Hades 必须先判断 FLEX 的持有/止损/止盈/加仓，而不是默认再买 |
| MSFT 是最大亏损 | 不得用亏损本身作为补仓理由；必须判断云/AI thesis 是否恶化或只是估值/时机错误 |
| NVDA/AMD/SPY 已有 AI/风险资产盈利 | 新买不得重复堆同一 beta；必须证明利润池表达更优 |
| CLI 实时行情滞后 | Zeus 实时事实行情必须使用 financeBusiness；CLI 只作为历史指标和质量缺口 |
| 强势不等于 FOMO | 只有 R/R、止损、量价、现金、数据质量失败时才否决强势股 |

## 当前 P&L 必须贯穿下游

| Ticker | 当前未实现盈亏 | 下游必须回答 |
|---|---:|---|
| MSFT | -1,750.50 USD / -19.18% | 是可恢复的云/AI估值错配，还是 thesis 受损？是否需要止损/等待？ |
| TSM | -104.25 USD / -4.17% | 是否只是盘中弱势，还是半导体制造/地缘折价恶化？ |
| ANET | -8.40 USD / -1.18% | Q1 后下跌是否已反映估值过高，是否不应加仓？ |
| FLEX | +9.79 USD / +0.62% | 已成交 starter 是否继续有效？是否需要把止损/止盈规则重申？ |
| NVDA | +232.79 USD / +18.05% | 是否需要利润保护，还是继续持有？ |
| AMD | +39.15 USD / +9.47% | 追加强周期是否重复暴露？ |
| SPY | +177.27 USD / +8.70% | 组合已有市场 beta，是否降低新增 ETF 必要性？ |

## Zeus 情报任务

Zeus 必须读取：

- `00_metadata.md`
- `01_buffett_review.md`
- `02_buffett_plan.md`

Zeus 输出：`03_zeus_intelligence.md`。

### Zeus 必做事项

| 规划事项 | 具体要求 |
|---|---|
| 实时行情事实源 | 使用 financeBusiness `StockCurrentMarket` 作为事实实时行情；覆盖 KO、MSFT、NVDA、SPY、AMD、TSM、ANET、FLEX、MU、WDC、STX、INTC、VRT、DELL、SMH、SOXX、QQQ |
| 历史趋势 | 使用 financeBusiness `StockMarketList` 覆盖上述核心持仓/候选/ETF fallback；本地 CLI 仅作历史指标第二路径 |
| Python 工具记录 | 记录已运行 `indicators`、`quality`、`sector-map` 的命令、退出码、关键输出和缺口 |
| 数据质量 | 明确 akshare/CLI 对 2026-05-11 缺口，不能把它当实时事实行情 |
| 关键人物言论 | 补查 Fed/FOMC、Treasury/White House、AMD、ANET、DELL、Micron、NVIDIA、Intel、TSMC、Vertiv、hyperscaler 管理层 |
| 关键事件 | 补查 AMD Q1、ANET Q1、DELL AI server 指引、存储/HBM 供需、FOMC 最新声明、半导体/AI server 资金流与盘中反应 |
| AI 产业链 | 覆盖 AI 应用/云 CAPEX、GPU/ASIC、半导体制造、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、AI server/ODM/EMS、数据中心电力/散热、PCB/CCL、安全/数据基础设施、ETF/basket |
| 输出字段 | 每个核心交易候选至少给当前价、昨收、开盘、高低、涨跌幅、量比、成交量、成交额、更新时间、市场源、可否用于当前交易 |

### Zeus 验收门槛

缺少 financeBusiness 实时行情的标的，不得用于最终当前 BUY/SELL。若 CLI 与 financeBusiness 冲突，以 financeBusiness 实时行情为事实源，并把冲突写入 `数据冲突与缺口`。

## Poseidon 研究任务

Poseidon 必须读取 00-03，并输出 `04_poseidon_research.md`。

### Poseidon 必做事项

| 规划事项 | 具体要求 |
|---|---|
| P&L 使用 | 使用 `01_buffett_review.md` 当前 P&L 判断持有、止损、加仓、盈利保护和风险预算 |
| 板块地图 | 比较 broad market、semiconductor、memory/HBM、AI server/ODM、power/cooling、cloud/software、安全/数据基础设施 |
| AI 漏斗 | 不只看已有持仓；需分核心候选、战术候选、观察、回避/否决 |
| FLEX 复盘 | 判断已持 FLEX 是否继续持有、加仓、止盈、止损或等待；如果不加仓，说明 R/R |
| 强周期候选 | AMD、MU、WDC、STX、INTC、VRT、DELL、SMH、SOXX、QQQ 必须给 swing verdict |
| Python 工具 | 运行 pnl、score-sector、score-stock、score-short-term、rr、sizing、veto-check、swing-verdict、post-trade |
| 错误修正 | 说明是否纠正了关键人物遗漏、关键事件遗漏、把长期 thesis 当波段 setup、缺少二源和 R/R 的问题 |

### Poseidon 当前动作边界

若 FLEX 仍在止损之上但新增买入 R/R 不足，本轮应优先 `本次不买入、不卖出` 或只给 SELL 风控动作；不得把候选名单放进最终行动区。

## Hades 验证任务

Hades 必须读取 00-04，并输出 `05_hades_verification.md`。

### Hades 必做事项

| 审计项 | 要求 |
|---|---|
| P&L 审计 | 独立核验总盈亏、每股盈亏、现金折算假设 |
| 数据质量 | 审计 Zeus 是否把 financeBusiness 作为实时事实源，是否错误使用 stale CLI |
| 关键遗漏 | 审计关键人物、关键事件、分析错误是否已修正 |
| 交易合规 | 若有 BUY/SELL，检查整股、USD 5 费用、现金、25% 单股上限、止损、R/R |
| no-trade 证明 | 若最终无交易，验证每个核心/战术候选和 ETF fallback 均有等待/否决理由 |
| post-trade | 审计交易后预计盈亏；若无交易，也需确认交易后等同交易前且无新增费用 |

## 圆桌任务

圆桌必须在 00-05 文件齐全后写 `06_roundtable.md`，至少三轮讨论：

1. 事实校准：financeBusiness 实时行情、P&L、现金、CLI 缺口。
2. 投资与仓位：FLEX 是否持有/止损/止盈/加仓，是否新增 MU/WDC/STX/AMD/ETF。
3. 验证异议：Hades 对数据质量、R/R、现金和 no-chase 的裁决。

圆桌必须裁定 Buffett 自我反思是否有效，并把当前动作约束交给 `07_final_decision.md`。

## Final Decision 要求

`07_final_decision.md` 必须包含：

- `当前持仓盈亏复盘`
- `本次当前操作`
- `交易后预计盈亏`
- `下一次建议启动分析时间（北京时间）`
- `SQLite 写入：skipped_by_disabled_policy`

若本轮没有 BUY/SELL，`交易后预计盈亏` 仍需说明交易后等同交易前：无已实现盈亏、无费用、现金和持仓不变。
