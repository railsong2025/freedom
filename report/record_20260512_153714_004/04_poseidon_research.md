# 04_poseidon_research

## 研究输入

Poseidon 已读取 00/01/02 和 Zeus 的 03 情报。研究结论以 financeBusiness 当前价、历史核验、aiwebsearch 官方/新闻证据、当前 P&L 和本地 CLI 输出为依据。

本轮关键事实：

- USD 持仓市值 18,705.61 美元，成本 19,976.83 美元，未实现盈亏 -1,271.22 美元（-6.36%）。
- 背景现金 165,627 HKD，按 `USD/HKD=7.8282` 折算约 21,157.74 美元。
- 估算组合权益约 39,863.35 美元。
- financeBusiness 已解决纳指/标普代理审议：IXIC 可作为纳指市场 regime，QQQ 是可交易代理；SPY 是标普可交易代理。

## Python 工具调用记录

| 工具 | 命令 | 输出摘要 |
|---|---|---|
| P&L | `python3 workspace/analysis/cli.py pnl --portfolio-file base_short.md --prices ... --markdown` | USD 持仓合计市值 18,705.61、成本 19,976.83、未实现 -1,271.22（-6.36%）。 |
| sector score | `score-sector --sector AI_semiconductors ...` | AI 半导体 72.80，`tactical_overweight`。 |
| sector score | `score-sector --sector AI_memory_storage ...` | AI 存储/HBM 73.55，`tactical_overweight`，但 valuation/crowding 低分。 |
| stock score | `score-stock --symbol NVDA ...` | 78.60，`tactical`。 |
| stock score | `score-stock --symbol AMD ...` | 71.10，`tactical`。 |
| stock score | `score-stock --symbol INTC ...` | 51.80，`avoid`。 |
| stock score | `score-stock --symbol FLEX ...` | 67.40，`watch`。 |
| R/R | `rr AMD/NVDA/FLEX/QQQ/SMH/SOXX` | AMD、NVDA、QQQ、SMH、SOXX 第二目标仅 marginal；FLEX 两档均 insufficient。 |
| sizing | `sizing --equity 39863.35 --entry 458.79 --stop 430 --risk-pct 2 --cash 21157.74` | AMD 2% 风险会给出 27 股、总仓位 31.07%，超过单股 25% 上限；不能按风险预算直接买足。 |
| swing verdict | `swing-verdict AMD/NVDA/FLEX/INTC/QQQ/SMH/SOXX ...` | 均因 `volume_relative_strength_unverified`，或费用后 R/R 不足，进入 `hard_veto` 当前交易。 |

## 当前盈亏与仓位含义

| Ticker | 当前 P&L | 研究解释 | 当前动作含义 |
|---|---:|---|---|
| MSFT | -1,697.40 (-18.60%) | 基本面 AI 云强，但波段趋势未修复；最大亏损不可用补仓掩盖 | 不加仓；等待趋势修复 |
| NVDA | +246.47 (+19.11%) | 直接利润池和技术生态最强；已有盈利仓位提供 AI beta | 不追新；持有并保护利润 |
| SPY | +179.97 (+8.83%) | 标普代理有效，组合已有 broad market 风险 | 不新增 SPY |
| AMD | +45.56 (+11.03%) | 受益 AI accelerator，但近期涨幅和波动大 | 不新增；保留 1 股观察 |
| TSM | -73.02 (-2.92%) | 代工核心地位仍在，近端弱于半导体 ETF | 不加仓 |
| ANET | -31.75 (-4.45%) | AI 网络主题在，但个股价格转弱 | 不加仓，不卖出 |
| FLEX | +24.75 (+1.58%) | 从风险线附近修复到微盈；利润质量仍需验证 | 保留，不追加 |
| KO | +34.20 (+1.47%) | 防御仓，非 AI 主线 | 保留 |

## 美股板块地图

| 板块/链条 | 评分/状态 | 利润池判断 | 当前交易结论 |
|---|---|---|---|
| 半导体/GPU | 72.80，tactical overweight | NVDA 直接占利润池，AMD 次级受益，TSM/设备分摊周期 | 允许作为核心研究方向，但当前不追价 |
| 存储/HBM | 73.55，tactical overweight | MU/WDC/STX 短线最强，供需和价格弹性高 | 强势但高拥挤，当前等待回撤承接 |
| 电力/散热 | 强主题，VRT +8.22% | AI 数据中心从 GPU 扩散到 power/cooling | 当前追价风险高 |
| AI服务器/EMS | FLEX 持仓微盈，DELL 单日 -5.15% | 订单大但毛利与竞争分化 | FLEX 保留，DELL 不追 |
| 云/AI应用 | MSFT 基本面强但持仓大亏 | 云 CAPEX 是上游需求源 | MSFT 不补亏损仓 |
| Broad market | IXIC/SPY/QQQ 代理有效 | 风险偏好偏强但已接近高位 | 用作环境，不作为当前新增 |

## AI 产业链机会漏斗

