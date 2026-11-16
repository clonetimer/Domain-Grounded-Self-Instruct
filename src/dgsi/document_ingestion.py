"""Local DOCX/PDF structure extractor for DGSI source ingestion.

It extracts structure and text only. It does not interpret diagrams,
prove equation semantics, perform OCR, or create training data.
"""
from __future__ import annotations
import hashlib, zipfile
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A="{http://schemas.openxmlformats.org/drawingml/2006/main}"
R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
M="{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MAX_FILE_BYTES=100*1024*1024
MAX_PDF_PAGES=2000
MAX_DOCX_XML_BYTES=16*1024*1024
MAX_DOCX_TOTAL_UNCOMPRESSED_BYTES=256*1024*1024
MAX_DOCX_ENTRIES=10000
REVISION_MARKERS={W+"del",W+"delText",W+"moveFrom",W+"moveTo",W+"ins"}
DELETED_CONTENT={W+"del",W+"delText",W+"moveFrom"}
HIDDEN_RUN_MARKERS={W+"vanish",W+"webHidden",W+"specVanish"}

class DocumentIngestionError(ValueError): pass

def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def _run_is_hidden(node: ET.Element) -> bool:
    """Only explicit, enabled Word run-level hiding is safe to suppress."""
    if node.tag != W+"r": return False
    rpr=node.find(W+"rPr")
    if rpr is None: return False
    return any(prop.tag in HIDDEN_RUN_MARKERS and
               prop.attrib.get(W+"val","true").strip().casefold() not in {"0","false","off"}
               for prop in rpr)

def _text(node: ET.Element) -> str:
    """Extract visible text; never treat tracked deletions as source facts."""
    parts=[]
    stack=[node]
    while stack:
        item=stack.pop()
        if item.tag in DELETED_CONTENT or _run_is_hidden(item):
            continue
        if item.tag in {W+"t",M+"t"}:
            parts.append(item.text or "")
        stack.extend(reversed(list(item)))
    return "".join(parts)

def _block(block_id: str, kind: str, text: str, locator: str, manual: bool=False) -> dict[str,Any]:
    return {"block_id":block_id,"block_type":kind,"text":text,"locator":locator,
            "review_status":"MANUAL_REVIEW_REQUIRED" if manual else "AUTO_EXTRACTED_REVIEW_REQUIRED"}

def _docx(path: Path):
    try:
        with zipfile.ZipFile(path) as z:
            infos=z.infolist()
            if len(infos)>MAX_DOCX_ENTRIES: raise DocumentIngestionError("DOCX_ENTRY_LIMIT_EXCEEDED")
            if sum(info.file_size for info in infos)>MAX_DOCX_TOTAL_UNCOMPRESSED_BYTES:
                raise DocumentIngestionError("DOCX_UNCOMPRESSED_SIZE_LIMIT_EXCEEDED")
            names=set(z.namelist())
            if "word/document.xml" not in names: raise DocumentIngestionError("DOCX_MAIN_DOCUMENT_MISSING")
            for member in ("word/document.xml","word/_rels/document.xml.rels"):
                if member in names and z.getinfo(member).file_size>MAX_DOCX_XML_BYTES:
                    raise DocumentIngestionError("DOCX_XML_SIZE_LIMIT_EXCEEDED")
            xml=ET.fromstring(z.read("word/document.xml"))
            rels={}
            if "word/_rels/document.xml.rels" in names:
                relroot=ET.fromstring(z.read("word/_rels/document.xml.rels"))
                rels={x.attrib.get("Id"):x.attrib.get("Target","") for x in relroot}
            body=xml.find(W+"body")
            if body is None: raise DocumentIngestionError("DOCX_BODY_MISSING")
            pages=[]; assets=[]; warnings=[]; page_blocks=[]; pno=1; bno=0; revision_seen=False; hidden_seen=False
            for child in list(body):
                has_revision=any(n.tag in REVISION_MARKERS for n in child.iter())
                has_hidden=any(_run_is_hidden(n) for n in child.iter())
                revision_seen=revision_seen or has_revision
                hidden_seen=hidden_seen or has_hidden
                if child.tag==W+"p":
                    bno+=1; eq=any(n.tag.startswith(M) for n in child.iter()); txt=_text(child)
                    if txt.strip() or eq: page_blocks.append(_block("B%06d"%bno,"EQUATION" if eq else "PARAGRAPH",txt,"DOCX paragraph %d"%bno,eq or has_revision or has_hidden))
                    for drawing in child.iter():
                        if drawing.tag==A+"blip":
                            target=rels.get(drawing.attrib.get(R+"embed"),"")
                            assets.append({"asset_id":"IMG%04d"%(len(assets)+1),"asset_type":"IMAGE","locator":"DOCX paragraph %d; media/%s"%(bno,target),"extraction_status":"REFERENCE_ONLY"})
                elif child.tag==W+"tbl":
                    bno+=1; rows=[]
                    for row in child.findall(".//"+W+"tr"):
                        rows.append(["".join(_text(p) for p in cell.findall(".//"+W+"p")) for cell in row.findall(W+"tc")])
                    table_text="\\n".join(" | ".join(row) for row in rows)
                    page_blocks.append(_block("B%06d"%bno,"TABLE",table_text,"DOCX table %d"%bno,True))
                page_break=any(n.tag==W+"lastRenderedPageBreak" or (n.tag==W+"br" and n.attrib.get(W+"type")=="page") for n in child.iter())
                if page_break:
                    pages.append({"locator":"DOCX logical page %d (explicit breaks only)"%pno,"blocks":page_blocks}); page_blocks=[]; pno+=1
            if page_blocks or not pages: pages.append({"locator":"DOCX logical page %d (pagination not rendered)"%pno,"blocks":page_blocks})
            if revision_seen: warnings.append("Tracked revisions detected. Deleted text excluded; all affected blocks require manual source review.")
            if hidden_seen: warnings.append("Explicit hidden Word run text excluded; affected blocks require manual source review. Style-inherited visibility is not resolved.")
            if assets: warnings.append("Embedded images/drawings are indexed but not OCRd or semantically interpreted.")
            if any(b["block_type"]=="EQUATION" for pg in pages for b in pg["blocks"]): warnings.append("OMML equation text is extracted conservatively and requires manual mathematical review.")
            warnings.append("DOCX page boundaries are logical break markers, not rendered page numbers.")
            return pages,assets,warnings
    except zipfile.BadZipFile: raise DocumentIngestionError("DOCX_PACKAGE_INVALID") from None

