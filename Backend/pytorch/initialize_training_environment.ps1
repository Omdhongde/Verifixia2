# ============================================
# EfficientNet Video Deepfake Detection Training
# PowerShell Script for Windows
# ============================================

# Parameters
param(
    [string]$ModelType = "efficientnet_b0",
    [int]$BatchSize = 32,
    [string]$ConfigFile = "config.yaml"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  EfficientNet Video Deepfake Detection Training" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Validate model type
$ValidModels = @("efficientnet_b0", "efficientnet_b4")
if ($ModelType -notin $ValidModels) {
    Write-Host "❌ Invalid model type: $ModelType" -ForegroundColor Red
    Write-Host "   Supported: efficientnet_b0, efficientnet_b4" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Configuration:" -ForegroundColor Green
Write-Host "   Model Type: $ModelType" -ForegroundColor Green
Write-Host "   Batch Size: $BatchSize" -ForegroundColor Green
Write-Host "   Config File: $ConfigFile" -ForegroundColor Green
Write-Host "   Script: train_efficientnet_video.py" -ForegroundColor Green
Write-Host ""

# Check if config exists
if (-not (Test-Path $ConfigFile)) {
    Write-Host "❌ Config file not found: $ConfigFile" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
Write-Host ""

try {
    $Version = python -c "import torch; print(torch.__version__)"
    Write-Host "   ✓ PyTorch $Version" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Installing PyTorch..." -ForegroundColor Yellow
    pip install torch torchvision
}

try {
    python -c "import yaml"
    Write-Host "   ✓ PyYAML" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Installing PyYAML..." -ForegroundColor Yellow
    pip install pyyaml
}

try {
    $Version = python -c "import cv2; print(cv2.__version__)"
    Write-Host "   ✓ OpenCV $Version" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Installing OpenCV..." -ForegroundColor Yellow
    pip install opencv-python
}

try {
    python -c "import sklearn"
    Write-Host "   ✓ scikit-learn" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Installing scikit-learn..." -ForegroundColor Yellow
    pip install scikit-learn
}

# Start training
Write-Host ""
Write-Host "🚀 Starting training..." -ForegroundColor Cyan
Write-Host ""

python train_efficientnet_video.py `
    --config $ConfigFile `
    --model-type $ModelType `
    --batch-size $BatchSize

Write-Host ""
Write-Host "✅ Training completed!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
