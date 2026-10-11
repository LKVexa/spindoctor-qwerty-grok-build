# SpinDoctor Qwerty for Grok Build

A [Grok Build](https://github.com/xai-org/grok-build) plugin that runs the **SpinDoctor 3.1.2 quantum-circuit simulator** on your
computer: `q.*` circuit scripts (1-298 logical qubits), the 241 built-in presets, folders of command files (`q.folder`), and theory
tests from a file, pasted text or the chat itself, each with TXT, PDF, JSON and CSV reports. It adds a local MCP server (6 tools), a
skill, five slash commands and a helper subagent.

> **Honest limits.** SpinDoctor is a classical FP64 simulator. It is not a quantum computer, does not connect to quantum hardware,
> and gives no quantum speed-up or advantage. One entangled group is limited to 59 qubits and dense groups are limited by memory
> (2^n x 16 bytes). Registers wider than 29 qubits sample in basis Z only. Histograms are seeded Born samples.

Version 1.1.0 - engine 1.1.0 (SpinDoctor 3.1.2 parity) - tested with Grok Build 1.0.50 - Python 3.8+, standard library only - no
network, no account and no keys for the plugin itself.

**Not using Grok Build?** This repo is the plugin for the Grok Build coding CLI (`grok`). For Grok Bot and other agents that load
Agent Skills folders, use [spindoctor-qwerty-grok-bot-skill](https://github.com/LKVexa/spindoctor-qwerty-grok-bot-skill): the same
engine and reports as a single `SKILL.md` folder that the agent runs through its shell.

## Install

```bash
grok plugin marketplace add LKVexa/spindoctor-qwerty-grok-build
grok plugin install spindoctor-qwerty --trust
```

Without `--trust` Grok only shows a warning and installs nothing: installing activates the plugin's MCP server, skill, commands and
agent. Grok copies the plugin into `~/.grok/installed-plugins/` and enables it. Check with `grok plugin list` or `grok inspect`
(skill `spindoctor-qwerty`, commands `qwerty-*`, agent `spindoctor-qwerty:qwerty-helper`, MCP server `spindoctor-qwerty (stdio)`).
Start a new session after installing. Update with `grok plugin update spindoctor-qwerty`; remove with
`grok plugin uninstall spindoctor-qwerty --confirm`. From a local clone: `grok plugin marketplace add ./spindoctor-qwerty-grok-build`.

Requirements: Python 3.8 or newer as `python3`. **Windows:** the python.org installer provides `py` and `python`, not `python3`. In a
clone run `py tools/set_python.py py` (or `python`), then add the clone as the marketplace and install from it as above.

## What's in the repo

| Path | What it is |
|---|---|
| `.grok-plugin/marketplace.json` | Marketplace index: one plugin, `spindoctor-qwerty`, local source `./spindoctor-qwerty` |
| `spindoctor-qwerty/.grok-plugin/plugin.json` | Plugin manifest (name, version, license, author) |
| `spindoctor-qwerty/.mcp.json` | MCP server `spindoctor-qwerty`: `python3 ${GROK_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py` |
| `spindoctor-qwerty/skills/spindoctor-qwerty/` | Skill (`SKILL.md`), the bundled engine (`spindoctor/`), CLI and MCP server (`scripts/`), examples |
| `spindoctor-qwerty/commands/` | `/qwerty-functions`, `/qwerty-run`, `/qwerty-preset`, `/qwerty-folder`, `/qwerty-theory` |
| `spindoctor-qwerty/agents/qwerty-helper.md` | Subagent `spindoctor-qwerty:qwerty-helper` |
| `tools/set_python.py` | Switches the server's Python command (Windows) |
| `FUNCTIONS.md` | The full function table with a runnable example for every command |
| `tests/` | Host check, shared end-to-end suite, local OpenAI-compatible stand-in, reference outputs |

No hooks: nothing runs on its own.

## Using it

- Ask in plain language ("show the SpinDoctor functions", "run a 3-qubit GHZ circuit"), use the slash commands, run the skill with
  `/spindoctor-qwerty`, or delegate to the helper subagent.
- Grok lists MCP tools through `search_tool` and calls them with `use_tool` by catalog name: `spindoctor-qwerty__spindoctor_functions`
  and so on. Searching for `spindoctor-qwerty` finds all six (a bare `spindoctor` matches fewer, since search ranks by description).
- Grok asks before tool calls unless you approve them (`--yolo` or `--always-approve` turn that off; use only in folders you trust).
- Pass absolute paths. Reports and state go to `~/spindoctor-workspace` unless a tool call passes `workspace`.
- If the tools aren't available, the skill tells Grok to run the CLI with the shell tool:
  `python3 "${GROK_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py" functions` (Grok fills in the installed folder).

### Listing in the official catalog

[xai-org/plugin-marketplace](https://github.com/xai-org/plugin-marketplace) lists third-party plugins as a remote source pinned to a
full commit. An entry for this plugin would look like this (sha = the commit to ship, from `git ls-remote ... HEAD`):

```json
{
  "name": "spindoctor-qwerty",
  "description": "SpinDoctor 3.1.2 quantum-circuit simulator (classical, not a quantum computer)",
  "category": "education",
  "source": { "source": "url", "url": "https://github.com/LKVexa/spindoctor-qwerty-grok-build.git", "path": "spindoctor-qwerty", "sha": "<40-hex commit>" },
  "homepage": "https://github.com/LKVexa/spindoctor-qwerty-grok-build",
  "keywords": ["quantum", "simulator"]
}
```

The host check runs that catalog's own validator and plugin-index extractor on this repo. Nothing has been submitted to it.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | `/qwerty-functions` or ask: "show the SpinDoctor functions" |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | `/qwerty-preset qc-067 shots=64` |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | `/qwerty-theory we discussed`, ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Grok Build, give the file's absolute path on your computer (or paste the text).
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `spindoctor-qwerty/skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 spindoctor-qwerty/skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.


## Testing

| Test | Command |
|---|---|
| Static checks | `python3 tests/grok_host_check.py` |
| + official catalog tools | `python3 tests/grok_host_check.py --spec /path/to/plugin-marketplace` (a clone of xai-org/plugin-marketplace) |
| Real Grok Build | `python3 tests/grok_host_check.py --grok "$(command -v grok)" --spec /path/to/plugin-marketplace` |

**Real host, scripted model.** The host check uses the real Grok Build CLI (1.0.50 release binary) with a throwaway HOME and no xAI
account or sign-in: `grok plugin validate`, `plugin marketplace add`, `plugin install --trust` (and that installing without `--trust`
does nothing), `grok inspect`, then headless `grok -p` sessions with a custom model (`[model.stub]` in the throwaway config, placeholder
key) pointing at `tests/stub_llm.py`, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1. Through Grok's own MCP
client (`search_tool`/`use_tool`) it shows the function table, runs a Bell circuit and presets qc-001/qc-002/qc-003, tests a theory
from the chat (verdict *supported*, PDF written), expands `/qwerty-preset`, loads the skill, runs the helper subagent and the CLI
through the shell tool, checks the Windows route (`set_python.py` + `plugin update`), runs the shared end-to-end suite through the
installed plugin's MCP server and uninstalls. Not tested: a real Grok model choosing the tools, the TUI and its approval prompts,
Windows, macOS. Results: [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). Grok is a trademark of xAI; this project is not affiliated with xAI.
