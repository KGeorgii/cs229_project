from ultralytics import YOLO
from pathlib import Path

DATA_YAML = Path("dataset/data.yaml")

model = YOLO("yolov8m.pt")

results = model.train(
    data=DATA_YAML,
    epochs=100,
    imgsz=512,
    batch=8,
    device="cpu",
    workers=4,
    cache=True,
    name="vsesvit_yolov8m",
    project="runs",
    patience=20,
    save=True,
    save_period=10,
    degrees=5,
    hsv_v=0.6,
    mosaic=0.5,
)

print(f"\nBest weights: runs/vsesvit_yolov8m/weights/best.pt")
print(f"mAP@0.5: {results.box.map50:.4f}")