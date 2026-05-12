# Buffett A股短线手动建议系统

这是 A 股短线交易建议的本地手动运行系统，独立于美股系统。

## 规则

- 运行时区：北京时间 `Asia/Shanghai`
- 主市场：A 股
- 每次手动运行先读取唯一共享源文件 `workspace/buffett_a_short_advisor/base_short_A.md`
- 每次正式运行必须启动项目本地 `$buffett` 完整流程
- `base_short_A.md` 的“操作记录”只由用户手动填写真实交易，系统不修改
- 系统运行日志写入 `system_log.md`，每次运行快照写入 `runs/`

## 文件

- `a_short_advisor.py`：手动单次运行入口
- `base_short_A.md`：唯一共享的 A 股持仓、资金、用户人工交易记录源文件
- `config.example.json`：dry-run 安全配置
- `config.live.example.json`：正式执行配置示例
- `system_log.md`：手动运行日志
- `runs/`：每次运行的 prompt、只读审计快照和元数据；这里的快照不是新的操作记录源

## 命令

生成一次完整 Buffett 流程 prompt，但不执行外部命令：

```bash
python3 workspace/buffett_a_short_advisor/a_short_advisor.py run --dry-run
```

正式手动运行，需要先复制并确认 `config.live.json`：

```bash
python3 workspace/buffett_a_short_advisor/a_short_advisor.py --config workspace/buffett_a_short_advisor/config.live.json run
```

`run-once` 仍可作为 `run` 的兼容别名。

## 正式执行

正式模式必须配置 `execute_command`。如果不配置，脚本会退出报错，避免误以为已经启动 Buffett。

`execute_command` 支持以下占位符：

- `{prompt_file}`
- `{run_dir}`
- `{timestamp}`
- `{base_short_path}`

示例：

```json
{
  "execute_command": "/usr/local/bin/codex --search exec --cd /Users/newsong/Desktop/AIstudio/Freedom_Multi_EN --skip-git-repo-check -"
}
```

The runner sends `prompt.md` to `codex exec` through stdin. Keep the final `-`
in the command unless you intentionally change `a_short_advisor.py`.

## Buffett 完整流程要求

每次 prompt 都要求 Buffett：

- 先读唯一共享 `base_short_A.md` 的用户手工交易记录
- 读取上一次同类 SQLite 决策
- Buffett 复盘
- Buffett 规划
- Zeus 情报
- Poseidon 研究
- Hades 验证
- 圆桌会议
- 最终决策
- 写中文本地 Markdown，并在 SQLite 决策日志保存英文圆桌会议和最终决策

## 共享记录文件

`workspace/buffett_a_short_advisor/base_short_A.md` 是唯一共享的 A 股短线操作记录文件。用户只维护这一份文件。系统每次运行会读取它，并在 `runs/` 中保存只读快照用于审计，但不会创建第二份可写操作记录。
