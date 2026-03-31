#!/usr/bin/env python3
"""
Quick verification script for training setup
Checks dataset, dependencies, and model configuration
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Warning: Python 3.8+ recommended")
        return False
    print("✓ Python version OK")
    return True

def check_dependencies():
    """Check required packages"""
    print_header("Dependencies")
    
    dependencies = {
        'torch': 'PyTorch',
        'torchvision': 'torchvision',
        'cv2': 'OpenCV',
        'yaml': 'PyYAML',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'sklearn': 'scikit-learn',
        'tqdm': 'tqdm'
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'installed')
            print(f"✓ {name:<20} {version}")
        except ImportError:
            print(f"✗ {name:<20} NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install torch torchvision opencv-python pyyaml pillow numpy scikit-learn tqdm")
        return False
    
    print("\n✓ All dependencies installed")
    return True

def check_dataset():
    """Check dataset structure"""
    print_header("Dataset Structure")
    
    data_dir = Path("../../DATA")
    
    if not data_dir.exists():
        print(f"✗ Dataset directory not found: {data_dir.resolve()}")
        return False
    
    print(f"✓ Found DATA directory: {data_dir.resolve()}")
    
    real_videos = data_dir / "Real Videos"
    fake_videos1 = data_dir / "Fake Vedios"  # Original spelling
    fake_videos2 = data_dir / "Fake Videos"  # Correct spelling
    
    real_count = 0
    fake_count = 0
    
    if real_videos.exists():
        videos = [f for f in real_videos.iterdir() if f.suffix.lower() in 
                 ['.mp4', '.avi', '.mov', '.mkv', '.webm']]
        real_count = len(videos)
        print(f"✓ Real Videos/: {real_count} videos")
    else:
        print(f"✗ Real Videos/ not found")
    
    if fake_videos1.exists():
        videos = [f for f in fake_videos1.iterdir() if f.suffix.lower() in 
                 ['.mp4', '.avi', '.mov', '.mkv', '.webm']]
        fake_count = len(videos)
        print(f"✓ Fake Vedios/: {fake_count} videos")
    elif fake_videos2.exists():
        videos = [f for f in fake_videos2.iterdir() if f.suffix.lower() in 
                 ['.mp4', '.avi', '.mov', '.mkv', '.webm']]
        fake_count = len(videos)
        print(f"✓ Fake Videos/: {fake_count} videos")
    else:
        print(f"✗ Fake Vedios/ or Fake Videos/ not found")
    
    total = real_count + fake_count
    if total == 0:
        print("\n⚠️  No videos found in dataset!")
        return False
    
    print(f"\n✓ Total videos: {total} ({real_count} real, {fake_count} fake)")
    
    # Split statistics
    print(f"\nExpected split:")
    print(f"  Training (80%):   {int(total * 0.8)} videos")
    print(f"  Validation (10%): {int(total * 0.1)} videos")
    print(f"  Testing (10%):    {int(total * 0.1)} videos")
    
    return total > 0

def check_config():
    """Check configuration file"""
    print_header("Configuration")
    
    config_file = Path("efficientnet_video_training_config.yaml")
    
    if not config_file.exists():
        print(f"✗ efficientnet_video_training_config.yaml not found")
        return False
    
    print(f"✓ efficientnet_video_training_config.yaml found")
    
    try:
        import yaml
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"\nKey settings:")
        print(f"  Model type:        {config.get('model_type', 'N/A')}")
        print(f"  Batch size:        {config.get('batch_size', 'N/A')}")
        print(f"  Learning rate:     {config.get('learning_rate', 'N/A')}")
        print(f"  Num epochs:        {config.get('num_epochs', 'N/A')}")
        print(f"  Frames per video:  {config.get('frames_per_video', 'N/A')}")
        print(f"  Optimizer:         {config.get('optimizer', 'N/A')}")
        print(f"  Scheduler:         {config.get('scheduler', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"✗ Error reading config: {e}")
        return False

def check_gpu():
    """Check GPU availability"""
    print_header("GPU/Compute")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            print(f"✓ CUDA available")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA Version: {torch.version.cuda}")
            
            # Memory
            total_memory = torch.cuda.get_device_properties(0).total_memory
            print(f"  Total Memory: {total_memory / 1e9:.1f} GB")
        else:
            print(f"ℹ CUDA not available (will use CPU)")
            print(f"  Training will be slower")
        
        print(f"  PyTorch: {torch.__version__}")
        return True
    except Exception as e:
        print(f"⚠️  Could not check GPU: {e}")
        return True

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  Verifixia Training Setup Verification")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Dataset", check_dataset),
        ("Configuration", check_config),
        ("GPU/Compute", check_gpu),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during {name}: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    all_ok = all(result for _, result in results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    if all_ok:
        print("\n" + "="*60)
        print("✓ All checks passed! Ready to start training.")
        print("\nRun training with:")
        print("  On Windows:  .\\train.ps1")
        print("  On Linux:    bash run_training.sh")
        print("="*60 + "\n")
        return 0
    else:
        print("\n" + "="*60)
        print("⚠️  Some checks failed. Please fix issues above.")
        print("="*60 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
