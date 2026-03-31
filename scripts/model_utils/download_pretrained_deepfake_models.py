"""
================================================================================
CLASSIFICATION: MODEL UTILITY - Pretrained Model Downloader
================================================================================
TYPE:        Model deployment & management
PURPOSE:     Download pre-trained model weights for production deployment
CATEGORY:    Model Management
STATUS:      Active (Deployment Critical)
DEPENDENCIES: requests, argparse, shutil

DESCRIPTION:
Fetches both PyTorch and scikit-learn model weights from specified URLs
(e.g., GitHub releases, S3 buckets, private storage) and saves them into
the `models/` directory. Intended for CI/deployment pipelines so the backend
never has to train models locally.

This avoids storing large binary files in the Git repository while ensuring
models are always available in production environments.

USAGE (from repo root):
    python scripts/model_utils/download_pretrained_models.py \\
        --pytorch-url https://example.com/xception_deepfake.pth \\
        --sklearn-url https://example.com/deepfake_sklearn.pkl

ARGUMENTS:
    --pytorch-url URL    URL to download PyTorch model (.pth)
    --sklearn-url URL    URL to download scikit-learn model (.pkl)

OUTPUT LOCATION:  models/

SECURITY NOTE:
Host weights in private storage with appropriate ACLs. Downloaded files are
platform-independent; on startup, the server merely loads them into CPU
memory via PyTorch/pickle.

================================================================================
"""

import argparse
import os
import shutil
import sys

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(BASE_DIR, "models")


def download(url, target_path):
    if not url:
        print(f"No URL provided for {target_path}, skipping.")
        return False

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    try:
        print(f"Downloading {url} -> {target_path}")
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(target_path, "wb") as f:
            shutil.copyfileobj(resp.raw, f)
        print("Download complete")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fetch pretrained model files")
    parser.add_argument("--pytorch-url", help="URL of PyTorch .pth weights")
    parser.add_argument("--sklearn-url", help="URL of scikit-learn pickle file")
    args = parser.parse_args()

    if not args.pytorch_url and not args.sklearn_url:
        parser.print_help()
        sys.exit(1)

    success = True
    if args.pytorch_url:
        success &= download(args.pytorch_url, os.path.join(MODEL_DIR, "xception_deepfake.pth"))
    if args.sklearn_url:
        success &= download(args.sklearn_url, os.path.join(MODEL_DIR, "deepfake_sklearn.pkl"))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
