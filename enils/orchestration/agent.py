import time
import logging
from enils.orchestration.state_machine import AgentState
from enils.audio.mic import MicHandler
from enils.stt.transcriber import Transcriber
from enils.llm.tutor import TutorLLM
from enils.tts.speaker import Speaker
from enils.config import WAKE_WORDS, WAKE_WORD_SNIPPET_SECONDS

logger = logging.getLogger("EnilsAgent")

class EnilsAgent:
    """
    The central orchestration agent for the ENILS system.
    Manages the state machine and coordinates audio, STT, LLM, and TTS components.
    """

    def __init__(self):
        """Initializes the agent components and sets the initial state to IDLE."""
        self.state = AgentState.IDLE
        self.mic = MicHandler()
        self.transcriber = Transcriber()
        self.tutor = TutorLLM()
        self.speaker = Speaker()
        logger.info("EnilsAgent initialized successfully.")

    def transition_to(self, new_state):
        """
        Transitions the agent to a new state and logs the change.

        Args:
            new_state (AgentState): The state to transition to.
        """
        logger.info(f"Transitioning to state: {new_state.value}")
        self.state = new_state

    def run(self):
        """
        Starts the main agent loop. Runs continuously until a KeyboardInterrupt is received.
        """
        logger.info("=== ENILS MVP Started ===")
        self.transition_to(AgentState.IDLE)

        while True:
            try:
                self.loop_iteration()
            except KeyboardInterrupt:
                logger.info("Exiting ENILS. Goodbye!")
                break
            except Exception as e:
                logger.exception(f"Agent encountered an unexpected error: {e}. Recovering to IDLE state.")
                self.transition_to(AgentState.IDLE)
                time.sleep(1) # Prevent tight crash loops

    def loop_iteration(self):
        """
        Executes a single iteration of the agent's state machine.
        """
        if self.state == AgentState.IDLE:
            # 1. Wait for energy spike (maintains rolling buffer internally)
            self.mic.wait_for_energy_spike()

            # 2. Record additional audio to capture the full wake word
            # The MicHandler now prepends the pre-trigger buffer
            snippet = self.mic.record_duration(WAKE_WORD_SNIPPET_SECONDS)

            # 3. Transcribe snippet
            text = self.transcriber.transcribe(snippet).lower()
            logger.info(f"[Wake Word Check] Heard: '{text}'")

            # Normalize text: remove punctuation and lowercase
            normalized_text = "".join(char for char in text if char.isalnum() or char.isspace()).lower()

            # Check if any of the wake words are in the normalized text
            if any(word in normalized_text for word in WAKE_WORDS):
                logger.info(f"Wake word detected! Heard: '{text}' (normalized: '{normalized_text}')")
                self.speaker.speak("Yes?")
                self.transition_to(AgentState.LISTENING)
            else:
                # False alarm, stay IDLE
                logger.info(f"Wake word not found. Heard: '{text}' (normalized: '{normalized_text}')")
                pass

        elif self.state == AgentState.LISTENING:
            # 1. Record until silence (prepends pre-trigger buffer)
            query_audio = self.mic.record_until_silence()
            self.transition_to(AgentState.TRANSCRIBING)

            # Start timing for latency measurement
            start_time = time.time()

            # 2. Transcribe query
            query_text = self.transcriber.transcribe(query_audio)
            logger.info(f"[Query] {query_text}")

            if not query_text:
                logger.info("No query detected, returning to IDLE.")
                self.transition_to(AgentState.IDLE)
                return

            # Check for exit keywords to end the conversation
            exit_keywords = ["stop", "exit", "goodbye", "bye", "quit"]
            if any(word in query_text.lower() for word in exit_keywords):
                logger.info("Exit keyword detected. Ending conversation.")
                self.speaker.speak("Goodbye! Have a great day of learning.")
                self.transition_to(AgentState.IDLE)
                return

            self.transition_to(AgentState.THINKING)

            # 3. Generate response from LLM
            response = self.tutor.generate_response(query_text)
            logger.info(f"[Response] {response}")

            self.transition_to(AgentState.SPEAKING)

            # Calculate latency (from end of speech to start of TTS)
            latency = time.time() - start_time
            logger.info(f"[LATENCY] End of speech to start of TTS: {latency:.2f} seconds")

            # 4. Speak response
            self.speaker.speak(response)

            # Instead of returning to IDLE, we transition back to LISTENING for continuous chat
            logger.info("Conversation continues... returning to LISTENING state.")
            self.transition_to(AgentState.LISTENING)
