import os
import logging

# -- Logging Configuration --
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

def setup_logging():
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

# -- Audio & Wake Word Settings --
SAMPLE_RATE = 16000
CHANNELS = 2  # Changed to 2 because the WASAPI driver requires the hardware channel count
MIC_DEVICE_ID = None  # Set to None to use the system default device automatically
WAKE_WORDS = ["tutor", "yo", "hey"]  # Multiple trigger words to handle misinterpretations
ENERGY_THRESHOLD = 0.00002  # Set very low to match the user's microphone gain
SILENCE_DURATION = 1.0   # Seconds of silence before stopping recording
MAX_RECORDING_DURATION = 10.0 # Fail-safe: Stop recording after 10s even if no silence is detected

WAKE_WORD_SNIPPET_SECONDS = 2.0  # How long to record after a spike to check for wake word

# -- STT Settings --
WHISPER_MODEL = "base.en"  # base.en is fast and good enough for english MVP
WHISPER_DEVICE = "cpu"     # 'cuda' if NVIDIA GPU is available
WHISPER_COMPUTE_TYPE = "int8" # or "float16" for GPU

# -- LLM Settings --
# Make sure Ollama is running locally and you've pulled this model
OLLAMA_MODEL = os.getenv("ENILS_OLLAMA_MODEL", "qwen2.5:3b")

SYSTEM_PROMPT = """You are the ENILS AI Tutor, a patient and encouraging educational companion for students in rural classrooms.
Your goal is to provide clear, concise, and age-appropriate explanations that spark curiosity.

Guidelines:
1. Subject Awareness: Whether the question is about Mathematics, Science, Language, or General knowledge, adapt your explanation to be intuitive. Use simple analogies for complex concepts.
2. Spoken-Word Optimization: Your responses will be read by a text-to-speech engine.
   - Avoid all markdown, emojis, and special characters.
   - Use clear punctuation to guide the TTS prosody.
   - Keep responses brief (under 3-4 sentences) to maintain student engagement.
3. Tone: Be encouraging and supportive. Instead of just giving the answer, occasionally guide the student to think about the 'why'.
4. Directness: Start your response immediately with the answer or the guiding question. Do not use introductory phrases like "Sure, I can help with that."
5. Clarity: If the student's query is empty, unclear, or sounds like background noise, politely ask them to repeat their question. Do NOT provide example answers or invent a topic.
"""

# -- TTS Settings --
TTS_RATE = 150      # Words per minute
TTS_VOLUME = 1.0    # 0.0 to 1.0
