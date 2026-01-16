"""Strategy loading and execution for the 32word library."""

import json
from pathlib import Path
from typing import Optional


class Strategy:
    """A pre-computed Wordle strategy with second-guess lookups."""

    def __init__(self, version="v1.0", lookup_table: dict = None):
        self.version = version
        self.first_guess_word = "STARE"
        self.lookup_table = lookup_table or {}

    def first_guess(self) -> str:
        """Return the recommended first guess."""
        return self.first_guess_word

    def second_guess(self, clue: tuple) -> Optional[str]:
        """Get the optimal second guess for a given first-guess clue.

        Args:
            clue: A tuple of 5 characters representing the Wordle clue
              'G' for green, 'Y' for yellow, 'B' for black/gray

        Returns:
            The optimal second guess word, or None if clue not in lookup table
        """
        if not self.lookup_table:
            return None

        # Convert clue tuple to string pattern
        # Replace 'B' (black) with 'X' (the convention used in strategy lookup)
        clue_list = list(clue)
        clue_list = ['X' if c == 'B' else c for c in clue_list]
        clue_pattern = ''.join(clue_list)

        # Get the lookup table for this first guess
        first_guess_table = self.lookup_table.get(self.first_guess_word)
        if not first_guess_table:
            return None

        # Get candidates for this clue pattern
        candidates = first_guess_table.get(clue_pattern)
        if not candidates or len(candidates) == 0:
            return None

        # Return the top-ranked (rank 1) second guess
        return candidates[0]['second_guess']

    def metadata(self) -> dict:
        return {
            'version': self.version,
            'penalty_function': 'expected_remaining',
            'depth': 2,
            'symmetric': True,
            'created': '2026-01-15',
            'description': 'Optimal two-deep strategy minimizing expected remaining targets'
        }


def load_strategy(version: str = "v1.0") -> Strategy:
    """Load a pre-computed strategy table.

    Args:
        version: Strategy version (default "v1.0")

    Returns:
        A Strategy object with populated lookup table
    """
    # Load the strategy JSON file
    data_dir = Path(__file__).parent.joinpath('data')
    strategy_file = data_dir.joinpath(f'{version}.json')

    lookup_table = {}
    if strategy_file.exists():
        with open(strategy_file, 'r') as f:
            lookup_table = json.load(f)

    return Strategy(version=version, lookup_table=lookup_table)


def get_second_guess(strategy: Strategy, first_clue: tuple) -> Optional[str]:
    """Convenience function for getting the optimal second guess.

    Args:
        strategy: A Strategy object (from load_strategy)
        first_clue: The clue tuple from the first guess

    Returns:
        The optimal second guess word, or None if not found
    """
    return strategy.second_guess(first_clue)
