# Buffett Short Advisor

This is a manual runner for Buffett short-term trading advice.

## Purpose

- Run on Beijing time, `Asia/Shanghai`.
- Focus the manual advice on US short-term trading.
- Read `base_short.md` before every run, including user-filled manual operation records.
- Read the previous same-task SQLite decision before continuing the Buffett workflow.
- Start the full project-local `$buffett` workflow on every live run.
- Store prompts, logs, and run metadata under `workshop/buffett_short_advisor/runs/`.
- Keep `base_short.md` operation records user-owned; the runner never writes user trade records.
- Execute an external Buffett/Codex command in live mode.

## Files

- `short_advisor.py`: manual one-shot runner.
- `config.example.json`: dry-run/safe example configuration.
- `config.live.example.json`: live example that starts an external Buffett/Codex command.
- `runs/`: generated runtime files.
- `system_log.md`: manual-run log.
- Root `base_short.md`: position, capital, and user-filled manual trade records read before every run.

## Quick Commands

Generate one full-workflow Buffett prompt and write a system-log entry without executing an external command:

```bash
python3 workshop/buffett_short_advisor/short_advisor.py run --dry-run
```

Run one live manual check after confirming `execute_command` in a local config:

```bash
python3 workshop/buffett_short_advisor/short_advisor.py --config workshop/buffett_short_advisor/config.live.json run
```

`run-once` remains available as a compatibility alias for `run`.

## Optional Execution Command

Dry-run mode is safe and creates a full-workflow prompt but does not call an external model or trading system. Live mode requires `execute_command`; without it the runner exits with an error because live runs are expected to start the full Buffett workflow.

To make each manual live run execute a command, create a local config copied from `config.live.example.json` and confirm `execute_command`. The command can use these placeholders:

- `{prompt_file}`
- `{run_dir}`
- `{timestamp}`
- `{base_short_path}`

Example:

```json
{
  "execute_command": "codex exec --cd /Users/newsong/Desktop/AIstudio/Freedom_Multi_EN --prompt-file {prompt_file}"
}
```

Keep the command local. This system does not submit orders by itself.

The generated prompt explicitly requires the full Buffett local workflow:

- Buffett review of user manual trade records and the previous same-task SQLite decision
- Buffett planning
- Zeus intelligence
- Poseidon research
- Hades verification
- Roundtable
- Final decision
- Chinese local Markdown and SQLite decision journal with English roundtable/final-decision text

## Run Behavior

Each run creates:

- `prompt.md`: the exact Buffett prompt for this manual check.
- `base_short_snapshot.md`: the state read before the run.
- `run.json`: metadata, run timestamp, market, and command status.
- `stdout.txt` and `stderr.txt` if an external command is executed.

If `write_system_log` is enabled, `system_log.md` receives a concise manual-run entry. `base_short.md` is only read and snapshotted. Its "操作记录" section is for user-filled manual stock trades based on the suggestions.
