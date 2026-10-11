#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - Grok Build host check
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run from the repo root:

  python3 tests/grok_host_check.py                                         # static checks only
  python3 tests/grok_host_check.py --spec /path/to/xai-org/plugin-marketplace # + the marketplace's own catalog tools
  python3 tests/grok_host_check.py --grok "$(command -v grok)" [--spec ...] [--out tests/host_check.json]

Static: marketplace index, plugin manifest, .mcp.json, skill, commands, agent, set_python.py, MCP server `initialize`.
--spec: runs the xai-org/plugin-marketplace scripts (validate-catalog.py and plugin_catalog.extract_plugin) on this repo, plus a
remote-source catalog entry pinned to a commit, as the official catalog would list it. Nothing from that repo is copied here.
--grok: with a throwaway HOME, the real Grok Build CLI: `grok plugin validate`, `plugin marketplace add <this repo>`,
`plugin install spindoctor-qwerty --trust`, `plugin list --json`, `grok inspect`, then headless `grok -p` sessions against
tests/stub_llm.py, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1 (a `[model.stub]` entry with a
placeholder key in the throwaway config: no xAI account, no sign-in, nothing leaves the machine). Covers search_tool/use_tool with the
6 MCP tools, a slash command, the skill, the plugin subagent, the shell fallback, set_python.py + `plugin update`, the shared end-to-end
suite through the installed plugin's MCP server, and `plugin uninstall`. Standard library only.
"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); PL = os.path.join(ROOT, "spindoctor-qwerty")
SK = os.path.join(PL, "skills", "spindoctor-qwerty"); MCP = os.path.join(SK, "scripts", "spindoctor_mcp.py")
TOOLS = ["spindoctor_functions", "spindoctor_list_presets", "spindoctor_report", "spindoctor_run_preset", "spindoctor_run_script", "spindoctor_test_theory"]
N = lambda t: "spindoctor-qwerty__" + t
CMDS = ["qwerty-folder", "qwerty-functions", "qwerty-preset", "qwerty-run", "qwerty-theory"]
R = []
OK = lambda s: bool(re.search(r'"ok":\s*true', s or ""))


def T(name, ok, detail=""):
    R.append({"check": name, "pass": bool(ok), "detail": str(detail)[:600]})
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + str(detail)[:500])); sys.stdout.flush()


