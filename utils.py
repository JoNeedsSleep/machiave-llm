from typing import List, Dict
import os
from pathlib import Path
from config import POWER_MODELS, MODEL_CLASSES
from api import ModelAPI
import re

class LLMUtils:
    def __init__(self):
        self.prompt_templates = {
            "draft_message": self._read_prompt("Prompt_Draft_Messages"),
            "orders": self._read_prompt("Prompt_Orders.txt"),
            "strategize": self._read_prompt("Prompt_Strategize.txt")
        }
        self._model_instances: Dict[str, ModelAPI] = {}
        self.valid_powers = list(POWER_MODELS.keys())
    
    def _read_prompt(self, filename: str) -> str:
        with open(Path(__file__).parent / filename, 'r') as f:
            return f.read()
    
    def _get_model(self, power: str) -> ModelAPI:
        """Get or create the appropriate model instance for a power."""
        if power not in self._model_instances:
            model_name = POWER_MODELS[power]
            model_class = MODEL_CLASSES[model_name]
            self._model_instances[power] = model_class()
        return self._model_instances[power]
    
    def prepare_message(self, initiator: str, target: str, turns_left: int, memory: List[str], game_state: str) -> str:
        """Prepare a diplomatic message using the appropriate model."""
        model = self._get_model(initiator)
        prompt = self.prompt_templates["draft_message"].format(
            initiator_power=initiator,
            target_power=target,
            game_state=game_state,
            turns_left=turns_left,
            memory="\n".join(memory)
        )
        return model.call_model(prompt)
    
    def decide_order(self, power: str, memory: List[str], possible_orders: Dict[str, List[str]], game_state: str) -> str:
        """Decide on military orders using the appropriate model."""
        print(f"Deciding orders for {power}")
        model = self._get_model(power)
        
        # Format possible orders for the prompt
        formatted_orders = []
        for location, orders in possible_orders.items():
            formatted_orders.append(f"{location}:")
            for order in orders:
                formatted_orders.append(f"  - {order}")
        
        prompt = self.prompt_templates["orders"].format(
            power_name=power,
            game_state=game_state,
            memory="\n".join(memory),
            possible_orders="\n".join(formatted_orders)
        )
        
        response = model.call_model(prompt)
        print(f"{power}'s reponse: {response}")
        # Extract orders from response
        orders = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith(('A ', 'F ')):  # Army or Fleet orders
                orders.append(line)
        
        return orders
    
    def strategize(self, initiator: str, turns_left: int, memory: List[str], game_state: str) -> List[str]:
        """Determine which powers to negotiate with."""
        model = self._get_model(initiator)
        prompt = self.prompt_templates["strategize"].format(
            power_name=initiator,
            turns_left=turns_left,
            game_state=game_state,
            memory="\n".join(memory)
        )
        response = model.call_model(prompt)
        
        # Extract comma-separated list of power names
        # Look for patterns "ENGLAND,FRANCE,GERMANY"
        power_pattern = r'(?:ENGLAND|FRANCE|GERMANY|ITALY|AUSTRIA|RUSSIA|TURKEY)'
        matches = re.findall(power_pattern, response)
        
        # Filter out the initiator's power and any invalid power names
        valid_powers = [power for power in matches 
                       if power in self.valid_powers and power != initiator]
        
        return valid_powers 