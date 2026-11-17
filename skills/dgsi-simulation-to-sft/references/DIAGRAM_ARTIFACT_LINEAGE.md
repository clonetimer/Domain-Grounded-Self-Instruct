# Diagram artifact lineage and review invalidation (P5-B4.4)

This local audit detects byte changes and stale declared dependency snapshots. It does not authenticate source provenance, reviewer identity, image inspection, semantic derivation or engineering truth.

| Artifact kind | Required parent kind(s) |
|---|---|
| DOCUMENT_SOURCE | none |
| EXTRACTED_ASSET | DOCUMENT_SOURCE |
| OCR_RECORD | EXTRACTED_ASSET |
| TEXT_CANDIDATES | EXTRACTED_ASSET, OCR_RECORD |
| TEXT_REVIEW | TEXT_CANDIDATES |
| NODE_GRAPH | TEXT_REVIEW |
| TOPOLOGY_REVIEW | NODE_GRAPH, EXTRACTED_ASSET, DOCUMENT_SOURCE |

Each artifact stores its relative path, exact file SHA-256, dependency IDs and frozen dependency digest. The digest is SHA-256 over canonical UTF-8 JSON of sorted {artifact_id, sha256} parent records. Changed files are CONTENT_CHANGED; unchanged descendants with outdated parent snapshots are DEPENDENCY_STALE. Invalidation propagates only downstream.

Audit only:
```sh
python scripts/audit_diagram_artifact_lineage.py --manifest review/artifact-lineage.json --root review/workspace
```

Write detailed report to a new file:
```sh
python scripts/audit_diagram_artifact_lineage.py --manifest review/artifact-lineage.json --root review/workspace --output review/lineage-audit.json
```

Exit codes: 0 current, 2 blocked input/manifest/path, 3 review invalidation required. Duplicate JSON keys, malformed UTF-8, symlinks, traversal, oversized files and output overwrite are rejected. Detailed IDs and hashes stay in the local report; stdout is aggregate-only.

Never edit an old receipt to make a stale chain appear current. Regenerate affected artifacts and issue new immutable versions and review receipts. Dependency declarations are caller-supplied: this tool checks byte and declared-snapshot consistency, not whether the child was truly derived from its parents. All outputs remain not_for_sft=true and training/Gold-disabled.
