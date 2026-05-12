# Poseidon 研究报告 — us_equity_portfolio

## 输入与研究范围

| 项目 | 内容 |
|---|---|
| 请求来源 | Buffett workflow |
| 已读上游 | `00_metadata.md`、`01_buffett_review.md`、`02_buffett_plan.md`、`03_zeus_intelligence.md` |
| 研究目标 | 结合 financeBusiness 实时行情、当前 P&L、AI 产业链和强周期波段 setup，给出当前可执行 BUY/SELL/no-trade 研究结论 |
| 时间框架 | 波段：数日至数周；当前动作截止 2026-05-12 00:00 CST |
| 现金假设 | 165,627 HKD 按 HKD/USD=0.1278 折算约 21,167.13 USD；需券商换汇确认 |

## 一句话结论

AI/半导体/存储/服务器链仍是战术超配方向，但当前组合已持 FLEX starter 且强势候选普遍延伸，新增买入的费用后 R/R 不足；本轮研究建议 `本次不买入、不卖出`，保留现有持仓并严格执行 FLEX 135.10 风控线与 154/164 目标复盘。

## 研究问题清单

| 问题 | 结论 |
|---|---|
| 是否加仓 FLEX | 不加仓。已有 11 股，当前价 143.71，高于成本 142.82，但短线评分 66/watch，第一目标 R/R 不足 |
| 是否追买 MU/WDC/STX | 不追。存储/HBM 最强，但当前价已延伸，swing-verdict 多数 hard_veto |
| 是否补 MSFT | 不补。MSFT 最大亏损，当前下跌且不属于本轮最强链条 |
| 是否卖出 MSFT/TSM/ANET | 不卖。未触发明确止损；但不得加仓 |
| 是否买 ETF fallback | 不买。SMH/SOXX 量比缺失，QQQ 不优于单链条候选 |
| 当前最终动作 | 倾向 `本次不买入、不卖出` |

## 请求/规划执行情况

| 规划事项 | 完成状态 | 证据章节 | 缺口 | 处理 |
|---|---|---|---|---|
| 使用当前 P&L | 完成 | `当前盈亏与仓位含义` | 成交税费/券商现金未核验 | 平均成本法，现金折算标注 |
| sector-first | 完成 | `市场环境与板块地图` | 未做全市场所有行业深挖 | 与本轮 AI 强周期目标匹配 |
| AI 漏斗 | 完成 | `AI 产业链机会漏斗` | 长尾股未逐一实时估值 | 聚焦可交易代表 |
| 特别观察股票 swing verdict | 完成 | `强周期波段交易计划` | ETF 量比缺失 | ETF 降级为 fallback |
| Python 工具 | 完成 | `Python 工具调用记录` | 无 |
| 错误修正 | 完成 | `上游证据采纳与降权`、`盈利路径与防踏空计划` | transcript 未全量抽取 | 降低置信，不新增交易 |

## Python 工具调用记录