def mcp_init(cmd, timeout=60):
    req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "check", "version": "1"}}}) + "\n"
    p = subprocess.run(cmd, input=req.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def fm(path):
    t = open(path, encoding="utf-8").read()
    return t.split("---")[1] if t.startswith("---") else "", t


def static():
    mk = json.load(open(os.path.join(ROOT, ".grok-plugin", "marketplace.json"), encoding="utf-8"))
    e = (mk.get("plugins") or [{}])[0]
    T("marketplace index .grok-plugin/marketplace.json: name, description, owner, one kebab-case entry with a local source ./spindoctor-qwerty",
      mk.get("name") == "spindoctor-qwerty-grok-build" and mk.get("description") and mk.get("owner", {}).get("name") and len(mk["plugins"]) == 1
      and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", e.get("name", "")) and e.get("source") == {"type": "local", "path": "./spindoctor-qwerty"}, mk)
    p = json.load(open(os.path.join(PL, ".grok-plugin", "plugin.json"), encoding="utf-8"))
    T("plugin manifest spindoctor-qwerty/.grok-plugin/plugin.json: name, version 1.1.0, description, author, license GPL-3.0-or-later",
      p.get("name") == "spindoctor-qwerty" and p.get("version") == "1.1.0" and p.get("description") and p.get("license") == "GPL-3.0-or-later"
      and p.get("author", {}).get("name") == "RUSSELL PHILIP SMITHSON", p)
    m = json.load(open(os.path.join(PL, ".mcp.json"), encoding="utf-8"))["mcpServers"]["spindoctor-qwerty"]
    T(".mcp.json: stdio python3 ${GROK_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py (Grok's own variable), UTF-8 env, no secrets",
      m.get("type") == "stdio" and m.get("command") == "python3" and m.get("args") == ["${GROK_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py"]
      and m.get("env") == {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}, m)
    f, sk = fm(os.path.join(SK, "SKILL.md"))
    cm = {c: fm(os.path.join(PL, "commands", c + ".md")) for c in CMDS}
    af, ag = fm(os.path.join(PL, "agents", "qwerty-helper.md"))
    body = sk + ag + "".join(t for _, t in cm.values())
    T("skill + 5 commands + agent: front matter (skill name/description/license; commands description + argument-hint + $ARGUMENTS; agent name/description), honest limits, no Droid/Claude leftovers, no hooks",
      "name: spindoctor-qwerty" in f and "license: GPL-3.0-or-later" in f and "not a quantum computer" in sk
      and sorted(os.listdir(os.path.join(PL, "commands"))) == [c + ".md" for c in CMDS]
      and all("description:" in a and "argument-hint:" in a for a, _ in cm.values()) and all("$ARGUMENTS" in t for c, (_, t) in cm.items() if c != "qwerty-functions" or True)
      and "name: qwerty-helper" in af and "description:" in af and "mcpServers" not in af
      and not re.search(r"DROID|Droid|CLAUDE_PLUGIN_ROOT|Execute", body) and not os.path.exists(os.path.join(PL, "hooks")), f[:200])
    tmp = tempfile.mkdtemp(prefix="sdq-setpy-"); shutil.copytree(ROOT, os.path.join(tmp, "r"), ignore=shutil.ignore_patterns(".git", "tests"))
    mj = os.path.join(tmp, "r", "spindoctor-qwerty", ".mcp.json"); orig = open(mj, "rb").read()
    sp = lambda *a: subprocess.run([sys.executable, os.path.join(tmp, "r", "tools", "set_python.py")] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    r1 = sp("py"); c1 = json.load(open(mj))["mcpServers"]["spindoctor-qwerty"]["command"]; r2 = sp("py; rm -rf /"); r3 = sp("python3")
    T("tools/set_python.py: sets the Windows command (py), refuses shell metacharacters, python3 restores .mcp.json byte for byte",
      r1.returncode == 0 and c1 == "py" and r2.returncode == 2 and r3.returncode == 0 and open(mj, "rb").read() == orig, (r1.stdout, r2.stdout))
    shutil.rmtree(tmp, ignore_errors=True)
    rc, out, err = mcp_init([sys.executable, MCP])
    T("MCP server starts (initialize answered, server spindoctor-qwerty 1.1.0)", '"spindoctor-qwerty"' in out and '"1.1.0"' in out, (rc, out[:200], err[-300:]))


def spec(path):
    sc = os.path.join(path, "scripts")
    r = subprocess.run([sys.executable, os.path.join(sc, "validate-catalog.py")], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    T("xai-org/plugin-marketplace validate-catalog.py accepts this repo's .grok-plugin/marketplace.json", r.returncode == 0, r.stdout.decode()[-400:])
    sys.path.insert(0, sc)
    try:
        import plugin_catalog
        from pathlib import Path
        x = plugin_catalog.extract_plugin(Path(PL))
    finally:
        sys.path.remove(sc)
    names = lambda k: sorted(i.get("name") for i in x.get("components", {}).get(k, []))
    T("xai-org plugin_catalog.extract_plugin (the plugin-index generator) sees 1 skill, 5 commands, 1 agent, MCP server spindoctor-qwerty (stdio), no hooks, version 1.1.0",
      names("skills") == ["spindoctor-qwerty"] and names("commands") == CMDS and names("agents") == ["qwerty-helper"]
      and names("mcpServers") == ["spindoctor-qwerty"] and not x.get("components", {}).get("hooks") and x.get("version") == "1.1.0", json.dumps(x)[:500])
    tmp = tempfile.mkdtemp(prefix="sdq-cat-"); os.makedirs(os.path.join(tmp, ".grok-plugin"))
    entry = {"name": "spindoctor-qwerty", "description": "SpinDoctor 3.1.2 quantum-circuit simulator (classical)", "category": "education",
             "source": {"source": "url", "url": "https://github.com/LKVexa/spindoctor-qwerty-grok-build.git", "path": "spindoctor-qwerty", "sha": "0" * 40},
             "homepage": "https://github.com/LKVexa/spindoctor-qwerty-grok-build", "keywords": ["quantum", "simulator"]}
    json.dump({"name": "t", "owner": {"name": "t"}, "plugins": [entry]}, open(os.path.join(tmp, ".grok-plugin", "marketplace.json"), "w"))
    ok1 = subprocess.run([sys.executable, os.path.join(sc, "validate-catalog.py")], cwd=tmp, stdout=subprocess.PIPE).returncode == 0
    entry["source"]["sha"] = "main"; json.dump({"name": "t", "owner": {"name": "t"}, "plugins": [entry]}, open(os.path.join(tmp, ".grok-plugin", "marketplace.json"), "w"))
    ok2 = subprocess.run([sys.executable, os.path.join(sc, "validate-catalog.py")], cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0
    shutil.rmtree(tmp, ignore_errors=True)
    T("official-catalog entry (remote url source + plugin path, pinned 40-hex sha) validates; an unpinned ref is rejected", ok1 and ok2)


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def content(c):
    if isinstance(c, list): return "".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
    return c if isinstance(c, str) else json.dumps(c)


def real(grok):
    tmp = tempfile.mkdtemp(prefix="sdq-grok-"); home = os.path.join(tmp, "home"); work = os.path.join(tmp, "work"); ws = os.path.join(tmp, "ws")
    for d in (home, work): os.makedirs(d)
    port = free_port(); log = os.path.join(tmp, "stub.jsonl"); script = os.path.join(tmp, "script.json")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GROK", "XAI", "SPINDOCTOR", "OPENAI", "CLAUDE"))}
    env.update(HOME=home, USERPROFILE=home, NO_COLOR="1")
    run = lambda args, t=300: subprocess.run([grok] + args, cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=t)
    stub = None
    src = os.path.join(tmp, "spindoctor-qwerty-grok-build"); shutil.copytree(ROOT, src, ignore=shutil.ignore_patterns(".git", "__pycache__", "e2e_results.json", "host_check.json"))
    try:
        v = run(["--version"], t=60).stdout.decode().strip()
        o = run(["plugin", "validate", os.path.join(src, "spindoctor-qwerty")], t=60).stdout.decode("utf-8", "replace")
        T("real %s (no xAI account): grok plugin validate -> manifest valid, 1.1.0, skills/commands/agents/MCP servers" % v,
          "Plugin manifest is valid." in o and "version: 1.1.0" in o and "1 skill dir(s), 1 command dir(s), 1 agent dir(s), MCP servers" in o, o[-300:])
        r = run(["plugin", "install", src + os.sep + "spindoctor-qwerty"]); o = r.stdout.decode("utf-8", "replace")
        T("real grok: plugin install without --trust only warns and installs nothing", "spindoctor-qwerty" not in run(["plugin", "list"], t=60).stdout.decode(), o[-300:])
        o1 = run(["plugin", "marketplace", "add", src]).stdout.decode("utf-8", "replace")
        o2 = run(["plugin", "install", "spindoctor-qwerty", "--trust"]).stdout.decode("utf-8", "replace")
        lj = run(["plugin", "list", "--json"], t=60).stdout.decode("utf-8", "replace")
        try: lst = json.loads(lj[lj.index("["):])
        except Exception: lst = []
        inst = lst[0]["path"] if lst else ""
        T("real grok: plugin marketplace add <repo> + plugin install spindoctor-qwerty --trust -> 1.1.0 copied to ~/.grok/installed-plugins, enabled",
          "Added marketplace source: spindoctor-qwerty-grok-build" in o1 and "Installed 1 plugin(s)" in o2 and lst and lst[0]["version"] == "1.1.0"
          and inst.startswith(os.path.join(home, ".grok", "installed-plugins")) and os.path.isfile(os.path.join(inst, "skills", "spindoctor-qwerty", "scripts", "spindoctor_mcp.py")),
          (o1[-200:], o2[-200:], lj[-300:]))
        o = run(["inspect"], t=120).stdout.decode("utf-8", "replace")
        T("real grok inspect: skill + 5 commands, agent spindoctor-qwerty:qwerty-helper, MCP server spindoctor-qwerty (stdio), plugin enabled",
          all(re.search(r"%s\s+plugin: spindoctor-qwerty" % c, o) for c in ["spindoctor-qwerty"] + CMDS) and "spindoctor-qwerty:qwerty-helper" in o
          and re.search(r"spindoctor-qwerty \(stdio\)\s+plugin: spindoctor-qwerty", o) and "spindoctor-qwerty (user, enabled)" in o, o[-600:])
        with open(os.path.join(home, ".grok", "config.toml"), "a") as f:
            f.write('\n[model.stub]\nmodel = "stub"\nbase_url = "http://127.0.0.1:%d/v1"\nname = "Local stub"\napi_key = "local-stub"\ncontext_window = 128000\n' % port)

        def session(steps, prompt):
            json.dump(steps, open(script, "w")); open(log, "w").close()
            nonlocal stub
            if stub: stub.kill(); stub.wait()
            stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(port), log, script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            r = run(["-p", prompt, "-m", "stub", "--yolo", "--no-auto-update"], t=900); o = r.stdout.decode("utf-8", "replace")
            recs = [json.loads(l) for l in open(log)]
            return r.returncode, o, [x for x in recs if x["tools"] and x["tools"] != ["session_title"]]

        def results(agent, who="main"):
            a = [x for x in agent if x.get("who", "main") == who]
            return [content(c) for c in (a[-1]["tool_results"] if a else [])], a

        thy = {"source": "chat", "text": "Theory: H then CX makes a Bell state; only 00 and 11, about half each.",
               "excerpts": ["User: does H then CX entangle two qubits?", "Assistant: yes, a Bell state."], "hypothesis": "H(0) then CX(0,1) prepares a Bell state",
               "prediction": "P(00)=P(11)=0.5", "script": "q.circuit new th 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 4000 basis z",
               "checks": [{"kind": "probability", "outcome": x, "expected": 0.5, "tolerance": 0.05} for x in ("00", "11")], "workspace": ws}
        U = lambda t, a: {"tool": "use_tool", "args": {"tool_name": N(t), "tool_input": a}}
        cli = os.path.join(inst, "skills", "spindoctor-qwerty", "scripts", "spindoctor_cli.py")
        steps = [{"tool": "search_tool", "args": {"query": "spindoctor-qwerty", "limit": 10}}, U("spindoctor_functions", {}),
                 U("spindoctor_run_script", {"script": "q.circuit new bell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z", "workspace": ws}),
                 U("spindoctor_run_preset", {"preset_id": "qc-001", "workspace": ws}), U("spindoctor_test_theory", thy),
                 {"tool": "run_terminal_command", "args": {"command": 'python3 "%s" functions gates' % cli, "description": "SpinDoctor gate table via the CLI"}},
                 {"text": "Done. SpinDoctor is a classical simulation, not quantum hardware."}]
        rc, o, agent = session(steps, "Show the SpinDoctor functions, run a Bell circuit and preset qc-001, and test the Bell theory we discussed.")
        res, _ = results(agent)
        ctx = " ".join(u or "" for u in (agent[0]["user"] if agent else []))
        T("headless grok -p --yolo (custom model -> local stand-in): MCP server connected with 6 tools, search_tool/use_tool offered, skill + 5 commands listed with installed paths",
          agent and {"search_tool", "use_tool", "run_terminal_command"} <= set(agent[0]["tools"]) and "spindoctor-qwerty (6 tools)" in ctx
          and "- spindoctor-qwerty: Run the SpinDoctor 3.1.2" in ctx and all("- %s:" % c in ctx for c in CMDS) and inst in ctx, ctx[-500:])
        G = lambda i: res[i] if len(res) > i else ""
        T("search_tool (query spindoctor-qwerty, limit 10) finds all 6 tools as spindoctor-qwerty__<tool>", all(N(t) in G(0) for t in TOOLS), G(0)[:300])
        T("use_tool via Grok: function table, Bell run (ok, PDF report in the workspace), preset qc-001 ok",
          "| Function |" in G(1) and OK(G(2)) and ".pdf" in G(2) and ws in G(2) and "qc-001" in G(3) and OK(G(3)), [x[:120] for x in res[1:4]])
        pdfs = re.findall(r'"([^"]+\.pdf)', G(4))
        T("theory test from the chat via Grok: verdict supported, 2 excerpts recorded, theory PDF on disk",
          re.search(r'"verdict":\s*"supported"', G(4)) and re.search(r'"excerptsRecorded":\s*2', G(4)) and pdfs and os.path.isfile(pdfs[0]), G(4)[:300])
        T("shell fallback: run_terminal_command runs the installed plugin's CLI (gate table); session ends with the answer",
          "Gate set" in G(5) and rc == 0 and "classical simulation" in o and len(agent) == len(steps), (G(5)[:200], o[-200:]))
        rc, o, agent = session([U("spindoctor_run_preset", {"preset_id": "qc-002", "workspace": ws}), {"text": "Preset done (classical simulation)."}], "/qwerty-preset qc-002")
        ut = " ".join(agent[0]["user"]) if agent else ""; res, _ = results(agent)
        T("slash command /qwerty-preset qc-002: Grok expands the plugin command with $ARGUMENTS; the preset runs",
          '<skill name="qwerty-preset" args="qc-002">' in ut and "Run SpinDoctor preset qc-002" in ut and res and "qc-002" in res[0] and rc == 0, ut[-400:])
        rc, o, agent = session([{"text": "ok (classical simulation)"}], "/spindoctor-qwerty show the functions")
        ut = " ".join(agent[0]["user"]) if agent else ""
        T("skill /spindoctor-qwerty: body loaded with ${GROK_PLUGIN_ROOT} replaced by the installed folder",
          '<skill name="spindoctor-qwerty"' in ut and "Honesty rules" in ut and cli in ut and "${GROK_PLUGIN_ROOT}" not in ut, ut[-400:])
        sub = {"main": [{"tool": "spawn_subagent", "args": {"description": "Run SpinDoctor preset", "prompt": "Run SpinDoctor preset qc-003 and report the paths.",
                                                          "subagent_type": "spindoctor-qwerty:qwerty-helper", "run_in_background": False}},
                        {"text": "Helper finished (classical simulation)."}],
               "child": [U("spindoctor_run_preset", {"preset_id": "qc-003", "workspace": ws}), {"text": "qc-003 done; reports written."}]}
        rc, o, agent = session(sub, "Ask the SpinDoctor helper to run preset qc-003.")
        cres, ca = results(agent, "child"); mres, _ = results(agent, "main")
        T("plugin subagent spindoctor-qwerty:qwerty-helper: runs with the helper instructions (${GROK_PLUGIN_ROOT} filled in), inherits the MCP server, runs qc-003, result returns to the parent",
          ca and "SpinDoctor Qwerty helper" in (ca[0]["system"] or "") and "${GROK_PLUGIN_ROOT}" not in (ca[0]["system"] or "") and "use_tool" in ca[0]["tools"]
          and cres and OK(cres[0]) and "qc-003" in cres[0] and mres and "qc-003 done" in mres[0] and rc == 0, (cres[:1], mres[:1]))
        e2e = os.path.join(HERE, "e2e_results.json")
        r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", sys.executable, os.path.join(inst, "skills", "spindoctor-qwerty", "scripts", "spindoctor_mcp.py"),
                            "--examples", os.path.join(SK, "examples", "theory"), "--out", e2e], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=3600, cwd=work)
        t = r.stdout.decode("utf-8", "replace"); mm = re.search(r"SUMMARY (\d+)/(\d+)", t)
        T("shared E2E suite through the installed plugin's MCP server: %s" % (mm.group(0) if mm else "?"),
          r.returncode == 0 and mm and mm.group(1) == mm.group(2), "\n".join(l for l in t.splitlines() if l.startswith("FAIL"))[-500:])
        subprocess.run([sys.executable, os.path.join(src, "tools", "set_python.py"), "python"], stdout=subprocess.DEVNULL, check=True)
        o = run(["plugin", "update", "spindoctor-qwerty"]).stdout.decode("utf-8", "replace")
        lst = json.loads((lambda s: s[s.index("["):])(run(["plugin", "list", "--json"], t=60).stdout.decode()))
        inst2 = lst[0]["path"] if lst else inst
        cmd = json.load(open(os.path.join(inst2, ".mcp.json")))["mcpServers"]["spindoctor-qwerty"]["command"]
        T("Windows route: set_python.py python in the clone + grok plugin update -> the installed .mcp.json starts `python`", cmd == "python", o[-300:])
        o = run(["plugin", "uninstall", "spindoctor-qwerty", "--confirm"]).stdout.decode("utf-8", "replace")
        T("real grok: plugin uninstall --confirm removes the plugin", "spindoctor-qwerty" not in run(["plugin", "list"], t=60).stdout.decode() and not os.path.exists(inst2), o[-300:])
    finally:
        if stub: stub.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    a = sys.argv[1:]; opt = dict(zip(a[::2], a[1::2]))
    static()
    if opt.get("--spec"): spec(os.path.abspath(opt["--spec"]))
    if opt.get("--grok"): real(os.path.abspath(opt["--grok"]))
    outp = opt.get("--out", os.path.join(HERE, "host_check.json"))
    json.dump({"passed": sum(r["pass"] for r in R), "total": len(R), "python": sys.version.split()[0], "checks": R}, open(outp, "w"), indent=1)
    print("HOST CHECK %d/%d passed" % (sum(r["pass"] for r in R), len(R)))
    return 0 if all(r["pass"] for r in R) else 1


if __name__ == "__main__":
    sys.exit(main())
