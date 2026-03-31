# Training Scripts Reference Guide

## Quick Start

### 1. **Video-based Training (Recommended PRIMARY)**
```bash
# Linux/Mac
cd Backend/pytorch
bash run_training.sh

# Windows PowerShell
cd Backend/pytorch
./initialize_training_environment.ps1
```
**What it does:** Extracts frames from video files, trains EfficientNet model
**Config:** `Backend/pytorch/efficientnet_video_training_config.yaml`
**Script:** `Backend/pytorch/train_efficientnet_video.py`

---

### 2. **HuggingFace Transformer Model (Alternative)**
```bash
python Backend/pytorch/train_huggingface_transformer.py
```
**What it does:** Fine-tunes pre-trained Deep-Fake-Detector-v2 from HuggingFace
**Use case:** When you want a transformer-based approach
**Config:** Built-in (see script for parameters)

---

### 3. **Scikit-learn Baseline (CPU-only, Lightweight)**
```bash
python scripts/training/train_sklearn_ensemble_detector.py
```
**What it does:** Trains SVM + GradientBoosting with manual feature extraction (HOG, DCT, LBP)
**Use case:** Quick testing, CPU environments, baseline comparison
**Requirements:** No GPU needed, sklearn + cv2

---

## Configuration

### Main Config File
- **Location:** `Backend/pytorch/efficientnet_video_training_config.yaml`
- **Used by:** `train_efficientnet_video.py`
- **Key settings:**
  - `epochs`: Number of training epochs (default: 50)
  - `batch_size`: Batch size (default: 4)
  - `learning_rate`: Learning rate (default: 1e-4)
  - `frames_per_video`: Frames extracted per video (default: 8)
  - `model_type`: EfficientNet version (b0 or b4)

### Quick Test Config
- **Location:** `Backend/pytorch/efficientnet_video_test_config.yaml`
- **Purpose:** Fast validation/CI testing (1 epoch)
- **Used by:** CI/CD pipelines

---

## Dataset Structure Expected

```
DATA/
├── Real/          # Real videos/images (label: 0)
│   ├── video1.mp4
│   ├── video2.mp4
│   └── image1.jpg
├── Fake/          # Fake/deepfake videos/images (label: 1)
│   ├── deepfake1.mp4
│   ├── deepfake2.mp4
│   └── fake_image.jpg
```

---

## Output Locations

| Item | Location |
|------|----------|
| Trained Model | `models/efficientnet_b0_video.pth` or similar |
| Training Logs | `Backend/pytorch/training_YYYYMMDD_HHMMSS.log` |
| Checkpoints | `checkpoints/` directory |

---

## Removed/Consolidated Files

**These scripts were redundant and have been removed:**
- ~~`scripts/train.py`~~ → Use `Backend/pytorch/train_efficientnet_video.py` instead
- ~~`Backend/pytorch/train_improved.py`~~ → Obsolete version

---

## Notes
- All cache files (`.pyc`, `__pycache__`) have been cleaned
- Old training logs and checkpoint histories removed to save space
- macOS system files (`.DS_Store`) removed
- Use the training script that matches your workflow and data format

For data download and model setup, see:
- Download data: `scripts/download_data.py`, `scripts/download_more_data.py`
- Download pretrained models: `scripts/download_pretrained_models.py`
- Verify model: `scripts/verify_model.py`
