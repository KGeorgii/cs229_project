# Vsesvit Document Layout Analysis

YOLOv8m fine-tuned for layout analysis of *Vsesvit*, a Ukrainian Soviet-era literary periodical (1925–1934). Achieves **mAP@0.5 = 0.799** on a held-out test set of 139 pages across an 8-class taxonomy.

Model weights and annotated dataset will be released on HuggingFace.

---

## Classes

| ID | Class | Description |
|----|-------|-------------|
| 0 | `journal_name` | Masthead typography |
| 1 | `article_title` | Display-weight heading |
| 2 | `author_name` | By-line |
| 3 | `page_number` | Numerals in corner or header |
| 4 | `mixed_text` | Inseparable typographic-graphic composites |
| 5 | `text_block` | Body prose columns |
| 6 | `image` | Photographs and illustrations |
| 7 | `decorative_element` | Ornamental borders, rules, vignettes |

---

## Requirements

```bash
pip install ultralytics pymupdf requests
```

---

## Pipeline

Run scripts in this order:

### 1. `clean_pdf_names.py`
Sanitizes filenames in `pdfs/` by removing `+` characters that cause downstream path errors. Run once before any other step.

```bash
python clean_pdf_names.py
```

### 2. `extract_images.py`
Renders each PDF in `pdfs/` to per-page JPEG images at 200 DPI using PyMuPDF, writing output to `images/`. Only processes issues that have a corresponding annotation file in `jsonl_clean/`.

```bash
python extract_images.py
```

### 3. `verify.py`
Cross-checks `images/` against `jsonl_clean/` to confirm every annotated page has a rendered image and every image has an annotation. Reports missing and extra files. Run after extraction and after any manual annotation changes.

```bash
python verify.py
```

### 4. `data_prep.py`
Converts the JSONL annotations in `jsonl_clean/` into YOLO TXT label files and organizes images into `dataset/train/`, `dataset/val/`, and `dataset/test/` using a 70/15/15 stratified split by decade of publication. Writes `dataset/data.yaml`.

```bash
python data_prep.py
```

### 5. `merge_pesp.py`
Downloads 1,000 pages from the [PESP HuggingFace dataset](https://huggingface.co/datasets/apjanco/pesp), remaps their class IDs to the Vsesvit taxonomy (`image→5, mixedtext→6, title→1, textblock→4`), and appends images and labels directly into `dataset/train/`. Supports resuming interrupted downloads.

```bash
python merge_pesp.py
```

### 6. `train_yolov8.py`
Fine-tunes COCO-pretrained YOLOv8m on `dataset/` for 100 epochs (batch 8, 512px, CPU). Saves checkpoints to `runs/vsesvit_yolov8m/`.

```bash
python train_yolov8.py
```

### 7. `pesp_finetune.py`
Continues training from the best Experiment 1 checkpoint for 50 additional epochs on the PESP-augmented dataset. Update the checkpoint path inside the script before running. Saves to `runs/vsesvit_yolov8m_pesp/`.

```bash
python pesp_finetune.py
```

---


---

## Results

| Experiment | Data | mAP@0.5 | mAP@0.5:0.95 |
|------------|------|---------|--------------|
| Exp. 1 | Vsesvit only (974 pages) | 0.799 | 0.600 |
| Exp. 2 | + 500 PESP pages | 0.802 | 0.602 |

---
