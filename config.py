from typing import Dict, Type
from api import ModelAPI, OpenAIModel

# Configuration for which model each power uses
POWER_MODELS: Dict[str, str] = {
    "FRANCE": "gpt-4o-mini",      # France uses GPT-4o-mini
    "ENGLAND": "gpt-4o-mini",      # England uses GPT-4o-mini 
    "GERMANY": "gpt-4o-mini",      # Germany uses GPT-4o-mini
    "ITALY": "gpt-4o-mini",      # Italy uses GPT-4o-mini
    "AUSTRIA": "gpt-4o-mini",      # Austria uses GPT-4o-mini
    "RUSSIA": "gpt-4o-mini",      # Russia uses GPT-4o-mini
    "TURKEY": "gpt-4o-mini"       # Turkey uses GPT-4o-mini
}

# Map model names to their implementation classes
MODEL_CLASSES: Dict[str, Type[ModelAPI]] = {
    "gpt-4o-mini": OpenAIModel
}

# Game configuration
TURNS_PER_ROUND = 1