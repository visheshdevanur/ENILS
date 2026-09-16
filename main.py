import sys
import os
from enils.config import setup_logging

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize professional logging
setup_logging()

from enils.orchestration.agent import EnilsAgent

def main():
    agent = EnilsAgent()
    agent.run()

if __name__ == "__main__":
    main()
