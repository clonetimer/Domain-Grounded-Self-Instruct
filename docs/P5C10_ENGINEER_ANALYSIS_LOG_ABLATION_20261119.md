# P5-C10 — quarantine answer-bearing synthetic engineer analysis in negative history A/B (2026-11-19)

**Status: DEV_ONLY / NOT_RUN / not_for_sft=true. Original 21-task REV1 is frozen and unchanged.**

## Scientific finding

After P5-C9 removed explicit L0 literature fact-card answers, the TROPICS Pathfinder pairs (tasks **003** and **013**) still provided a synthetic log, **LOG-23**, with `log_type=ENGINEERING_ANALYSIS` and `author_role=engineer`, stating that multiple interface anomalies share the rotating interface and 12V power/serial path. This is an *analysis/hypothesis*, not an independent alarm, sensor observation or an actual engineer/mission log. It could shortcut the intended inference from the upstream synthetic ML candidate and two independently described interface anomalies even though both A/B arms are matched. Neither its existence nor its content validates the physical root cause.

Unlike the earlier source fact-card shortcut, this passage sits in `input.diagnostic_logs` and is therefore unaffected by `knowledge_evidence=[]`. It is **not** grounds to delete it from an approved full diagnostic case: a real engineer's prior analysis can be relevant evidence if labeled and timestamped. Here, we exclude the *fabricated engineer explanation* only from a restricted **scientific DEV negative-transfer ablation**.

## Actual bounded correction and evidence

- Input: fixed v0.3 DEV_ONLY source-blind ZIP, exact SHA-256 `d30e8867da8e1a8bd15de5f98e19a32f3bd8e88aadbe42974e5a5e432c6c58c6`.
- Output: v0.4 local DEV_ONLY archive (supplied separately to user), SHA-256 `f6b5880068d9ca594fbb2467c832291781389362cb810d802604f7a44e46b462`.
- Two *occurrences* of the same `LOG-23` in two TROPICS task types are quarantined from **both arms**. The FUSE pair has no removed engineering-analysis log.
- Preserve original synthetic ML findings, ALARM/EVENT logs, operating context, spacecraft configuration, analysis cutoff and task instructions. The only difference between the two arms **within each v0.4 pair** remains `input.historical_cases`.
- Keep IDs and digest of removed log records in a **coordinator-only manifest**; never copy them to the model-visible inputs. The source v0.3 exact hash binds the reversible scientific intervention; it does **not** certify original source authenticity.
- 3 pairs, **2 unique current evidence cores**, **2 event families**, **1 distinct quarantined log ID**, and **0 model-visible `ENGINEERING_ANALYSIS` logs**. The duplicated TROPICS input is not an independent third result.
- Local v0.4 ZIP CRC/members SHA-256 and two separately rebuilt byte-identical archives: PASS. No model run or independent scientific scoring.
- New `history_pair_science_audit` v0.4 branch validates the strict purpose, safe release flags, zero remaining ENGINEERING_ANALYSIS log type, per-task coordinator-only quarantine ledger, and preservation of A/B controlled core. The old v0.2/v0.3 DEV gates remain supported. Five extra synthetic regression tests.

## Interpretation boundaries

This removes one explicit *narrative answer channel*, not all leakage. **The upstream ML candidate `SLIP_RING_12V_SERIAL_CROSS_SHORT` remains model-visible intentionally**, since interpreting upstream ML outputs is the product objective. Its candidate status must not be turned into a confirmed diagnosis. Model pretraining may know the TROPICS case; scenario and mission names may bias output. A valid effect claim still requires independent holdout families and external assessor judgment. Positive history benefit remains **NOT_EVALUABLE**: all three history hits have uncertain hardware fit and missing trusted `verified_at`.

No independent expert review, use-rights clearance, real Gold promotion, official split allocation, paid model API call, model scoring or training was performed. The four science review findings SCI-002/009/016/017 stay open. Distinguish synthetic operation logs, synthetic ML outputs, and literature source facts when preparing subsequent assessments.

**Lesson:** merely removing explicit fact-card answers is insufficient if a synthetic narrative log restates the diagnosis; scientific evaluations must distinguish contemporaneous observation from prewritten interpretation, while preserving the legitimate upstream ML input.
