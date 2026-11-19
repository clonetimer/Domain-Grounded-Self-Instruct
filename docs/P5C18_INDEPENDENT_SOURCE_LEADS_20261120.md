# P5-C18 — Four independently traceable source leads for singleton-task coverage (2026-11-20)

**DEV_ONLY / coordinator-only / not_for_sft=true.** This is a *public bibliographic discovery* contribution, not additional SFT training data, an L0 science-admitted fact card, a verified independent final holdout, or a rights determination.

## Why source discovery, not more task paraphrases

P5-C17 found 21 synthetic task variants across 6 strict model-visible document clusters. Three task types occur in only one cluster each: `historical_case_reuse`, `next_step_recommendation` and `handover_summary`. Enlarging the current 21-task cohort by rewriting those same event families cannot establish cross-source generalization. This run located four *different-mission* public records that may help diversify those roles **after** real source checks and independent expert review.

The metadata-only, no-copyright-text-copied triage ledger is [p5c18_independent_source_leads_DEV_ONLY_20261120.json](../examples/p5c18_independent_source_leads_DEV_ONLY_20261120.json). Its parent is #183 exact head `ddf97f4a3d74e6b4575dd7bc6ec3cd38a3a0d34f`, pinned to unchanged L1 blob `f141694748d5425b63b469b5b0b25064e1b402c8` and L0 blob `73f8f00dd6ecaf60cb75b0e1d566537c4e27579f`. These four leads are **outside** the frozen REV1 list; no official split assignment occurs.

| Lead | Direct public citation | Source-grounded event boundary | Possible new task role | Source/rights decision |
| --- | --- | --- | --- | --- |
| SAMPEX | [NASA NTRS 20080039634](https://ntrs.nasa.gov/citations/20080039634) | 2007 reaction-wheel anomaly; spin-stabilized recovery using magnetic torquer bars | next-step / handover / history reuse | Publication record states Public Use Permitted, but actual full-text, excerpts and training/redistribution scope must be checked |
| TOMS-EP | [NASA NTRS 20000033274](https://ntrs.nasa.gov/citations/20000033274) | 1998 safe-mode anomaly and December 28–31 staged recovery | handover / next-step | NTRS publication date **1998-01-01 predates the December 1998 event described in its own abstract**; treat date as inconsistent; check primary version, author rights |
| Voyager 2 | [NASA LLIS lesson 284](https://llis.nasa.gov/lesson/284) | Receiver/anomaly and separate scan-platform actuator issue; spare hardware used for workaround tests | history reuse / handover | LLIS lesson date is **not** flight event date; JPL-specific use rights and precise episodes unavailable |
| CloudSat | [NASA NTRS 20170008193](https://ntrs.nasa.gov/citations/20170008193) | 2011 battery anomaly; daylight-only operations and science resumption; 2012 A-Train return | handover / history reuse | NTRS says **Copyright: Other** and currently offers no downloadable source; low priority until rights/source access verified |

## Admission sequence — do not shortcut

1. **SAMPEX, then TOMS-EP:** retrieve an authorized full primary paper, verify its exact page/section and scientific uncertainty, reconcile TOMS-EP chronology, and independently decide source-specific extraction/paraphrase/training/distribution rights.
2. **Voyager 2:** obtain a primary event timeline and source-specific rights; *separate receiver and scan-platform episodes*. Historical use as-of requires trustworthy `available_at` and `verified_at`, not the LLIS lesson date alone. Nothing from this lead currently enters production Context.
3. **CloudSat:** do not construct source-claimed detail from a record with no authorized full text; retain as a citation lead only.
4. **After admission and independent review:** build L0 only from source-supported facts. If an L1 diagnostic task is warranted, explicitly synthesize all invented upstream ML results, logs and configurations with field-level recipe attribution; never present them as flight records. The REAL Gold track remains separately gated on actual authorized upstream results/logs/context and expert decisions.
5. **Benchmark:** re-audit source overlaps and retrieval exposures before treating any new mission as a genuinely untouched source-publication group. Hold back different publications selected *before* development as the actual final benchmark; current REV1 is already development-exposed. Do not use these same P5-C18 leads both for new synthetic training development and for a claimed independent final holdout.

No new real ML output, operational timestamp, expert approval, exact hardware construction, cause certainty or disposal implementation has been inferred. In particular, **the historical recovery action described by a paper is not an executed action in any new synthetic current case**.

## Verified reference-level evidence vs still unknown

- NASA's NTRS summary for SAMPEX identifies the August 18, 2007 wheel problem and September 25, 2007 recovery, and displays a May 12, 2008 publication date.
- NTRS's TOMS-EP summary describes the December 13, 1998 upset and December 28–31 recovery. The displayed January 1, 1998 publication date is internally inconsistent with that chronology: no `verified_at` or true publication date was manufactured.
- LLIS lesson 284 describes two distinct Voyager 2 faults and the use of a near-identical ground testbed; it does not supply precise flight timestamps or runtime historical truth status.
- NTRS's CloudSat summary describes battery emergency mode and recovery milestones, but its rights field reads Other and no downloadable file appears on the entry.

### Status after P5-C18

**New source leads 4; approved L0 cards added 0; L1 tasks added 0; accepted expert reviews 0; REAL Gold 0; official splits 0; SFT exports 0; training authorization false.** Four leads are genuinely traceable URLs, **not** four domain-accepted independent publication groups.

### Development experience

The bottleneck is independent *scientific source breadth and reviewer decisions*, not validator coverage. One new mission with a genuine response narrative is more useful than many paraphrases of FUSE/Cassini, but even an official NASA index can have contradictory bibliographic dates and limited/ambiguous reuse rights. Preserve that uncertainty explicitly and delay L0/L1 construction until the underlying primary documents and their permitted use are verified.

See #183 for the six-cluster denominator and first-pass 10-task expert calibration queue. Do not publish private reviewer identities or restricted source excerpts. No merge, training or Gold promotion is authorized.
