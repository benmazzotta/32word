"""
32word - The game engine for 3-2-Word: Solve Wordle in three guesses.
"""

__version__ = "0.1.0"

from .core import generate_clue, filter_targets, is_valid_word, get_remaining_candidates
from .strategy import load_strategy, get_second_guess, Strategy
from .data_loader import VALID_TARGETS, VALID_GUESSES

__all__ = [
    "generate_clue",
    "filter_targets",
    "is_valid_word",
    "get_remaining_candidates",
    "load_strategy",
    "get_second_guess",
    "Strategy",
    "VALID_TARGETS",
    "VALID_GUESSES",
]
