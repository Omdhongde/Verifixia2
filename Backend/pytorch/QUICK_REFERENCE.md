# ⚡ Training Quick Reference

## 🎬 Video Training with EfficientNet B0/B4

### Dataset Status
- ✅ **100 videos** ready (50 real + 50 fake)  
- ✅ Located in: `DATA/Real Videos/` and `DATA/Fake Vedios/`
- ✅ Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`

---

## 🚀 Quick Start Commands

### Windows PowerShell
```powershell
cd Backend\pytorch
.\train.ps1
```

### Windows (Direct Python)
```powershell
cd Backend\pytorch
python train_efficientnet_video.py --config config.yaml
```

### Linux/Mac
```bash
cd Backend/pytorch
bash run_training.sh
```

---

## ⚙️ Model Options

### EfficientNet B0 (Default)  
```bash
.\train.ps1                              # Auto-selects B0
python train_efficientnet_video.py       # Auto-selects B0
```

### EfficientNet B4 (Better Accuracy)
```bash
.\train.ps1 -ModelType "efficientnet_b4" -BatchSize 16
python train_efficientnet_video.py --model-type efficientnet_b4
```

---

## 📝 Config File (`config.yaml`)

**Quick edits:**

| Setting | Value | To Change |
|---------|-------|-----------|
| Model | `efficientnet_b0` | Change to `efficientnet_b4` |
| Epochs | `30` | Increase for better accuracy |
| Batch Size | `32` | Reduce to 16 if OOM error |
| Frames | `16` | Reduce to 8 for faster training |
| Learning Rate | `0.001` | Reduce to 0.0005 for B4 |

---

## 📊 Expected Results

| Metric | Expected | Excellent |
|--------|----------|-----------|
| **Accuracy** | 70%+ | 85%+ |
| **Precision** | 70%+ | 85%+ |
| **Recall** | 70%+ | 85%+ |
| **F1 Score** | 0.70+ | 0.85+ |
| **AUC** | 0.80+ | 0.90+ |

---

## ⏱️ Training Duration

| Model | Dataset | GPU | CPU |
|-------|---------|-----|-----|
| **B0** | 100 vids | 2-3h | 8-12h |
| **B4** | 100 vids | 4-6h | 16-20h |

---

## 🔍 Monitoring Training

Watch for:
- ✅ Loss decreasing (0.6 → 0.4)
- ✅ Accuracy increasing (55% → 75%+)
- ✅ Val metrics tracking train metrics
- ✅ F1 score above 0.75

Stop if:
- ⚠️ Loss not changing after 5-10 epochs
- ⚠️ GPU memory errors (OOM)
- ⚠️ No improvement after 5+ epochs (early stopping)

---

## ⚙️ GPU Memory Optimization

**If OOM Error:**

```yaml
# In config.yaml, reduce:
batch_size: 16          # From 32
frames_per_video: 8     # From 16
num_workers: 2          # From 4
```

---

## 📂 Output Files

After training:
```
Backend/pytorch/
├── models/
│   └── efficientnet_b0_video.pth      ← Use this in app.py
├── checkpoints/
│   └── training_history_*.json        ← Metrics
└── training_*.log                     ← Full logs
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| "No video samples" | Check `DATA/Real Videos/` folder exists |
| "CUDA out of memory" | Reduce batch_size, frames_per_video |
| "Frame extraction failed" | Convert videos to MP4 |
| "Very slow training" | Reduce num_workers, use B0 model |
| "Training stuck" | Reduce learning_rate to 0.0005 |

---

## 📚 Detailed Guides

- **Full Training Guide:** [TRAINING_GUIDE.md](./TRAINING_GUIDE.md)
- **Complete Setup Info:** [SETUP_COMPLETE.md](./SETUP_COMPLETE.md)
- **Setup Verification:** `python verify_setup.py`

---

## 🎯 Next: Integration

Once training completes:

1. **Model saved to:** `models/efficientnet_b0_video.pth`
2. **Update Backend/app.py** to load new model
3. **Test with:** `curl -X POST -F "file=@video.mp4" http://localhost:3001/api/upload`
4. **Expected response:**
```json
{
  "prediction": "Fake",
  "confidence": 85.23,
  "threat_level": "high",
  "model_used": "EfficientNet B0 + LSTM"
}
```

---

## 🆘 Help Commands

```bash
# Verify setup
python verify_setup.py

# View detailed logs
type training_*.log

# Check model size
ls -lh models/efficientnet_b0_video.pth

# Count videos
dir DATA\Real
dir DATA\Fake
```

---

**Status:** ✅ Ready to Train  
**Dataset:** 100 videos (50 real, 50 fake)  
**Run:** `.\train.ps1` (Windows) or `bash run_training.sh` (Linux)  
**Duration:** 2-6 hours depending on GPU
