"""
Voice Module — SnapSense AI
============================
Real-time Speech-to-Text (ASR) using Whisper model,
optimized for Snapdragon Hexagon NPU via Qualcomm AI Hub.

Model: openai/whisper-base (INT8 quantized for NPU)
Latency target: <200ms for 5-second audio clips on Snapdragon X Elite
"""

import os
import numpy as np
import soundfile as sf
import sounddevice as sd
from pathlib import Path

# Qualcomm AI Hub — for NPU-compiled model
try:
    import qai_hub as hub
    from qai_hub_models.models.whisper_base_en import Model as WhisperModel
    QAI_AVAILABLE = True
except ImportError:
    QAI_AVAILABLE = False

# Fallback to CPU whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class VoiceModule:
    """
    Whisper ASR running on Snapdragon Hexagon NPU via Qualcomm AI Hub.
    Falls back to CPU-based Whisper if AI Hub is not configured.
    """

    SAMPLE_RATE = 16000  # Whisper expects 16kHz audio
    MODEL_DIR = Path(__file__).parent.parent / "models" / "whisper"

    def __init__(self):
        self._model = None
        self._mode = None
        self._load_model()

    def _load_model(self):
        """Load Whisper model — NPU preferred, CPU fallback."""
        if QAI_AVAILABLE:
            try:
                print("[VoiceModule] Loading Whisper from Qualcomm AI Hub (NPU)...")
                self._model = WhisperModel.from_pretrained()
                self._mode = "npu"
                print("[VoiceModule] ✓ Whisper loaded on Snapdragon NPU")
                return
            except Exception as e:
                print(f"[VoiceModule] AI Hub unavailable ({e}), falling back to CPU")

        if WHISPER_AVAILABLE:
            print("[VoiceModule] Loading Whisper on CPU (fallback)...")
            self._model = whisper.load_model("base")
            self._mode = "cpu"
            print("[VoiceModule] ✓ Whisper loaded on CPU")
        else:
            print("[VoiceModule] ⚠️ No Whisper backend available. Install whisper or qai_hub_models.")
            self._mode = "mock"

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Transcribed text string.
        """
        if self._mode == "mock":
            return "[Demo Mode] Whisper model not loaded. Please configure Qualcomm AI Hub."

        # Load and preprocess audio
        audio, sample_rate = sf.read(audio_path)
        audio = self._preprocess_audio(audio, sample_rate)

        if self._mode == "npu":
            return self._transcribe_npu(audio)
        else:
            return self._transcribe_cpu(audio_path)

    def _preprocess_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Resample to 16kHz mono as required by Whisper."""
        # Convert stereo to mono
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        # Resample if needed
        if sample_rate != self.SAMPLE_RATE:
            from scipy.signal import resample
            target_length = int(len(audio) * self.SAMPLE_RATE / sample_rate)
            audio = resample(audio, target_length)

        return audio.astype(np.float32)

    def _transcribe_npu(self, audio: np.ndarray) -> str:
        """Run Whisper inference on Snapdragon Hexagon NPU via AI Hub."""
        try:
            # Qualcomm AI Hub handles NPU compilation and execution
            result = self._model.transcribe(audio)
            return result.get("text", "").strip()
        except Exception as e:
            return f"[NPU Transcription Error] {e}"

    def _transcribe_cpu(self, audio_path: str) -> str:
        """CPU fallback transcription."""
        result = self._model.transcribe(audio_path)
        return result.get("text", "").strip()

    def record_audio(self, duration_seconds: int = 5) -> np.ndarray:
        """
        Record audio from microphone.

        Args:
            duration_seconds: How long to record.

        Returns:
            NumPy array of audio samples at 16kHz.
        """
        print(f"[VoiceModule] Recording {duration_seconds}s of audio...")
        audio = sd.rec(
            int(duration_seconds * self.SAMPLE_RATE),
            samplerate=self.SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        return audio.flatten()
