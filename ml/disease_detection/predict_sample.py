"""
Quick sanity check: run the trained model on a single image
before wiring it into the backend.

Usage:
    cd ml/disease_detection
    python predict_sample.py /path/to/some_leaf_image.jpg
"""
import sys
import json
import os

import torch
from PIL import Image
from torchvision import transforms

import config
from train import build_model, get_device


def load_model(model_path: str):
    checkpoint = torch.load(model_path, map_location="cpu")
    model = build_model(checkpoint["num_classes"], checkpoint["architecture"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, checkpoint["class_names"], checkpoint["image_size"]


def predict(image_path: str, model_path: str = None):
    model_path = model_path or os.path.join(config.OUTPUT_DIR, config.MODEL_FILENAME)
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"No trained model found at {model_path}. Run train.py first."
        )

    device = get_device()
    model, class_names, image_size = load_model(model_path)
    model.to(device)

    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        top5 = torch.topk(probs, k=min(5, len(class_names)))

    print(f"\nPredictions for: {image_path}\n")
    for score, idx in zip(top5.values, top5.indices):
        print(f"  {class_names[idx]:45s} {score.item()*100:.2f}%")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_sample.py /path/to/image.jpg")
        sys.exit(1)
    predict(sys.argv[1])
