# Buffett 美股投研入口

这是 `buffett开始` 的本地手动入口，用于启动今日完整的美股专用 Buffett 投研流程。

## 目标

- 读取根目录 `base_short.md` 的美股持仓、可用美股资金和用户手工操作记录。
- 读取上一条同任务本地 report 记录文件夹并复盘。新格式优先 `report/record_*`；若没有新格式，才读取旧 `report/YYYY-MM-DD_*` 完整文件夹作为 legacy 背景。SQLite 只作 legacy 英文索引只读交叉检查，不再写入本轮结果。
- 复盘必须计算当前美股持仓总未实现盈亏和每个美股/ETF 的未实现盈亏，并让后续所有阶段持续考虑该信息。
- 要求完整 Buffett 本地流程刷新美股行情、板块、财报、新闻、宏观和反证。
- 必须加入美股板块地图和 AI 产业链机会漏斗，覆盖 AI 应用、云 CAPEX、GPU/ASIC、半导体、存储/HBM、先进封装、光模块/网络、AI 服务器、数据中心/电力/散热、PCB/CCL、设备、材料、安全和数据基础设施等相关环节，并寻找当前可交易机会。
- 默认启用美股强周期波段交易 overlay，所有策略遵从波段交易策略，重点候选池必须覆盖 AI 产业链上中下游：AI 应用/云 CAPEX、GPU/ASIC、晶圆代工、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、AI 服务器/ODM/EMS、数据中心电力/散热、PCB/CCL、安全/数据基础设施和链条 ETF/篮子，以数日至数周为主要持有周期。
- 特别观察范围必须覆盖 AMD、MU、FLEX、INTC/英特尔、WDC、STX、VRT、ANET、TSM、NVDA、SMH、SOXX、QQQ；INTC/英特尔必须作为独立观察标的，检查晶圆制造/代工转型、AI PC 与服务器 CPU、美国半导体政策/补贴、资本开支和毛利压力、相对 SMH/SOXX 强弱，不能只并入“半导体整体”。
- 波段候选必须按 `动能突破`、`回撤承接`、`超跌反弹` 分类，给出技术触发、成交量确认、限价、止损、第一/第二止盈、移动止损、最长持有期和盘中复盘时间。
- 每轮强周期复盘必须加入 `错过机会账本`，复盘上轮未买候选的后续 1 日/5 日表现、机会成本和错误归因，防止把所有强势突破都误判为追高。
- 复盘后必须加入 `Buffett 自我反思`，根据最新数据和历史决策审视 Buffett 自己在任务定义、候选覆盖、数据连续性、仓位执行、防错过、防追高、止损/止盈和费用后 R/R 上的流程责任；其中必须包含 `关键遗漏与分析错误复盘`，覆盖未关注到关键人物讲话、关键事件未捕捉、关键分析错误，并给出 `基于反思的新策略`，再把反思和新策略转成后续派工约束。
- `动能突破` 不自动等同于 FOMO 追高；只要板块领先、相对强弱和量能确认、止损/止盈明确、费用后风险收益合格，必须允许小仓 starter 或当前 BUY 进入 Hades 三态审计。
- 默认波段 profile 为 `swing_trading`：单笔最大亏损约账户权益 2%，强周期单票初始仓位通常 5%-8%，硬止损通常 3%-5%，但必须经 Hades 费用后期望值和风险预算审计。
- Hades 对强周期 BUY 候选必须给出 `批准当前交易`、`批准小仓 starter` 或 `否决`；不能仅因“涨得多”否决。
- Zeus 必须增加 `关键人物言论与市场影响`：覆盖 Fed/FOMC、财政部、白宫/总统、监管部门、当前持仓公司 CEO/CFO、AI 云厂商和核心供应链管理层、重要地缘政治人物；每条重要言论都要评估来源层级、影响链条、受影响资产、可观察市场反应、置信度和反证。
- Buffett 调度 Zeus、Poseidon、Hades 时必须发送明确派工合同，并在每个阶段后读取 Markdown 做验收；缺少规划执行表、financeBusiness 来源时间戳、financeBusiness 内部核验、P&L 使用、AI 链条覆盖、候选分层或 Hades 上游完整性审计时，必须返工，不能进入下一阶段。
- 最终只输出当前本次要执行的整股买入/卖出行为。
- 最终报告必须包含 `## 当前持仓盈亏复盘`，展示总盈亏、个股盈亏以及这些信息如何影响本次决策。
- 最终报告必须在 `## 本次当前操作` 后包含 `## 交易后预计盈亏`，按限价成交和每笔 `USD 5` 费用计算卖出后已实现盈亏、买入后费用成本、剩余持仓未实现盈亏、交易后现金和交易后组合权益。
- 每笔交易固定计入 `USD 5` 费用。
- 用户交易时间限制为北京时间 `00:00` 前。

## 默认波段配置

`config.example.json` 与 `config.live.example.json` 支持以下波段字段：