| 工具 | 命令摘要 | 退出码 | 关键输出 |
|---|---|---:|---|
| P&L | `pnl --portfolio-file portfolio_usd_for_tools.md --prices ...` | 0 | 总市值 18,594.57；成本 19,976.83；未实现 P&L -1,382.26（-6.92%）；估算总权益 39,761.70 |
| 板块评分 | `score-sector --sector AI_semiconductor_memory_infra ...` | 0 | weighted_score 73.25，rating `tactical_overweight` |
| FLEX 股票评分 | `score-stock --sector AI_server_ODM --symbol FLEX ...` | 0 | weighted_score 68.8，tier `watch` |
| MU 股票评分 | `score-stock --sector memory_HBM --symbol MU ...` | 0 | weighted_score 74.4，tier `tactical` |
| AMD 股票评分 | `score-stock --sector semiconductor_GPU --symbol AMD ...` | 0 | weighted_score 71.3，tier `tactical` |
| INTC 股票评分 | `score-stock --sector foundry_turnaround --symbol INTC ...` | 0 | weighted_score 53.8，tier `avoid` |
| VRT 股票评分 | `score-stock --sector datacenter_power --symbol VRT ...` | 0 | weighted_score 68.3，tier `watch` |
| FLEX short-term | `score-short-term --symbol FLEX ...` | 0 | weighted_score 66.0，action_bias `watch` |
| FLEX R/R | `rr --entry 143.71 --stop 135.10 --target 154 --target-2 164 --shares 11` | 0 | target1 RR 0.9648 insufficient；target2 RR 2.0044 positive_expectancy |
| FLEX sizing | `sizing --equity 39761.70 --entry 143.71 --stop 135.10 --risk-pct 2 --cash 21167.13` | 0 | 工具按最大风险给 90 股会超过单股 cap；对本轮不加仓形成约束 |
| FLEX swing verdict | `swing-verdict --symbol FLEX ...` | 0 | `wait`，无硬否决，但 setup 不可执行 |
| MU swing verdict | `swing-verdict --symbol MU ...` | 0 | `hard_veto`，fomo_justified；当前追价 R/R 不足 |
| WDC swing verdict | `swing-verdict --symbol WDC ...` | 0 | `hard_veto`，fomo_justified |
| STX swing verdict | `swing-verdict --symbol STX ...` | 0 | `hard_veto`，fomo_justified |
| AMD swing verdict | `swing-verdict --symbol AMD ...` | 0 | `hard_veto`，fomo_justified |
| INTC swing verdict | `swing-verdict --symbol INTC ...` | 0 | `hard_veto`，valuation_assumes_best_case |
| VRT swing verdict | `swing-verdict --symbol VRT ...` | 0 | `hard_veto`，fomo_justified |
| DELL swing verdict | `swing-verdict --symbol DELL ...` | 0 | `hard_veto`，volume_relative_strength_unverified |
| ANET swing verdict | `swing-verdict --symbol ANET ...` | 0 | `hard_veto`，volume_relative_strength_unverified |
| post-trade | `post-trade --trades ''` | 0 | 无交易：realized_pnl 0、fees 0、cash 21,167.13、equity 39,761.70 |

## 上游证据采纳与降权

| 上游事实 | 采纳/降权 | 投资含义 |
|---|---|---|
| financeBusiness 实时行情 | 完全采纳 | 当前交易价格、P&L 和盘中强弱均以此为准 |
| 本地 CLI akshare 2026-05-08 日线 | 降权 | 用于历史技术背景，不用于当前下单 |
| AMD/ANET/DELL 官方事件 | 采纳 | AI 基础设施 thesis 仍成立 |
| Micron/HBM 搜索证据 | 部分采纳 | 产业方向强，但当前没有足够官方最新 transcript 支持追价 |
| ETF 量比缺失 | 采纳为缺口 | SMH/SOXX 不作为当前买入替代 |

## 关键人物言论采纳与投资含义

| 信号 | 分类 | 投资含义 |
|---|---|---|
| Fed/FOMC 最新声明 | 宏观政策信号 | 高估值 AI 链需更高 R/R；不支持盲目放大仓位 |
| AMD Q1 数据中心增长 | 公司基本面/供应链信号 | 支持 AI 加速器和 server 链，但 AMD 已冲高回落，不追 |
| Arista Q1 与 AI networking | 公司基本面信号 | ANET 长期链条仍在，但短线弱于主题，不加仓 |
| Dell AI server 指引 | 供应链/order 信号 | 支持 FLEX/VRT，但 DELL 本日失败；已有 FLEX 可持有 |
| Micron/HBM 供需 | 供应链/价格信号 | 支持 MU/WDC/STX 战术关注，但当前价格延伸过大 |

## 当前盈亏与仓位含义

| Ticker | 当前 P&L | 研究判断 | 当前动作 |
|---|---:|---|---|
| MSFT | -1,750.50 / -19.18% | 最大亏损，不应补仓；云/AI 长期逻辑未在本轮短线修复 | 不买不卖，等待修复或下轮设止损 |
| NVDA | +232.79 / +18.05% | 上游 AI beta 已盈利，需保护已有收益 | 不追买，不卖 |
| SPY | +177.27 / +8.70% | 大盘 beta 已有 | 不买 ETF |
| AMD | +39.15 / +9.47% | 强但当前追买 R/R 差 | 不买不卖 |
| TSM | -104.25 / -4.17% | 当前弱，未触发硬止损 | 不买不卖 |
| ANET | -8.40 / -1.18% | 量价弱于网络 thesis | 不加仓，不卖 |
| FLEX | +9.79 / +0.62% | starter 仍有效，但不适合加仓 | 持有，维持止损/目标 |
| KO | +21.90 / +0.94% | 防御仓位，非本轮主线 | 不动 |

## 投资主张

