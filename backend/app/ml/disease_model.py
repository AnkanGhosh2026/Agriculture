"""
Crop disease detection model wrapper.

Loads a real trained PyTorch model (trained via ml/disease_detection/train.py)
from DISEASE_MODEL_PATH. If no trained model file is found, falls back to
mock predictions so the API keeps working during development.

To activate real predictions:
    1. Train the model: see ml/disease_detection/README.md
    2. Copy saved_models/disease_model.pt into backend/app/ml/artifacts/
    3. Set DISEASE_MODEL_PATH in .env (or leave default, it already points there)
    4. Restart the API — this file auto-detects the file and loads it
"""
import io
import os
import random

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.core.config import settings
from app.schemas.disease import DiseasePrediction

# Fallback class list used only in mock mode (no trained model present)
MOCK_DISEASE_CLASSES = [
    "Healthy",
    "Leaf Blight",
    "Powdery Mildew",
    "Bacterial Spot",
    "Rust",
    "Mosaic Virus",
]


def _build_architecture(architecture: str, num_classes: int) -> nn.Module:
    if architecture == "mobilenet_v2":
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    elif architecture == "resnet18":
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError(f"Unknown architecture: {architecture}")
    return model


class DiseaseModel:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or settings.DISEASE_MODEL_PATH
        self._model: nn.Module | None = None
        self._class_names: list[str] = []
        self._image_size: int = 224
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._transform: transforms.Compose | None = None
        self._loaded = False

        self.load()

    def load(self):
        """Loads the trained model if present. Safe to call multiple times."""
        if not os.path.exists(self.model_path):
            self._loaded = False
            return

        checkpoint = torch.load(self.model_path, map_location=self._device)
        self._class_names = checkpoint["class_names"]
        self._image_size = checkpoint.get("image_size", 224)

        model = _build_architecture(checkpoint["architecture"], checkpoint["num_classes"])
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        model.to(self._device)

        self._model = model
        self._transform = transforms.Compose([
            transforms.Resize((self._image_size, self._image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self._loaded = True

    @property
    def is_using_real_model(self) -> bool:
        return self._loaded

    def predict(self, image_bytes: bytes) -> list[DiseasePrediction]:
        """
        Takes raw image bytes, returns ranked disease predictions
        (highest confidence first).
        """
        if self._loaded:
            return self._predict_real(image_bytes)
        return self._predict_mock()

    def _predict_real(self, image_bytes: bytes) -> list[DiseasePrediction]:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self._transform(image).unsqueeze(0).to(self._device)

        with torch.no_grad():
            outputs = self._model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]

        ranked = sorted(
            zip(self._class_names, probs.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )

        return [
            DiseasePrediction(
                disease_name=_format_class_name(cls),
                confidence=round(conf, 4),
                is_healthy=("healthy" in cls.lower()),
            )
            for cls, conf in ranked
        ]

    def _predict_mock(self) -> list[DiseasePrediction]:
        scores = sorted(
            [(cls, round(random.uniform(0, 1), 3)) for cls in MOCK_DISEASE_CLASSES],
            key=lambda x: x[1],
            reverse=True,
        )
        total = sum(s for _, s in scores) or 1
        normalized = [(cls, round(s / total, 3)) for cls, s in scores]

        return [
            DiseasePrediction(
                disease_name=cls,
                confidence=conf,
                is_healthy=(cls == "Healthy"),
            )
            for cls, conf in normalized
        ]


def _format_class_name(raw_class_name: str) -> str:
    """
    PlantVillage class folders look like 'Tomato___Late_blight'.
    Convert to a friendlier display string: 'Tomato - Late blight'.
    """
    parts = raw_class_name.replace("___", "|").split("|")
    formatted = [p.replace("_", " ").strip() for p in parts]
    return " - ".join(formatted)


disease_model = DiseaseModel()