- `trading_profile`: 默认 `swing_trading`
- `short_term_primary_horizon`: 默认 `swing_days_to_weeks`
- `short_term_single_trade_risk_pct`: 默认 `2.0`
- `strong_cycle_initial_position_pct_min/max`: 默认 `5.0` / `8.0`
- `short_term_stop_loss_pct_min/max`: 默认 `3.0` / `5.0`
- `strong_cycle_focus`: 默认覆盖 AI 产业链上中下游代表美股/ETF，包括 `MSFT, AMZN, GOOGL, META, ORCL, PLTR, SNOW, DDOG, NVDA, AMD, AVGO, MRVL, ARM, TSM, INTC, MU, WDC, STX, ASML, AMAT, LRCX, KLAC, CDNS, SNPS, ENTG, PLAB, AMKR, ANET, CIEN, COHR, LITE, DELL, HPE, SMCI, FLEX, JBL, CLS, SANM, VRT, ETN, PWR, GEV, TTMI, PANW, CRWD, NET, SMH, SOXX, QQQ, IGV, AIQ`
- `market_data_sources`: 默认且仅允许 `financeBusiness_mcp`
- `market_data_timeout_seconds`: 默认 `8.0`
- `market_data_cache_dir`: 默认 `workspace/buffett_research_advisor/data/market_data`
- `market_data_aktools_api_url`: 旧兼容字段，Buffett 当前行情/P&L 工作流不使用
- `market_data_http_api_url`: 旧兼容字段，Buffett 当前行情/P&L 工作流不使用

## 行情数据

Buffett 工作流行情、估值和 P&L 输入只使用 financeBusiness MCP。公共
`workspace/interface/market_data.py` 与
`workspace/buffett_research_advisor/market_data.py` 仅保留为旧导入兼容，
不得作为 Buffett 当前工作流的数据 fallback。

- Zeus 必须直接调用 `mcp__financeBusiness__StockCurrentMarket` 和
  `mcp__financeBusiness__StockMarketList`。
- 若 financeBusiness 字段缺失、过旧或内部冲突，记录
  `ZEUS_FIELD_FAILURE`，不得用其他源补齐。
- 本地 CSV/cache、AkShare、AKTools、HTTP/API、Stooq、Yahoo/yfinance、搜索或
  网页来源不能作为 Buffett 工作流行情、估值、P&L 或催化事实来源。

本地 fetch 脚本只保留为旧兼容入口，不用于 Buffett 当前行情/P&L
工作流。

## 命令

生成 prompt、快照和运行元数据，但不进入当前 Codex 执行流程：

```bash
python3 workspace/buffett_research_advisor/research_advisor.py buffett开始 --dry-run
```

默认本地文件模式：复盘仍读取上一轮本地 report/record 文件夹；SQLite 只允许只读交叉检查，最终结果不写入
`decisions.sqlite3`，只写本地 Markdown 和 `local_result_snapshot.json`：

```bash
python3 workspace/buffett_research_advisor/research_advisor.py buffett开始 --dry-run
```

只修复/生成第二步本地报告 `00_metadata.md`、`01_buffett_review.md`、
`02_buffett_plan.md`，不进入 Zeus/Poseidon/Hades：

```bash
python3 workspace/buffett_research_advisor/research_advisor.py prepare-step2 \
  --local-only \
  --prices <SYMBOL=PRICE,...> \
  --hkd-usd-rate <HKD_PER_USD>
```

正式启动完整 Buffett 工作流，需要先复制并确认 live 配置。默认
`execute_command` 为 `current_codex`，即把本地组合 prompt 交给当前 Codex
流程继续处理，不再启动子 Codex 进程。SQLite 默认禁写：

```bash
python3 workspace/buffett_research_advisor/research_advisor.py --config workspace/buffett_research_advisor/config.live.json buffett开始
```

`--local-only` 仍保留为兼容参数；当前默认已经只写本地文件、不写 SQLite：

```bash
python3 workspace/buffett_research_advisor/research_advisor.py --config workspace/buffett_research_advisor/config.live.json buffett开始 --local-only
```

如果显式把 `execute_command` 改成外部命令，`execute_timeout_seconds`
控制该命令最长运行时间。默认 `current_codex` 模式不会启动外部子进程，
而是在本轮 run 目录写入 `current_codex_handoff.json`，并把 prompt 镜像到
`stdout.txt` 供当前 Codex 流程读取。

## 输出

每次运行会生成：

- `prompt.md`：传给 Buffett 的完整执行合同。
- `base_short_snapshot.md`：本次读取的 `base_short.md` 只读快照。
- `run.json`：运行时间、路径、任务身份、费用和命令状态。
- `stdout.txt` / `stderr.txt`：`current_codex` 模式下 `stdout.txt` 镜像
  `prompt.md`，`stderr.txt` 为空；外部命令模式下为命令输出。
- `current_codex_handoff.json`：`current_codex` 模式下的当前流程交接元数据。
- `system_log.md`：本地运行日志。
- `prepare-step2` 额外生成 `report/record_YYYYMMDD_HHMMSS_序号/00_metadata.md`、
  `01_buffett_review.md`、`02_buffett_plan.md` 和 `step2_audit.json`。

`base_short.md` 的“操作记录”只由用户手动维护，本工具不会改写。

## 数据源限制

Buffett 工作流的行情、估值价格、P&L、成交量、FX 和当前交易 sizing
只使用 financeBusiness。新闻、公告、SEC/IR、宏观、政策、关键人物讲话、
网页、PDF、板块事件和反证必须恢复使用 aiwebsearch 优先，官方网页、
兼容 WebSearch/PDF 抽取作为 fallback；这些新闻源不得补齐缺失的
financeBusiness 行情字段。
