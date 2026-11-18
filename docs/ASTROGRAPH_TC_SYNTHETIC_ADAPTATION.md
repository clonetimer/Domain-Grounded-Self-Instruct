# Synthetic AstroGraph acceptance adapter: TC01–TC09

Source: `clonetimer/AstroGraph-LLM/examples/platform_acceptance_cases_v1/`.
Each row in `resources/astrograph_tc_synthetic_adapter_matrix.json` is
explicitly **SYNTHETIC**, non-Gold, not training eligible. The serialized
diagnosis inputs contain only small, publicly visible field subsets; no
`operations.log`, raw telemetry, restricted data, generated target report
or expert approval is imported.

The mapping tests the *upstream result adapter* and its intake boundary:

| Case | Synthetic expectation |
| --- | --- |
| TC01 | ADCS reaction-wheel candidate, never a confirmed root cause |
| TC02 | EPS battery resistance candidate, score not fabricated |
| TC03 | Star-tracker candidate without corroborating machine evidence IDs |
| TC04 | Unknown propulsion fault identifier remains a provisional candidate |
| TC05 | Log anomaly cannot become a machine fault when upstream says NORMAL |
| TC06 | Two distinct upstream candidates remain distinct |
| TC07 | Missing reference artifact blocks the AstroGraph acceptance workflow |
| TC08 | Reference prompt injection is untrusted; no automatic authorization |
| TC09 | Standalone optional graph building has **no diagnosis result** and is not a DGSI SFT case |

TC07 is an AstroGraph acceptance-workflow preflight requirement, not a
universal prohibition on documenting uncertainty when references are missing.
TC08 is a **metadata safety assertion**, not a full execution-level
prompt-injection test; no untrusted reference content is passed through an LLM
in this suite. TC09 has no `diagnosis_result.json`, so the adapter must not
invent one.

A passing adapter test is not a complete case packet or an evaluated
diagnostic report. Logs, mission/configuration context, source permissions,
expert review and historical outcome verification are required before any
real case admission. No TC fixture may be counted toward 5–10 real cases,
20 manually reviewed samples, or the 300–500 controlled pilot.
