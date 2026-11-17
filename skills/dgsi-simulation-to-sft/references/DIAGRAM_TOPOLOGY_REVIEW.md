# Port and connection evidence review (P5-B4.3c)

This is a local, declaration-level review workflow. It does not recognize arrows,
authenticate a reviewer, inspect source image pixels, or authorize training.

## Inputs and commands

`--node-graph` accepts the **inner `diagram_annotation` object** emitted by B4.3b,
not its full import wrapper. Save that object to a permitted local workspace.
Keep the preceding B4.1 provenance audit and B4.3a/b receipts with the original
image. This stage accepts only an unchanged, node-only graph; existing ports or
edges require a separately reviewed merge workflow, not silent replacement.

Fill a receipt against `schemas/diagram_topology_review.schema.json`. Its
`graph_sha256` is the digest of UTF-8 JSON serialized with sorted keys,
`ensure_ascii=False`, separators `(',', ':')`, and `allow_nan=False`; the module's
`canonical_digest(graph)` implements this rule. Source/asset identity must match.
Use a known-offset timestamp such as `2026-11-17T04:00:00+09:00`.

```sh
# Audit only: no output file or network call.
python scripts/audit_diagram_topology_review.py \
  --node-graph review/nodes.json --review-receipt review/topology-review.json

# Explicitly write a NEW proposed graph in an existing authorized directory.
python scripts/audit_diagram_topology_review.py \
  --node-graph review/nodes.json --review-receipt review/topology-review.json \
  --output review/topology-proposed.json
```

The output path must not exist. The CLI rejects duplicate JSON keys, malformed
UTF-8, non-finite numbers, and input files larger than 2 MiB. Standard output
contains counts and fixed status/error codes only; the local output file contains
labels, reviewer-supplied metadata and exact evidence regions. Treat it as source
material, not an automatically public artifact.

## Separate the claims

A port records its owning node, label, direction, medium and unit. A connection
records endpoints, direction basis and relation type. Do not infer any of these
from a component name or visual proximity.

Every evidence record has an ID, **subject ID**, **claim field**, evidence basis,
and an original-image bounding box `[left, top, width, height]`. References must
match the exact subject and field; a port's evidence cannot support a different
port. Connector existence, arrow direction and POWER/CONTROL/DATA meaning require
separately typed evidence records, even when they cite the same visible region.

Port evidence fields are `label`, `direction`, `signal_or_medium`, `unit`.
Connection evidence fields are `connection`, `direction`, `relation`.
Known values require matching evidence. UNKNOWN values and null units require
null references, rather than unused or contradictory evidence. Allowed bases are
visible labels/connectors, arrows or explicit source text, according to the claim.
This increment does not support implicit PORT_DIRECTION inference for edges.

Coordinates are checked against **caller-declared** image dimensions, not decoded
image pixels. Source text and physical correctness still require inspection of
the original image. No source authenticity or upstream rejection-state check is
inferred solely from a consistent graph digest.

## Import behavior

Accepted declarations create a fresh graph with proposed/unresolved ports and
edges; no object becomes HUMAN_CONFIRMED. Input objects are not mutated.
Direction-UNKNOWN links remain in `unresolved_connections` **outside** the directed
`diagram_annotation.edges` array. Their two endpoint fields are storage slots,
not a claim of flow direction. Unknown relation types stay UNKNOWN.

The wrapper retains the complete typed `evidence_receipt`, review and input/output
graph hashes. Do not discard this sidecar: the generic diagram graph has only one
locator per object and cannot alone preserve all field-specific evidence.
Successful audit means `TOPOLOGY_RECEIPT_BOUND_NOT_AUTHENTICATED`; all records remain
REVIEW_REQUIRED, not_for_sft=true and Gold/training-disabled. These graph proposals
are not a deployed satellite model or a diagnostic training dataset.
