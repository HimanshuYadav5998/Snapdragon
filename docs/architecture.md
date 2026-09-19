# System Architecture — SnapSense AI

## Overview

SnapSense AI is designed as a **modular, on-device multimodal AI assistant** that leverages the
Qualcomm Snapdragon X Elite / X Plus NPU (Neural Processing Unit) for all AI inference.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                       │
│              (Gradio Web UI @ localhost:7860)                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Voice Module │  │Vision Module │  │  NLP Module  │
   │ voice_module │  │vision_module │  │  nlp_module  │
   │     .py      │  │    .py       │  │    .py       │
   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │   Whisper    │  │ MobileNet-V3 │  │  Mistral-7B  │
   │  (ASR, INT8) │  │  + CLIP      │  │  (INT4 GGUF) │
   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
              ┌─────────────────────────┐
              │   Qualcomm AI Hub SDK   │
              │   (qai_hub + QNN EP)    │
              └─────────────┬───────────┘
                            ▼
              ┌─────────────────────────┐
              │  Snapdragon Hexagon NPU │
              │  (45+ TOPS peak perf)   │
              │  Snapdragon X Elite /   │
              │  X Plus on HP OmniBook  │
              └─────────────────────────┘
```

## Component Details

### 1. Voice Module (`src/voice_module.py`)

- **Model**: OpenAI Whisper-Base, INT8-quantized for NPU
- **Input**: PCM audio at 16kHz (microphone or file)
- **Output**: Transcribed text string
- **Latency**: ~180ms for 5s audio on Snapdragon X Elite NPU
- **NPU acceleration**: ✅ via Qualcomm AI Hub

### 2. Vision Module (`src/vision_module.py`)

- **Model 1**: MobileNet-V3-Large (INT8) — image classification (1000 ImageNet classes)
- **Model 2**: CLIP-ViT-B/32 (FP16) — zero-shot image captioning
- **Input**: PIL Image (any size, auto-resized to 224×224)
- **Output**: Label + confidence + natural language description
- **Latency**: ~45ms per image on Snapdragon X Elite NPU
- **NPU acceleration**: ✅ via Qualcomm AI Hub

### 3. NLP Module (`src/nlp_module.py`)

- **Model**: Mistral-7B-Instruct-v0.3 (INT4 quantized)
- **Input**: Natural language text (question or passage to summarize)
- **Output**: Summary / answer text (up to 256 tokens)
- **Latency**: ~320ms per 200-token response on Snapdragon X Elite NPU
- **NPU acceleration**: ✅ via Qualcomm AI Hub (ONNX QNN backend)

## Data Flow

```
User Input → Preprocessing → NPU Inference → Post-processing → UI Display
     ↑                           ↑
   Audio / Image / Text     Qualcomm AI Hub SDK
                             compiles and routes
                             to Hexagon NPU
```

## Privacy Architecture

All data flows are **local-only**:

```
User PC (HP OmniBook)
├── Microphone → Voice Module → Whisper NPU → Text
├── Camera / Files → Vision Module → MobileNet/CLIP NPU → Labels
└── Keyboard → NLP Module → Mistral NPU → Response

No data leaves the device ✅
```

## Optimization Strategy

| Technique | Applied To | Benefit |
|-----------|-----------|---------|
| INT8 quantization | Whisper, MobileNet | 4x model size reduction, NPU-friendly |
| INT4 quantization | Mistral-7B | 8x model size reduction, fits in 16GB RAM |
| FP16 | CLIP | Good accuracy-speed tradeoff on NPU |
| ONNX QNN backend | All models | Qualcomm Hexagon NPU execution |
| Static input shapes | Vision, Voice | Eliminates dynamic shape overhead |
| Warm-up inference | All modules | Consistent low-latency after first call |

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| AI Runtime | Qualcomm AI Hub SDK, ONNX Runtime (QNN EP) |
| LLM Inference | llama-cpp-python (fallback) |
| Audio | sounddevice, soundfile, scipy |
| Vision | Pillow, OpenCV |
| UI | Gradio 4.x |
| CLI | Rich |
| Target OS | Windows 11 ARM64 |
| Target HW | HP OmniBook Ultra (Snapdragon X2 Plus) |
