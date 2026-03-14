from pathlib import Path
import json

JSONL_DIR = Path("jsonl_clean")
IMAGE_DIR = Path("images")

missing = []
extra   = []

expected_stems = set()
for jsonl_path in sorted(JSONL_DIR.glob("*.jsonl")):
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            stem = row["filename"]
            expected_stems.add(stem)
            img_path = IMAGE_DIR / f"{stem}.jpg"
            if not img_path.exists():
                missing.append(stem)

actual_stems = {p.stem for p in IMAGE_DIR.glob("*.jpg")}
for stem in sorted(actual_stems):
    if stem not in expected_stems:
        extra.append(stem)

print(f"Expected images : {len(expected_stems)}")
print(f"Actual images   : {len(actual_stems)}")
print(f"Missing         : {len(missing)}")
print(f"Extra (no JSONL): {len(extra)}")

if missing:
    print("\nMissing images:")
    for m in sorted(missing):
        print(f"  {m}")

if extra:
    print("\nExtra images (no annotation):")
    for e in sorted(extra):
        print(f"  {e}")

print("\nDone.")