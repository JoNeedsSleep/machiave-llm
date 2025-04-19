from typing import Dict, Any
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file in the same directory
current_dir = os.path.dirname(__file__)
env_path = os.path.join(current_dir, '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

class ModelAPI:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def call_model(self, prompt: str) -> str:
        """Call the OpenAI API with the given prompt."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a strategic player in a game of Diplomacy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return ""

class OpenAIModel(ModelAPI):
    def __init__(self):
        super().__init__()
    
    def submit_order(self, power: str, order: str) -> bool:
        """Submit an order to the game engine."""
        # To be implemented based on the game engine API
        pass
    
    def get_board_state(self) -> Dict[str, Any]:
        """Get the current state of the game board."""
        # To be implemented based on the game engine API
        pass

class AnthropicModel(ModelAPI):
    def __init__(self):
        super().__init__()
        # Anthropic specific initialization
    
    def call_model(self, prompt: str) -> str:
        """Make API call to Anthropic."""
        # Implement Anthropic API call
        pass 