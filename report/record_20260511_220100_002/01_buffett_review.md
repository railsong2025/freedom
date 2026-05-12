# 01_buffett_review

## 复盘范围与历史模式

| 项目 | 结论 |
|---|---|
| history mode | reviewed_with_noncompliant_prior_background |
| 本轮任务 | `buffett开始` 美股组合复盘与当前整股 BUY/SELL 决策 |
| 主输入 | 根目录 `base_short.md` |
| 上一轮本地文件夹 | `report/record_20260511_151843_001` |
| 合规性 | 非合规主记录：缺 `local_result_snapshot.json` 且含 `db_record.json` |
| SQLite 交叉参考 | 已只读查询 `decision_db.py last --task-type portfolio_review --subject us_equity_portfolio` |
| 当前行情事实源 | financeBusiness `StockCurrentMarket` 2026-05-11 21:56:59-21:57:48 CST |
| 第二路径状态 | 本地 `indicators/quality` 只取到 akshare 2026-05-08 日线；不可作为实时事实行情 |

本轮按新规则不把上一轮 `record_20260511_151843_001` 当作合规主历史，因为它没有 `local_result_snapshot.json` 且存在 `db_record.json`。但它仍可作为非合规背景：上一轮最终文件和 SQLite 只读索引均显示建议 `BUY FLEX 11 股，限价 142.17，止损 135.10，第一目标 154，第二目标 164`。当前 `base_short.md` 已列入 `FLEX:11股，成本142.82美元`，因此本轮按 FLEX 已成为当前美股持仓处理；若该成本来自手动编辑而非真实成交，P&L 精度需以券商成交记录复核。

## 当前持仓与现金背景

根目录 `base_short.md` 当前显示：

| 资产 | 股数 | 成本 | 币种 | 本轮处理 |
|---|---:|---:|---|---|
| 腾讯控股 | 400 | 549.00 | HKD | 背景，不给港股交易建议 |
| KO | 30 | 77.52 | USD | 美股持仓 |
| MSFT | 18 | 506.96 | USD | 美股持仓 |
| NVDA | 7 | 184.23 | USD | 美股持仓 |
| SPY | 3 | 679.31 | USD | 美股 ETF |
| AMD | 1 | 413.23 | USD | 美股持仓 |
| TSM | 6 | 416.71 | USD | 美股持仓 |
| ANET | 5 | 142.78 | USD | 美股持仓 |
| FLEX | 11 | 142.82 | USD | 美股持仓 |
| 可用资金 | 165,627 | - | HKD | financeBusiness 汇率估算约 21,167.13 USD，实际需券商换汇确认 |

financeBusiness `SettleAccount` 2026-05-11 09:15:00：HKD/USD=0.1278，USD/HKD=7.828。现金估算只用于风险预算，不代表券商已完成换汇。

## 当前持仓盈亏复盘

P&L 使用 financeBusiness `StockCurrentMarket` 盘中价。港股腾讯不并入美元组合盈亏。

| Ticker | 股数 | 成本价 | financeBusiness 最新价 | 市值 | 成本额 | 未实现盈亏 | 未实现盈亏率 | 盘中状态 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| KO | 30 | 77.52 | 78.25 | 2,347.50 | 2,325.60 | 21.90 | 0.94% | 交易中，量比 1.42 |
| MSFT | 18 | 506.96 | 409.71 | 7,374.78 | 9,125.28 | -1,750.50 | -19.18% | 交易中，量比 3.16 |
| NVDA | 7 | 184.23 | 217.485 | 1,522.39 | 1,289.61 | 232.79 | 18.05% | 交易中，量比 3.27 |
| SPY | 3 | 679.31 | 738.40 | 2,215.20 | 2,037.93 | 177.27 | 8.70% | 交易中，ETF 量比缺失 |
| AMD | 1 | 413.23 | 452.38 | 452.38 | 413.23 | 39.15 | 9.47% | 交易中，量比 3.00 |
| TSM | 6 | 416.71 | 399.335 | 2,396.01 | 2,500.26 | -104.25 | -4.17% | 交易中，量比 3.96 |
| ANET | 5 | 142.78 | 141.10 | 705.50 | 713.90 | -8.40 | -1.18% | 交易中，量比 1.31 |
| FLEX | 11 | 142.82 | 143.71 | 1,580.81 | 1,571.02 | 9.79 | 0.62% | 交易中，量比 1.34 |
| **合计** |  |  |  | **18,594.57** | **19,976.83** | **-1,382.26** | **-6.92%** | 不含港股与未换汇现金 |

