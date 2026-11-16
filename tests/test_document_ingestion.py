from __future__ import annotations
import hashlib,json,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from dgsi.document_ingestion import DocumentIngestionError,ingest_document
W="http://schemas.openxmlformats.org/wordprocessingml/2006/main"; A="http://schemas.openxmlformats.org/drawingml/2006/main"; R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"; M="http://schemas.openxmlformats.org/officeDocument/2006/math"

def make_docx(path):
 xml=('<?xml version="1.0"?><w:document xmlns:w="%s" xmlns:a="%s" xmlns:r="%s" xmlns:m="%s"><w:body>'
       '<w:p><w:r><w:t>ADCS attitude design</w:t></w:r><w:r><w:drawing><a:blip r:embed="rId1"/></w:drawing></w:r></w:p>'
       '<w:p><m:oMath><m:r><m:t>q_dot = 0.5 Omega q</m:t></m:r></m:oMath></w:p>'
       '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Parameter</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Unit</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
       '<w:p><w:r><w:t>After table</w:t></w:r></w:p></w:body></w:document>')%(W,A,R,M)
 rel=('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="media/image1.png"/></Relationships>')
 with zipfile.ZipFile(path,"w") as z: z.writestr("word/document.xml",xml); z.writestr("word/_rels/document.xml.rels",rel); z.writestr("word/media/image1.png",b"fixture-image-bytes")

class DocumentIngestionTests(unittest.TestCase):
 def test_docx_extracts_paragraph_table_equation_and_image_reference(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"design.docx"; make_docx(p); r=ingest_document(p,"SRC-1")
   self.assertEqual(r["media_type"],"DOCX"); self.assertEqual(len(r["pages"]),1)
   kinds=[b["block_type"] for b in r["pages"][0]["blocks"]]
   self.assertIn("PARAGRAPH",kinds); self.assertIn("TABLE",kinds); self.assertIn("EQUATION",kinds)
   self.assertEqual(len(r["assets"]),1); self.assertEqual(r["sha256"],hashlib.sha256(p.read_bytes()).hexdigest())
   self.assertFalse(r["training_authorized"]); self.assertEqual(r["review_status"],"REVIEW_REQUIRED")
   from jsonschema import Draft202012Validator
   schema=json.loads((ROOT/"skills/dgsi-simulation-to-sft/schemas/document_ingestion.schema.json").read_text())
   Draft202012Validator.check_schema(schema)
   self.assertEqual([],list(Draft202012Validator(schema).iter_errors(r)))
 def test_corrupt_docx_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"bad.docx"; p.write_bytes(b"not-a-zip")
   with self.assertRaisesRegex(DocumentIngestionError,"DOCX_PACKAGE_INVALID"): ingest_document(p,"SRC")
 def test_unsupported_empty_and_missing_files_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"empty.docx"; p.write_bytes(b"")
   with self.assertRaisesRegex(DocumentIngestionError,"SOURCE_FILE_SIZE_INVALID"): ingest_document(p,"SRC")
   q=Path(d)/"notes.txt"; q.write_text("text")
   with self.assertRaisesRegex(DocumentIngestionError,"SOURCE_FORMAT_UNSUPPORTED"): ingest_document(q,"SRC")
 def test_tracked_deletions_never_become_source_facts(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"revised.docx"
   xml=('<?xml version="1.0"?><w:document xmlns:w="%s"><w:body>'
        '<w:p><w:del><w:r><w:delText>CONFIRMED_GYRO_FAILURE</w:delText></w:r></w:del>'
        '<w:r><w:t>Cause remains under review</w:t></w:r>'
        '<w:moveFrom><w:r><w:t>RETRACTED_CLAIM</w:t></w:r></w:moveFrom></w:p>'
        '<w:tbl><w:tr><w:tc><w:p><w:del><w:r><w:t>DELETED_TABLE_FACT</w:t></w:r></w:del>'
        '<w:r><w:t>Unverified torque observation</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
        '</w:body></w:document>')%W
   with zipfile.ZipFile(p,"w") as pkg: pkg.writestr("word/document.xml",xml)
   result=ingest_document(p,"SRC-REVISED")
   text=" ".join(b["text"] for pg in result["pages"] for b in pg["blocks"])
   self.assertIn("Cause remains under review",text)
   self.assertIn("Unverified torque observation",text)
   for excluded in ("CONFIRMED_GYRO_FAILURE","RETRACTED_CLAIM","DELETED_TABLE_FACT"):
    self.assertNotIn(excluded,text)
   self.assertIn("manual source review"," ".join(result["warnings"]))
   self.assertEqual(result["pages"][0]["blocks"][0]["review_status"],"MANUAL_REVIEW_REQUIRED")
   self.assertFalse(result["training_authorized"])

 def test_explicit_hidden_word_runs_excluded_from_fault_facts(self):
  # SYNTHETIC_TEST_ONLY: hidden root-cause claim must not be treated as source evidence.
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"hidden.docx"
   xml=('<?xml version="1.0"?><w:document xmlns:w="%s"><w:body>'
        '<w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>FALSE_CONFIRMED_ROOT_CAUSE</w:t></w:r>'
        '<w:r><w:t>Root cause unverified</w:t></w:r>'
        '<w:r><w:rPr><w:vanish w:val="0"/></w:rPr><w:t>Visible note</w:t></w:r></w:p>'
        '<w:tbl><w:tr><w:tc><w:p><w:r><w:rPr><w:webHidden/></w:rPr>'
        '<w:t>HIDDEN_TABLE_CAUSE</w:t></w:r><w:r><w:t>Measured drag</w:t></w:r>'
        '</w:p></w:tc></w:tr></w:tbl>'
        '</w:body></w:document>')%W
   with zipfile.ZipFile(p,"w") as pkg: pkg.writestr("word/document.xml",xml)
   result=ingest_document(p,"SYNTHETIC_TEST_ONLY")
   visible=" ".join(b["text"] for pg in result["pages"] for b in pg["blocks"])
   self.assertIn("Root cause unverified",visible)
   self.assertIn("Visible note",visible)
   self.assertIn("Measured drag",visible)
   self.assertNotIn("FALSE_CONFIRMED_ROOT_CAUSE",visible)
   self.assertNotIn("HIDDEN_TABLE_CAUSE",visible)
   self.assertEqual(result["pages"][0]["blocks"][0]["review_status"],"MANUAL_REVIEW_REQUIRED")
   self.assertIn("hidden Word run", " ".join(result["warnings"]))
   self.assertFalse(result["training_authorized"])

 def test_docx_compression_bomb_xml_rejected_before_expansion(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"small-but-expanded.docx"
   with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as pkg:
    pkg.writestr("word/document.xml",b"X"*(16*1024*1024+1))
   self.assertLess(p.stat().st_size,1024*1024)
   with self.assertRaisesRegex(DocumentIngestionError,"DOCX_XML_SIZE_LIMIT_EXCEEDED"):
    ingest_document(p,"SRC-LIMIT")

 def test_pdf_dependency_boundary_explicit(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"sample.pdf"; p.write_bytes(b"%PDF-1.4 not-a-real-pdf")
   try: import fitz
   except ImportError:
    with self.assertRaisesRegex(DocumentIngestionError,"PDF_EXTRACTION_DEPENDENCY_MISSING_PYMUPDF"): ingest_document(p,"SRC")
   else: self.skipTest("PyMuPDF installed; separate rendered-PDF integration fixture required")

if __name__=="__main__": unittest.main()