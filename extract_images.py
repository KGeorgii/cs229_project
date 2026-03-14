from pathlib import Path
import json
import fitz

PDF_DIR   = Path("pdfs")
JSONL_DIR = Path("jsonl_clean")
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)

expected = set()
for jsonl_path in sorted(JSONL_DIR.glob("*.jsonl")):
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            expected.add(row["journal"])

for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    issue_key = pdf_path.stem
    if issue_key not in expected:
        print(f"  SKIP (no JSONL): {pdf_path.name}")
        continue

    print(f"Rendering {pdf_path.name} ...")
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc, start=1):
        out_path = IMAGE_DIR / f"{issue_key}_{i}.jpg"
        if out_path.exists():
            continue
        mat = fitz.Matrix(200/72, 200/72)
        pix = page.get_pixmap(matrix=mat)
        pix.save(out_path)

    print(f"  → {len(doc)} pages saved")
    doc.close()

print("\nDone.")