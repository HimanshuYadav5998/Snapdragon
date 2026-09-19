"""
NLP Module — SnapSense AI
==========================
On-device text intelligence using Mistral-7B-Instruct (INT4 quantized),
optimized for Snapdragon Hexagon NPU via Qualcomm AI Hub.

Capabilities:
  - Text summarization
  - Question answering
  - Instruction following

Model: Mistral-7B-Instruct-v0.3 (INT4 GGUF / ONNX for NPU)
Latency target: <400ms for 200-token responses on Snapdragon X Elite
"""

from __future__ import annotations
from pathlib import Path

# Qualcomm AI Hub — NPU LLM
try:
    import qai_hub as hub
    from qai_hub_models.models.mistral_7b_instruct import Model as MistralModel
    QAI_AVAILABLE = True
except ImportError:
    QAI_AVAILABLE = False

# Fallback: llama-cpp-python (GGUF CPU/GPU)
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# System prompt for the assistant
SYSTEM_PROMPT = """You are SnapSense AI, a helpful on-device AI assistant running on a
Snapdragon-powered HP PC. You are fast, private, and accurate. Answer concisely and clearly."""

SUMMARIZE_PROMPT = """Summarize the following text in 3-5 bullet points. Be concise and capture
the key points:\n\n{text}"""

QA_PROMPT = """Answer the following question clearly and concisely:\n\n{question}"""


class NLPModule:
    """
    On-device text AI using Mistral-7B (INT4 quantized) on Snapdragon Hexagon NPU.
    Falls back to llama-cpp-python on CPU if AI Hub is not available.
    """

    MODEL_DIR = Path(__file__).parent.parent / "models" / "mistral"
    GGUF_FILENAME = "mistral-7b-instruct-v0.3.Q4_K_M.gguf"

    def __init__(self):
        self._model = None
        self._mode = None
        self._load_model()

    def _load_model(self):
        """Load Mistral-7B — NPU preferred, CPU fallback."""
        if QAI_AVAILABLE:
            try:
                print("[NLPModule] Loading Mistral-7B from Qualcomm AI Hub (NPU)...")
                self._model = MistralModel.from_pretrained()
                self._mode = "npu"
                print("[NLPModule] ✓ Mistral-7B loaded on Snapdragon NPU (INT4)")
                return
            except Exception as e:
                print(f"[NLPModule] AI Hub unavailable ({e}), falling back to CPU")

        gguf_path = self.MODEL_DIR / self.GGUF_FILENAME
        if LLAMA_CPP_AVAILABLE and gguf_path.exists():
            print(f"[NLPModule] Loading Mistral-7B GGUF on CPU: {gguf_path}")
            self._model = Llama(
                model_path=str(gguf_path),
                n_ctx=4096,
                n_threads=8,
                n_gpu_layers=0,   # CPU only on non-NPU path
                verbose=False,
            )
            self._mode = "cpu"
            print("[NLPModule] ✓ Mistral-7B loaded on CPU (GGUF INT4)")
        else:
            self._mode = "mock"
            print("[NLPModule] ⚠️ NLP model not found. Run `python download_models.py` first.")

    def summarize(self, text: str, max_tokens: int = 256) -> str:
        """
        Summarize a block of text.

        Args:
            text: Text to summarize.
            max_tokens: Maximum output tokens.

        Returns:
            Bullet-point summary string.
        """
        if self._mode == "mock":
            return "[Demo Mode] Mistral model not loaded. Run `python src/download_models.py`."

        prompt = SUMMARIZE_PROMPT.format(text=text)
        return self._generate(prompt, max_tokens=max_tokens)

    def answer(self, question: str, max_tokens: int = 256) -> str:
        """
        Answer a question using on-device LLM.

        Args:
            question: The question to answer.
            max_tokens: Maximum output tokens.

        Returns:
            Answer string.
        """
        if self._mode == "mock":
            return "[Demo Mode] Mistral model not loaded. Run `python src/download_models.py`."

        prompt = QA_PROMPT.format(question=question)
        return self._generate(prompt, max_tokens=max_tokens)

    def _generate(self, prompt: str, max_tokens: int = 256) -> str:
        """Run text generation on the loaded model."""
        if self._mode == "npu":
            return self._generate_npu(prompt, max_tokens)
        elif self._mode == "cpu":
            return self._generate_cpu(prompt, max_tokens)
        return "[Error] No model loaded."

    def _generate_npu(self, prompt: str, max_tokens: int) -> str:
        """Generate text using Mistral-7B on Snapdragon Hexagon NPU."""
        try:
            # Format as Mistral instruct chat
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
            output = self._model.generate(messages, max_new_tokens=max_tokens)
            return output.strip()
        except Exception as e:
            return f"[NPU Generation Error] {e}"

    def _generate_cpu(self, prompt: str, max_tokens: int) -> str:
        """Generate text using Mistral-7B GGUF on CPU via llama-cpp-python."""
        formatted = f"<s>[INST] {SYSTEM_PROMPT}\n\n{prompt} [/INST]"
        output = self._model(
            formatted,
            max_tokens=max_tokens,
            stop=["</s>", "[INST]"],
            echo=False,
            temperature=0.7,
            top_p=0.9,
        )
        return output["choices"][0]["text"].strip()
