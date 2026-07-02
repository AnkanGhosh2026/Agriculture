"""
Train a crop disease classifier on the PlantVillage dataset using
transfer learning (MobileNetV2 or ResNet18 pretrained on ImageNet).

Usage:
    cd ml/disease_detection
    python inspect_dataset.py     # confirm dataset is laid out correctly first
    python train.py

Output:
    saved_models/disease_model.pt        - trained model weights + metadata
    saved_models/class_names.json        - ordered list of class names
    saved_models/training_history.json   - loss/accuracy per epoch (for review)
"""
import json
import os
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms

import config


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():  # Apple Silicon
        return torch.device("mps")
    return torch.device("cpu")


def build_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    eval_transform = transforms.Compose([
        transforms.Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return train_transform, eval_transform


def build_model(num_classes: int, architecture: str):
    if architecture == "mobilenet_v2":
        model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    elif architecture == "resnet18":
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError(f"Unknown architecture: {architecture}")
    return model


def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return total_loss / total, correct / total


def train():
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    device = get_device()
    print(f"Using device: {device}")

    if not os.path.isdir(config.DATA_DIR):
        raise FileNotFoundError(
            f"DATA_DIR not found: {config.DATA_DIR}\n"
            "Update DATA_DIR in config.py to point to your extracted "
            "PlantVillage 'color' folder, then run inspect_dataset.py to verify."
        )

    train_transform, eval_transform = build_transforms()

    # Load full dataset once (for class discovery + splitting)
    full_dataset = datasets.ImageFolder(config.DATA_DIR)
    class_names = full_dataset.classes
    num_classes = len(class_names)
    print(f"Found {num_classes} classes, {len(full_dataset)} total images")

    # Split into train/val/test
    torch.manual_seed(config.RANDOM_SEED)
    n_total = len(full_dataset)
    n_val = int(n_total * config.VAL_SPLIT)
    n_test = int(n_total * config.TEST_SPLIT)
    n_train = n_total - n_val - n_test

    train_subset, val_subset, test_subset = random_split(
        full_dataset, [n_train, n_val, n_test]
    )

    # Apply the right transforms to each split
    train_subset.dataset = datasets.ImageFolder(config.DATA_DIR, transform=train_transform)
    val_subset.dataset = datasets.ImageFolder(config.DATA_DIR, transform=eval_transform)
    test_subset.dataset = datasets.ImageFolder(config.DATA_DIR, transform=eval_transform)

    train_loader = DataLoader(
        train_subset, batch_size=config.BATCH_SIZE, shuffle=True,
        num_workers=config.NUM_WORKERS,
    )
    val_loader = DataLoader(
        val_subset, batch_size=config.BATCH_SIZE, shuffle=False,
        num_workers=config.NUM_WORKERS,
    )
    test_loader = DataLoader(
        test_subset, batch_size=config.BATCH_SIZE, shuffle=False,
        num_workers=config.NUM_WORKERS,
    )

    print(f"Train: {n_train} | Val: {n_val} | Test: {n_test}")

    model = build_model(num_classes, config.ARCHITECTURE).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    best_val_acc = 0.0
    best_model_state = None

    for epoch in range(1, config.NUM_EPOCHS + 1):
        model.train()
        start = time.time()
        running_loss, correct, total = 0.0, 0, 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        train_loss = running_loss / total
        train_acc = correct / total
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        elapsed = time.time() - start
        print(
            f"Epoch {epoch}/{config.NUM_EPOCHS} "
            f"[{elapsed:.0f}s] "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            print(f"  ↳ New best val_acc: {val_acc:.4f} (checkpoint saved in memory)")

    # Restore best model before final test + save
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    print(f"\nFinal test accuracy: {test_acc:.4f} (loss: {test_loss:.4f})")

    # Save model weights + metadata needed for inference
    model_path = os.path.join(config.OUTPUT_DIR, config.MODEL_FILENAME)
    torch.save({
        "model_state_dict": model.state_dict(),
        "architecture": config.ARCHITECTURE,
        "num_classes": num_classes,
        "image_size": config.IMAGE_SIZE,
        "class_names": class_names,
        "test_accuracy": test_acc,
    }, model_path)
    print(f"Saved model to: {model_path}")

    class_names_path = os.path.join(config.OUTPUT_DIR, config.CLASS_NAMES_FILENAME)
    with open(class_names_path, "w") as f:
        json.dump(class_names, f, indent=2)
    print(f"Saved class names to: {class_names_path}")

    history_path = os.path.join(config.OUTPUT_DIR, "training_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"Saved training history to: {history_path}")

    print("\nNext step: copy these files into your backend and update")
    print("backend/app/ml/disease_model.py to load the real model.")
    print("See ml/disease_detection/README.md for exact instructions.")


if __name__ == "__main__":
    train()
