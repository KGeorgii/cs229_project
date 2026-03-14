from pathlib import Path

pdf_dir = Path("pdfs")

for pdf_path in sorted(pdf_dir.glob("*.pdf")):
    if "+" in pdf_path.name:
        new_name = pdf_path.name.replace("+", "")
        new_path = pdf_dir / new_name
        print(f"{pdf_path.name}  →  {new_name}")
        pdf_path.rename(new_path)

print("\nDone.")