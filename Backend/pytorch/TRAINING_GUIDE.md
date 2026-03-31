# 🎬 EfficientNet Video Deepfake Detection - Training Guide

## Overview

This training pipeline uses **EfficientNet B0/B4** with **LSTM temporal modeling** for video-based deepfake detection. The system extracts frames from videos and uses bidirectional LSTM to aggregate temporal information.

## ✨ Features

- ✅ **EfficientNet-based architecture** (B0 or B4 models)
- ✅ **Automatic video frame extraction** - extracts 16 evenly-spaced frames per video
- ✅ **Temporal LSTM modeling** - bidirectional LSTM captures temporal patterns
- ✅ **Advanced augmentation** - ColorJitter, Rotation, Horizontal Flip
- ✅ **Cosine annealing scheduler** - smooth learning rate decay
- ✅ **Early stopping** - prevents overfitting with configurable patience
- ✅ **Comprehensive metrics** - Accuracy, Precision, Recall, F1, AUC
- ✅ **Training history** - JSON logs for analysis
- ✅ **Cross-platform** - Works on Windows (PowerShell), Linux/Mac (Bash)

## 📁 Expected Dataset Structure

```
DATA/
├── Real Videos/
│   ├── real_video_1.mp4
│   ├── real_video_2.avi
│   └── ...
└── Fake Vedios/  (or "Fake Videos")
    ├── fake_video_1.mp4
    ├── fake_video_2.mp4
    └── ...
```

**Supported video formats:** `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

## 🚀 Quick Start

### Prerequisites

```bash
# Install PyTorch (CPU or GPU version)
pip install torch torchvision

# Install other dependencies
pip install opencv-python pyyaml scikit-learn tqdm numpy Pillow
```

### On Windows (PowerShell)

```powershell
# Navigate to training directory
cd Backend/pytorch

# Run with EfficientNet B0 (default)
.\train.ps1

# Or with EfficientNet B4
.\train.ps1 -ModelType "efficientnet_b4" -BatchSize 16
```

### On Linux/Mac (Bash)

```bash
# Navigate to training directory
cd Backend/pytorch

# Run with EfficientNet B0 (default)
bash run_training.sh

# Or with EfficientNet B4
bash run_training.sh efficientnet_b4 16 config.yaml
```

### Command-Line Options

```bash
# Python direct invocation
python train_efficientnet_video.py \
    --config config.yaml \
    --model-type efficientnet_b0 \
    --batch-size 32
```

## 📋 Configuration (config.yaml)

Key settings you can customize:

```yaml
# Model selection
model_type: "efficientnet_b0"  # or "efficientnet_b4"
pretrained: true               # Use ImageNet weights

# Training parameters
num_epochs: 30
batch_size: 32
learning_rate: 0.001
weight_decay: 1e-4

# Video extraction
frames_per_video: 16           # Frames per video
video_extensions: ['.mp4', '.avi', '.mov', '.mkv', '.webm']

# Augmentation
augmentation:
  random_horizontal_flip: true
  random_rotation: 15
  color_jitter: true
  color_brightness: 0.2
  color_contrast: 0.2

# Learning rate schedule
scheduler: "cosine"            # "cosine", "step", or "linear"

# Early stopping
early_stopping_patience: 5
```

## 📊 Model Architecture

### Backbone
- **EfficientNet B0:** 1.2M parameters, 224x224 input
- **EfficientNet B4:** 19M parameters, 384x384 input
- Both pretrained on ImageNet

### Temporal Module
```
Input: (Batch, 16, 3, 384, 384)  # 16 frames per video
  ↓
EfficientNet (frame-wise feature extraction)
  ↓
Features: (Batch, 16, 1280 or 1792)  # 1280 for B0, 1792 for B4
  ↓
Bidirectional LSTM (2 layers, 512 hidden dim)
  ↓
Dense Head: LSTM output → 256 → sigmoid
  ↓
Output: Binary classification (Real=0, Fake=1)
```

## 📈 Training Output

During training, you'll see:

```
Training Loss: 0.5234, Train Acc: 0.7812
Val Loss: 0.4891, Val Acc: 0.8234, Precision: 0.8156, Recall: 0.8120, F1: 0.8138, AUC: 0.8945
✓ Best model saved: ../../models/efficientnet_b0_video.pth (F1: 0.8138)
```

### Output Files

1. **Model Checkpoint:** `models/efficientnet_b0_video.pth` (or efficientnet_b4)
2. **Training Log:** `training_YYYYMMDD_HHMMSS.log`
3. **Training History:** `checkpoints/training_history_YYYYMMDD_HHMMSS.json`

## 🎯 Performance Tips

### For Faster Training (EfficientNet B0)
- Batch size: 32-64
- Frames per video: 8-12
- Image size: 224-256
- Epochs: 20-25

### For Better Accuracy (EfficientNet B4)
- Batch size: 16-32
- Frames per video: 16-20
- Image size: 384
- Epochs: 25-35
- Lower learning rate: 0.0005

### GPU Optimization
```python
# Enable mixed precision training (uncomment in train_efficientnet_video.py)
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

# Use in training loop:
with autocast():
    outputs = model(frames)
    loss = criterion(outputs, labels)
```

## 🔧 Troubleshooting

### "No video samples found"
- Check that `DATA/Real Videos/` and `DATA/Fake Videos/` (or `Fake Vedios/`) folders exist
- Ensure videos have correct extensions (.mp4, .avi, etc.)

### "Could not open video"
- Videos might be corrupted
- Check video codec compatibility with OpenCV
- Try converting videos to `.mp4` (H.264 codec)

### Out of Memory (OOM)
- Reduce batch size: `--batch-size 16`
- Reduce frames per video: Edit `config.yaml` → `frames_per_video: 8`
- Use EfficientNet B0 instead of B4

### Training too slow
- Reduce number of workers: Edit `config.yaml` → `num_workers: 2`
- Reduce frames per video
- Use a GPU: PyTorch will auto-detect CUDA

## 📝 Integration with Frontend

After training, the model is saved to:
```
models/efficientnet_b0_video.pth  (or efficientnet_b4_video.pth)
```

Update `Backend/app.py` to load the new model:

```python
# In app.py
model_path = os.path.join("models", "efficientnet_b0_video.pth")

# Load with:
model = EfficientNetVideoModel(model_type="efficientnet_b0")
model.load_state_dict(torch.load(model_path, map_location=DEVICE))
model.eval()
```

Then update the prediction endpoint to handle 16-frame sequences.

## 📚 References

- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [PyTorch EfficientNet Docs](https://pytorch.org/vision/main/models/efficientnet.html)
- [Understanding LSTM](https://colah.github.io/posts/2015-08-Understanding-LSTMs/)

## 🤝 Support

For issues:
1. Check the training log file
2. Verify dataset structure and video formats
3. Try reducing batch size or frames per video
4. Check GPU memory with `nvidia-smi` (if using CUDA)

---

**Last Updated:** March 21, 2026
**Version:** 2.0 (EfficientNet + Video)
