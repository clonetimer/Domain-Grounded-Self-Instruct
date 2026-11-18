#!/usr/bin/env python3
"""Create local JSON/HTML source-bound annex for two C2 blank expert forms."""
from __future__ import annotations

import argparse
from html import escape
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dgsi.l1_c2_scientific_dossier import (
    C2ReviewDossierError, build_c2_scientific_dossier,
)
from dgsi.l1_blind_review_manifest import L1BlindReviewManifestError
from dgsi.l1_model_projection_audit import L1ProjectionAuditError


def _html(dossier: dict) -> str:
    def section(title: str, data: object) -> str:
        value = escape(json.dumps(data, ensure_ascii=False, indent=2))
        return f"<h3>{escape(title)}</h3><pre>{value}</pre>"

    parts = [
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<title>DGSI C2 SYNTHETIC · 科学审核附件</title>',
        '<style>body{font:15px/1.6 system-ui,sans-serif;max-width:1100px;',
        'margin:30px auto;padding:0 24px}pre{white-space:pre-wrap;',
        'overflow-wrap:anywhere;background:#f5f6f8;padding:14px;',
        'border:1px solid #ddd;border-radius:5px}h2{border-top:2px solid #ddd;',
        'padding-top:24px}strong{color:#9a2b22}</style></head><body>',
        '<h1>DGSI P5-C2 · SYNTHETIC 科学审核附件</h1>',
        '<p><strong>仅供专家核查；不是 SFT、真实遥测、真实 ML 输出或 Gold。</strong></p>',
        f'<p>Collection SHA-256: {escape(dossier["collection_projection_sha256"])}</p>',
        '<p><strong>L0 领域审核状态必须逐卡核查：待审不代表专家确认。</strong></p>',
        f'<p>绑定 L0 事实卡：{dossier["l0_bound_fact_card_count"]}；'
        f'审核状态：{escape(json.dumps(dossier["l0_domain_review_status_counts"], ensure_ascii=False, sort_keys=True))}</p>',
        '<p>核对原始文献与使用权利；L0 不是当前合成故障的直接证据。</p>',
    ]
    for item in dossier["items"]:
        parts.append(f'<h2>{escape(item["task_id"])} / {escape(item["task_type"])}</h2>')
        parts.append(f'<p>Packet: {escape(item["packet_sha256"])} / L0: '
                     f'{escape(item["source_public_sha256"])}</p>')
        parts.append('<p><strong>L0 文献不是当前合成事件的直接证据。</strong></p>')
        for title, field in (
            ("L0 公开来源事实与定位", "l0_public_source_context"),
            ("合成任务指令", "task_instruction"),
            ("合成输入：上游结果、日志及任务上下文", "synthetic_input"),
            ("正式诊断目标（仅供科学审阅）", "formal_target_for_expert_review"),
            ("历史 Context", "historical_context"),
            ("字段级合成来源与假设", "synthetic_provenance"),
        ):
            parts.append(section(title, item[field]))
    parts.append("</body></html>")
    return "".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True, type=Path)
    parser.add_argument("--source-facts", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    stage = "READ_INPUT"
    try:
        collection = json.loads(args.collection.read_text(encoding="utf-8"))
        sources = json.loads(args.source_facts.read_text(encoding="utf-8"))["cards"]
        stage = "BUILD_REVIEW_ONLY_DOSSIER"
        dossier = build_c2_scientific_dossier(collection, source_fact_cards=sources)
        stage = "CREATE_NEW_DIRECTORY"
        os.mkdir(args.output_dir, 0o700)
        stage = "WRITE_REVIEW_ONLY_DOSSIER"
        (args.output_dir / "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json").write_text(
            json.dumps(dossier, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        (args.output_dir / "C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html").write_text(
            _html(dossier), encoding="utf-8"
        )
    except (L1BlindReviewManifestError, L1ProjectionAuditError,
            C2ReviewDossierError) as exc:
        print(json.dumps({"decision": "REJECTED", "stage": stage,
                          "error_code": str(exc), "training_authorized": False,
                          "sft_records_emitted": 0}))
        return 2
    except (OSError, KeyError, TypeError, ValueError, UnicodeError):
        print(json.dumps({"decision": "REJECTED", "stage": stage,
                          "error_code": "C2_DOSSIER_INPUT_OR_OUTPUT_INVALID",
                          "training_authorized": False, "sft_records_emitted": 0}))
        return 2
    print(json.dumps({"decision": "REVIEW_ONLY_DOSSIER_GENERATED",
                      "packet_count": dossier["packet_count"],
                      "event_family_count": dossier["event_family_count"],
                      "files_created": 2, "training_authorized": False,
                      "sft_records_emitted": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
