---
description: Run a SpinDoctor preset (qc-001..qc-241)
argument-hint: "<preset-id> [name=value ...]"
---

Run SpinDoctor preset $ARGUMENTS with the `spindoctor_run_preset` tool (overrides such as shots=500 go in `overrides`; without arguments, list presets with `spindoctor_list_presets` and ask which one). Summarise each step and give the report paths. Classical FP64 simulation on this computer, not quantum hardware, no quantum advantage.
