"""
Vision Module — SnapSense AI
=============================
On-device image classification and captioning using:
  - MobileNet-V3 (image classification, INT8 on Snapdragon NPU)
  - CLIP-ViT-B/32 (image-text similarity, FP16 on Snapdragon NPU)

Both models sourced from Qualcomm AI Hub and optimized for
Snapdragon X Elite / X Plus Hexagon NPU.

Latency target: <50ms per image on Snapdragon X Elite
"""

from __future__ import annotations
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple

# Qualcomm AI Hub — NPU models
try:
    import qai_hub as hub
    from qai_hub_models.models.mobilenet_v3_large import Model as MobileNetModel
    from qai_hub_models.models.clip import Model as CLIPModel
    QAI_AVAILABLE = True
except ImportError:
    QAI_AVAILABLE = False

# Fallback torchvision
try:
    import torch
    import torchvision.transforms as T
    import torchvision.models as models
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# ImageNet class labels (top-5 categories for demo)
IMAGENET_LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"

# Descriptive prompts for CLIP zero-shot captioning
CLIP_PROMPTS = [
    "a photo of a person",
    "a photo of a cat",
    "a photo of a dog",
    "a photo of a car",
    "a photo of food",
    "a photo of a building",
    "a photo of nature",
    "a photo of text or document",
    "a photo of a device or technology",
    "a photo of sports or athletics",
]


class VisionModule:
    """
    On-device image analysis using MobileNet-V3 and CLIP,
    both optimized for Snapdragon Hexagon NPU via Qualcomm AI Hub.
    """

    def __init__(self):
        self._mobilenet = None
        self._clip = None
        self._labels = []
        self._mode = None
        self._transform = None
        self._load_models()

    def _load_models(self):
        """Load vision models — NPU preferred, CPU fallback."""
        self._labels = self._load_imagenet_labels()

        if QAI_AVAILABLE:
            try:
                print("[VisionModule] Loading MobileNet-V3 + CLIP from Qualcomm AI Hub (NPU)...")
                self._mobilenet = MobileNetModel.from_pretrained()
                self._clip = CLIPModel.from_pretrained()
                self._mode = "npu"
                print("[VisionModule] ✓ Vision models loaded on Snapdragon NPU")
                return
            except Exception as e:
                print(f"[VisionModule] AI Hub unavailable ({e}), falling back to CPU")

        if TORCH_AVAILABLE:
            print("[VisionModule] Loading MobileNet-V3 on CPU (fallback)...")
            self._mobilenet = models.mobilenet_v3_large(weights="IMAGENET1K_V2")
            self._mobilenet.eval()
            self._transform = T.Compose([
                T.Resize(256),
                T.CenterCrop(224),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            self._mode = "cpu"
            print("[VisionModule] ✓ MobileNet-V3 loaded on CPU")
        else:
            self._mode = "mock"
            print("[VisionModule] ⚠️ No vision backend available.")

    def analyze(self, image: Image.Image) -> Tuple[str, float, str]:
        """
        Classify and describe an image.

        Args:
            image: PIL Image object.

        Returns:
            Tuple of (label, confidence, description).
        """
        if self._mode == "mock":
            return "Demo Mode", 0.99, "Vision model not loaded. Please configure Qualcomm AI Hub."

        if self._mode == "npu":
            label, confidence = self._classify_npu(image)
            description = self._describe_npu(image)
        else:
            label, confidence = self._classify_cpu(image)
            description = f"Image classified as: {label}"

        return label, confidence, description

    def _classify_npu(self, image: Image.Image) -> Tuple[str, float]:
        """Classify image using MobileNet-V3 on Snapdragon NPU."""
        try:
            outputs = self._mobilenet.predict({"image": image})
            probs = outputs["logits"].softmax(dim=-1)
            top_idx = probs.argmax().item()
            label = self._labels[top_idx] if self._labels else f"Class {top_idx}"
            return label, probs[top_idx].item()
        except Exception as e:
            return f"[NPU Error] {e}", 0.0

    def _classify_cpu(self, image: Image.Image) -> Tuple[str, float]:
        """Classify image using MobileNet-V3 on CPU."""
        import torch
        tensor = self._transform(image.convert("RGB")).unsqueeze(0)
        with torch.no_grad():
            logits = self._mobilenet(tensor)
        probs = torch.softmax(logits, dim=1)[0]
        top_idx = probs.argmax().item()
        label = self._labels[top_idx] if self._labels else f"Class {top_idx}"
        return label, probs[top_idx].item()

    def _describe_npu(self, image: Image.Image) -> str:
        """Use CLIP to generate a natural language description on NPU."""
        try:
            # Zero-shot image captioning with CLIP prompts
            outputs = self._clip.predict({
                "image": image,
                "text": CLIP_PROMPTS
            })
            probs = outputs["logits_per_image"].softmax(dim=-1)[0]
            best_idx = probs.argmax().item()
            best_prompt = CLIP_PROMPTS[best_idx]
            confidence = probs[best_idx].item()
            # Clean up the prompt into a natural description
            description = best_prompt.replace("a photo of ", "").capitalize()
            return f"This appears to be {description} (CLIP confidence: {confidence:.1%})"
        except Exception as e:
            return f"[CLIP Description Error] {e}"

    @staticmethod
    def _load_imagenet_labels() -> list:
        """Load ImageNet class labels."""
        try:
            import urllib.request
            with urllib.request.urlopen(IMAGENET_LABELS_URL, timeout=5) as f:
                labels = [line.strip().decode() for line in f.readlines()]
            return labels
        except Exception:
            return []  # Will show class index if labels unavailable

    @staticmethod
    def preprocess_image(image_input) -> Image.Image:
        """Accept file path, bytes, or PIL Image and return PIL Image."""
        if isinstance(image_input, str):
            return Image.open(image_input).convert("RGB")
        elif isinstance(image_input, bytes):
            from io import BytesIO
            return Image.open(BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
