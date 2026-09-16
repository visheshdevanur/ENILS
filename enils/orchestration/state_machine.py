from enum import Enum

class AgentState(Enum):
    """
    Defines the possible states of the ENILS agent state machine.
    """
    IDLE = "IDLE"                   # Waiting for wake word energy spike
    LISTENING = "LISTENING"         # Wake word heard, recording user query
    TRANSCRIBING = "TRANSCRIBING"   # Converting captured audio to text
    THINKING = "THINKING"           # Processing text via LLM to generate response
    SPEAKING = "SPEAKING"           # Reading the response aloud via TTS
