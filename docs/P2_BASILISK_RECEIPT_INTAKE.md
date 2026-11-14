# P2 — Basilisk evidence receipt intake boundary

## Purpose

Connect the ADCS research line to the R84-R3A native IMU–reaction-wheel multichannel pilot without turning a successful simulation run into a Gold Seed automatically.

The intake path is deliberately two-stage:

1. **Package preflight:** verify immutable manifest/artifact hashes, per-record sample structure, time-axis monotonicity and cross-stream alignment, channel whitelist, replay equality, observer-noise isolation and explicit non-training flags.
2. **Human research admission:** independently review source archive provenance, simulator version/build, event-to-observable mapping, units, physical effect, truth separation and run/source/scenario split groups.

A package passing stage 1 receives `REVIEW_REQUIRED`, never `ADMITTED`.

## R84-R3A facts used by this adapter

The SatAgentSimulation R84-R3A contract describes 12 unique native Basilisk arms plus one exact seeded replay, 31 samples per execution, four separated JSONL streams, native IMU observations, RW state feedback, FSW command torque and pointing-error estimate. Actual applied torque, actuator capacity and hub truth remain QA-only. The R84-R3A preregistration explicitly prohibits model training and formal train/validation/test eligibility.

The RW speed channel is an ideal native state-feedback upper bound. It is not an encoder measurement and has no encoder noise, quantization, dropout or hardware correlation model. Motor current is not measured by this pilot.

## Intake contract

`dgsi.basilisk_receipt.validate_r84r3_package(path)` verifies:

- manifest schema and PASS status;
- exactly 12 unique arms plus one replay, 31 samples per execution;
- all 12 physical-baseline comparisons and six observer-noise isolation checks;
- explicit false flags for model training, formal train/test eligibility and flight/hardware qualification;
- SHA-256 of all four JSONL artifacts and three immutable upstream source archives against the execution manifest and source registry;
- the Basilisk compatibility report proves all 880 native payload files remain byte-identical to the pinned upstream wheel;
- unique record IDs across telemetry, IMU, case and physics-QA streams;
- exact channel whitelists, finite numeric samples and the frozen 0.2 s / 31-point time grid;
- aligned timestamps between telemetry, IMU and QA records;
- IMU channels agree between the dedicated IMU stream and model-facing telemetry;
- QA-only truth, labels, hub state and fault fields are rejected from model-facing telemetry;
- the frozen 2×3×2 arm matrix and deterministic seed formula;
- physical baseline deltas remain within the preregistered tolerance;
- the replay is linked to one of the 12 unique arms and is sample-exact across telemetry, IMU and QA streams.

The adapter does not copy private trace data into the public repository. It emits only a compact local preflight receipt.

## Hard boundary

Passing preflight is not evidence that the generated labels are scientifically correct. It does not establish an admitted dataset, diagnostic accuracy, model improvement, or expert approval. No training export is implemented at this stage.

## Next research gate

After an R84-R3A artifact is actually produced and locally validated, perform a qualified ADCS review of the physical effect and observable channels. Then design a separate diagnostic seed pilot with hidden fault truth, independent run/scenario split groups, and explicit normal / fault / ambiguous / insufficient-evidence tasks. Only after that gate should P3 candidate generation begin.
