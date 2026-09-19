# Setup Guide — SnapSense AI

## Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| OS | Windows 11 ARM64 | Windows 11 ARM64 24H2 |
| Hardware | Any Snapdragon X-series PC | HP OmniBook Ultra (Snapdragon X2 Plus) |
| Python | 3.10 | 3.11 |
| RAM | 16GB | 32GB |
| Storage | 10GB free | 20GB free |
| Internet | Required (first setup only) | — |

## Step 1: Install Python 3.11 (ARM64)

Download Python 3.11 ARM64 for Windows from:
https://www.python.org/downloads/windows/

**Important**: Choose the **ARM64** installer, not x64.

Verify installation:
```powershell
python --version   # Should show Python 3.11.x
```

## Step 2: Clone the Repository

```powershell
git clone https://github.com/HimanshuYadav5998/Snapdragon.git
cd Snapdragon
```

## Step 3: Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

## Step 4: Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

> ⚠️ Note: `llama-cpp-python` requires a C++ compiler. If installation fails:
> ```powershell
> pip install llama-cpp-python --extra-index-url https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cpu
> ```

## Step 5: Configure Qualcomm AI Hub

1. Create a free account at https://aihub.qualcomm.com/
2. Go to **Settings → API Token**
3. Copy your API token
4. Run:
   ```powershell
   qai-hub configure --api_token YOUR_API_TOKEN_HERE
   ```

## Step 6: Download AI Models

```powershell
python src/download_models.py
```

This downloads ~5GB of model files. Run once, then models are cached locally.

## Step 7: Launch SnapSense AI

```powershell
python src/app.py
```

Open your browser to: **http://localhost:7860**

---

## Troubleshooting

### "qai_hub not found" error
```powershell
pip install qai_hub qai_hub_models
qai-hub configure --api_token YOUR_TOKEN
```

### "sounddevice PortAudio not found" error
Install PortAudio:
- Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Or install via: `pip install pipwin && pipwin install pyaudio`

### App runs in CPU mode instead of NPU
- Ensure you're on a Snapdragon X-series HP PC
- Verify Qualcomm AI Hub configuration: `qai-hub list-devices`
- Check that your PC shows up in the device list

### Gradio UI doesn't open
Try opening manually: http://localhost:7860

---

## Performance Tips

1. **Close other apps** before running — the NPU is shared
2. **Use Windows High Performance power mode** for best NPU throughput
3. **First inference is slow** (NPU warm-up) — subsequent calls are fast
4. **Mistral-7B** is the largest model — ensure 16GB+ RAM available
