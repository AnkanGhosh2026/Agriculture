# Training the Crop Disease Detection Model

This trains a real CNN (transfer learning on MobileNetV2) using your
downloaded **PlantVillage** dataset from Kaggle, then wires it into the
FastAPI backend.

## Step 1 — Download & extract the dataset

Download from Kaggle:
https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

Extract it, then move (or copy) the **`color`** folder into your project's
`data/raw/` directory like this:

```
ai-agriculture-platform/
└── data/
    └── raw/
        └── plantvillage/
            └── color/
                ├── Apple___Apple_scab/
                ├── Apple___Black_rot/
                ├── ...
                └── Tomato___healthy/
```

(The dataset also includes `grayscale/` and `segmented/` folders — you don't
need those, only `color/`.)

## Step 2 — Install training dependencies

```bash
cd ml/disease_detection
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

If you have an NVIDIA GPU and want CUDA acceleration, instead install torch
following the instructions at https://pytorch.org/get-started/locally/
(pick your CUDA version) before installing the rest.

## Step 3 — Verify the dataset is laid out correctly

```bash
python inspect_dataset.py
```

This should print all 38 classes and their image counts. If it can't find
the folder, edit `DATA_DIR` in `config.py` to match your actual path.

## Step 4 — Train

```bash
python train.py
```

- On CPU: expect roughly 15–40 minutes per epoch depending on your machine
  (10 epochs by default — reduce `NUM_EPOCHS` in `config.py` if you want a
  quicker first run, e.g. 3–5 epochs to sanity check things).
- On GPU: a few minutes per epoch.
- You'll see live progress per epoch (loss/accuracy for train + validation).
- The best-performing checkpoint (by validation accuracy) is kept and saved
  at the end, along with a final held-out test accuracy score.

Outputs land in `ml/disease_detection/saved_models/`:
- `disease_model.pt` — trained weights + metadata (architecture, classes, image size)
- `class_names.json` — the 38 class names in order
- `training_history.json` — per-epoch metrics, useful if you want to plot a training curve later

## Step 5 — Quick sanity check (optional but recommended)

Test the model on a single image before wiring it into the backend:

```bash
python predict_sample.py /path/to/some_leaf_image.jpg
```

This prints the top 5 predicted classes with confidence scores.

## Step 6 — Deploy the model into the backend

Copy the trained model file into the backend's artifacts folder:

```bash
# from the project root
cp ml/disease_detection/saved_models/disease_model.pt backend/app/ml/artifacts/disease_model.pt
```

That's it — **no code changes needed**. `backend/app/ml/disease_model.py`
already checks for a file at `DISEASE_MODEL_PATH` (which defaults to
`./app/ml/artifacts/disease_model.pt`) on startup. If found, it loads and
uses the real model automatically. If not found, it silently falls back to
mock predictions, so the API never breaks.

## Step 7 — Restart the backend and test

```bash
cd backend
uvicorn app.main:app --reload
```

Then hit the disease detection endpoint with a real leaf image:

```bash
curl -X POST http://localhost:8000/api/v1/disease-detection/predict \
  -F "file=@/path/to/leaf.jpg" \
  -F "crop_type=tomato"
```

You should now get real predictions instead of random mock scores.

## Tips for better accuracy

- **More epochs**: bump `NUM_EPOCHS` in `config.py` to 15–20 once you've
  confirmed the pipeline works end-to-end.
- **Class imbalance**: some PlantVillage classes have far more images than
  others. If accuracy on rare classes looks weak, consider adding class
  weights to the loss function in `train.py` (`nn.CrossEntropyLoss(weight=...)`).
- **Try ResNet18**: set `ARCHITECTURE = "resnet18"` in `config.py` for
  potentially higher accuracy at the cost of slower training.
- **GPU strongly recommended** if you plan to train many epochs — consider
  Google Colab (free GPU) if you don't have one locally. Just upload the
  `ml/disease_detection/` folder and your dataset there, run the same
  scripts, then download `disease_model.pt` back to your machine.