估算背景权益：美股持仓市值 18,594.57 USD + HKD 现金折算 21,167.13 USD = 39,761.70 USD。此权益不是券商确认净值，主要用于本轮仓位和风险预算。

## 上一轮建议与当前结果

| 上一轮项目 | 内容 |
|---|---|
| 上一轮非合规本地文件 | `report/record_20260511_151843_001/07_final_decision.md` |
| 上一轮只读 SQLite 记录 | id=22，created_at=2026-05-11T15:32:42 |
| prior action | `BUY FLEX 11 shares at 142.17 limit` |
| prior stop/targets | stop 135.10；target 1 154；target 2 164 |
| 当前 base_short 状态 | 已出现 FLEX 11 股，成本 142.82 |
| 当前 FLEX 盘中价 | 143.71，较成本 +0.62% |
| outcome classification | mixed / unreviewed：方向暂正确，但目标未触达，成交细节与券商现金未核验 |

初步评价：上一轮“AI server/ODM 小仓 starter”目前没有失败，FLEX 盘中略高于成本，但其上涨后的 R/R 已变差；本轮必须避免把上一轮 starter 变成追价加仓。FLEX 若无法继续站稳 142-144 区间或跌破上一轮止损 135.10，必须退出或等待，而不是用长期 AI 服务器叙事拖延止损。

## 已发现的关键风险

| 风险 | 事实依据 | 对本轮影响 |
|---|---|---|
| MSFT 大额亏损与仓位集中 | MSFT 市值 7,374.78 USD，占估算美股持仓市值 39.7%，未实现亏损 -1,750.50 USD | 不得机械补仓摊低；除非云/AI 与技术面同步修复，否则只能持有观察或另设止损 |
| FLEX 刚买入后不宜追高 | FLEX 成本 142.82，盘中 143.71；上一轮限价 142.17 已被抬高 | 本轮加仓必须有新的突破/回撤承接证据，不能因小浮盈追买 |
| AMD/MU/WDC/STX 强但过热 | financeBusiness 显示 MU +3.46%、WDC +6.01%、STX +3.90%、AMD 盘中先冲高后回落 | AI/存储方向是强链条，但新开仓需 R/R 和止损通过 |
| TSM/ANET 弱于半导体链 | TSM -3.00%，ANET -0.47%；ANET 仍低于成本 | 不机械卖出，但不能作为当前加仓优先 |
| 本地 CLI 实时质量缺口 | `quality` 显示 akshare 日线滞后 3 天，缺 2026-05-11 | Zeus 实时事实行情必须使用 financeBusiness；CLI 只做历史指标参考 |

## Buffett 自我反思

### 依据的最新数据

- financeBusiness 2026-05-11 21:56:59-21:58:41 CST 给出当前事实行情：FLEX 143.71、AMD 452.38、MU 772.64、WDC 508.84、STX 813.20、INTC 126.715、VRT 356.88、DELL 248.00、SMH 569.175、SOXX 523.89、QQQ 710.88。
- 当前美元持仓总市值 18,594.57 USD，成本 19,976.83 USD，未实现亏损 -1,382.26 USD（-6.92%）。
- 最大未实现亏损：MSFT -1,750.50 USD（-19.18%）。
- 最大未实现收益：NVDA +232.79 USD（+18.05%），SPY +177.27 USD（+8.70%）。
- 可投资现金背景：165,627 HKD，按 financeBusiness HKD/USD=0.1278 折算约 21,167.13 USD；真实美股现金可用性需券商确认。
- 第二来源缺口：本地 CLI 只能给出 2026-05-08 日线指标并标记 2026-05-11 缺失，因此不能用作当前事实行情。

### 依据的历史决策

