"""
Run this FIRST after downloading the dataset, to confirm everything
is laid out correctly before you kick off training.

Usage:
    cd ml/disease_detection
    python inspect_dataset.py
"""
import os
from config import DATA_DIR


def inspect():
    if not os.path.isdir(DATA_DIR):
        print(f"❌ DATA_DIR not found: {DATA_DIR}")
        print("   Update DATA_DIR in config.py to point to your extracted")
        print("   PlantVillage 'color' folder, e.g.:")
        print("   DATA_DIR = '../../data/raw/plantvillage/color'")
        return

    classes = sorted(
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    )

    if not classes:
        print(f"❌ No class subfolders found inside {DATA_DIR}")
        return

    print(f"✅ Found {len(classes)} classes in {DATA_DIR}\n")

    total_images = 0
    for cls in classes:
        cls_path = os.path.join(DATA_DIR, cls)
        n_images = len([
            f for f in os.listdir(cls_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
        total_images += n_images
        print(f"  {cls:45s} {n_images:6d} images")

    print(f"\nTotal images: {total_images}")
    print(f"Total classes: {len(classes)}")
    print("\nIf these numbers look right, proceed to: python train.py")


if __name__ == "__main__":
    inspect()
