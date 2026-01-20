"""Strategy loading and execution for the 32word library."""

import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class Strategy:
    """A pre-computed Wordle strategy with second-guess lookups.

    Supports both legacy format (full clues dict) and new lightweight format
    (selected patterns with phase3_lookup reference).
    """

    def __init__(self, version="v1.0", data: dict = None, lookup_table: dict = None, phase3_lookup: dict = None):
        """Initialize a strategy.

        Args:
            version: Strategy version string
            data: Strategy data dict (for lightweight format)
            lookup_table: Full lookup table (for legacy format or populated from phase3_lookup)
            phase3_lookup: Phase 3 lookup table for pattern-based filtering
        """
        self.version = version
        self.data = data or {}
        self.lookup_table = lookup_table or {}
        self._phase3_lookup = phase3_lookup
        self._metadata = self.data.get("metadata", {})
        self.first_guess_word = self.data.get("first_guess", "ATONE")
        self.remainder_guess2 = self.data.get("remainder_guess2")
        self._selected_patterns = self.data.get("selected_patterns")

        # For v1.0 legacy format, the lookup_table is the full dict keyed by first guess
        # Extract the ATONE strategy from it
        if self.version == "v1.0" and self.lookup_table and "ATONE" in self.lookup_table:
            self.lookup_table = {"ATONE": self.lookup_table["ATONE"]}
            self.first_guess_word = "ATONE"

        # Build clues from phase3_lookup if needed
        if self._selected_patterns and not self.lookup_table:
            self._build_clues_from_lookup(phase3_lookup)

    def _build_clues_from_lookup(self, phase3_lookup: dict) -> None:
        """Build clues dict from phase3_lookup and selected patterns."""
        if not phase3_lookup:
            # Load phase3_lookup if not provided
            data_dir = Path(__file__).parent.joinpath('data')
            lookup_path = data_dir / 'phase3_lookup.json'
            if lookup_path.exists():
                with open(lookup_path, 'r') as f:
                    phase3_lookup = json.load(f)
            else:
                return

        self._phase3_lookup = phase3_lookup
        self.lookup_table = {}
        first_guess_upper = self.first_guess_word.upper()

        if first_guess_upper not in phase3_lookup:
            return

        first_guess_strategy = phase3_lookup[first_guess_upper]

        # Filter to only selected patterns
        for pattern in self._selected_patterns:
            if pattern in first_guess_strategy:
                # Create a clues dict similar to the old format
                candidates = first_guess_strategy[pattern]
                if candidates:
                    self.lookup_table[pattern] = {
                        'second_guess': candidates[0]['second_guess'],
                        'pattern_id': pattern
                    }

    def first_guess(self) -> str:
        """Return the recommended first guess."""
        return self.first_guess_word

    def second_guess(self, clue: Tuple[str, str, str, str, str]) -> Optional[str]:
        """Get the optimal second guess for a given first-guess clue.

        Args:
            clue: A tuple of 5 characters representing the Wordle clue
              'G' for green, 'Y' for yellow, 'B' for black/gray

        Returns:
            The optimal second guess word, or remainder_guess2, or None if not found
        """
        # Convert clue tuple to string pattern
        # Replace 'B' (black) with 'X' (the convention used in strategy lookup)
        clue_list = list(clue)
        clue_list = ['X' if c == 'B' else c for c in clue_list]
        clue_pattern = ''.join(clue_list)

        # For v1.0 legacy format, lookup_table is {FIRST_GUESS: {CLUE_PATTERN: [candidates]}}
        if self.version == "v1.0" and self.first_guess_word in self.lookup_table:
            first_guess_data = self.lookup_table[self.first_guess_word]
            if clue_pattern in first_guess_data:
                candidates = first_guess_data[clue_pattern]
                if candidates and len(candidates) > 0:
                    return candidates[0]['second_guess']

        # For new lightweight format, lookup_table is {CLUE_PATTERN: {second_guess: ...}}
        elif clue_pattern in self.lookup_table:
            return self.lookup_table[clue_pattern]['second_guess']

        # Fall back to remainder_guess2 if available
        if self.remainder_guess2:
            return self.remainder_guess2

        # Fall back to phase3_lookup if available
        if self._phase3_lookup:
            first_guess_upper = self.first_guess_word.upper()
            if first_guess_upper in self._phase3_lookup:
                first_guess_table = self._phase3_lookup[first_guess_upper]
                if clue_pattern in first_guess_table:
                    candidates = first_guess_table[clue_pattern]
                    if candidates:
                        return candidates[0]['second_guess']

        return None

    def metadata(self) -> dict:
        """Return strategy metadata."""
        if self._metadata:
            return self._metadata.copy()

        return {
            'version': self.version,
            'first_guess': self.first_guess_word,
            'penalty_function': 'expected_remaining',
            'depth': 2,
            'created': '2026-01-15',
            'description': f'Strategy for {self.first_guess_word}',
        }

    def clue_count(self) -> int:
        """Return the number of clue patterns in this strategy."""
        if self._selected_patterns:
            return len(self._selected_patterns)
        return len(self.lookup_table)