| 分层 | 候选 | 直接/间接受益 | 估值/时机 | 结论 |
|---|---|---|---|---|
| 核心候选 | NVDA、SMH、SOXX | 直接利润池/篮子 | 强势但 R/R marginal，已收盘无确认 | 核心研究，不当前买入 |
| 核心候选 | AMD | 直接受益但定价权低于 NVDA | 波动大，当前费用后 R/R 不足 | 持有已有 1 股，不新增 |
| 战术候选 | MU、WDC、STX | 存储/HBM 弹性强 | 单日涨幅过大，追价风险高 | 等回撤承接；本轮不下单 |
| 战术候选 | VRT | 电力/散热利润池扩散 | +8.22%，估值与拥挤度高 | 等确认，不追 |
| 战术候选 | FLEX | AI服务器EMS，已有持仓 | 修复到微盈但 R/R insufficient | 保留，不加仓 |
| 观察名单 | MSFT、TSM、ANET、DELL | 基本面相关但近端弱或分歧 | 需要趋势修复 | 不买不卖 |
| 回避/否决 | INTC | 政策/制造/AI PC 可选项 | EPS/PE 质量弱，转型不确定 | 当前交易回避 |
| 数据不足 | 安全、PCB/CCL、封装/材料多票 | 有主题但本轮未完整行情包 | 不能作为当前交易依据 | 后续补筛 |

## 候选动作对照表

| 候选 | 价格 | 入场类型 | R/R | swing verdict | Hades 预期 | 最终动作 |
|---|---:|---|---|---|---|---|
| AMD | 458.79 | 追随/回撤 | 第二目标 1.83，marginal | hard_veto：量价相对强弱未验证 | 等待 | 不买 |
| NVDA | 219.44 | 追随/保护利润 | 第二目标 1.15，marginal | hard_veto：量价相对强弱未验证 | 等待 | 不买 |
| FLEX | 145.07 | 加仓 | 第二目标 0.98，insufficient | hard_veto：R/R不足+量价未验证 | 否决加仓 | 不买不卖 |
| INTC | 129.44 | 强势反弹 | insufficient | hard_veto：R/R不足+量价未验证 | 否决 | 不买 |
| MU | 795.33 | 强势延伸 | 未形成费用后计划 | 待盘中回撤 | 等待 | 不买 |
| WDC | 515.83 | 强势延伸 | 未形成费用后计划 | 待盘中回撤 | 等待 | 不买 |
| STX | 834.01 | 强势延伸 | 未形成费用后计划 | 待盘中回撤 | 等待 | 不买 |
| VRT | 367.92 | 主题追随 | 未形成费用后计划 | 追价风险 | 等待 | 不买 |
| ANET | 136.43 | 修复 | 未满足趋势修复 | 观察 | 等待 | 不买不卖 |
| TSM | 404.54 | 修复 | 未满足趋势修复 | 观察 | 等待 | 不买不卖 |
| MSFT | 412.66 | 亏损修复 | 未满足趋势修复 | 观察 | 等待 | 不加仓 |
| QQQ | 713.29 | 纳指代理 | 第二目标 1.40，marginal | hard_veto：量价未验证 | 等待 | 不买 |
| SMH | 576.31 | 半导体篮子 | 第二目标 1.75，marginal | hard_veto：量价未验证 | 等待 | 不买 |
| SOXX | 532.76 | 半导体篮子 | 第二目标 1.64，marginal | hard_veto：量价未验证 | 等待 | 不买 |

## 强周期波段交易计划

当前不形成 BUY 计划。原因不是“上涨多所以不买”，而是：

- 美股常规盘尚未开，financeBusiness 状态均为已收盘，缺少本轮交易窗口的开盘后成交量确认。
- 多数强势候选的费用后 R/R 只有 marginal，第一目标不足以覆盖波动与 USD 5 固定费用。
- AMD 按 2% 风险预算会推到 27 股并超过单股 25% 上限，说明风险预算不能直接转为大仓。
- 存储、VRT、INTC 单日强势过大，若无回撤承接和止损定义，容易把 FOMO 当执行纪律。

## 错过机会修正

上一轮 `本次不买入、不卖出` 在风险控制上是部分成功：FLEX 从上一轮风险线附近修复到微盈，没有被恐慌卖出；组合总未实现亏损从上一轮约 -1,355.79 改善到 -1,271.22。失败或不足在于：存储/HBM、INTC、VRT、WDC、STX 等强势分支没有被完整建立为可审计候选池。本轮已建立漏斗，但由于交易窗口和 R/R 不满足，不把“补错过”变成追涨。

## 仓位升级阶梯与盈利路径

本轮只保留方法，不写入最终当前操作：

- 盈利路径来自正期望，而不是保证收益：先保住 NVDA/SPY/AMD/FLEX 已有利润，再等回撤或开盘确认。
- 后续若要增加 AI beta，优先从 ETF 代理或最强直接利润池开始，但必须重新计算 USD 5 费用、整股数量、止损、目标和单股 25% 上限。
- MSFT 的亏损修复必须依靠趋势和业务证据，不能靠补仓摊成本。

## Poseidon 结论

研究部不建议本轮执行 BUY 或 SELL。当前最佳动作是保留现有美股仓位，等待北京时间 2026-05-12 22:30 后刷新盘中量价、相对强弱和费用后 R/R。若最终报告晚于交易截止，则只能写 `本次不买入、不卖出`。
