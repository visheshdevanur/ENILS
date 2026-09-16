import sounddevice as sd
import numpy as np
from enils.config import SAMPLE_RATE, CHANNELS

def debug_audio():
    print("--- Audio Level Debugger ---")
    print("Speak into your microphone to see the energy levels...")
    print("Press Ctrl+C to stop.\n")

    try:
        # Try to open a stream with default settings
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS) as stream:
            while True:
                data, overflowed = stream.read(1024)
                # Convert to float32 mono
                if data.ndim > 1:
                    audio_data = np.mean(data, axis=1)
                else:
                    audio_data = data

                rms = np.sqrt(np.mean(audio_data**2))
                # Print a simple visual bar
                bar = "#" * int(rms * 1000)
                print(f"RMS: {rms:.6f} | {bar}", end="\r")

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    debug_audio()
