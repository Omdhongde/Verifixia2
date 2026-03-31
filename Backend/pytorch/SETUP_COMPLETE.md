# 🎬 Training Setup Complete - Summary & Quick Start Guide

## ✅ Setup Status

| Component | Status | Details |
|-----------|--------|---------|
| **Dataset** | ✅ Ready | 100 videos (50 real, 50 fake) |
| **Python Version** | ✅ OK | Python 3.12.3 |
| **Configuration** | ✅ Ready | EfficientNet B0 + LSTM |
| **Model Type** | ✅ Ready | Video-based deepfake detector |
| **Frame Extraction** | ✅ Ready | 16 frames per video |

## 📊 Dataset Distribution

```
Total Videos: 100
├── Real Videos/        50 videos
├── Fake Vedios/        50 videos
│
Split:
├── Training (80%)      80 videos
├── Validation (10%)    10 videos
└── Testing (10%)       10 videos
```

## 🚀 Start Training (3 Steps)

### Step 1: Install Dependencies (One Time Only)

**Windows (PowerShell):**
```powershell
pip install torch torchvision opencv-python pillow numpy scikit-learn tqdm
```

**Linux/Mac (Bash):**
```bash
pip install torch torchvision opencv-python pillow numpy scikit-learn tqdm
```

Alternatively, if you already have the packages from the installation done earlier, you're good to go!

### Step 2: Navigate to Training Directory

**Windows:**
```powershell
cd Backend/pytorch
```

**Linux/Mac:**
```bash
cd Backend/pytorch
```

### Step 3: Start Training

#### Option A: Windows PowerShell (Recommended for Windows)
```powershell
# Run with default settings (EfficientNet B0, Batch Size 32, 30 epochs)
.\train.ps1

# Or customize parameters
.\train.ps1 -ModelType "efficientnet_b4" -BatchSize 16
```

#### Option B: Linux/Mac Bash
```bash
# Run with default settings
bash run_training.sh

# Or customize parameters
bash run_training.sh efficientnet_b4 16 config.yaml
```

#### Option C: Direct Python (Any Platform)
```bash
python train_efficientnet_video.py \
    --config config.yaml \
    --model-type efficientnet_b0 \
    --batch-size 32
```

## 📋 Configuration Summary

### File: `config.yaml`

```yaml
# Model Selection (Choose one)
model_type: "efficientnet_b0"     # Faster, smaller (~1.2M params)
# model_type: "efficientnet_b4"   # Better accuracy, larger (~19M params)

# Training Parameters
batch_size: 32                    # Reduce to 16-24 for GPU memory issues
learning_rate: 0.001             # Default learning rate
num_epochs: 30                    # Number of training epochs
weight_decay: 1e-4                # L2 regularization

# Video Processing
frames_per_video: 16              # Frames extracted from each video
video_extensions: ['.mp4', '.avi', '.mov', '.mkv', '.webm']

# Optimization
optimizer: "adamw"                # AdamW optimizer
scheduler: "cosine"               # Cosine annealing schedule
early_stopping_patience: 5        # Stop if no improvement for 5 epochs

# Augmentation
augmentation:
  random_horizontal_flip: true    # Flip images left-right
  random_rotation: 15             # Random rotation ±15°
  color_jitter: true              # Brightness/contrast variation
  color_brightness: 0.2
  color_contrast: 0.2
```

## 📈 What to Expect

### Training Output Example
```
Epoch 1/30
Training Loss: 0.6234, Train Acc: 0.6234
Val Loss: 0.5891, Val Acc: 0.6234, Precision: 0.6156, Recall: 0.6120, F1: 0.6138, AUC: 0.6945
✓ Best model saved: models/efficientnet_b0_video.pth

Epoch 2/30
Training Loss: 0.5234, Train Acc: 0.7812
...
```

### Training Duration
- **EfficientNet B0** (32 batch): ~2-3 hours per 30 epochs (on GTX 1080 Ti)
- **EfficientNet B4** (16 batch): ~4-6 hours per 30 epochs

### Output Files
Generated after training:
```
Backend/pytorch/
├── models/
│   └── efficientnet_b0_video.pth          ← Trained model
├── checkpoints/
│   └── training_history_20260321_143022.json
└── training_20260321_143022.log            ← Training log
```

## 🔧 Model Architecture

### EfficientNet B0
- **Input:** 16 frames of 384×384 RGB video
- **Backbone:** EfficientNet B0 (ImageNet pretrained)
- **Feature Extraction:** Frame-wise CNN feature extraction
- **Temporal Modeling:** 2-layer Bidirectional LSTM (512 hidden units)
- **Classification:** Dense head (256 → 1 output)
- **Output:** Binary classification (0=Real, 1=Fake)

### EfficientNet B4
- Same architecture as B0 but with larger capacity
- Better accuracy but slower training/inference
- 1792-dim feature extraction vs 1280 for B0

