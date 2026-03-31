# Model Utilities

Scripts for model deployment, management, and validation.

## Scripts

### `download_pretrained_deepfake_models.py`
**Purpose:** Download pre-trained model weights for deployment

Fetches PyTorch and scikit-learn model weights from specified URLs and saves them in the `models/` directory. Designed for CI/deployment pipelines.

**Usage:**
```bash
# Download both PyTorch and scikit-learn models
python download_pretrained_deepfake_models.py \
  --pytorch-url https://example.com/xception_deepfake.pth \
  --sklearn-url https://example.com/deepfake_sklearn.pkl

# Download only PyTorch model
python download_pretrained_models.py \
  --pytorch-url https://example.com/xception_deepfake.pth
```

**Output:** Saves to `models/` directory

**Environment Variables:**
- `MODEL_URL` — PyTorch model URL
- `SKLEARN_URL` — scikit-learn model URL

---

### `validate_model_file_integrity.py`
**Purpose:** Validate models are functional

Quick diagnostic to check if models can be loaded and make predictions. Useful before deployment.

**Usage:**
```bash
# Test with a sample image
python validate_model_file_integrity.py /path/to/test/image.jpg
```

**Output:** Shows which models are available and prediction result

**Exit Codes:**
- `0` — Success
- `1` — File not found or error

---

## Deployment Checklist

- [ ] Models downloaded with `download_pretrained_models.py`
- [ ] Models verified with `verify_model.py`
- [ ] Backend dependencies installed
- [ ] API endpoints tested

---

## Notes

- Both scripts are production-safe
- Models are downloaded to memory efficiently with streaming
- Path relative to script location is handled automatically