本轮核心判断是“主题强，交易不强”。AI 基础设施链条仍有真实利润池迁移：GPU/ASIC、HBM/存储、AI server/ODM、数据中心电力散热均强于大盘；但当前价格已经把短线好消息大量反映在 MU/WDC/STX/AMD/VRT/FLEX 中。组合已经持有 FLEX starter 和 NVDA/AMD/TSM/ANET 的 AI 暴露，最优动作是守纪律，而不是继续扩大同一高 beta 暴露。

## 市场环境与板块地图

| Sector/Theme | Score | Rating | Cycle Phase | Key Catalyst | Profit-Pool Direction | Main Risk | Action |
|---|---:|---|---|---|---|---|---|
| AI semiconductor/memory/infra | 73.25 | tactical_overweight | 强周期上行但拥挤 | AMD Q1、存储/HBM、AI server | 上游/存储/电力散热占优 | 估值和追价 | 持有已有，等待回撤 |
| Memory/HBM | 78 | tactical_overweight | 强趋势后延伸 | MU/WDC/STX 高量比 | 直接受益 | 追高、回撤 | 等待回撤承接 |
| AI server/ODM | 70 | tactical_overweight | 分化 | Dell/FLEX/VRT | 订单外溢 | DELL 失败，FLEX 已涨 | 持有 FLEX |
| Cloud/software | 55 | underweight/watch | 分化偏弱 | 云 CAPEX 长期支持 | 间接受益 | MSFT 当前弱 | 不补 MSFT |
| Broad ETF | 60 | neutral/watch | 高位震荡 | 风险偏好 | 分散 beta | ETF 量比缺失 | 不买 ETF |

## 行业、主题与供应链漏斗

| 环节 | 代表 | 直接性 | 评分 | 结论 |
|---|---|---|---:|---|
| 存储/HBM | MU/WDC/STX | 直接 | 高 | 最强链条，但当前 hard_veto 追价 |
| GPU/ASIC | NVDA/AMD | 直接 | 中高 | 持有已有，不加 AMD |
| AI server/ODM | FLEX/DELL/JBL/CLS | 直接/间接 | 中高 | 持有 FLEX，不买 DELL |
| Power/cooling | VRT/ETN/PWR | 直接 | 中高 | VRT 强但追价 |
| Networking | ANET | 直接 | 中 | 基本面在，短线弱 |
| ETF basket | SMH/SOXX/QQQ | 分散 | 中 | fallback 不优于等待 |

## AI 产业链机会漏斗

| 链条环节 | 核心候选 | 战术候选 | 观察名单 | 回避/否决 |
|---|---|---|---|---|
| AI 应用/云 CAPEX | - | MSFT（持有，不补） | GOOGL、AMZN、META、ORCL | 当前不新开 |
| GPU/ASIC | NVDA（持有） | AMD（持有，不追） | AVGO、MRVL、ARM | 追价 AMD |
| 半导体制造 | - | TSM（持有） | INTC 特别观察 | INTC 当前 hard_veto |
| 存储/HBM | - | MU | WDC、STX | 当前追买 hard_veto |
| 设备/EDA/材料 | - | ASML/AMAT/LRCX 观察 | CDNS/SNPS/ENTG | 当前非主线交易 |
| 光模块/网络 | - | - | ANET（持有） | 当前加仓 ANET |
| AI server/ODM/EMS | FLEX（已持） | VRT | DELL、JBL、CLS | 追买 DELL |
| 电力/散热 | - | VRT | ETN/PWR/GEV | 当前追价 |
| PCB/CCL | FLEX proxy | TTMI/JBL/SANM | - | 当前不扩张 |
| 安全/数据基础设施 | - | - | PANW/CRWD/NET/SNOW/DDOG | 当前非主线 |
| ETF/basket | - | QQQ 背景 | SMH/SOXX | ETF 当前 BUY |

## 候选股票评分与分层

| Tier | Ticker | Market | Role In Thesis | Directness | Score | Valuation View | Timing | Key Risk | Action |
|---|---|---|---|---|---:|---|---|---|---|
| 核心候选 | FLEX（已持） | US | AI server/ODM/EMS | 直接/间接 | 68.8 | 不再便宜 | 已持，当前加仓 watch | 刚突破后延伸 | 持有，不加 |
| 战术候选 | MU | US | HBM/存储 | 直接 | 74.4 | 强但贵 | 追价 hard_veto | 回撤急 | 等回撤 |
| 战术候选 | AMD | US | GPU/CPU/AI server | 直接 | 71.3 | 估值高 | 追价 hard_veto | 盘中冲高回落 | 持有1股，不加 |
| 观察名单 | VRT | US | 电力/散热 | 直接 | 68.3 | 高估值 | 追价 hard_veto | 高 beta | 等回撤 |
| 观察名单 | WDC/STX | US | 存储设备 | 直接 | 未单独评分 | 强周期重估 | hard_veto | 延伸 | 等回撤 |
| 观察名单 | ANET | US | AI networking | 直接 | 未单独评分 | 估值消化 | hard_veto | 相对弱 | 持有，不加 |
| 回避/否决 | INTC | US | foundry/turnaround | 直接/政策 | 53.8 | 依赖最佳情境 | hard_veto | EPS 负、执行风险 | 不买 |
| 回避/否决 | DELL | US | AI server | 直接 | 未单独评分 | 事件已反映 | hard_veto | 当日失败 | 不买 |