def load_strategy(version: str = "v1.0") -> Strategy:
    """Load a pre-computed strategy table.

    Supports both legacy v1.0 format and new lightweight depth-based formats.

    Examples:
        load_strategy("v1.0")  # Legacy format
        load_strategy("2d-8r-trice")  # New lightweight format

    Args:
        version: Strategy version (default "v1.0")

    Returns:
        A Strategy object with populated lookup table
    """
    data_dir = Path(__file__).parent.joinpath('data')

    # Check for lightweight format in strategies subdirectory
    strategy_file = data_dir / 'strategies' / f'{version.replace("-", "_")}.json'

    # Fall back to legacy location
    if not strategy_file.exists():
        strategy_file = data_dir / f'{version}.json'

    data = {}
    lookup_table = {}
    phase3_lookup = None

    if strategy_file.exists():
        with open(strategy_file, 'r') as f:
            data = json.load(f)

        # Check if this is a lightweight format
        if data.get("lookup_source") == "phase3_lookup":
            # Load phase3_lookup for this strategy
            lookup_path = data_dir / 'phase3_lookup.json'
            if lookup_path.exists():
                with open(lookup_path, 'r') as f:
                    phase3_lookup = json.load(f)
        else:
            # Legacy format - data is the lookup table itself
            lookup_table = data

    return Strategy(version=version, data=data, lookup_table=lookup_table, phase3_lookup=phase3_lookup)


def load_strategy_by_components(guess1: str, depth: int) -> Strategy:
    """Load a strategy by first guess and depth.

    Args:
        guess1: First guess word (e.g., "TRICE", "CRONE")
        depth: Number of clue patterns to memorize (e.g., 8, 16, 32)

    Returns:
        A Strategy object for the specified guess1 and depth

    Example:
        strategy = load_strategy_by_components("TRICE", 8)
    """
    version = f"2d-{depth}r-{guess1.lower()}"
    return load_strategy(version)


def list_strategies_by_depth(depth: int) -> List[dict]:
    """List all available strategies for a given depth.

    Args:
        depth: Clue count (8, 16, 32, 64, 243)

    Returns:
        List of strategy metadata dicts, sorted by win_rate descending

    Example:
        strategies = list_strategies_by_depth(8)
        for s in strategies:
            print(f"{s['guess1']}: {s['win_rate_2d']*100:.1f}%")
    """
    data_dir = Path(__file__).parent.joinpath('data')
    strategies_dir = data_dir / 'strategies'

    strategies = []
    if not strategies_dir.exists():
        return strategies

    pattern = f"2d_{depth}r_*.json"
    for filepath in strategies_dir.glob(pattern):
        with open(filepath, 'r') as f:
            data = json.load(f)
            if "metadata" in data:
                strategies.append(data["metadata"])

    # Sort by win rate descending
    strategies.sort(key=lambda s: -s.get("win_rate_2d", 0))

    return strategies


def list_all_strategies() -> List[dict]:
    """List all available strategies across all depths.

    Returns:
        List of all strategy metadata dicts, sorted by depth then win_rate

    Example:
        all_strategies = list_all_strategies()
    """
    data_dir = Path(__file__).parent.joinpath('data')
    strategies_dir = data_dir / 'strategies'

    strategies = []
    if not strategies_dir.exists():
        return strategies

    for filepath in strategies_dir.glob("2d_*.json"):
        with open(filepath, 'r') as f:
            data = json.load(f)
            if "metadata" in data:
                strategies.append(data["metadata"])

    # Sort by depth, then win rate
    strategies.sort(key=lambda s: (s.get("clue_count", 0), -s.get("win_rate_2d", 0)))

    return strategies


def get_second_guess(strategy: Strategy, first_clue: tuple) -> Optional[str]:
    """Convenience function for getting the optimal second guess.

    Args:
        strategy: A Strategy object (from load_strategy)
        first_clue: The clue tuple from the first guess

    Returns:
        The optimal second guess word, or None if not found
    """
    return strategy.second_guess(first_clue)


# Phase 4.3: First guess selection and strategy lookup functions

# Cache for first guess options and strategy lookup (loaded once)
_first_guess_cache: Optional[List[Dict]] = None
_strategy_lookup_cache: Optional[Dict] = None


