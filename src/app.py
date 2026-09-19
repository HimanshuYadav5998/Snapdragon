"""
SnapSense AI — Main Application Entry Point
============================================
On-device multimodal AI assistant for Snapdragon-powered HP PCs.
Uses Qualcomm AI Hub models running on Snapdragon Hexagon NPU.

Author: Himanshu Yadav
Competition: Snapdragon AI Lab Build & Present Challenge (Qualcomm x Unstop)
"""

import os
import gradio as gr
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from voice_module import VoiceModule
from vision_module import VisionModule
from nlp_module import NLPModule

console = Console()

# ─── Initialize AI Modules ───────────────────────────────────────────────────

def initialize_modules():
    """Load and warm up all NPU-optimized AI modules."""
    console.print(Panel(
        Text("SnapSense AI — Starting up...", style="bold cyan"),
        subtitle="Snapdragon X Elite NPU",
        border_style="blue"
    ))

    voice = VoiceModule()
    vision = VisionModule()
    nlp = NLPModule()

    console.print("[green]✓[/green] All modules loaded on Snapdragon NPU")
    return voice, vision, nlp


# ─── Gradio Handler Functions ─────────────────────────────────────────────────

def transcribe_audio(audio_path, voice_module):
    """Handle audio input: run Whisper ASR on Snapdragon NPU."""
    if audio_path is None:
        return "⚠️ Please record or upload audio first."
    try:
        result = voice_module.transcribe(audio_path)
        return f"📝 Transcription:\n\n{result}"
    except Exception as e:
        return f"❌ Error during transcription: {e}"


def analyze_image(image, vision_module):
    """Handle image input: run MobileNet + CLIP on Snapdragon NPU."""
    if image is None:
        return "⚠️ Please upload an image first."
    try:
        label, confidence, description = vision_module.analyze(image)
        return (
            f"🏷️ **Classification:** {label} ({confidence:.1%} confidence)\n\n"
            f"📖 **Description:** {description}"
        )
    except Exception as e:
        return f"❌ Error during image analysis: {e}"


def text_ai(text, mode, nlp_module):
    """Handle text input: run Mistral-7B on Snapdragon NPU."""
    if not text.strip():
        return "⚠️ Please enter some text first."
    try:
        if mode == "Summarize":
            result = nlp_module.summarize(text)
            return f"📋 **Summary:**\n\n{result}"
        else:
            result = nlp_module.answer(text)
            return f"💬 **Answer:**\n\n{result}"
    except Exception as e:
        return f"❌ Error during text processing: {e}"


# ─── Build Gradio UI ──────────────────────────────────────────────────────────

