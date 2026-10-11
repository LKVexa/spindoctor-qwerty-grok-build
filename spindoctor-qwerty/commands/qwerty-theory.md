---
description: Test a theory with the SpinDoctor simulator (file path, pasted text, or 'the theory we discussed')
argument-hint: "<absolute file path | theory text | 'we discussed'>"
---

Test this theory with the spindoctor-qwerty skill: $ARGUMENTS

If it is a file path, call `spindoctor_test_theory` with source=file and action=extract first. If it refers to our conversation, summarise the theory from the chat (claims, assumptions, variables, measurable prediction), show it to me and wait for my confirmation, then use source=chat with short verbatim excerpts. Restate the hypothesis, give a measurable prediction, write the q.* script and checks, run it (action=run), and report the verdict, observed vs predicted numbers and the TXT/PDF theory report paths, with the limits (classical simulation of an idealised model, shot noise, qubit limits).
