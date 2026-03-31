# Training Scripts

Model training and baseline development scripts.

## Scripts

### `train_sklearn_ensemble_detector.py`
**Purpose:** Train lightweight scikit-learn baseline model

Trains an ensemble model (SVM + GradientBoosting) using hand-crafted image features. Useful for quick prototyping and baseline comparison without requiring GPU or deep learning frameworks.

**Features:**
- CPU-only training (no GPU needed)
- Hand-crafted features: HOG, DCT, color histograms, LBP, statistics
- Python 3.13/3.14 compatible
- Supports data augmentation
- Fast training on modest hardware

**Usage:**
```bash
# Default training (3 augmentations per image)
python train_sklearn_ensemble_detector.py

# Faster training with fewer augmentations
python train_sklearn_ensemble_detector.py --n_aug 1

# Better model with more augmentations
python train_sklearn.py --n_aug 10

# Custom data directory
python train_sklearn.py --data_dir MY_DATA --n_aug 5
```

**Arguments:**
```
--n_aug N         Number of augmentations per image (default: 3)
--data_dir PATH   Path to DATA directory (default: DATA)
```

**Output:** `models/deepfake_sklearn.pkl`

**Expected Runtime:** 5-15 minutes depending on augmentation count

---

## When to Use

✅ **Use this script for:**
- Quick prototyping and validation
- Baseline comparison metric
- Resource-constrained environments (no GPU available)
- Feature engineering experiments
- CI/testing pipelines

❌ **Don't use for:**
- Production deepfake detection (use PyTorch models)
- Video data processing (image-only)
- Cutting-edge performance requirements

---

## Feature Engineering

The model extracts multiple feature groups:

1. **HOG (Histogram of Oriented Gradients)**
   - Captures edge patterns
   - Uses scikit-image if available, falls back to NumPy

2. **Color Histograms**
   - RGB and LAB color spaces
   - Multiple scales

3. **DCT Features**
   - Frequency-domain analysis
   - Top 128 coefficients

4. **Statistical Moments**
   - Per-channel: mean, std, skew, kurtosis

5. **Texture Features**
   - LBP-lite (Local Binary Patterns)
   - Pixel difference patterns

---

## Data Requirements

Expected directory structure:
```
DATA/
├── Real/
│   ├── real_image_1.jpg
│   ├── real_image_2.jpg
│   └── ...
└── Fake/
    ├── fake_image_1.jpg
    ├── fake_image_2.jpg
    └── ...
```

See `scripts/data_utils/download_dataset.py` to fetch data.

---

## Output & Evaluation

The trained model is saved as a pickle file: `models/deepfake_sklearn.pkl`

Training also outputs:
- Accuracy, precision, recall, F1-score
- ROC-AUC score
- Confusion matrix
- Training time

---

## Notes

- Deterministic training (seed = 42)
- Data augmentation includes: rotation, zoom, flip, brightness, contrast
- Works on Python 3.8+
- Dependencies: scikit-learn, numpy, PIL
- Optional: scikit-image (for faster HOG, otherwise uses NumPy fallback)

## See Also

- **PyTorch trainers:** See `Backend/pytorch/TRAINING_SCRIPTS_GUIDE.md`
- **Data utilities:** See `scripts/data_utils/README.md`
- **Model verification:** See `scripts/model_utils/verify_model.py`