## ⚡ Performance Tuning

### For Faster Training (Limited GPU Memory)
```yaml
model_type: "efficientnet_b0"
batch_size: 24                    # Reduce from 32
frames_per_video: 8               # Reduce from 16
num_epochs: 20                    # Reduce from 30
```

### For Better Accuracy
```yaml
model_type: "efficientnet_b4"
batch_size: 16
frames_per_video: 20
num_epochs: 40
learning_rate: 0.0005
weight_decay: 5e-4
```

### For CPU-Only Training
```yaml
batch_size: 8
num_workers: 0                    # Disable parallel data loading
```

## 📺 Training Process Details

### Phase 1: Data Loading
- Discovers all .mp4, .avi, .mov, .mkv, .webm files in `Real Videos/` and `Fake Vedios/`
- Splits into 80% training, 10% validation, 10% testing
- No additional data needs to be downloaded

### Phase 2: Frame Extraction
- Extracts 16 evenly-spaced frames from each video
- Resizes to 384×384 pixels
- Applies augmentation (ColorJitter, Rotation, Horizontal Flip)
- Normalizes with ImageNet statistics

### Phase 3: Training Loop
- Forward pass through EfficientNet + LSTM
- Binary cross-entropy loss computation
- Backward pass with gradient clipping
- Adam/AdamW optimization
- Learning rate scheduling (cosine annealing)

### Phase 4: Validation
- Evaluates on validation split
- Computes metrics: Accuracy, Precision, Recall, F1, AUC
- Saves best model based on F1 score
- Early stopping if no improvement

## 🎯 Success Indicators

Good training shows:
- ✅ Decreasing loss (0.68 → 0.45 over first few epochs)
- ✅ Increasing accuracy (55% → 75%+)
- ✅ Validation metrics tracking training metrics
- ✅ F1 score above 0.75
- ✅ No early stopping triggered

Warning signs:
- ⚠️ Loss not decreasing → Learning rate too high or too low
- ⚠️ Constant accuracy → Model memorizing or stuck
- ⚠️ Early stopping after 5 epochs → Increase num_epochs or reduce regularization

## 🐛 Troubleshooting

### Issue: "No video samples found"
**Solution:** Check that `DATA/Real Videos/` and `DATA/Fake Vedios/` (or `Fake Videos/`) exist and contain video files

### Issue: "CUDA out of memory"
**Solution:** Reduce batch_size or frames_per_video in config.yaml
```yaml
batch_size: 16  # Was 32
frames_per_video: 8  # Was 16
```

### Issue: "Frame extraction failed"
**Solution:** Some video formats may not work with OpenCV. Convert to MP4:
```bash
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
```

### Issue: Training is very slow
**Solution:** 
- Check if GPU is being used: `nvidia-smi` (NVIDIA) or `rocm-smi` (AMD)
- Reduce num_workers in config.yaml
- Use EfficientNet B0 instead of B4
- Reduce frames_per_video

## 📊 Integration with Inference

After training, update `Backend/app.py` to use the new model:

```python
# In Backend/app.py
from Backend.pytorch.train_efficientnet_video import EfficientNetVideoModel

# Load trained model
model = EfficientNetVideoModel(model_type="efficientnet_b0")
checkpoint = torch.load("models/efficientnet_b0_video.pth")
model.load_state_dict(checkpoint)
model.eval()

# For inference on 16-frame video sequences
with torch.no_grad():
    output = model(frames_tensor)  # Shape: (1, 16, 3, 384, 384)
    confidence = output.item()     # Get probability (0-1)
```

## 📚 Additional Resources

- **Training Guide:** [TRAINING_GUIDE.md](./TRAINING_GUIDE.md)
- **Setup Verification:** `python verify_setup.py`
- **PyTorch Docs:** https://pytorch.org/
- **EfficientNet Paper:** https://arxiv.org/abs/1905.11946
- **LSTM Tutorial:** https://colah.github.io/posts/2015-08-Understanding-LSTMs/

## ✨ Next Steps

1. **Verify setup:** `python verify_setup.py`
2. **Review config:** Check `config.yaml` for your desired settings
3. **Start training:** Run `.\train.ps1` (Windows) or `bash run_training.sh` (Linux)
4. **Monitor progress:** Watch the console output for loss/accuracy
5. **Evaluate results:** Check `training_history_*.json` for detailed metrics
6. **Integrate model:** Update `Backend/app.py` with the new model path

## 🎉 You're All Set!

Everything is configured and ready to train. Your dataset of **100 videos** is perfect for initial training. Simply run the training command above to get started!

**Questions?** Check `TRAINING_GUIDE.md` for detailed documentation.

---
**Setup Date:** March 21, 2026  
**Dataset:** 100 videos (50 real, 50 fake)  
**Model:** EfficientNet B0 + Bidirectional LSTM  
**Status:** ✅ Ready for Training
