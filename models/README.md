# AI Models — SnapSense AI

This directory stores AI models after download. Models are NOT committed to Git (too large).

## How to Download Models

Run the model downloader script from the repository root:

```bash
# Activate your virtual environment first
venv\Scripts\activate

# Run the downloader
python src/download_models.py
```

## What Gets Downloaded

| Model | Task | Size | Source |
|-------|------|------|--------|
| `whisper/` | Speech-to-Text ASR | ~150MB | Qualcomm AI Hub |
| `mobilenet/` | Image Classification | ~22MB | Qualcomm AI Hub |
| `clip/` | Image-Text Similarity | ~350MB | Qualcomm AI Hub |
| `mistral/` | Text Q&A (GGUF INT4) | ~4.1GB | Hugging Face (TheBloke) |

## Requirements

1. **Qualcomm AI Hub account** (free): https://aihub.qualcomm.com/
2. **API Key**: Run `qai-hub configure --api_token YOUR_TOKEN`
3. **Python 3.10+** with venv
4. **~5GB disk space** total

## NPU Compilation

When you first run the app on a Snapdragon-powered HP PC, models will be automatically
compiled for your specific Snapdragon NPU (X Elite / X Plus) by Qualcomm AI Hub.
This one-time compilation takes ~2-5 minutes per model.

## Directory Structure After Download

```
models/
├── README.md          (this file)
├── whisper/           (Whisper ASR, INT8 NPU-optimized)
├── mobilenet/         (MobileNet-V3, INT8 NPU-optimized)
├── clip/              (CLIP ViT-B/32, FP16 NPU-optimized)
└── mistral/
    └── mistral-7b-instruct-v0.3.Q4_K_M.gguf  (4.1GB)
```

## Note on Privacy

All models run **100% on-device**. After the one-time download, no internet
connection is needed. Your data never leaves your HP PC.
