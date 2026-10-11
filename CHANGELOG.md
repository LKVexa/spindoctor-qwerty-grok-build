# Changelog

## 1.1.0 - 2026-10-11

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics, CSV report copies and measurement-CSV fitting equations. All 241
  presets replayed. Tools `spindoctor_functions` (function table, marked read-only) and `spindoctor_test_theory` (theory testing
  from a file, pasted text or the chat, with TXT+JSON+PDF theory reports). 1.0 described SpinDoctor 3.0.3 and a 29-qubit cap.
- **Installable as a marketplace.** The repo root is now a Grok Build marketplace (`.grok-plugin/marketplace.json`) with the plugin in
  `spindoctor-qwerty/`, so `grok plugin marketplace add LKVexa/spindoctor-qwerty-grok-build` then
  `grok plugin install spindoctor-qwerty --trust` works. 1.0 had only the plugin folder.
- **Grok's own plugin variable.** `.mcp.json`, the commands and the skill used `${CLAUDE_PLUGIN_ROOT}` (and 1.0's README doubted it
  was expanded). Grok Build documents and expands `${GROK_PLUGIN_ROOT}`; everything now uses it, and the host check confirms the
  installed folder is filled in for the MCP server, the skill, the commands and the subagent.
- **Windows.** The server starts with `python3`, which the python.org installer doesn't provide on Windows; `tools/set_python.py`
  switches it to `py` or `python` in a clone before installing from it (`grok plugin update` after changes).
- Commands updated for 3.1.2 (new `/qwerty-folder`), the helper agent runs folders and theory tests, the empty `hooks/hooks.json` is
  gone (no hooks), `PYTHONUTF8` set for the server, plugin manifest and catalog entry carry license, author, homepage and keywords.
- Tests: `tests/grok_host_check.py` (static checks; the xai-org/plugin-marketplace catalog validator and plugin-index extractor; and
  the real Grok Build CLI: validate, marketplace add, install, inspect, headless sessions against a local stand-in model through
  `search_tool`/`use_tool`, a slash command, the skill, the plugin subagent, the shell fallback, the Windows route, the shared
  end-to-end suite, uninstall).
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` plugin folder (skill, four commands, helper agent, empty hooks, `.mcp.json` with
  `${CLAUDE_PLUGIN_ROOT}`), engine described as SpinDoctor 3.0.3.
