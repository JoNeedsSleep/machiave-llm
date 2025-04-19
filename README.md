# MachiaveLLM

A Diplomacy game implementation where LLMs test out their Machiavellian prowess - and we watch and observe!

1. Clone the repository:
```bash
git clone https://github.com/JoNeedsSleep/machiave-llm.git
cd machiave-llm
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run a new game:
```bash
python main.py
```

Run in debug mode:
```bash
python main.py --debug
```

Load a saved game state:
```bash
python main.py --load YYYY_MM_DD_HH
```

## Project Structure

- `main.py`: Entry point for the game
- `diplomacy_pipeline.py`: Main game logic and flow
- `utils.py`: Utility functions for LLM interactions
- `api.py`: API interface for different LLM providers
- `config.py`: Configuration settings
- `game_state_manager.py`: Handles saving and loading game states
- `Prompt_*.txt`: Templates for LLM prompts

## License

MIT License 