#!/usr/bin/env python3
"""Create separate BLANK C2 reviewer Word/JSON packs, no expert approval."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dgsi.l1_blind_review_manifest import L1BlindReviewManifestError
from dgsi.l1_c2_expert_handoff import build_c2_expert_handoff
from dgsi.l1_model_projection_audit import L1ProjectionAuditError


def _para(value: str, *, heading: bool = False, page_break_before: bool = False) -> str:
    properties = (
        ('<w:pStyle w:val="Heading1"/>' if heading else "")
        + ('<w:pageBreakBefore/>' if page_break_before else "")
    )
    style = "<w:pPr>" + properties + "</w:pPr>" if properties else ""
    return (
        "<w:p>" + style + "<w:r><w:rPr><w:rFonts "
        'w:ascii="Arial" w:eastAsia="Microsoft YaHei" w:hAnsi="Arial"/>'
        '</w:rPr><w:t xml:space="preserve">' + escape(value)
        + "</w:t></w:r></w:p>"
    )


def _word_document(handoff: dict) -> bytes:
    """Minimal interoperable OOXML Word form using only stdlib."""
    from io import BytesIO
    slot = handoff["reviewer_slot"]
    body = [
        _para("DGSI P5-C2 / 专家盲审表 / Reviewer " + slot, heading=True),
        _para("空白审核表：未获得专家评分、身份确认、来源权利许可或训练授权。"),
        _para("两名专家须独立填写；不得将已填材料上传公开仓库。"),
        _para("候选集合 SHA-256: " + handoff["collection_projection_sha256"]),
        _para("任务数: " + str(handoff["packet_count"]) +
              "；事件族: " + str(handoff["event_family_count"])),
    ]
    for index, task in enumerate(handoff["tasks"], 1):
        body.extend([
            _para(f"{index:02d}. {task['task_id']} / {task['task_type']}",
                  heading=True, page_break_before=index > 1),
            _para("事件族: " + task["event_family"]),
            _para("Case: " + task["case_id"]),
            _para("Packet SHA-256: " + task["packet_sha256"][:32] +
                  " " + task["packet_sha256"][32:]),
            _para("L0 source SHA-256: " + task["source_public_sha256"][:32] +
                  " " + task["source_public_sha256"][32:]),
            _para("来源事实卡: " + ", ".join(
                b["source_fact_ref"] for b in task["source_fact_bindings"]
            )),
            _para("对照来源原文和 L1 完整任务包独立核查；文献事实不能冒充当前合成事件证据。"),
        ])
        for dimension in handoff["rubric_dimensions"]:
            body.append(_para(dimension + "  ___ / 5"))
        body.extend([
            _para("Finding codes: _________________________________"),
            _para("判定：ACCEPT_L1 / REVISE / REJECT（圈选）"),
            _para("Reviewer token（仅在安全工作区填写）: __________________"),
            _para("问题、来源定位和修改建议：请另存于受控审核记录。"),
            _para("审核备注: _____________________________________________________"),
            _para("_____________________________________________________________"),
        ])
    body.append(
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="950" w:right="850" w:bottom="950" w:left="850" '
        'w:header="400" w:footer="400" w:gutter="0"/></w:sectPr>'
    )
    doc = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body>'
        + "".join(body) + "</w:body></w:document>"
    )
    types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    )
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
    return buffer.getvalue()


def _reject(code: str, stage: str) -> int:
    print(json.dumps({
        "decision": "REJECTED", "error_code": code, "stage": stage,
        "sft_records_emitted": 0, "training_authorized": False,
    }))
    return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collection", type=Path, required=True)
    ap.add_argument("--source-facts", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args(argv)
    stage = "READ_INPUT"
    try:
        collection = json.loads(args.collection.read_text(encoding="utf-8"))
        facts = json.loads(args.source_facts.read_text(encoding="utf-8"))
        if not isinstance(facts, dict) or not isinstance(facts.get("cards"), list):
            return _reject("SOURCE_FACTS_SCHEMA_INVALID", stage)
        stage = "BUILD_BLANK_HANDOFF"
        a = build_c2_expert_handoff(collection, source_fact_cards=facts["cards"], reviewer_slot="A")
        b = build_c2_expert_handoff(collection, source_fact_cards=facts["cards"], reviewer_slot="B")
        stage = "CREATE_NEW_DIRECTORY"
        # Exclusive directory creation: never reuse or overwrite reviewer work.
        os.mkdir(args.output_dir, 0o700)
        stage = "WRITE_BLANK_FORMS"
        for slot, handoff in (("A", a), ("B", b)):
            (args.output_dir / f"C2_reviewer_{slot}_BLANK.json").write_text(
                json.dumps(handoff, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                encoding="utf-8",
            )
            (args.output_dir / f"C2_reviewer_{slot}_BLANK.docx").write_bytes(
                _word_document(handoff)
            )
    except (L1BlindReviewManifestError, L1ProjectionAuditError) as exc:
        return _reject(str(exc), stage)
    except FileExistsError:
        return _reject("OUTPUT_DIRECTORY_EXISTS", stage)
    except FileNotFoundError:
        return _reject("INPUT_FILE_NOT_FOUND", stage)
    except PermissionError:
        return _reject("INPUT_OR_OUTPUT_PERMISSION_DENIED", stage)
    except json.JSONDecodeError:
        return _reject("INPUT_JSON_INVALID", stage)
    except (KeyError, TypeError, ValueError, OSError, UnicodeError):
        return _reject("INPUT_OR_OUTPUT_INVALID", stage)
    print(json.dumps({
        "decision": "BLANK_TWO_REVIEWER_HANDOFF_ONLY",
        "packet_count": a["packet_count"],
        "event_family_count": a["event_family_count"],
        "separate_reviewer_forms": 2,
        "files_created": 4,
        "expert_adjudicated_count": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
