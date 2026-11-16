"""Local DOCX/PDF structure and embedded-image extraction for DGSI.
Image extraction is optional and local; no OCR, diagram interpretation or training.
"""
from __future__ import annotations
import hashlib, zipfile
from pathlib import Path, PurePosixPath
from typing import Any
import xml.etree.ElementTree as ET
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"; A="{http://schemas.openxmlformats.org/drawingml/2006/main}"; R="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"; M="{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MAX_FILE_BYTES=100*1024*1024; MAX_PDF_PAGES=2000; MAX_ASSET_BYTES=20*1024*1024; MAX_TOTAL_ASSET_BYTES=200*1024*1024
class DocumentIngestionError(ValueError): pass
def _sha_bytes(data: bytes)->str: return hashlib.sha256(data).hexdigest()
def _sha(path: Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def _text(node: ET.Element)->str: return "".join(x.text or "" for x in node.iter() if x.tag in {W+"t",W+"delText",M+"t"})
def _block(i,k,t,l,manual=False): return {"block_id":i,"block_type":k,"text":t,"locator":l,"review_status":"MANUAL_REVIEW_REQUIRED" if manual else "AUTO_EXTRACTED_REVIEW_REQUIRED"}
def _store(data:bytes,dest:Path|None,name:str,aid:str,loc:str)->dict:
 if len(data)>MAX_ASSET_BYTES: raise DocumentIngestionError("DOCUMENT_ASSET_TOO_LARGE")
 item={"asset_id":aid,"asset_type":"IMAGE","locator":loc,"extraction_status":"REFERENCE_ONLY","sha256":_sha_bytes(data),"size_bytes":len(data),"stored_path":None}
 if dest is not None:
  dest.mkdir(parents=True,exist_ok=True); target=dest/name
  if target.exists() or target.is_symlink(): raise DocumentIngestionError("DOCUMENT_ASSET_DESTINATION_EXISTS")
  target.write_bytes(data); item["extraction_status"]="EXTRACTED"; item["stored_path"]=name
 return item
def _docx(path:Path,dest:Path|None):
 try:
  with zipfile.ZipFile(path) as z:
   names=set(z.namelist())
   if "word/document.xml" not in names: raise DocumentIngestionError("DOCX_MAIN_DOCUMENT_MISSING")
   xml=ET.fromstring(z.read("word/document.xml")); rels={}
   if "word/_rels/document.xml.rels" in names:
    relroot=ET.fromstring(z.read("word/_rels/document.xml.rels")); rels={x.attrib.get("Id"):x.attrib.get("Target","") for x in relroot}
   body=xml.find(W+"body")
   if body is None: raise DocumentIngestionError("DOCX_BODY_MISSING")
   pages=[]; assets=[]; warnings=[]; blocks=[]; pno=1; bno=0; total=0
   for child in list(body):
    if child.tag==W+"p":
     bno+=1; eq=any(n.tag.startswith(M) for n in child.iter()); txt=_text(child)
     if txt.strip() or eq: blocks.append(_block("B%06d"%bno,"EQUATION" if eq else "PARAGRAPH",txt,"DOCX paragraph %d"%bno,eq))
     for drawing in child.iter():
      if drawing.tag==A+"blip":
       target=rels.get(drawing.attrib.get(R+"embed"),"")
       if not target: raise DocumentIngestionError("DOCX_IMAGE_RELATIONSHIP_MISSING")
       rel=PurePosixPath(target)
       if rel.is_absolute() or ".." in rel.parts or "\\" in target: raise DocumentIngestionError("DOCX_IMAGE_PATH_UNSAFE")
       member=str(PurePosixPath("word")/rel)
       if member not in names: raise DocumentIngestionError("DOCX_IMAGE_ASSET_MISSING")
       data=z.read(member); total+=len(data)
       if total>MAX_TOTAL_ASSET_BYTES: raise DocumentIngestionError("DOCUMENT_ASSET_BUDGET_EXCEEDED")
       aid="IMG%04d"%(len(assets)+1); assets.append(_store(data,dest,aid+Path(member).suffix.casefold(),aid,"DOCX paragraph %d; %s"%(bno,member)))
    elif child.tag==W+"tbl":
     bno+=1; rows=[]
     for row in child.findall(".//"+W+"tr"): rows.append(["".join(_text(p) for p in cell.findall(".//"+W+"p")) for cell in row.findall(W+"tc")])
     blocks.append(_block("B%06d"%bno,"TABLE","\n".join(" | ".join(row) for row in rows),"DOCX table %d"%bno,True))
    if any(n.tag==W+"lastRenderedPageBreak" or (n.tag==W+"br" and n.attrib.get(W+"type")=="page") for n in child.iter()):
     pages.append({"locator":"DOCX logical page %d (explicit breaks only)"%pno,"blocks":blocks}); blocks=[]; pno+=1
   if blocks or not pages: pages.append({"locator":"DOCX logical page %d (pagination not rendered)"%pno,"blocks":blocks})
   if assets: warnings.append("Embedded images extracted/indexed; OCR and diagram semantics are not performed.")
   if any(b["block_type"]=="EQUATION" for pg in pages for b in pg["blocks"]): warnings.append("OMML equation text is conservative and requires manual mathematical review.")
   warnings.append("DOCX page boundaries are logical break markers, not rendered page numbers.")
   return pages,assets,warnings
 except zipfile.BadZipFile: raise DocumentIngestionError("DOCX_PACKAGE_INVALID") from None
def _pdf(path:Path,dest:Path|None):
 try: import fitz
 except ImportError: raise DocumentIngestionError("PDF_EXTRACTION_DEPENDENCY_MISSING_PYMUPDF") from None
 pages=[]; assets=[]; warnings=[]; total=0
 try:
  doc=fitz.open(path)
  if doc.page_count>MAX_PDF_PAGES: raise DocumentIngestionError("PDF_PAGE_LIMIT_EXCEEDED")
  for i,page in enumerate(doc):
   blocks=[]
   for j,item in enumerate(page.get_text("blocks")):
    txt=item[4].strip()
    if txt: blocks.append(_block("P%04dB%04d"%(i+1,j+1),"PARAGRAPH",txt,"PDF page %d block %d"%(i+1,j+1)))
   for j,img in enumerate(page.get_images(full=True)):
    xref=img[0]; extracted=doc.extract_image(xref); data=extracted["image"]; ext="."+extracted.get("ext","bin").casefold(); total+=len(data)
    if total>MAX_TOTAL_ASSET_BYTES: raise DocumentIngestionError("DOCUMENT_ASSET_BUDGET_EXCEEDED")
    aid="P%04dIMG%03d"%(i+1,j+1); assets.append(_store(data,dest,aid+ext,aid,"PDF page %d image %d xref %d"%(i+1,j+1,xref)))
   pages.append({"locator":"PDF page %d"%(i+1),"blocks":blocks})
  doc.close()
 except DocumentIngestionError: raise
 except Exception: raise DocumentIngestionError("PDF_PARSE_FAILED") from None
 if assets: warnings.append("Embedded PDF images extracted/indexed; OCR and semantic interpretation are not performed.")
 warnings.append("Complex reading order, tables and mathematical semantics require manual review.")
 return pages,assets,warnings
def ingest_document(path:str|Path,source_id:str,*,asset_dir:str|Path|None=None)->dict[str,Any]:
 p=Path(path)
 if p.is_symlink() or not p.is_file(): raise DocumentIngestionError("SOURCE_FILE_UNAVAILABLE")
 size=p.stat().st_size
 if size<=0 or size>MAX_FILE_BYTES: raise DocumentIngestionError("SOURCE_FILE_SIZE_INVALID")
 dest=Path(asset_dir) if asset_dir is not None else None
 if dest is not None and (dest.exists() or dest.is_symlink()): raise DocumentIngestionError("DOCUMENT_ASSET_DESTINATION_EXISTS")
 if p.suffix.casefold()==".docx": media="DOCX"; pages,assets,warnings=_docx(p,dest)
 elif p.suffix.casefold()==".pdf": media="PDF"; pages,assets,warnings=_pdf(p,dest)
 else: raise DocumentIngestionError("SOURCE_FORMAT_UNSUPPORTED")
 return {"schema_version":"dgsi.document-ingestion.v1","source_id":source_id,"filename":p.name,"media_type":media,"sha256":_sha(p),"size_bytes":size,"extraction_status":"PARTIAL_REVIEW_REQUIRED" if assets or warnings else "TEXT_EXTRACTED","pages":pages,"assets":assets,"warnings":warnings,"review_status":"REVIEW_REQUIRED","training_authorized":False}
