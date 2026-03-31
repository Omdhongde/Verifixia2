# Scripts Directory Guide

## 📂 Organization Structure

This directory contains utility scripts organized by functionality and purpose. Each script is classified and documented for easy navigation.

```
scripts/
├── README.md                                          ← You are here
├── data_utils/                                        ← Dataset acquisition & preprocessing
│   ├── download_deepfake_dataset.py                 [ACTIVE] Download deepfake data from HuggingFace
│   └── inspect_huggingface_datasets.py              [DISCOVERY] Explore available datasets
├── model_utils/                                       ← Model management & deployment
│   ├── download_pretrained_deepfake_models.py      [DEPLOYMENT] Download trained weights
│   └── validate_model_file_integrity.py             [TESTING] Validate model functionality
└── training/                                          ← Training scripts
    └── train_sklearn_ensemble_detector.py           [TRAINING] Baseline sklearn trainer
```

---

## 🎯 Quick Reference

### Data Management (`data_utils/`)

#### **download_deepfake_dataset.py** — Download Training Data
- **Classification:** DATA UTILITY - Dataset Downloader
- **Status:** ✅ Active
- **Purpose:** Fetch deepfake detection images from HuggingFace Hub
- **Command:**
  ```bash
  python scripts/data_utils/download_deepfake_dataset.py --real 500 --fake 500
  ```
- **Output:** Populates `DATA/Real/` and `DATA/Fake/` directories

#### **inspect_huggingface_datasets.py** — Explore Available Datasets
- **Classification:** DATA UTILITY - Dataset Inspector
- **Status:** ℹ️ Informational / Discovery
- **Purpose:** List and inspect available deepfake datasets
- **Command:**
  ```bash
  python scripts/data_utils/inspect_huggingface_datasets.py
  ```
- **Use Case:** Research, finding new data sources, understanding dataset structure

---

### Model Management (`model_utils/`)

#### **download_pretrained_deepfake_models.py** — Get Pre-trained Weights
- **Classification:** MODEL UTILITY - Pretrained Model Downloader
- **Status:** ⚠️ Deployment Critical
- **Purpose:** Download trained model weights for production
- **Command:**
  ```bash
  python scripts/model_utils/download_pretrained_deepfake_models.py \
    --pytorch-url https://example.com/model.pth \
    --sklearn-url https://example.com/model.pkl
  ```
- **Output:** Saves to `models/` directory
- **Use Case:** CI/CD pipelines, production deployment

#### **validate_model_file_integrity.py** — Test Model Functionality
- **Classification:** MODEL UTILITY - Model Verification
- **Status:** ✅ Active (Pre-deployment)
- **Purpose:** Validate models load correctly and can make predictions
- **Command:**
  ```bash
  python scripts/model_utils/validate_model_file_integrity.py /path/to/test/image.jpg
  ```
- **Use Case:** Deployment verification, troubleshooting

---

### Training (`training/`)

#### **train_sklearn_ensemble_detector.py** — Scikit-learn Baseline Training
- **Classification:** TRAINING SCRIPT - Baseline Trainer
- **Status:** ✅ Active (Alternative)
- **Purpose:** Train lightweight ensemble model (SVM + GradientBoosting)
- **Features:**
  - CPU-only, no GPU required
  - Hand-crafted features (HOG, DCT, color histograms, LBP)
  - Python 3.13/3.14 compatible
  - Fast baseline for comparison
- **Command:**
  ```bash
  python scripts/training/train_sklearn.py --n_aug 5
  ```
- **Output:** `models/deepfake_sklearn.pkl`
- **Use Case:** Quick prototyping, resource-constrained environments, baseline comparison

---

### Primary Training Scripts (Backend Only)

These scripts are in the main training directories and NOT in `scripts/`:

| Script | Location | Purpose |
|--------|----------|---------|
| **train_efficientnet_video.py** | `Backend/pytorch/` | PRIMARY video trainer with frame extraction |
| **train_huggingface_transformer.py** | `Backend/pytorch/` | HuggingFace transformer baseline |

See [Backend/pytorch/TRAINING_SCRIPTS_GUIDE.md](../Backend/pytorch/TRAINING_SCRIPTS_GUIDE.md) for details.

---

## 🔄 Common Workflows

### Setup New Training Environment
```bash
# 1. Download dataset
python scripts/data_utils/download_deepfake_dataset.py --real 1000 --fake 1000

# 2. Train baseline model quickly
python scripts/training/train_sklearn_ensemble_detector.py --n_aug 3

# 3. Verify model works
python scripts/model_utils/validate_model_file_integrity.py DATA/Real/sample.jpg
```

### Prepare for Deployment
```bash
# 1. Download pre-trained production models
python scripts/model_utils/download_pretrained_deepfake_models.py \
  --pytorch-url https://releases.example.com/model.pth \
  --sklearn-url https://releases.example.com/model.pkl

# 2. Verify everything works
python scripts/model_utils/verify_model.py test_image.jpg
```

### Explore Dataset Options
```bash
python scripts/data_utils/inspect_huggingface_datasets.py
```

---

## 📋 Classification Legend

| Label | Meaning | Active |
|-------|---------|--------|
| ✅ ACTIVE | In regular use | Yes |
| ⚠️ DEPLOYMENT CRITICAL | Required for production | Yes |
| ℹ️ INFORMATIONAL | Useful but optional | Yes |
| 🗑️ DEPRECATED | Legacy, use alternative | No |

---

## 🧹 Maintenance Notes

### Deleted/Consolidated Files
- ~~`download_data.py`~~ → Use `data_utils/download_dataset.py` instead
- ~~`find_real_data.py`~~ → Use `data_utils/inspect_huggingface_datasets.py` instead
- ~~`train.py`~~ → Use `Backend/pytorch/train_efficientnet_video.py` instead
- ~~`train_improved.py`~~ → Obsolete intermediate version

### Path Changes
- `download_dataset.py` moved to `data_utils/`
- `inspect_huggingface_datasets.py` moved to `data_utils/`
- `train_sklearn.py` moved to `training/`
- Model utilities moved to `model_utils/`

All import paths have been updated to reflect new locations.

---

## 🔧 Adding New Scripts

When adding new utility scripts:

1. **Choose the right category:**
   - `data_utils/` — Data downloading, inspection, preprocessing
   - `model_utils/` — Model management, validation, deployment
   - `training/` — Model training scripts

2. **Add classification header:**
   ```python
   """
   ================================================================================
   CLASSIFICATION: [CATEGORY] - [Script Name]
   ================================================================================
   TYPE:        [Type of script]
   PURPOSE:     [What it does]
   CATEGORY:    [Category]
   STATUS:      [Active/Inactive]
   DEPENDENCIES: [Required packages]
   
   DESCRIPTION:
   [Detailed description]
   
   USAGE:
   [How to run]
   
   ================================================================================
   """
   ```

3. **Update this README** with the new script details

---

## 📚 Additional Resources

- [Backend Training Guide](../Backend/pytorch/TRAINING_SCRIPTS_GUIDE.md)
- [Project Cleanup Summary](../CLEANUP_SUMMARY.md)
- [Main README](../README.md)
