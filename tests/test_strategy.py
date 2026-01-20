"""Tests for the strategy functions of the 32word library."""

from word32.strategy import load_strategy, get_second_guess, Strategy

def test_load_strategy():
    strategy = load_strategy("v1.0")
    assert isinstance(strategy, Strategy)
    assert strategy.version == "v1.0"
    assert strategy.first_guess() == "ATONE"

def test_get_second_guess():
    strategy = load_strategy()
    # Test with a valid clue pattern from ATONE: all black (XXXXX -> no letters match)
    clue = ('B', 'B', 'B', 'B', 'B')
    second_guess = get_second_guess(strategy, clue)
    assert isinstance(second_guess, str)
    assert len(second_guess) == 5
    assert second_guess.upper() == "PIRLS"

    # Test with another clue pattern: last letter green (XXXXG)
    clue = ('B', 'B', 'B', 'B', 'G')
    second_guess = strategy.second_guess(clue)
    assert isinstance(second_guess, str)
    assert second_guess.upper() == "GERLE"

def test_strategy_metadata():
    strategy = load_strategy()
    metadata = strategy.metadata()
    assert isinstance(metadata, dict)
    assert metadata['version'] == 'v1.0'
    assert 'description' in metadata


# Tests for new depth-based strategies (v0.2.0)

def test_load_2d_8r_trice():
    """Test loading 2d-8r-trice strategy."""
    strategy = load_strategy("2d-8r-trice")
    assert isinstance(strategy, Strategy)
    assert strategy.first_guess() == "TRICE"
    assert strategy.clue_count() == 8
    assert strategy.metadata()['win_rate_2d'] > 0.35
    assert strategy.metadata()['guess1'] == "TRICE"


def test_load_2d_8r_siren():
    """Test loading 2d-8r-siren strategy."""
    strategy = load_strategy("2d-8r-siren")
    assert strategy.first_guess() == "SIREN"
    assert strategy.clue_count() == 8


def test_load_strategy_by_components():
    """Test loading strategy by first guess and depth components."""
    from word32 import load_strategy_by_components

    strategy = load_strategy_by_components("TRICE", 8)
    assert strategy.first_guess() == "TRICE"
    assert strategy.clue_count() == 8
    assert strategy.version == "2d-8r-trice"


def test_load_strategy_by_components_different_guesses():
    """Test loading different first guesses."""
    from word32 import load_strategy_by_components

    for guess in ["CRONE", "SIREN", "DEALT"]:
        strategy = load_strategy_by_components(guess, 8)
        assert strategy.first_guess() == guess
        assert strategy.clue_count() == 8


def test_list_strategies_by_depth():
    """Test listing strategies for a specific depth."""
    from word32 import list_strategies_by_depth

    strategies_8r = list_strategies_by_depth(8)

    assert len(strategies_8r) >= 10  # At least top 10
    assert all(s["clue_count"] == 8 for s in strategies_8r)

    # Should be sorted by win_rate descending
    for i in range(len(strategies_8r) - 1):
        assert strategies_8r[i]["win_rate_2d"] >= strategies_8r[i+1]["win_rate_2d"]


def test_list_all_strategies():
    """Test listing all strategies."""
    from word32 import list_all_strategies

    all_strategies = list_all_strategies()

    assert len(all_strategies) >= 10
    assert all("clue_count" in s for s in all_strategies)
    assert all("win_rate_2d" in s for s in all_strategies)


def test_2d_8r_second_guess_selected_pattern():
    """Test that second guess lookup works for selected patterns."""
    strategy = load_strategy("2d-8r-trice")

    # XXGXX is one of TRICE's selected patterns
    clue = ("X", "X", "G", "X", "X")
    second = strategy.second_guess(clue)
    assert second is not None
    assert isinstance(second, str)
    assert len(second) == 5


def test_2d_8r_second_guess_remainder():
    """Test fallback to remainder_guess2 for non-selected patterns."""
    strategy = load_strategy("2d-8r-trice")
    remainder = strategy.remainder_guess2
    assert remainder == "SALON"

    # Use a pattern not in the 8 selected
    clue = ("G", "G", "G", "Y", "B")
    second = strategy.second_guess(clue)
    assert second == remainder


def test_backward_compat_v1_0():
    """Test that v1.0 still works (backward compatibility)."""
    strategy = load_strategy("v1.0")

    assert isinstance(strategy, Strategy)
    assert strategy.first_guess() == "ATONE"

    # Should still return valid second guesses
    clue = ("X", "X", "X", "X", "X")
    second = strategy.second_guess(clue)
    assert isinstance(second, str)
    assert len(second) == 5


def test_phase_4_3_functions_still_work():
    """Ensure Phase 4.3 functions remain functional after v0.2.0 changes."""
    from word32 import (
        get_available_first_guesses,
        select_first_guess,
        get_strategy_for_first_guess,
        get_second_guess_recommendation
    )

    # get_available_first_guesses should still return 32
    guesses = get_available_first_guesses()
    assert len(guesses) == 32

    # select_first_guess should still work
    selected = select_first_guess("STARE")
    assert selected is not None
    assert selected['first_guess'] == "STARE"

    # get_strategy_for_first_guess should still return dict
    strategy_dict = get_strategy_for_first_guess("STARE")
    assert isinstance(strategy_dict, dict)
    assert len(strategy_dict) > 0

    # get_second_guess_recommendation should still work
    clue = ("X", "Y", "X", "X", "G")
    recommendation = get_second_guess_recommendation("STARE", clue)
    assert isinstance(recommendation, str)
    assert len(recommendation) == 5
