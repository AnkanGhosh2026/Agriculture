"""
Configuration for the crop disease detection model training.

CLASS_NAMES below is the exact 38-class list from the PlantVillage dataset
(color folder). If your Kaggle download has slightly different folder names,
run `python inspect_dataset.py` first to confirm — the training script also
auto-detects classes from your actual folders, so this list is mainly for
reference and for the backend's disease_model.py to stay in sync.
"""

# Path to the "color" folder from the Kaggle PlantVillage dataset.
# Update this to wherever you extracted the dataset.
DATA_DIR = "../../data/raw/plantvillage/color"

# Where to save outputs
OUTPUT_DIR = "./saved_models"
MODEL_FILENAME = "disease_model.pt"
CLASS_NAMES_FILENAME = "class_names.json"

# Image / training settings
IMAGE_SIZE = 224          # standard input size for MobileNetV2/ResNet
BATCH_SIZE = 32
NUM_EPOCHS = 10           # increase to 15-20 for better accuracy if time allows
LEARNING_RATE = 1e-3
VAL_SPLIT = 0.15          # 15% held out for validation
TEST_SPLIT = 0.10         # 10% held out for final test
RANDOM_SEED = 42

# Model architecture: "mobilenet_v2" (fast, good for CPU) or "resnet18"
ARCHITECTURE = "mobilenet_v2"

# Number of dataloader workers (set to 0 on Windows if you hit issues)
NUM_WORKERS = 2
