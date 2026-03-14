from ultralytics import YOLO
from pathlib import Path

DATA_YAML = Path("dataset/data.yaml")
model = YOLO("runs/detect/runs/vsesvit_yolov8m5/weights/best.pt")

results = model.train(
    data=DATA_YAML,
    epochs=50,
    imgsz=512,
    batch=8,
    device="cpu",
    workers=4,
    cache=True,
    patience=20,
    save=True,
    save_period=10,
    degrees=5,
    hsv_v=0.6,
    mosaic=0.5,
    name="vsesvit_yolov8m_pesp",
    project="runs",
)

print(f"mAP@0.5: {results.box.map50:.4f}")