"""
UI Helpers — SnapSense AI
==========================
Utility functions for the Gradio web interface.
"""

import gradio as gr
from typing import Optional


def create_status_badge(text: str, color: str = "green") -> str:
    """Create an HTML status badge for the UI."""
    colors = {
        "green": "#10B981",
        "blue": "#3B82F6",
        "purple": "#8B5CF6",
        "red": "#EF4444",
        "yellow": "#F59E0B",
    }
    hex_color = colors.get(color, "#10B981")
    return f"""
    <span style="
        background-color: {hex_color}20;
        color: {hex_color};
        border: 1px solid {hex_color}40;
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 0.8em;
        font-weight: 600;
    ">{text}</span>
    """


def npu_status_html(mode: str) -> str:
    """Return HTML showing NPU or CPU mode."""
    if mode == "npu":
        return (
            create_status_badge("⚡ NPU Accelerated", "purple") +
            create_status_badge("Snapdragon X Elite", "blue")
        )
    else:
        return create_status_badge("💻 CPU Mode (Fallback)", "yellow")


def format_latency(ms: float) -> str:
    """Format latency for display."""
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.1f}s"


def error_html(message: str) -> str:
    """Return formatted error HTML."""
    return f"""
    <div style="
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 12px;
        color: #DC2626;
    ">
        <b>❌ Error:</b> {message}
    </div>
    """


def success_html(message: str) -> str:
    """Return formatted success HTML."""
    return f"""
    <div style="
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px;
        color: #16A34A;
    ">
        <b>✅</b> {message}
    </div>
    """
