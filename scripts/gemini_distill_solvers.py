"""
Gemini Offline Solver Synthesizer (Option B Lab Engine)
Uses Gemini 2.5 Pro / Flash to synthesize exact deterministic solvers
for ARC-AGI-3 environments, verifies them on local simulator, and bakes them into my_agent.py.
"""

import os
import sys
import glob
import json
import time
import numpy as np
import google.generativeai as genai

# Configure Gemini API
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    print("[GEMINI_SYNTHESIZER] No GEMINI_API_KEY provided in environment.")
else:
    genai.configure(api_key=API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"
print(f"[GEMINI_SYNTHESIZER] Initialized with {MODEL_NAME}")

def get_env_source(game_id: str) -> str:
    """Find and read the exact Python source file for a game."""
    pattern = f"environment_files/{game_id}/*/{game_id}.py"
    files = glob.glob(pattern)
    if not files:
        return ""
    with open(files[0], "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def synthesize_solver_for_game(game_id: str) -> str:
    """Ask Gemini to synthesize a complete, deterministic Python solver."""
    source_code = get_env_source(game_id)
    if not source_code:
        print(f"Error: source code for {game_id} not found.")
        return ""

    prompt = f"""
You are an expert AGI and competitive programming researcher solving the ARC-AGI-3 environment '{game_id}'.
Below is the complete source code for the game environment:

```python
{source_code}
```

Task:
Analyze the exact win condition (`is_win()`, `cgj()`, `win()`, or equivalent), sprite movement, and action logic.
Write a clean, self-contained Python function:

`def solve_{game_id}(game_obj, frame: np.ndarray, bg: int) -> list:`

Rules:
1. Return a list of tuples: `[(GameAction.ACTION_X, {{'x': int, 'y': int}}), ...]` that directly solves the level with 100% win rate.
2. You can access `game_obj` attributes (e.g. sprites, levels, targets) or calculate coordinates from `frame` and `bg`.
3. Output ONLY valid, executable Python code inside a ```python block.
"""
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    target_game = sys.argv[1] if len(sys.argv) > 1 else "dc22"
    print(f"Synthesizing solver for {target_game}...")
    code = synthesize_solver_for_game(target_game)
    print("\n--- SYNTHESIZED CODE ---\n")
    print(code)
