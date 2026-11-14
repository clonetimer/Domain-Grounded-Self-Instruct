# P2 — Basilisk evidence receipt intake boundary

## Purpose

Connect the ADCS research line to the R84-R3A native IMU–reaction-wheel multichannel pilot without turning a successful simulation run into a Gold Seed automatically.

The intake path is deliberately two-stage:

1. **Package preflight:** verify immutable manifest/artifact hashes, record alignment, channel whitelist, replay control, observer-noise isolation and explicit non-training flags.
2. **Human research admission:** independently review source archive provenance, simulator version/build, event-to-observable mapping, units, physical effect, truth separation and run/source/scenario split groups.

A package passing stage 1 receives `REVIEW_REQUIRED`, never `ADMITTED`.

## R84-R3A facts used by this adapter

The SatAgentSimulation R84-R3A contract describes 12 unique native Basilisk arms plus one exact seeded replay, 31 samples per execution, four separated JSONL streams, native IMU observations, RW state feedback, FSW command torque and pointing-error estimate. Actual applied torque, actuator capacity and hub truth remain QA-only. The R84-R3A preregistration explicitly prohibits model training and formal train/validation/test eligibility.

The RW speed channel is an ideal native state-feedback upper bound. It is not an encoder measurement and has no encoder noise, quantization, dropout or hardware correlation model. Motor current is not measured by this pilot.

## Intake contract

`dgsi.basilisk_receipt.validate_r84r3_package(path)` verifies:

- manifest schema and PASS status;
- exactly 12 unique arms + one replay, 31 samples per execution;
- all 12 physical-baseline comparisons and six observer-noise isolation checks;
- `model_trained=false`, `formal_training_or_test_eligible=false`, and no flight/hardware qualification;
- SHA-256 of all four JSONL artifacts against the execution manifest;
- 13 aligned record IDs across telemetry, IMU, case and physics-QA streams;
- 31 telemetry samples per record, required channel presence and no QA/truth/label fields in model-facing telemetry;
- exactly one replay control linked to a recorded arm.

The adapter does not copy private trace data into the public repository. It emits only a compact local preflight receipt.

## Hard boundary

Passing preflight is not evidence that the generated labels are scientifically correct. It does not establish an admitted dataset, diagnostic accuracy, model improvement, or expert approval. No training export is implemented at this stage.

## Next research gate

After an R84-R3A artifact is actually produced and locally validated, perform a qualified ADCS review of the physical effect and observable channels. Then design a separate diagnostic seed pilot with hidden fault truth, independent run/scenario split groups, and explicit normal / fault / ambiguous / insufficient-evidence tasks. Only after that gate should P3 candidate generation begin.
