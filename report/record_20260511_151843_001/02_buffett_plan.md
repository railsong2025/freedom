# 02_buffett_plan

## 本轮目标

- 计划时间：2026-05-11 15:18:43 CST（星期一）。
- 固定触发：`buffett开始`。
- 固定身份：`task_type=portfolio_review`，`subject=us_equity_portfolio`，`task_key=portfolio_review:993c7d93e383`。
- 任务目录命名：本轮和后续报告目录必须使用 `record_YYYYMMDD_HHMMSS_序号`。
- 复盘主索引：按本地 report 文件夹复盘，优先上一轮 `report/record_*` 完整报告；SQLite 只作英文索引交叉检查。
- 目标：在完整复盘当前 USD 持仓 P&L 后，先做美股板块地图和 AI 产业链机会漏斗，再决定当前会话是否执行整股 BUY/SELL，或写 `本次不买入、不卖出`。
- 策略：所有策略遵从波段交易策略；默认持有数日至数周，禁止把失败波段拖成长线。

## 从 01 继承的约束

- 当前 USD 持仓总市值：$17,178.14；总成本：$18,405.81；未实现盈亏：$-1,227.67（-6.67%）。
- 上一轮本地复盘状态：no_local_record_found；本地扫描规则必须写入报告：`local scan: report/record_* first, then legacy report/YYYY-MM-DD_* folders`。
- 错过机会账本必须贯穿 03-06：MU、AMD、FLEX、INTC、WDC、STX、VRT、ANET、TSM、SMH、SOXX 和全 AI 链代表票都要复盘覆盖/未覆盖、涨跌、机会成本和是否过度保守。
- Buffett 自我反思和新策略必须贯穿 03-06：下游部门必须基于最新数据和历史决策，回应 Buffett 在历史连续性、候选覆盖、仓位执行、防错过、防追高、止损/止盈和费用后 R/R 上的流程责任，并验证 `基于反思的新策略` 是否可执行。
- 关键遗漏与分析错误复盘必须贯穿 03-06：关键人物讲话遗漏、关键事件未捕捉、关键分析错误必须被 Zeus 补证、Poseidon 归因、Hades 审计，并在圆桌中确认是否改变当前策略。
- 当前价和 P&L 仍需 Zeus 第二来源核验；未经核验的价格只能作为临时计算。

## 数据刷新计划

本轮 manifest：`workspace/buffett_research_advisor/runs/20260511_151843/market_data/manifest.json`，Zeus 先读 manifest/CSV，再 fallback。

- 结构化行情：financeBusiness MCP 优先；失败或字段不足时用公共 `workspace/interface/market_data.py` 的 AkShare、HTTP/API、Stooq、CSV/cache、yfinance_last_resort。
- 新闻/公告/宏观/人物言论：aiwebsearch 和官方源优先；关键 URL 用 searchJumps 的 URL 对象数组格式。
- 第二来源：所有关键价格、涨跌幅、成交量、催化和估值必须至少第二来源核验。
- 数据缺口：任何缺口要写入 `## 数据冲突与缺口`，并说明对波段交易是否降权或否决。

## AI 产业链两阶段漏斗

第一阶段：全链条轻量广覆盖初筛，覆盖下表所有环节，字段至少包括最新价/涨跌、量价状态、催化、追高风险、是否有可定义止损、初步 veto。

| 链条环节 | 必须覆盖的美股/ETF代表 |
|---|---|
| AI应用/云CAPEX/数据基础设施 | MSFT、AMZN、GOOGL、META、ORCL、PLTR、SNOW、DDOG |
| GPU/ASIC/AI加速器 | NVDA、AMD、AVGO、MRVL、ARM |
| 晶圆代工/半导体制造 | TSM、INTC |
| 存储/HBM/存储设备 | MU、WDC、STX |
| 半导体设备/EDA/材料 | ASML、AMAT、LRCX、KLAC、CDNS、SNPS、ENTG、PLAB |
| 先进封装/测试 | AMKR、TSM |
| 光模块/网络 | ANET、CIEN、COHR、LITE |
| AI服务器/ODM/EMS | DELL、HPE、SMCI、FLEX、JBL、CLS、SANM |
| 数据中心电力/散热/工程 | VRT、ETN、PWR、GEV |
| PCB/CCL/电子制造 | TTMI、SANM、FLEX、JBL |
| 安全/数据基础设施 | PANW、CRWD、NET、SNOW、DDOG |
| 链条ETF/篮子 | SMH、SOXX、QQQ、IGV、AIQ |

第二阶段：筛出 Top 8-12 做深度波段计划。筛选依据：板块强弱、催化新鲜度、利润池归属、订单/业绩能见度、费用后 R/R、成交量确认、相对 SPY/QQQ/SMH/SOXX 强弱、现金和组合风险约束。

## Zeus 派工合同

- 必须读取：`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/00_metadata.md`、`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/01_buffett_review.md`、`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/02_buffett_plan.md`。
- 必须写入：`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/03_zeus_intelligence.md`。
- 必须运行 Python CLI：`workspace/intelligence/cli.py indicators`、`quality`、`sector-map`，并把命令和输出写入 `## Python 工具调用记录`。
- 必须覆盖：当前持仓、SPY/QQQ/SMH/SOXX、行业 ETF、宏观风险、关键人物言论，以及 AI 应用/云、GPU/ASIC、晶圆代工、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、服务器/ODM、数据中心电力散热、PCB/CCL、安全/数据基础设施。
- 必须补查：上一轮可能未关注到的关键人物讲话和关键事件，至少覆盖讲话/事件时间、来源层级、影响链、受影响资产、讲话或事件前后市场反应、反证和数据缺口。
- 最低报告门槛：来源分层、第二来源差异、数据时间戳、事实影响链、反证、数据缺口、波段量价字段。
- 禁止事项：不得只复盘现有持仓；不得伪造 manifest；不得用单一未核验来源支撑交易；不得忽略 Buffett 自我反思和新策略中提出的覆盖缺口。