## 估值分析

- FLEX：当前价 143.71，较上一轮限价 142.17 已上移。以止损 135.10、目标 154/164 估算，第一目标费用后 R/R 仅 0.9648，不足；第二目标 2.0044 通过，但需要价格继续强势，不能作为加仓依据。
- MU/WDC/STX：利润池最强，但当前 break-even 与目标距离显示首目标普遍不足，追买会把正确方向变成错误交易。
- AMD：Q1 事件强，但当前 entry 452.38、stop 430、target 475/500 的 R/R 分别为 0.3855/1.1552，新增不合格。
- INTC：政策/制造/AI PC 叙事存在，但 EPS 为负且评分 53.8，当前不是可执行核心候选。

## 护城河与成长

| 标的 | 护城河/成长 | 风险 |
|---|---|---|
| NVDA | AI 加速器生态和软件/平台锁定 | 估值、出口管制 |
| AMD | CPU/GPU 组合与数据中心增长 | 与 NVDA 竞争、估值 |
| MU/WDC/STX | 存储供需和 HBM/AI 需求 | 周期反转、价格波动 |
| FLEX | EMS/ODM、AI server 外溢 | 利润率薄、客户集中、价格已跳升 |
| VRT | 数据中心电力/散热 | 高估值、订单节奏 |
| MSFT | 云和 AI 软件生态 | 当前组合亏损与技术弱势 |

## 宏观、量化与技术面

- 宏观：FOMC 路径仍是高估值 AI 链的折现风险；当前不适合扩张多笔高 beta 仓位。
- 量化/技术：financeBusiness 盘中显示强链条高量比，但许多候选高开后回落，说明追价并非无风险。
- 技术约束：本轮多数候选首目标 R/R 不足，且交易窗口短，不能等待盘中确认后再完整执行。

## 风险与仓位

| 风险 | 处理 |
|---|---|
| 单股上限 | 当前所有持仓低于 25% 估算权益；MSFT 18.55% 为最大仓位 |
| 强周期回撤 | 不新增追高仓位 |
| FLEX starter 变长期持仓 | 维持 135.10 止损；下轮复盘是否触发移动止损 |
| 现金换汇 | 港币现金折算仅估算；若无美元现金，不得强行下单 |
| 数据质量 | financeBusiness 为实时事实；CLI stale 降权 |

## 可执行候选仓位表

| Ticker | Initial Position | Max Position | Buy Zone | Add Trigger | Trim Trigger | Exit/Inval. | Review Trigger |
|---|---:|---:|---|---|---|---|---|
| FLEX | 已持 11 股 | 不加仓 | 不新增 | 放量站稳 154 后下一轮重算 | 154/164 附近分批或移动止损 | 跌破 135.10 | 2026-05-12 22:00 CST |
| MU | 0 | 0 | 等回撤至支撑后重算 | 回撤承接且首目标 R/R>1.3 | 不适用 | 当前追价 hard_veto | 下轮 |
| WDC/STX | 0 | 0 | 等回撤 | 同上 | 不适用 | 当前追价 hard_veto | 下轮 |
| AMD | 已持 1 股 | 不加仓 | 不新增 | 回撤后重算 | 若跌破 430 下轮审计 | 当前追价 hard_veto | 下轮 |
| VRT | 0 | 0 | 等回撤 | 回撤承接 | 不适用 | 当前追价 hard_veto | 下轮 |

## 盈利路径与防踏空计划

