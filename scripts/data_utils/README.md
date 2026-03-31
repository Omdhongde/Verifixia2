# Data Utilities

Scripts for dataset acquisition, exploration, and management.

## Scripts

### `download_deepfake_dataset.py`
**Purpose:** Download training dataset from HuggingFace

Downloads deepfake detection images from the Hemg/deepfake-and-real-images dataset. Supports resumable downloads (skips existing files).

**Usage:**
```bash
# Download 500 Real + 500 Fake images
python download_deepfake_dataset.py --real 500 --fake 500

# Download more images (will skip existing)
python download_dataset.py --real 1000 --fake 1000

# Custom destination
python download_dataset.py --real 500 --fake 500 --data_dir MY_DATA
```

**Output:** Creates `DATA/Real/` and `DATA/Fake/` directories with images

---

### `inspect_huggingface_datasets.py`
**Purpose:** Explore available deepfake detection datasets

Lists publicly available datasets on HuggingFace and displays their structure, features, and sample data.

**Usage:**
```bash
python inspect_huggingface_datasets.py
```

**Output:** Dataset descriptions with feature lists and sample rows

---

## Notes

- Requires `datasets` library from HuggingFace
- All downloads are resumable (can stop and restart)
- Images are automatically converted to RGB format if needed
