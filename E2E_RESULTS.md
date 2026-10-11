# E2E results - spindoctor-qwerty-grok-build 1.1.0

Host: **real Grok Build 1.0.50** (official release binary from x.ai/cli, Linux x64) with a throwaway HOME and no xAI account or
sign-in. Model turns come from `tests/stub_llm.py`, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1 (a
`[model.stub]` custom model with a placeholder key), so tool calls are scripted; everything between the model and the engine
(marketplace add, trust-gated install, `${GROK_PLUGIN_ROOT}` expansion, MCP startup, `search_tool`/`use_tool`, slash-command and skill
expansion, the plugin subagent, the shell tool, update, uninstall) is the real Grok Build. The marketplace files were also checked with
the xai-org/plugin-marketplace validator and plugin-index extractor. Python 3.13.5.

Not tested: a real Grok model choosing the tools by itself, the TUI and its approval prompts, Windows, macOS.

## Host check: 24/24

| Result | Check |
|---|---|
| PASS | marketplace index .grok-plugin/marketplace.json: name, description, owner, one kebab-case entry with a local source ./spindoctor-qwerty |
| PASS | plugin manifest spindoctor-qwerty/.grok-plugin/plugin.json: name, version 1.1.0, description, author, license GPL-3.0-or-later |
| PASS | .mcp.json: stdio python3 ${GROK_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py (Grok's own variable), UTF-8 env, no secrets |
| PASS | skill + 5 commands + agent: front matter (skill name/description/license; commands description + argument-hint + $ARGUMENTS; agent name/description), honest limits, no Droid/Claude leftovers, no hooks |
| PASS | tools/set_python.py: sets the Windows command (py), refuses shell metacharacters, python3 restores .mcp.json byte for byte |
| PASS | MCP server starts (initialize answered, server spindoctor-qwerty 1.1.0) |
| PASS | xai-org/plugin-marketplace validate-catalog.py accepts this repo's .grok-plugin/marketplace.json |
| PASS | xai-org plugin_catalog.extract_plugin (the plugin-index generator) sees 1 skill, 5 commands, 1 agent, MCP server spindoctor-qwerty (stdio), no hooks, version 1.1.0 |
| PASS | official-catalog entry (remote url source + plugin path, pinned 40-hex sha) validates; an unpinned ref is rejected |
| PASS | real grok 1.0.50 (c58f321264ba) (no xAI account): grok plugin validate -> manifest valid, 1.1.0, skills/commands/agents/MCP servers |
| PASS | real grok: plugin install without --trust only warns and installs nothing |
| PASS | real grok: plugin marketplace add <repo> + plugin install spindoctor-qwerty --trust -> 1.1.0 copied to ~/.grok/installed-plugins, enabled |
| PASS | real grok inspect: skill + 5 commands, agent spindoctor-qwerty:qwerty-helper, MCP server spindoctor-qwerty (stdio), plugin enabled |
| PASS | headless grok -p --yolo (custom model -> local stand-in): MCP server connected with 6 tools, search_tool/use_tool offered, skill + 5 commands listed with installed paths |
| PASS | search_tool (query spindoctor-qwerty, limit 10) finds all 6 tools as spindoctor-qwerty__<tool> |
| PASS | use_tool via Grok: function table, Bell run (ok, PDF report in the workspace), preset qc-001 ok |
| PASS | theory test from the chat via Grok: verdict supported, 2 excerpts recorded, theory PDF on disk |
| PASS | shell fallback: run_terminal_command runs the installed plugin's CLI (gate table); session ends with the answer |
| PASS | slash command /qwerty-preset qc-002: Grok expands the plugin command with $ARGUMENTS; the preset runs |
| PASS | skill /spindoctor-qwerty: body loaded with ${GROK_PLUGIN_ROOT} replaced by the installed folder |
| PASS | plugin subagent spindoctor-qwerty:qwerty-helper: runs with the helper instructions (${GROK_PLUGIN_ROOT} filled in), inherits the MCP server, runs qc-003, result returns to the parent |
| PASS | shared E2E suite through the installed plugin's MCP server: SUMMARY 12/12 |
| PASS | Windows route: set_python.py python in the clone + grok plugin update -> the installed .mcp.json starts `python` |
| PASS | real grok: plugin uninstall --confirm removes the plugin |

## Shared end-to-end suite through the installed plugin: 12/12

Started with the installed plugin's MCP server: `python3 ~/.grok/installed-plugins/spindoctor-qwerty-<id>/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py`.

| Result | Check |
|---|---|
| PASS | initialize (server spindoctor-qwerty 1.1.0) |
| PASS | tools/list exposes the 6 tools |
| PASS | function table (Markdown, 19 sections, 298-qubit limits listed) |
| PASS | 241 presets listed |
| PASS | one script per command family (16 families, every table example) |
| PASS | 298-qubit circuit with mcx7 (prepared-factor-Born-Z) |
| PASS | q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped) |
| PASS | theory from a file -> supported, TXT+PDF report |
| PASS | theory from a chat summary + quoted excerpts -> supported |
| PASS | theory from an exported chat transcript -> supported |
| PASS | presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences) |
| PASS | TXT+PDF reports valid (255 PDFs, 255 TXT twins) |

## Runs

- Clean-room copy (fresh folder, no git metadata): host check 24/24 (incl. xai-org catalog tools), shared E2E 12/12 - PASS