def _pdf(path: Path):
    try: import fitz
    except ImportError: raise DocumentIngestionError("PDF_EXTRACTION_DEPENDENCY_MISSING_PYMUPDF") from None
    pages=[]; assets=[]; warnings=[]
    try:
        doc=fitz.open(path)
        if doc.page_count>MAX_PDF_PAGES: raise DocumentIngestionError("PDF_PAGE_LIMIT_EXCEEDED")
        for i,page in enumerate(doc):
            blocks=[]
            for j,item in enumerate(page.get_text("blocks")):
                txt=item[4].strip()
                if txt: blocks.append(_block("P%04dB%04d"%(i+1,j+1),"PARAGRAPH",txt,"PDF page %d block %d"%(i+1,j+1)))
            for j,_ in enumerate(page.get_images(full=True)): assets.append({"asset_id":"P%04dIMG%03d"%(i+1,j+1),"asset_type":"IMAGE","locator":"PDF page %d image %d"%(i+1,j+1),"extraction_status":"MANUAL_REVIEW_REQUIRED"})
            pages.append({"locator":"PDF page %d"%(i+1),"blocks":blocks})
        doc.close()
    except DocumentIngestionError: raise
    except Exception: raise DocumentIngestionError("PDF_PARSE_FAILED") from None
    if assets: warnings.append("PDF figures/images are indexed only; OCR and semantic interpretation are not performed.")
    warnings.append("Complex reading order, tables and mathematical semantics require manual review.")
    return pages,assets,warnings

def ingest_document(path: str|Path, source_id: str) -> dict[str,Any]:
    p=Path(path)
    if p.is_symlink() or not p.is_file(): raise DocumentIngestionError("SOURCE_FILE_UNAVAILABLE")
    size=p.stat().st_size
    if size<=0 or size>MAX_FILE_BYTES: raise DocumentIngestionError("SOURCE_FILE_SIZE_INVALID")
    if p.suffix.casefold()==".docx": media="DOCX"; pages,assets,warnings=_docx(p)
    elif p.suffix.casefold()==".pdf": media="PDF"; pages,assets,warnings=_pdf(p)
    else: raise DocumentIngestionError("SOURCE_FORMAT_UNSUPPORTED")
    return {"schema_version":"dgsi.document-ingestion.v1","source_id":source_id,"filename":p.name,
            "media_type":media,"sha256":_sha(p),"size_bytes":size,
            "extraction_status":"PARTIAL_REVIEW_REQUIRED" if assets or warnings else "TEXT_EXTRACTED",
            "pages":pages,"assets":assets,"warnings":warnings,"review_status":"REVIEW_REQUIRED","training_authorized":False}
