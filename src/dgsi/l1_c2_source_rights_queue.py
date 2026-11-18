"""Source-document rights intake for C2 expert-review kits, not a clearance decision.

One publication can support multiple L0 episodes and multiple L1 tasks.
Neither a public URL nor an expert's scientific score grants reuse rights.
"""
from __future__ import annotations

from typing import Any


class C2SourceRightsQueueError(ValueError):
    """A rights-review queue cannot be bound without unambiguous sources."""


def build_c2_source_rights_queue(dossier: dict[str, Any]) -> dict[str, Any]:
    """Build a blank, source-deduplicated rights queue from the bound dossier.

    Only bound L0 cards are included. An L0 card outside the current cohort
    must never be counted as clearance or as an extra training case.
    """
    if (
        not isinstance(dossier, dict)
        or dossier.get("purpose") != "INDEPENDENT_EXPERT_REVIEW_ONLY_NOT_SFT"
        or dossier.get("track") != "LITERATURE_DERIVED_SYNTHETIC"
        or dossier.get("training_authorized") is not False
        or dossier.get("source_rights_verified") is not False
        or not isinstance(dossier.get("items"), list)
    ):
        raise C2SourceRightsQueueError("C2_RIGHTS_DOSSIER_NOT_REVIEW_ONLY")
    documents: dict[str, dict[str, Any]] = {}
    # The same L0 case can appear in multiple L1 tasks. Its SHA alone
    # does not establish source-document or episode identity: a caller must
    # not move an unchanged digest to another publication, event family or episode.
    known_facts: dict[
        str, tuple[str, str, str, str | None, str, str | None, str, str | None]
    ] = {}
    seen_tasks: set[str] = set()
    for item in dossier["items"]:
        task_id = item.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in seen_tasks:
            raise C2SourceRightsQueueError("C2_RIGHTS_DUPLICATE_OR_INVALID_TASK")
        seen_tasks.add(task_id)
        bindings = item.get("source_fact_bindings")
        facts = item.get("l0_public_source_context")
        if not isinstance(bindings, list) or not isinstance(facts, list):
            raise C2SourceRightsQueueError("C2_RIGHTS_SOURCE_BINDINGS_MISSING")
        ref_to_digest: dict[str, str] = {}
        for binding in bindings:
            if not isinstance(binding, dict):
                raise C2SourceRightsQueueError("C2_RIGHTS_BINDING_INVALID")
            ref, digest = binding.get("source_fact_ref"), binding.get("public_fact_sha256")
            if not isinstance(ref, str) or not ref or ref in ref_to_digest:
                raise C2SourceRightsQueueError("C2_RIGHTS_BINDING_DUPLICATE")
            if (not isinstance(digest, str) or len(digest) != 64
                    or any(char not in "0123456789abcdef" for char in digest)):
                raise C2SourceRightsQueueError("C2_RIGHTS_BINDING_FINGERPRINT_INVALID")
            ref_to_digest[ref] = digest
        fact_ids: set[str] = set()
        for fact in facts:
            if not isinstance(fact, dict):
                raise C2SourceRightsQueueError("C2_RIGHTS_L0_FACT_INVALID")
            case_id = fact.get("case_id")
            ref = fact.get("source_reference")
            if not isinstance(case_id, str) or case_id in fact_ids:
                raise C2SourceRightsQueueError("C2_RIGHTS_L0_FACT_DUPLICATE")
            fact_ids.add(case_id)
            if not isinstance(ref, dict):
                raise C2SourceRightsQueueError("C2_RIGHTS_SOURCE_REFERENCE_MISSING")
            source_id, title, url = (ref.get(k) for k in
                                     ("source_id", "source_title", "source_url"))
            if not isinstance(source_id, str) or not source_id.strip():
                raise C2SourceRightsQueueError("C2_RIGHTS_DOCUMENT_ID_INVALID")
            if not isinstance(title, str) or not title.strip():
                raise C2SourceRightsQueueError("C2_RIGHTS_DOCUMENT_TITLE_INVALID")
            if url is not None and not isinstance(url, str):
                raise C2SourceRightsQueueError("C2_RIGHTS_SOURCE_URL_INVALID")
            digest = ref_to_digest.get(case_id)
            if digest is None:
                raise C2SourceRightsQueueError("C2_RIGHTS_UNBOUND_L0_FACT")
            family, source_class = fact.get("event_family_id"), fact.get("source_class")
            locator = ref.get("source_locator")
            if not isinstance(family, str) or not family.strip():
                raise C2SourceRightsQueueError("C2_RIGHTS_EVENT_FAMILY_INVALID")
            if not isinstance(source_class, str) or not source_class.strip():
                raise C2SourceRightsQueueError("C2_RIGHTS_SOURCE_CLASS_INVALID")
            if locator is not None and not isinstance(locator, str):
                raise C2SourceRightsQueueError("C2_RIGHTS_SOURCE_LOCATOR_INVALID")
            identity = (
                digest, source_id, title, url, family, fact.get("event_episode_id"),
                source_class, locator,
            )
            earlier = known_facts.get(case_id)
            if earlier is not None:
                if earlier[0] != digest:
                    raise C2SourceRightsQueueError("C2_RIGHTS_L0_FINGERPRINT_DRIFT")
                if earlier[1:] != identity[1:]:
                    raise C2SourceRightsQueueError("C2_RIGHTS_L0_IDENTITY_DRIFT")
            known_facts[case_id] = identity
            document = documents.setdefault(source_id, {
                "source_id": source_id,
                "source_title": title,
                "source_url": url,
                "bound_l0_facts": {},
                "task_ids": set(),
                "event_families": set(),
                "source_classes": set(),
                "source_locators": set(),
            })
            if document["source_title"] != title or document["source_url"] != url:
                raise C2SourceRightsQueueError("C2_RIGHTS_DOCUMENT_ID_COLLISION")
            document["bound_l0_facts"][case_id] = digest
            document["task_ids"].add(task_id)
            document["event_families"].add(fact["event_family_id"])
            document["source_classes"].add(fact["source_class"])
            if isinstance(locator, str) and locator.strip():
                document["source_locators"].add(locator)
        if fact_ids != set(ref_to_digest):
            raise C2SourceRightsQueueError("C2_RIGHTS_BINDING_SET_DRIFT")
    if not documents or len(seen_tasks) != dossier.get("packet_count"):
        raise C2SourceRightsQueueError("C2_RIGHTS_COHORT_COUNT_INVALID")
    if len(known_facts) != dossier.get("l0_bound_fact_card_count"):
        raise C2SourceRightsQueueError("C2_RIGHTS_L0_COHORT_COUNT_INVALID")

    rows: list[dict[str, Any]] = []
    for source_id, doc in sorted(documents.items()):
        rows.append({
            "source_id": source_id,
            "source_title": doc["source_title"],
            "source_url": doc["source_url"],
            "source_locators": sorted(doc["source_locators"]),
            "source_classes": sorted(doc["source_classes"]),
            "event_families": sorted(doc["event_families"]),
            "task_ids": sorted(doc["task_ids"]),
            "bound_l0_fact_bindings": [
                {"case_id": case_id, "public_fact_sha256": digest}
                for case_id, digest in sorted(doc["bound_l0_facts"].items())
            ],
            "rights_review_status": "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW",
            "license_or_permission_evidence_ref": None,
            "permitted_reuse_scope": None,
            "rights_decision": None,
            "rights_cleared": False,
        })
    return {
        "schema_version": "dgsi-c2-source-rights-review-queue.v1",
        "purpose": "BLANK_SOURCE_RIGHTS_INTAKE_ONLY_NOT_CLEARANCE",
        "notice": (
            "A publicly accessible publication is NOT a reuse license. "
            "No permission, license scope, legal review, scientific approval "
            "or training authorization has been inferred."
        ),
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "collection_id": dossier["collection_id"],
        "collection_projection_sha256": dossier["collection_projection_sha256"],
        "task_count": len(seen_tasks),
        "bound_l0_fact_count": len(known_facts),
        "distinct_source_document_count": len(rows),
        "source_documents": rows,
        "rights_cleared_document_count": 0,
        "source_rights_verified": False,
        "expert_review_complete": False,
        "not_for_sft": True,
        "gold_eligible": False,
        "official_splits_assigned": False,
        "training_authorized": False,
        "sft_records_emitted": 0,
    }
