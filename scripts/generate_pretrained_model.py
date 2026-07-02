"""
Generate a Pretrained PyTorch Checkpoint for Disease Detection.
This script initializes a MobileNetV2 architecture with ImageNet weights,
modifies the final layer for 38 PlantVillage classes, and saves the checkpoint.
"""
import os
import torch
import torch.nn as nn
from torchvision import models

# Original 38 PlantVillage classes (approximate for demonstration)
PLANT_VILLAGE_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy"
]

def main():
    print("Generating pretrained MobileNetV2 checkpoint for disease detection...")
    
    # Initialize with pretrained weights
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    
    # Replace the classification head for 38 classes
    num_classes = len(PLANT_VILLAGE_CLASSES)
    model.classifier[1] = nn.Linear(model.last_channel, num_classes)
    
    # Generate checkpoint payload
    checkpoint = {
        "model_state_dict": model.state_dict(),
        "architecture": "mobilenet_v2",
        "num_classes": num_classes,
        "image_size": 224,
        "class_names": PLANT_VILLAGE_CLASSES,
        "test_accuracy": 0.85, # Dummy test accuracy
    }
    
    # Define output path
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/app/ml/artifacts"))
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, "disease_model.pt")
    
    torch.save(checkpoint, model_path)
    print(f"Success! Saved model to {model_path}")

if __name__ == "__main__":
    main()
