#!/bin/bash

# ============================================
# EfficientNet Video Deepfake Detection Training
# ============================================

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "════════════════════════════════════════════════════"
echo "  EfficientNet Video Deepfake Detection Training"
echo "════════════════════════════════════════════════════"

# Parse arguments
MODEL_TYPE="${1:-efficientnet_b0}"
BATCH_SIZE="${2:-32}"
CONFIG_FILE="${3:-config.yaml}"

# Validate model type
if [[ "$MODEL_TYPE" != "efficientnet_b0" && "$MODEL_TYPE" != "efficientnet_b4" ]]; then
    echo "❌ Invalid model type: $MODEL_TYPE"
    echo "   Supported: efficientnet_b0, efficientnet_b4"
    exit 1
fi

echo "🔧 Configuration:"
echo "   Model Type: $MODEL_TYPE"
echo "   Batch Size: $BATCH_SIZE"
echo "   Config File: $CONFIG_FILE"
echo "   Script: train_efficientnet_video.py"

# Check if config exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."
python3 -c "import torch; print(f'   ✓ PyTorch {torch.__version__}')" || {
    echo "   ❌ PyTorch not installed. Installing..."
    pip install torch torchvision
}

python3 -c "import yaml; print('   ✓ PyYAML')" || {
    echo "   ❌ PyYAML not installed. Installing..."
    pip install pyyaml
}

python3 -c "import cv2; print(f'   ✓ OpenCV {cv2.__version__}')" || {
    echo "   ❌ OpenCV not installed. Installing..."
    pip install opencv-python
}

python3 -c "import sklearn; print('   ✓ scikit-learn')" || {
    echo "   ❌ scikit-learn not installed. Installing..."
    pip install scikit-learn
}

# Start training
echo ""
echo "🚀 Starting training..."
echo ""

python3 train_efficientnet_video.py \
    --config "$CONFIG_FILE" \
    --model-type "$MODEL_TYPE" \
    --batch-size "$BATCH_SIZE"

echo ""
echo "✅ Training completed!"
echo "════════════════════════════════════════════════════"
