---
description: Run every command file in a folder with q.folder
argument-hint: "<absolute folder path>"
---

Run `q.folder run path="$ARGUMENTS"` with the `spindoctor_run_script` tool (ask for an absolute folder path if none was given). It runs the top-level .txt/.csv/.json/.qasm/.qasm2/.circuit/.pdf files in name order (1-128 files, 4 MiB each, 1-128 commands per file, 4096 characters per command); other files are skipped and listed, and the first failing file stops the job. Report each file's outcome, the skipped files and the report paths. Classical FP64 simulation on this computer, not quantum hardware, no quantum advantage.