## Poseidon 派工合同

- 必须读取：00/01/02 和 03 Zeus 报告。
- 必须写入：`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/04_poseidon_research.md`。
- 必须运行 Python CLI：`workspace/analysis/cli.py pnl`、`score`、`rr`、`swing-verdict` 或同等本地分析命令，并把输出写入 `## Python 工具调用记录`。
- 必须输出：`## 美股板块地图`、`## AI 产业链机会漏斗`、`## 当前盈亏与仓位含义`、`## 强周期波段交易计划`、`## 错过机会修正与当前 starter 方案`、`## 仓位升级阶梯与大幅盈利路径`。
- 必须归因：上一轮关键分析错误，包括长期 thesis 替代波段 setup、动能突破被误判为一律追高、只因涨幅大否决、缺第二来源、缺费用后 R/R、缺硬止损/止盈、忽略关键讲话/事件、或把数据缺口当确定结论。
- 候选分层：核心候选 / 战术候选 / 观察名单 / 回避或否决。
- 可执行 BUY 至少包含：入场类型、技术触发、限价、整股数量、硬止损、第一/第二止盈、移动止损、最长持有期、单笔风险金额、费用后 R/R。
- 必须输出 `候选动作对照表`：候选、短线分数、入场类型、限价、止损、第一/第二目标、费用后 R/R、数据质量、Hades 预期状态、swing verdict、最终动作。
- 若所有单股候选都不是 `current_trade` 或 `small_starter`，必须评估 SMH/SOXX/QQQ 或更合适的 basket/ETF fallback；整体 no-trade 必须证明每个候选和 fallback 均失败。
- 禁止事项：不得只说“上涨多所以不买”；不得只给小仓而没有确认加仓或利润保护路径；不得保证盈利；不得回避 Buffett 自我反思和新策略中指出的过度保守或防错过机制不足。

## Hades 派工合同

- 必须读取：00/01/02/03/04。
- 必须写入：`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_151843_001/05_hades_verification.md`。
- 必须运行 Python CLI：`workspace/verification/cli.py audit-pnl --portfolio-file base_short.md`、`stress-test --portfolio-file base_short.md`、`compliance --portfolio-file base_short.md`、`audit-post-trade --portfolio-file base_short.md` 或同等审计命令，并把输出写入 `## Python 工具调用记录`。
- 必须审计：上游报告完整性、P&L 自洽性、数据质量、第二来源、费用后 R/R、止损/止盈、单股 25% 上限、现金、AI 链条遗漏、关键人物言论是否过度解读。
- 必须审计：关键人物讲话遗漏、关键事件未捕捉和关键分析错误是否被 Zeus/Poseidon 充分补证与修正；若没有，Hades 必须降权、要求补查或否决。
- 三态/四态裁决：`批准当前交易`、`批准小仓 starter`、`等待`、`否决`；确认加仓另给 `批准加仓`、`仅保留 starter` 或 `减仓/止盈`。
- 若单股因数据质量被否决但存在 ETF/basket fallback，Hades 必须要求 fallback 审议，不得直接接受整体 no-trade。
- 禁止事项：不得笼统说“不追高”；只能用交易窗口、数据源、止损、R/R、仓位/现金/25% 上限等可审计硬条件否决；必须审计 Buffett 自我反思和新策略是否已经转化为硬约束。

## Roundtable 与 Buffett 最终验收

- Buffett 只有在 03/04/05 均存在并通过最低门槛后，才能写 `06_roundtable.md`。
- 圆桌必须讨论：上一轮成功/失败/混合/待验证原因、Buffett 自我反思是否成立、关键人物讲话遗漏/关键事件未捕捉/关键分析错误是否被修正、新策略是否被最新数据支持、当前 P&L 对买卖的影响、错过机会修正、AI 链条 Top 8-12、Hades veto、是否当前下单。
- `07_final_decision.md` 必须包含 `## 当前持仓盈亏复盘`、`## 本次当前操作`、`## 交易后预计盈亏`、`## 下一次建议启动分析时间（北京时间）`。
- `本次当前操作` 只能列当前立即执行的 BUY/SELL；观察名单、未来条件单和非行动候选不得混入。
- 若交易窗口内最终仍是 `本次不买入、不卖出`，`06_roundtable.md` 和
  `07_final_decision.md` 必须写出 no-trade proof：每个核心/战术候选及
  SMH/SOXX/QQQ fallback 的 swing verdict、硬否决原因或等待原因。
- 若最终决策或复核晚于本轮具体交易截止时间，最终只能写 `本次不买入、不卖出`。

## 第二步验收门槛

- 00 已明确 task_key、`record_YYYYMMDD_HHMMSS_序号` 任务目录、源文件、数据源计划、AI 全链候选池、波段策略边界和文件计划。
- 01 已读取/说明上一轮本地 report/record 文件夹历史，使用最新 record 持仓计算 USD P&L，未重复计入初始持仓或已卖出 TSLA/MSFT 股数，建立错过机会账本，并基于最新数据和历史决策写出 Buffett 自我反思与新策略。
- 02 已把 P&L、历史状态、Buffett 自我反思、新策略、AI 全链覆盖、三部门派工合同、Python 工具调用、Hades veto 和最终报告格式写成可执行要求。
