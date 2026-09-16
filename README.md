# ENILS (Edge-Native Interactive Learning System)
Phase 1: Laptop MVP

ENILS is a fully offline, voice-interactive AI tutoring device for classrooms. It operates completely locally (no cloud APIs) using local SLMs (Small Language Models) and Speech-to-Text.

## Prerequisites

1. **Python 3.11+** installed on your system.
2. **Ollama** installed on your system (download from [ollama.com](https://ollama.com/)).

## Setup Instructions

### 1. Start Ollama and Pull the Model
First, ensure Ollama is running in the background. Then open a terminal and pull the default local model (we are using `qwen2.5:3b` as our lightweight, capable tutor model):

```bash
ollama pull qwen2.5:3b
```
*(If you want to use a different model, set `ENILS_OLLAMA_MODEL` environment variable or edit `enils/config.py`)*

### 2. Install Python Dependencies
Open your terminal in the project root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```
*(Note: `pyttsx3` is used for Text-to-Speech out-of-the-box on Windows. It requires no extra downloads.)*

### 3. Run the Application
Start the ENILS main loop:

```bash
python main.py
```

## How it works

1. **Wake Word Detection:** The system listens for sudden energy spikes. When you speak, it quickly transcribes the first 2 seconds. If it hears "Hey tutor" (case insensitive), it wakes up and replies "Yes?".
2. **Query Recording:** It will then record your question until it detects silence (default 1.5 seconds).
3. **STT:** Uses `faster-whisper` (base.en) to quickly convert your speech to text.
4. **LLM:** Forwards the transcribed query with a specialized system prompt to the local Ollama instance.
5. **TTS:** Reads the response aloud using the system's local Text-to-Speech engine.

## Configuration

You can customize wake words, timeouts, silence duration, and model parameters in `enils/config.py`.

## Latency Measurement

The system logs the end-to-end latency (from the moment you stop speaking to the moment the TTS starts responding) directly in the console.

## Future Plans (Phase 2)
- Port to Raspberry Pi 4/5.
- Upgrade TTS to Piper for more natural voices.
- Introduce `openwakeword` for ultra-low latency wake word spotting without STT.
