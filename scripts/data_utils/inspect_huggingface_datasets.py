"""
================================================================================
CLASSIFICATION: DATA UTILITY - Dataset Inspector
================================================================================
TYPE:        Data exploration & validation
PURPOSE:     Inspect available HuggingFace datasets for deepfake detection
CATEGORY:    Data Management
STATUS:      Active (Discovery/Informational)
DEPENDENCIES: requests, json

DESCRIPTION:
Lists publicly available deepfake detection datasets on HuggingFace Hub.
Displays dataset structure, features, and sample data for each dataset.
Useful for research and understanding available data sources.

DATASETS INSPECTED:
    • assassinwizz/deepfake-face-detection-dataset
    • prithivMLmods/Deepfake-vs-Real-60K  
    • Hemg/deepfake-and-real-images (USED - primary source)
    • snehalkr30/Deep-Fake-video

USAGE (from repo root):
    python scripts/data_utils/inspect_huggingface_datasets.py

OUTPUT:
    Dataset structure, features, and sample rows for each dataset

================================================================================
"""

import requests
import json

datasets = [
    "assassinwizz/deepfake-face-detection-dataset",
    "prithivMLmods/Deepfake-vs-Real-60K",
    "Hemg/deepfake-and-real-images",
    "snehalkr30/Deep-Fake-video"
]

def inspect_dataset(dataset_name):
    print(f"--- Inspecting {dataset_name} ---")
    url = f"https://datasets-server.huggingface.co/first-rows?dataset={requests.utils.quote(dataset_name)}&config=default&split=train"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed: {response.status_code}")
            return

        data = response.json()
        if "features" in data:
            print("Features:")
            for feature in data["features"]:
                print(f"  - {feature['name']} ({feature['type']})")
        
        if "rows" in data and len(data["rows"]) > 0:
            print("First Row Keys:", data["rows"][0]["row"].keys())
            # Print a sample value for non-image fields to identify labels
            row = data["rows"][0]["row"]
            for k, v in row.items():
                if k != "image":
                    print(f"  {k}: {v}")
                    
    except Exception as e:
        print(f"Error: {e}")
    print("\n")

if __name__ == "__main__":
    for ds in datasets:
        inspect_dataset(ds)
