# 00_metadata

## 任务身份

| 项目 | 内容 |
|---|---|
| 用户触发 | `buffett开始` |
| 运行时间 | 2026-05-12 15:37:14 CST（星期二） |
| 交易截止 | 2026-05-13 00:00:00 CST |
| 任务目录 | `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004` |
| 输入文件 | `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/base_short.md` |
| task_type | `portfolio_review` |
| subject | `us_equity_portfolio` |
| market | `US equities` |
| task_key | `portfolio_review:993c7d93e383` |
| report 命名 | `record_YYYYMMDD_HHMMSS_序号` |
| 复盘主索引 | `local_report_folder` |
| 上一轮本地记录 | `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_224540_003` |
| SQLite 模式 | `disabled` |

Why this task_key：`buffett开始` 是固定的美股组合复盘与本轮操作任务，身份必须稳定为 `task_type=portfolio_review`、`subject=us_equity_portfolio`、`market=US equities`；本轮不把候选股列表写入 task_key，避免同一组合复盘因候选池变化而失去历史连续性。

复盘主规则：本轮起复盘按本地 report 文件夹进行，优先读取 `report/record_*` 中上一轮同任务完整报告；若没有 record 新格式，才允许读取旧 `report/YYYY-MM-DD_*` 完整报告作为 legacy 背景。SQLite 只作为可选只读英文索引交叉检查，不得替代本地中文 Markdown 复盘，也不得写入本轮结果。

## 输入与资产范围

- 当前解析出的 USD 持仓：AMD、ANET、FLEX、KO、MSFT、NVDA、SPY、TSM。
- 组合背景现金：165,627.00 HKD。港股和港币资金只作为背景或可换汇约束，不生成港股/A股交易建议。
- 本轮提供的价格字段：AMD、ANET、FLEX、KO、MSFT、NVDA、SPY、TSM。
- 交易费用：每笔 BUY/SELL 固定 USD 5。
- 交易单位：整股；禁止碎股、百分比股数或只写金额下单。

## 策略边界

- 所有策略遵从波段交易策略：本轮买入、卖出、加仓、止盈、止损、等待和复盘，都以数日至数周为默认目标。
- 长期基本面只作为候选质量、估值和事件风险过滤器；当前 BUY/SELL 必须由波段 setup、量价、相对强弱、费用后 R/R、止损和交易窗口共同支持。
- 不承诺盈利；“需要利润”在本系统中等价于费用后正期望、明确下行、分阶段暴露、确认加仓、止盈保护和可复盘退出。

## 本轮 AI 产业链候选池

重点候选池必须覆盖 AI 产业链上中下游。Zeus 和 Poseidon 先做全链条轻量初筛，再筛出 Top 8-12 做深度波段计划。

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

## 特别观察范围

AMD（AMD/GPU-CPU加速器）、MU（美光/存储-HBM）、FLEX（伟创力/AI服务器EMS）、INTC（英特尔/晶圆制造、AI PC与服务器CPU、美国半导体政策）、WDC（西部数据/存储设备）、STX（希捷/存储设备）、VRT（Vertiv/数据中心电力散热）、ANET（Arista/AI网络）、TSM（台积电/晶圆代工）、NVDA（英伟达/GPU与AI加速器）、SMH（半导体ETF）、SOXX（半导体ETF）、QQQ（纳指100 ETF）

- INTC（英特尔）必须作为独立特别观察标的，而不是只并入半导体行业概括；Zeus、Poseidon、Hades 和圆桌都要给出独立结论。

## 指数基准与可交易代理

纳斯达克和标普必须先作为市场 regime / 风险偏好基准处理，再映射到可交易 ETF 代理；指数本身不得进入 `本次当前操作`。

| 指数基准 | financeBusiness 指数通道 | 可交易代理 | 当前动作规则 |
|---|---|---|---|
| 纳斯达克综合指数 | StockIndexList(IXIC) | QQQ | 指数只做市场 regime 和相对强弱背景；当前 BUY/SELL 只能使用 QQQ 等可交易 ETF 代理。 |
| 标普 500 | StockIndexList(SPX/GSPC/INX/SP500) | SPY | 若 financeBusiness 指数编码不可用，必须记录指数缺口；仍需用 SPY 作为可交易 ETF 代理进行审议。 |

## 数据源计划

- 行情数据源：`financeBusiness_mcp`；Buffett 工作流结构化行情只允许 financeBusiness MCP。
- 本地适配层：公共 `workspace/interface/market_data.py` 不得用于本轮 Buffett 行情补源；旧 `workspace/buffett_research_advisor/market_data.py` 仅作历史兼容。
- manifest：本轮无预取数据包；禁止伪造 manifest，后续直接调用 financeBusiness MCP，不得 fallback。
- 价格只做 financeBusiness 内部核验：`StockCurrentMarket` 对 `StockMarketList` 最新历史；不能使用外部核验源。
- 新闻、公告、SEC/IR、宏观和政策：恢复使用 aiwebsearch、官方网页、兼容 WebSearch 和 PDF 抽取；financeBusiness 只负责行情、价格、成交量、FX、P&L 和估值价格输入。

## 评分、分层与否决

- 板块评分：market regime、板块相对强弱、催化新鲜度、利润池归属、估值/拥挤度、技术结构、政策/地缘风险。
- 股票分层：核心候选 / 战术候选 / 观察名单 / 回避或否决。
- 波段 setup：动能突破 / 回撤承接 / 超跌反弹 / 止损卖出 / 止盈卖出 / 移动止损。
- Hades veto：financeBusiness 缺字段或内部冲突、数据过期、止损缺失、费用后 R/R 不足、FOMO 追价、仓位超过风险预算、单股超过 25%、把波段失败票拖成长线。
- 强周期三态/四态裁决：必须使用 `workspace/analysis/cli.py swing-verdict`
  或等价逻辑，把候选标记为 `current_trade`、`small_starter`、`wait`
  或 `hard_veto`。上涨多本身不是 FOMO；只有 R/R、止损、量价、跳空或
  仓位约束失败时才是硬否决。若个股数据不足，必须先审计 SMH/SOXX/QQQ
  等 ETF/basket fallback 后才能给整体 no-trade。

## 计划文件

- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/00_metadata.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/01_buffett_review.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/02_buffett_plan.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/03_zeus_intelligence.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/04_poseidon_research.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/05_hades_verification.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/06_roundtable.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/07_final_decision.md`
- `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260512_153714_004/local_result_snapshot.json（legacy 旧目录可读取既有 db_record.json）`
