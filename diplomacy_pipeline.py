from typing import List, Dict
from utils import LLMUtils
from api import ModelAPI
from config import TURNS_PER_ROUND
from diplomacy import Game
from game_state_manager import GameStateManager
import time
import random

class DiplomacyPipeline:
    def __init__(self, powers: List[str], game: Game, debug_mode: bool = False):
        self.powers = powers
        self.turns_per_round = TURNS_PER_ROUND
        self.memory: Dict[str, List[str]] = {power: [] for power in powers}
        self.utils = LLMUtils()
        self.game = game
        self.debug_mode = debug_mode
        self.state_manager = GameStateManager()
        
    def _generate_random_order(self, power: str, possible_orders: Dict[str, List[str]]) -> str:
        """Generate a random valid order for testing."""
        # Get all possible locations for this power
        orderable_locations = [loc for loc in self.game.get_orderable_locations(power) if possible_orders[loc]]
        if not orderable_locations:
            return ""
            
        # Pick a random location
        location = random.choice(orderable_locations)
        # Get possible orders for this location
        possible_moves = possible_orders[location]
        if not possible_moves:
            return ""
            
        # Pick a random order
        return random.choice(possible_moves)
        
    def _save_current_state(self):
        """Save the current game state, memory, and metadata."""
        metadata = {
            "phase": self.game.current_short_phase,
            "turns_per_round": self.turns_per_round,
            "debug_mode": self.debug_mode,
            "timestamp": int(time.time())
        }
        return self.state_manager.save_game_state(self.game, self.memory, metadata)
        
    def run_game(self):
        while not self.game.is_game_done:
            # Get current game state and possible orders
            board_state = self.game.get_state()
            possible_orders = self.game.get_all_possible_orders()
            # Negotiation phase
            if self.debug_mode:
                print("Debug mode is on")
            else:
                for i in range(self.turns_per_round):
                    print(f"Round {i+1}")
                    inbox = {power: [] for power in self.powers}
                
                for initiator in self.powers:
                    targets = self.utils.strategize(
                        initiator, 
                        self.turns_per_round - i,
                        self.memory[initiator],
                        game_state=board_state
                    )
                    print(f"{initiator}'s targets: {targets}")
                    for target in targets:
                        message = self.utils.prepare_message(
                            initiator,
                            target,
                            self.turns_per_round - i,
                            self.memory[initiator],
                            board_state
                        )
                        print(f"{initiator} to {target}: {message}")
                        inbox[initiator].append(message)
                        inbox[target].append(message)
                
                # Update memory with received messages
                for power in self.powers:
                    self.memory[power].extend(inbox[power])
            
            # Order phase
            for power in self.powers:
                print(power)
                power_possible_orders = {
                    loc: possible_orders[loc] 
                    for loc in self.game.get_orderable_locations(power)
                    if possible_orders[loc]
                }
                
                # Get orders from LLM
                orders = self.utils.decide_order(
                    power, 
                    self.memory[power],
                    power_possible_orders,
                    board_state
                )
                
                self.game.set_orders(power, orders)
            
            # Process the game to move to next phase
            orders = self.game.get_orders()
            for power in self.powers:
                self.memory[power].append(
                    f"After a round of negotiations in {self.game.get_current_phase()}, orders are as follows: {orders}"
                ) 
            self.game.process()
            print(f"Game state after processing: {self.game.get_state()}")
            
            # Update memory with new game state
            new_state = self.game.get_state()
            for power in self.powers:
                self.memory[power].append(
                    f"After a round of orders at the end of {self.game.get_current_phase()}, the board states are as follows: {new_state}"
                )
            
            # Save game state after each phase
            save_dir = self._save_current_state()
            print(f"Game state saved to: {save_dir}") 