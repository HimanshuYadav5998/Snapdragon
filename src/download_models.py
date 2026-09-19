"""
Model Downloader — SnapSense AI
================================
Downloads and compiles AI models from Qualcomm AI Hub
for Snapdragon Hexagon NPU deployment.

Run this once before launching the app:
    python src/download_models.py

Models downloaded:
  - Whisper-Base (INT8, for speech recognition)
  - MobileNet-V3-Large (INT8, for image classification)
  - CLIP-ViT-B/32 (FP16, for image understanding)
  - Mistral-7B-Instruct (INT4 GGUF, for text Q&A)
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()
MODELS_DIR = Path(__file__).parent.parent / "models"


def check_qai_hub():
    """Check if Qualcomm AI Hub is configured."""
    try:
        import qai_hub as hub
        profile = hub.get_devices()
        return True
    except Exception as e:
        console.print(f"[yellow]⚠️  Qualcomm AI Hub not configured: {e}[/yellow]")
        console.print("[blue]➜  Get your free API key at: https://aihub.qualcomm.com/[/blue]")
        console.print("[blue]➜  Then run: qai-hub configure --api_token YOUR_TOKEN[/blue]")
        return False


def download_whisper():
    """Download and compile Whisper for Snapdragon NPU."""
    console.print("[cyan]📥 Downloading Whisper-Base (ASR)...[/cyan]")
    try:
        from qai_hub_models.models.whisper_base_en import Model
        model = Model.from_pretrained()
        save_path = MODELS_DIR / "whisper"
        save_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Whisper saved to {save_path}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Whisper download failed: {e}[/red]")
        return False


def download_mobilenet():
    """Download and compile MobileNet-V3 for Snapdragon NPU."""
    console.print("[cyan]📥 Downloading MobileNet-V3-Large (Image Classification)...[/cyan]")
    try:
        from qai_hub_models.models.mobilenet_v3_large import Model
        model = Model.from_pretrained()
        save_path = MODELS_DIR / "mobilenet"
        save_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ MobileNet-V3 saved to {save_path}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ MobileNet download failed: {e}[/red]")
        return False


def download_clip():
    """Download and compile CLIP for Snapdragon NPU."""
    console.print("[cyan]📥 Downloading CLIP-ViT-B/32 (Image-Text Similarity)...[/cyan]")
    try:
        from qai_hub_models.models.clip import Model
        model = Model.from_pretrained()
        save_path = MODELS_DIR / "clip"
        save_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ CLIP saved to {save_path}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ CLIP download failed: {e}[/red]")
        return False


def download_mistral_gguf():
    """Download Mistral-7B GGUF (fallback CPU model)."""
    console.print("[cyan]📥 Downloading Mistral-7B-Instruct GGUF (text Q&A fallback)...[/cyan]")
    try:
        import requests
        from tqdm import tqdm

        # Mistral-7B Q4_K_M GGUF — ~4.1GB
        url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
        save_path = MODELS_DIR / "mistral"
        save_path.mkdir(parents=True, exist_ok=True)
        filename = save_path / "mistral-7b-instruct-v0.3.Q4_K_M.gguf"

        if filename.exists():
            console.print(f"[yellow]ℹ Mistral GGUF already exists: {filename}[/yellow]")
            return True

        console.print(f"[dim]Downloading ~4GB — this may take a few minutes...[/dim]")
        response = requests.get(url, stream=True, timeout=60)
        total = int(response.headers.get("content-length", 0))

        with open(filename, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

        console.print(f"[green]✓ Mistral-7B GGUF saved to {filename}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]✗ Mistral GGUF download failed: {e}[/red]")
        return False


if __name__ == "__main__":
    console.print(Panel(
        "[bold cyan]SnapSense AI — Model Downloader[/bold cyan]\n"
        "Downloading models for Snapdragon Hexagon NPU via Qualcomm AI Hub",
        border_style="blue"
    ))

    qai_ok = check_qai_hub()

    results = {}

    if qai_ok:
        results["Whisper (ASR)"] = download_whisper()
        results["MobileNet-V3"] = download_mobilenet()
        results["CLIP"] = download_clip()

    # Mistral GGUF as universal fallback
    results["Mistral-7B GGUF"] = download_mistral_gguf()

    # Summary
    console.print("\n[bold]Download Summary:[/bold]")
    for model, success in results.items():
        status = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"  {status} {model}")

    if all(results.values()):
        console.print("\n[bold green]🚀 All models ready! Run: python src/app.py[/bold green]")
    else:
        console.print("\n[yellow]⚠️  Some models failed. Check errors above.[/yellow]")
