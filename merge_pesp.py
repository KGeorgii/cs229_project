import json, os, requests, time
from pathlib import Path

N_PAGES = 1000
BATCH_SIZE = 100
OUT_IMG = Path("dataset/train/images")
OUT_LBL = Path("dataset/train/labels")

CLASS_MAP = {"0": 5, "1": 6, "2": 1, "3": 4}

OUT_IMG.mkdir(parents=True, exist_ok=True)
OUT_LBL.mkdir(parents=True, exist_ok=True)

def fetch_batch(offset, retries=5):
    url = (f"https://datasets-server.huggingface.co/rows"
           f"?dataset=apjanco%2Fpesp&config=default&split=train"
           f"&offset={offset}&length={BATCH_SIZE}")
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and resp.text.strip():
                return resp.json()["rows"]
            else:
                print(f"Empty/bad response at offset {offset}, attempt {attempt+1}/{retries}, waiting...")
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"Error at offset {offset}, attempt {attempt+1}/{retries}: {e}")
            time.sleep(5 * (attempt + 1))
    return None

existing = set(p.stem for p in OUT_IMG.glob("pesp_*.jpg"))
added = len(existing)
print(f"Resuming from {added} already downloaded pages...")

offset = 0

while added < N_PAGES:
    rows = fetch_batch(offset)
    if rows is None:
        print(f"Failed to fetch batch at offset {offset}, skipping...")
        offset += BATCH_SIZE
        continue
    if not rows:
        print("No more rows, stopping.")
        break

    for row in rows:
        if added >= N_PAGES:
            break
        r = row["row"]

        uri = r.get("uri", "").strip()
        if not uri:
            continue

        yolo_str = r.get("yolo", "").strip()
        if not yolo_str:
            continue

        safe_name = f"pesp_{offset:05d}_{added:05d}"

        if safe_name in existing:
            continue

        img_path = OUT_IMG / f"{safe_name}.jpg"
        try:
            img_resp = requests.get(uri, timeout=15)
            if img_resp.status_code != 200:
                continue
            img_path.write_bytes(img_resp.content)
        except Exception as e:
            print(f"Skipping {safe_name}: {e}")
            continue

        lbl_path = OUT_LBL / f"{safe_name}.txt"
        lines = []
        for line in yolo_str.strip().split("\n"):
            parts = line.strip().split()
            if not parts:
                continue
            old_class = parts[0]
            if old_class not in CLASS_MAP:
                continue
            new_class = CLASS_MAP[old_class]
            lines.append(f"{new_class} {' '.join(parts[1:])}")

        if not lines:
            img_path.unlink()
            continue

        lbl_path.write_text("\n".join(lines))
        added += 1
        if added % 100 == 0:
            print(f"Downloaded {added}/{N_PAGES} pages...")

    offset += BATCH_SIZE
    time.sleep(1)

print(f"Done — added {added} PESP pages to training set")