- 上一轮同类本地文件夹：`report/record_20260511_151843_001`。
- 文件夹格式：record-format，但非合规主历史，因为缺 `local_result_snapshot.json` 且含 `db_record.json`。
- 只读 SQLite 交叉参考：task_key `portfolio_review:993c7d93e383`，上一轮建议 `BUY FLEX 11 shares at 142.17 limit`，止损 135.10，目标 154/164。
- 历史决策与当前状态：当前 `base_short.md` 已包含 FLEX 11 股，成本 142.82；这与上一轮 BUY FLEX 方向一致，但成交价与上一轮限价不完全一致，需用券商记录确认。
- 上一轮关键问题：报告仍写了 `db_record.json`，违反本轮最新本地结果存储合同；本轮必须改用 `local_result_snapshot.json`。

### 关键遗漏与分析错误复盘

| 检查类别 | 复盘结论 | 本轮修正 |
|---|---|---|
| missed key-person remarks | 上一轮对 Fed/FOMC、AMD/ANET 管理层、hyperscaler CAPEX、AI server 供应链言论覆盖不足以支持继续加仓 | Zeus 必须补充 Fed/FOMC、AMD、ANET、DELL、Micron、NVIDIA、Intel、Vertiv 与 hyperscaler 关键信号；Poseidon 只允许把官方/高置信信号纳入估值和时机 |
| missed key events | 上一轮确认了 FLEX 量价，但对 FLEX 成交后是否仍有正 R/R 没有复盘；对 MU/WDC/STX 存储链新涨幅未充分比较 | 本轮必须比较 FLEX 加仓、存储链追随、ETF fallback 和 no-trade 四种表达 |
| key analytical mistakes | 最大错误风险是把“已买入 starter”误读为“必须继续加仓”，或把 MSFT 大亏当作摊低理由 | 本轮以 P&L 和 R/R 为硬约束：亏损不自动补，盈利不自动追，强势不等于 FOMO，但止损/RR/数据失败则等待 |
| single-source risk | 本地 CLI 滞后，不能作为事实行情 | Zeus 事实行情全部使用 financeBusiness 实时行情；报告显式区分实时行情和历史指标 |
| stop/take-profit discipline | FLEX 已持有，必须维持或重设止损/止盈，而不是重新包装成长期持仓 | Hades 必须审计 FLEX 是否仍满足止损 135.10、目标 154/164、移动止损规则 |

### 反思结论

Buffett 对流程责任如下：第一，上一次记录不符合新的本地快照合同，本轮必须修正；第二，上一轮 starter 如果已成交，本轮首要任务不是再买，而是复盘成交后风险收益是否仍成立；第三，不能因 AI 强周期上涨就无条件追 MU/WDC/STX，也不能因担心错过而忽略止损、费用和 2% 风险预算；第四，MSFT 的大额亏损必须被当作组合风险处理，不能把长期优质公司叙事直接替代当前波段 setup。

### 基于反思的新策略

- 数据刷新：Zeus 的事实实时行情必须使用 financeBusiness `StockCurrentMarket`；`StockMarketList` 用于短线趋势；本地 CLI 仅作第二路径历史指标和质量缺口。
- 候选覆盖：继续覆盖 AI 全链条，但优先判断是否需要对已持 FLEX 做止损/持有/止盈，而非默认新买。
- starter/add/stop/take-profit：FLEX 已是 starter，除非回撤承接或放量突破且二目标 R/R 仍为正，否则不加仓；硬止损参考上一轮 135.10，若价格跌破且无法快速收复，应执行风险退出。
- no-chase 边界：MU/WDC/STX/AMD 若已远离 5 日均线、第一目标不足以覆盖止损与 USD 5 费用，当前不追；可列入等待或下轮触发条件，不放入最终当前操作。
- Hades veto：缺硬止损、费用后 R/R 不足、实时行情字段失败、现金未确认、把亏损票摊低作为主理由、把强势票追高作为主理由，均可否决。
- 触发 `本次不买入、不卖出`：若 FLEX 无需止损/止盈、所有新增候选 R/R 不足或价格过度延伸、ETF fallback 也无更好 R/R，则本轮最终动作应为不买入不卖出，并给出下一次复盘时间。

## 本轮约束

1. 最终动作只允许当前可执行整股 BUY/SELL 或 `本次不买入、不卖出`。
2. 任何 BUY/SELL 必须含限价、股数、USD 5 费用、费用比例、现金影响、止损、目标、趋势证据、理由和无效条件。
3. 交易后预计盈亏必须使用平均成本法；若现金为 HKD 折算，必须标明券商换汇确认风险。
4. 本轮不得写 SQLite，不得生成 `db_record.json`。
