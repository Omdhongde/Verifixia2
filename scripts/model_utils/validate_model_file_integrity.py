"""
================================================================================
CLASSIFICATION: MODEL UTILITY - Model Verification & Testing
================================================================================
TYPE:        Model validation & testing
PURPOSE:     Verify that models can be loaded and make predictions
CATEGORY:    Model Management / Quality Assurance
STATUS:      Active (Pre-deployment Checks)
DEPENDENCIES: torch, sklearn, PIL (via Backend/app.py)

DESCRIPTION:
Quick diagnostic script to test if backend can load models and make sample
predictions. Verifies both PyTorch and scikit-learn models are functional.
Does NOT start the server; simply imports and tests the same utilities used
by app.py.

Useful when deploying to ensure:
    ✓ Binary model files are present
    ✓ ML stack is functioning correctly
    ✓ No import/dependency issues

USAGE (from repo root):
    python scripts/model_utils/verify_model.py /path/to/sample/image.jpg

EXPECTED OUTPUT:
    PyTorch available: [True/False]
    scikit-learn available: [True/False]
    Prediction result: [JSON output with confidence scores]

EXIT CODES:
    0 = Success (model loaded and prediction made)
    1 = File not found or verification failed

================================================================================
"""

import sys
import os

# make sure we can import the backend package path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Backend")))

from app import predict_deepfake, PYTORCH_AVAILABLE, SKLEARN_AVAILABLE


def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_model.py /path/to/sample.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        sys.exit(1)

    print("PyTorch available:", PYTORCH_AVAILABLE)
    print("scikit-learn available:", SKLEARN_AVAILABLE)

    result = predict_deepfake(image_path)
    print("Prediction result:")
    print(result)


if __name__ == "__main__":
    main()
