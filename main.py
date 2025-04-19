import json
import os
from diplomacy import Game
from diplomacy.utils.export import to_saved_game_format
import os
from dotenv import load_dotenv
from diplomacy_pipeline import DiplomacyPipeline
from config import POWER_MODELS
from game_state_manager import GameStateManager

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)


def main(debug_mode: bool = False, load_state: str = None):
    # Initialize the game state manager
    state_manager = GameStateManager()
    
    if load_state:
        # Load existing game state
        print(f"Loading game state from {load_state}...")
        game, memory, metadata = state_manager.load_game_state(load_state)
        powers = list(POWER_MODELS.keys())
        pipeline = DiplomacyPipeline(powers, game, debug_mode=debug_mode)
        pipeline.memory = memory  # Restore memory state
    else:
        # Initialize new game
        game = Game()
        powers = list(POWER_MODELS.keys())
        pipeline = DiplomacyPipeline(powers, game, debug_mode=debug_mode)
    
    # Run the game
    pipeline.run_game()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Run in debug mode with random orders')
    parser.add_argument('--load', type=str, help='Load a saved game state from the specified timestamp directory (format: YYYY_MM_DD_HH)')
    args = parser.parse_args()
    main(debug_mode=args.debug, load_state=args.load)