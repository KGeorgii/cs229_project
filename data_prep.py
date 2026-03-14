import json, shutil, random, re
from pathlib import Path

JSONL_DIR   = Path("jsonl_clean")
IMAGE_DIR   = Path("images")
DATASET_DIR = Path("dataset")

CLASSES = [
    "journal_name",
    "article_title",
    "author_name",
    "page_number",
    "text_block",
    "image",
    "mixed_text",
    "decorative_element",
]

random.seed(42)

issues = {}
for jsonl_path in sorted(JSONL_DIR.glob("*.jsonl")):
    issue_key = jsonl_path.stem
    year_match = re.search(r'(\d{4})', issue_key)
    decade = (int(year_match.group(1)) // 10 * 10) if year_match else 0
    pages = []
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            pages.append(row["filename"])
    issues[issue_key] = {"decade": decade, "pages": pages, "jsonl": jsonl_path}

by_decade = {}
for key, val in issues.items():
    by_decade.setdefault(val["decade"], []).append(key)

train_keys, val_keys, test_keys = [], [], []
for decade, keys in sorted(by_decade.items()):
    random.shuffle(keys)
    n = len(keys)
    t = max(1, int(n * 0.70))
    v = max(1, int(n * 0.15))
    train_keys += keys[:t]
    val_keys   += keys[t:t+v]
    test_keys  += keys[t+v:]
    print(f"  decade {decade}: {len(keys)} issues → "
          f"train={len(keys[:t])} val={len(keys[t:t+v])} test={len(keys[t+v:])}")

print(f"\nTotal: train={len(train_keys)} val={len(val_keys)} test={len(test_keys)} issues\n")

def write_split(split_name, keys):
    img_out = DATASET_DIR / split_name / "images"
    lbl_out = DATASET_DIR / split_name / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    n_pages, n_missing = 0, 0
    for key in keys:
        jsonl_path = issues[key]["jsonl"]
        with open(jsonl_path) as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                stem = row["filename"]

                src_img = IMAGE_DIR / f"{stem}.jpg"
                if not src_img.exists():
                    print(f"  MISSING image: {src_img}")
                    n_missing += 1
                    continue
                shutil.copy(src_img, img_out / f"{stem}.jpg")

                yolo_str = row.get("yolo", "").strip()
                if yolo_str:
                    (lbl_out / f"{stem}.txt").write_text(yolo_str)
                n_pages += 1

    print(f"  {split_name:6s}: {n_pages} pages, {n_missing} missing images")

write_split("train", train_keys)
write_split("val",   val_keys)
write_split("test",  test_keys)

yaml_content = f"""path: {DATASET_DIR.resolve()}
train: train/images
val:   val/images
test:  test/images

nc: {len(CLASSES)}
names:
""" + "\n".join(f"  {i}: {c}" for i, c in enumerate(CLASSES)) + "\n"

(DATASET_DIR / "data.yaml").write_text(yaml_content)
print(f"\nWrote data.yaml")
print("\nDone.")