| Ticker | Profit Path | Base Upside | Downside If Wrong | Expected Value | Missed-Out Risk | Anti-Miss Plan | No-Chase Rule |
|---|---|---|---|---|---|---|---|
| FLEX | AI server/ODM 延续，突破后去 154/164 | 154/164 | 跌破 135.10 | 持有正期望，加仓不足 | 若继续涨会少赚 | 持有已有 11 股 | 不在 143.71 以上追加 |
| MU/WDC/STX | HBM/存储价格与订单 | 5%-10% | 急跌回补缺口 | 当前追价期望不足 | 可能继续涨 | 下轮回撤承接再评估 | 首目标 R/R 不足不买 |
| AMD/NVDA | AI 芯片需求 | 持仓收益扩大 | 高估值回落 | 已有持仓参与 | 少赚新增 beta | 保留已有 | 不重复堆仓 |

## 强周期波段交易计划

| Ticker | Entry Type | Limit | Stop | Target 1 | Target 2 | Verdict | 理由 |
|---|---|---:|---:|---:|---:|---|---|
| FLEX | 回撤承接/持有复盘 | 不新增 | 135.10 | 154 | 164 | wait | 已持仓；第一目标 R/R 不足，加仓不合格 |
| MU | 动能突破但过热 | 不买 | 735 | 820 | 870 | hard_veto | fomo_justified，首目标 R/R 0.78 |
| WDC | 动能突破但过热 | 不买 | 488 | 540 | 570 | hard_veto | fomo_justified，首目标 R/R 0.68 |
| STX | 动能突破但过热 | 不买 | 790 | 850 | 890 | hard_veto | fomo_justified，首目标不足 |
| AMD | 动能后回落 | 不买 | 430 | 475 | 500 | hard_veto | fomo_justified，R/R 差 |
| INTC | turnaround 观察 | 不买 | 120 | 135 | 145 | hard_veto | valuation_assumes_best_case |
| VRT | 动能突破但过热 | 不买 | 342 | 375 | 395 | hard_veto | fomo_justified |
| DELL | 失败反弹 | 不买 | 240 | 260 | 275 | hard_veto | volume_relative_strength_unverified，当日 -4.78% |
| ANET | 弱势修复 | 不买 | 138 | 148 | 155 | hard_veto | relative strength 不足 |
| QQQ | ETF fallback | 不买 | - | - | - | wait | 不优于持有现仓 |
| SMH/SOXX | ETF fallback | 不买 | - | - | - | wait | financeBusiness 量比缺失 |

## 错过机会修正与当前 starter 方案

本轮不等于放弃机会：FLEX starter 已经在仓，NVDA/AMD/TSM/ANET 提供 AI 暴露。错过机会的修正方式是保留已有 starter 并等待确认加仓，而不是在强势股首目标 R/R 不足时追买。若 MU/WDC/STX 下轮回撤到支撑且量能不破，重新计算 starter。

## 仓位升级阶梯与大幅盈利路径

1. FLEX 站稳 154 且量比维持、AI server 链不转弱：下轮考虑移动止损到成本上方，不在本轮追。
2. 存储链回撤承接且 MU/WDC/STX 至少一个首目标 R/R>1.3、二目标>2：下轮可小仓 starter。
3. MSFT 若重新站上关键均线并云/AI 数据改善：下轮讨论是否持有修复，而非当前补仓。

## 波段执行与长期背景建议

长期背景仍支持 AI 基础设施，但本轮执行窗口短、价格延伸、组合已有暴露。当前建议把长期 thesis 和波段操作分开：长期看好不等于现在买，短线强势不等于现在追。

## 上游工作流承接

Poseidon 接受 Zeus 对事实行情源的修正：所有当前价格、P&L 和波段候选均以 financeBusiness 为事实行情。对 CLI 的 akshare stale 输出，Poseidon 只用于提示数据质量风险，不用于下单。

## 需要下游审计的问题

1. Hades 需核验 `本次不买入、不卖出` 是否满足候选-by-候选 no-trade proof。
2. Hades 需核验 FLEX 当前不加仓、也不卖出是否合规：止损是否仍明确，P&L 是否正确。
3. Hades 需核验现金折算、单股上限、空交易 post-trade 是否正确。

## 来源与引用

- `03_zeus_intelligence.md`
- financeBusiness `StockCurrentMarket` / `StockMarketList`
- AMD IR: https://ir.amd.com/news-events/press-releases/detail/1284/amd-reports-first-quarter-2026-financial-results
- Arista official: https://www.arista.com/en/company/news/press-release/24017-pr-20260505
- Dell IR: https://investors.delltechnologies.com/news-releases/news-release-details/dell-technologies-delivers-fourth-quarter-and-full-year-fiscal-3
- Federal Reserve: https://www.federalreserve.gov/newsevents/pressreleases/monetary20260429a.htm