def build_ui(voice, vision, nlp):
    """Build the Gradio web interface for SnapSense AI."""

    with gr.Blocks(
        title="SnapSense AI",
        theme=gr.themes.Soft(primary_hue="blue"),
        css="""
            .title-block { text-align: center; }
            .npu-badge { color: #8B5CF6; font-weight: bold; }
        """
    ) as demo:

        # Header
        gr.HTML("""
        <div class="title-block">
            <h1>⚡ SnapSense AI</h1>
            <p><b>On-Device Multimodal AI</b> — Powered by <span style="color:#8B5CF6;">Snapdragon X Elite NPU</span></p>
            <p style="color:gray; font-size:0.9em;">🔒 100% Private · Zero Cloud · Real-time inference via Qualcomm AI Hub</p>
        </div>
        """)

        with gr.Tabs():

            # ── Tab 1: Voice ASR ──────────────────────────────────────────
            with gr.Tab("🎙️ Voice → Text"):
                gr.Markdown("### Real-time Speech Recognition\nPowered by **Whisper** (INT8 quantized) on Snapdragon Hexagon NPU")
                with gr.Row():
                    with gr.Column():
                        audio_input = gr.Audio(
                            sources=["microphone", "upload"],
                            type="filepath",
                            label="Record or Upload Audio"
                        )
                        voice_btn = gr.Button("🎙️ Transcribe (On-Device)", variant="primary")
                    with gr.Column():
                        voice_output = gr.Textbox(
                            label="Transcription Result",
                            lines=8,
                            placeholder="Your transcribed text will appear here..."
                        )
                voice_btn.click(
                    fn=lambda audio: transcribe_audio(audio, voice),
                    inputs=audio_input,
                    outputs=voice_output
                )

            # ── Tab 2: Vision ─────────────────────────────────────────────
            with gr.Tab("🖼️ Image Understanding"):
                gr.Markdown("### On-Device Image Analysis\nPowered by **MobileNet-V3 + CLIP** on Snapdragon Hexagon NPU")
                with gr.Row():
                    with gr.Column():
                        image_input = gr.Image(
                            type="pil",
                            label="Upload Image"
                        )
                        vision_btn = gr.Button("🔍 Analyze Image (On-Device)", variant="primary")
                    with gr.Column():
                        vision_output = gr.Markdown(
                            label="Analysis Result",
                            value="Upload an image and click Analyze..."
                        )
                vision_btn.click(
                    fn=lambda img: analyze_image(img, vision),
                    inputs=image_input,
                    outputs=vision_output
                )

            # ── Tab 3: Text AI ────────────────────────────────────────────
            with gr.Tab("📝 Text AI (Q&A / Summarize)"):
                gr.Markdown("### On-Device Text Intelligence\nPowered by **Mistral-7B** (INT4 quantized) on Snapdragon Hexagon NPU")
                with gr.Row():
                    with gr.Column():
                        text_input = gr.Textbox(
                            label="Enter Text or Question",
                            lines=8,
                            placeholder="Paste text to summarize, or type a question..."
                        )
                        mode_radio = gr.Radio(
                            choices=["Summarize", "Answer Question"],
                            value="Summarize",
                            label="Mode"
                        )
                        nlp_btn = gr.Button("🧠 Process (On-Device)", variant="primary")
                    with gr.Column():
                        nlp_output = gr.Markdown(
                            label="AI Response",
                            value="Enter text and click Process..."
                        )
                nlp_btn.click(
                    fn=lambda text, mode: text_ai(text, mode, nlp),
                    inputs=[text_input, mode_radio],
                    outputs=nlp_output
                )

            # ── Tab 4: About ──────────────────────────────────────────────
            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
## SnapSense AI

**SnapSense AI** is a privacy-first multimodal AI assistant built specifically for
Snapdragon-powered HP PCs. Every AI inference runs locally on the Snapdragon Hexagon NPU —
no internet required after the initial model download.

### Why Snapdragon?
- Dedicated Hexagon NPU with **45+ TOPS** peak performance
- **6-14x faster** AI inference vs CPU-only
- Dramatically lower power consumption
- 100% on-device — your data never leaves your PC

### Models (via Qualcomm AI Hub)
| Model | Task | Optimization |
|-------|------|-------------|
| Whisper-Base | Speech-to-Text | INT8, NPU |
| MobileNet-V3 | Image Classification | INT8, NPU |
| CLIP-ViT-B/32 | Image-Text Similarity | FP16, NPU |
| Mistral-7B-Instruct | Text Q&A / Summarization | INT4, NPU |

### Submission
Built for the **Snapdragon® AI Lab Build & Present Challenge** by Qualcomm  
GitHub: https://github.com/HimanshuYadav5998/Snapdragon
                """)

        # Footer
        gr.HTML("""
        <div style="text-align:center; color:gray; font-size:0.85em; margin-top:20px;">
            ⚡ SnapSense AI · Snapdragon X Elite NPU · Qualcomm AI Hub<br/>
            Built for <b>Snapdragon AI Lab Build &amp; Present Challenge 2026</b>
        </div>
        """)

    return demo


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    voice, vision, nlp = initialize_modules()
    demo = build_ui(voice, vision, nlp)

    console.print("[bold green]🚀 Launching SnapSense AI...[/bold green]")
    console.print("[blue]📡 Open http://localhost:7860 in your browser[/blue]")

    demo.launch(
        server_name="localhost",
        server_port=7860,
        share=False,          # Keep local — no cloud relay
        inbrowser=True,
        show_error=True
    )
