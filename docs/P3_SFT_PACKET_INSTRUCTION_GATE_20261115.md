# P3 — Standalone SFT embedded-instruction gate (2026-11-15)

## Source defect

The SFT system instruction and pre-JSON user preamble were pinned, but the serialized case packet included a separate `instruction` string with no value check. Any arbitrary, schema-valid text in that field reached the LLM and could impersonate a confirmed expert verdict or instruct it to ignore counterevidence. Case→SFT binding only compared this instruction to a source-case field; it did not establish that the source instruction itself was permitted.

## Change

- The standalone SFT validator accepts **one registered v1 generic Chinese case-packet instruction**. All other instruction content, including appended approval claims, seemingly harmless wording changes, Unicode suffixes and additional role instructions, fails closed with a stable payload-free code `UNAPPROVED_PACKET_INSTRUCTION_TEMPLATE`.
- This gate runs before direct standalone SFT acceptance, batch lineage audit and Case→SFT binding. The binding API preserves its established `PROMPT_INSTRUCTION_MISMATCH` diagnostic.
- Synthetic lineage fixtures vary the **operational case context**, not the instruction string, to preserve meaningful split/duplicate tests without unreviewed prompt channels.
- The current generic directive applies to the six SFT task labels; task-specific instructions need separate versioned registration, adversarial tests and review. A source Case can remain a draft with a proposed instruction but cannot pass SFT export until the instruction is admitted.

## Evidence / limitations

Tests are entirely **SYNTHETIC**. They establish only syntax/template control and cannot establish source validity, prompt-injection resistance within untrusted diagnostic logs, model behavior, expert correctness, IP rights or Gold status. AstroGraph's material-report human review and history memory are not synonymous with independent truth review. No private telemetry, logs, case documents, credentials or restricted files are copied into this repository.

Real-data pilot still requires a locally authorized, metadata-only D0 survey and 5–10 consented/de-identified diagnosis-result + log + spacecraft/mission-context + history + independent adjudication packets. No auto Gold, no paid model inference, no fine-tuning and no main-branch merge.
