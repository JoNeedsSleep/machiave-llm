import os
import json
from datetime import datetime
from typing import Dict, List
from diplomacy import Game
from diplomacy.utils.export import to_saved_game_format, from_saved_game_format

class GameStateManager:
    def __init__(self, base_dir: str = "game_states"):
        """Initialize the GameStateManager with a base directory for saving states.
        
        Args:
            base_dir (str): Base directory for saving game states
        """
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def _get_timestamp_dir(self) -> str:
        """Get the current timestamp directory name."""
        return datetime.now().strftime("%Y_%m_%d_%H")

    def save_game_state(self, game: Game, memory: Dict[str, List[str]], metadata: Dict = None) -> str:
        """Save the current game state, memory, and metadata to a timestamped directory.
        
        Args:
            game: The current game state
            memory: Dictionary mapping powers to their memory lists
            metadata: Additional metadata to save (optional)
            
        Returns:
            str: Path to the saved state directory
        """
        # Create timestamped directory
        timestamp_dir = self._get_timestamp_dir()
        save_dir = os.path.join(self.base_dir, timestamp_dir)
        os.makedirs(save_dir, exist_ok=True)

        # Save game state
        game_state = to_saved_game_format(game)
        with open(os.path.join(save_dir, "game_state.json"), "w") as f:
            json.dump(game_state, f, indent=2)

        # Save memory
        with open(os.path.join(save_dir, "memory.json"), "w") as f:
            json.dump(memory, f, indent=2)

        # Save metadata if provided
        if metadata:
            with open(os.path.join(save_dir, "metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2)

        return save_dir

    def load_game_state(self, timestamp_dir: str) -> tuple[Game, Dict[str, List[str]], Dict]:
        """Load a game state from a timestamped directory.
        
        Args:
            timestamp_dir: Directory name in format YYYY_MM_DD_HH
            
        Returns:
            tuple: (Game object, memory dictionary, metadata dictionary)
        """
        save_dir = os.path.join(self.base_dir, timestamp_dir)
        
        # Load game state
        with open(os.path.join(save_dir, "game_state.json"), "r") as f:
            game_state = json.load(f)
        game = from_saved_game_format(game_state)

        # Load memory
        with open(os.path.join(save_dir, "memory.json"), "r") as f:
            memory = json.load(f)

        # Load metadata if it exists
        metadata = {}
        metadata_path = os.path.join(save_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

        return game, memory, metadata

    def list_saved_states(self) -> List[str]:
        """List all saved state directories.
        
        Returns:
            List[str]: List of timestamp directory names
        """
        if not os.path.exists(self.base_dir):
            return []
        return sorted([d for d in os.listdir(self.base_dir) 
                      if os.path.isdir(os.path.join(self.base_dir, d))], 
                     reverse=True) 