def _load_first_guess_options() -> List[Dict]:
    """Load Phase 2 naive-32 first guess options from data file."""
    global _first_guess_cache
    
    if _first_guess_cache is not None:
        return _first_guess_cache
    
    data_dir = Path(__file__).parent.joinpath('data')
    naive_32_file = data_dir.joinpath('phase2_naive_32.json')
    
    if not naive_32_file.exists():
        _first_guess_cache = []
        return _first_guess_cache
    
    with open(naive_32_file, 'r') as f:
        options = json.load(f)
    
    # Transform to match expected format
    _first_guess_cache = []
    for entry in options:
        transformed = {
            'first_guess': entry['guess'].upper(),
            'rank': entry['rank'],
            'expected_remaining': entry.get('expected_remaining', 0.0),
            'metrics': {
                'max_remaining': entry.get('max_remaining', 0),
                'clue_diversity': entry.get('clue_diversity', 0),
                'variance': entry.get('variance', 0.0),
                'std_dev': entry.get('std_dev', 0.0)
            },
            'available': True,
            'coverage': 0.8125  # Default coverage estimate
        }
        _first_guess_cache.append(transformed)
    
    return _first_guess_cache


def _load_strategy_lookup() -> Dict:
    """Load Phase 3 strategy lookup from data file."""
    global _strategy_lookup_cache
    
    if _strategy_lookup_cache is not None:
        return _strategy_lookup_cache
    
    data_dir = Path(__file__).parent.joinpath('data')
    lookup_file = data_dir.joinpath('phase3_lookup.json')
    
    if not lookup_file.exists():
        _strategy_lookup_cache = {}
        return _strategy_lookup_cache
    
    with open(lookup_file, 'r') as f:
        _strategy_lookup_cache = json.load(f)
    
    return _strategy_lookup_cache


def get_available_first_guesses() -> List[Dict]:
    """Get all available first guess options with metrics.
    
    Returns all 32 naive patterns from Phase 2 analysis, sorted by rank.
    Each entry includes rank, guess, expected_remaining, and other metrics.
    
    Returns:
        List of dictionaries, each containing:
        - first_guess: str (the word)
        - rank: int (1-32)
        - expected_remaining: float
        - max_remaining: int
        - clue_diversity: int
        - variance: float
        - std_dev: float
        - total_targets: int
        - available: bool (always True for these)
        - coverage: float (estimated coverage, default 0.8125)
    """
    return _load_first_guess_options().copy()


def select_first_guess(user_choice: str) -> Optional[Dict]:
    """Select and validate a first guess from available options.
    
    Args:
        user_choice: The first guess word selected by user (e.g., "RAISE", "STALE")
        
    Returns:
        Dictionary with first guess information, or None if not found:
        {
            "first_guess": "RAISE",
            "rank": 1,
            "expected_remaining": 90.15,
            "metrics": {
                "max_remaining": 240,
                "clue_diversity": 137,
                "variance": 1234.56,
                "std_dev": 35.12
            },
            "available": true,
            "coverage": 0.8125
        }
    """
    available = get_available_first_guesses()
    user_choice_upper = user_choice.upper()
    
    for option in available:
        if option['first_guess'] == user_choice_upper:
            return option
    
    return None


def get_strategy_for_first_guess(first_guess: str) -> Dict[str, str]:
    """Get all second-guess recommendations for a first guess.
    
    Returns a dictionary mapping clue patterns to recommended second guesses.
    This provides full strategy coverage for the selected first guess.
    
    Args:
        first_guess: The first guess word (e.g., "RAISE", "ATONE")
        
    Returns:
        Dictionary mapping clue pattern strings to second guess words:
        {
            "GXXXG": "AGILE",
            "GXXXX": "ALIAS",
            "XXGXG": "BROSE",
            ...
        }
        Returns empty dict if first guess not found in lookup.
    """
    lookup = _load_strategy_lookup()
    first_guess_upper = first_guess.upper()
    
    if first_guess_upper not in lookup:
        return {}
    
    # Extract second guesses from lookup structure
    # Lookup structure: {first_guess: {clue_pattern: [{second_guess: ..., rank: ...}, ...]}}
    first_guess_data = lookup[first_guess_upper]
    result = {}
    
    for clue_pattern, candidates in first_guess_data.items():
        if candidates and len(candidates) > 0:
            # Get the top-ranked (rank 1) second guess
            result[clue_pattern] = candidates[0]['second_guess']
    
    return result


def get_second_guess_recommendation(first_guess: str, clue: tuple) -> Optional[str]:
    """Get recommended second guess for a (first_guess, clue) pair.
    
    Args:
        first_guess: The first guess word
        clue: The clue tuple ('G', 'Y', 'B', ...)
        
    Returns:
        Recommended second guess word, or None if not found
    """
    lookup = _load_strategy_lookup()
    first_guess_upper = first_guess.upper()
    
    if first_guess_upper not in lookup:
        return None
    
    # Convert clue tuple to string pattern
    # Replace 'B' (black) with 'X' (the convention used in strategy lookup)
    clue_list = list(clue)
    clue_list = ['X' if c == 'B' else c for c in clue_list]
    clue_pattern = ''.join(clue_list)
    
    # Get candidates for this clue pattern
    first_guess_data = lookup[first_guess_upper]
    candidates = first_guess_data.get(clue_pattern)
    
    if not candidates or len(candidates) == 0:
        return None
    
    # Return the top-ranked (rank 1) second guess
    return candidates[0]['second_guess']
