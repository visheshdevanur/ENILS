import logging
import ollama
from enils.config import OLLAMA_MODEL, SYSTEM_PROMPT

logger = logging.getLogger("TutorLLM")

class TutorLLM:
    """
    Interacts with a local Ollama instance to generate tutoring responses.
    """

    def __init__(self):
        """
        Initializes the LLM configuration.
        """
        self.model = OLLAMA_MODEL
        logger.info(f"Initializing Tutor LLM with model: {self.model}")

    def generate_response(self, user_query):
        """
        Sends the transcribed text to Ollama and returns the generated response.

        Args:
            user_query (str): The student's transcribed question.

        Returns:
            str: The AI tutor's response.
        """
        if not user_query:
            logger.warning("Empty query provided to LLM.")
            return "I didn't hear a question. Could you please repeat that?"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ]

        try:
            response = ollama.chat(model=self.model, messages=messages)
            content = response['message']['content'].strip()

            if not content:
                logger.warning("Ollama returned an empty response.")
                return "I'm not sure how to answer that. Could you rephrase your question?"

            return content
        except Exception as e:
            logger.exception(f"Error communicating with Ollama: {e}")
            return "I'm having trouble thinking right now. Please ensure Ollama is running and try again."
