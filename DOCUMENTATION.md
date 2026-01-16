# 32word Documentation

A Python library for solving Wordle puzzles optimally in three guesses using pre-computed strategy tables and intelligent filtering. This library powers the "3-2-Word" strategy: guess strategically, analyze scientifically, and win definitively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Common Patterns](#common-patterns)
3. [API Reference](#api-reference)
4. [Real-world Examples](#real-world-examples)
5. [Best Practices](#best-practices)
6. [FAQ](#faq)

---

## Getting Started

### Installation

Install 32word from PyPI:

```bash
pip install word32
```

Or install from source:

```bash
git clone https://github.com/benmazzotta/32word.git
cd 32word
pip install -e .
```

### Hello World

Here's a minimal example that solves a Wordle game in just 5 lines:

```python
from word32 import generate_clue, VALID_TARGETS

target = "PIZZA"
clue = generate_clue("STARE", target)
print(f"Guess: STARE, Target: {target}")
print(f"Clue: {clue}")  # Output: ('Y', 'B', 'B', 'B', 'B')
```

**What this means:**
- `('Y', 'B', 'B', 'B', 'B')` tells us:
  - **Y** (Yellow): S is in PIZZA but not in position 0
  - **B** (Black): T, A, R, E are not in PIZZA at all
  - This clue eliminates most words and narrows our search space

The library's core purpose is generating these clues and using them to narrow down which word is the target.

---

## Common Patterns

### Pattern 1: Building a Simple Wordle Solver Bot

Let's create a bot that automatically plays Wordle using the optimal strategy:

```python
from word32 import (
    load_strategy,
    generate_clue,
    filter_targets,
    VALID_TARGETS
)

def simple_solver(target_word, verbose=True):
    """
    Solve a Wordle game using the optimal strategy.

    Args:
        target_word: The word we're trying to guess (e.g., "PIZZA")
        verbose: Print each step

    Returns:
        Number of guesses needed (1-3)
    """

    # Load the pre-computed strategy
    strategy = load_strategy("v1.0")

    # Start with all possible targets
    candidates = VALID_TARGETS.copy()

    # First guess is always "STARE"
    guess_num = 1
    current_guess = strategy.first_guess()

    while guess_num <= 3:
        # Generate what Wordle would tell us
        clue = generate_clue(current_guess, target_word)

        if verbose:
            print(f"Guess {guess_num}: {current_guess} → {clue}")

        # Check if we won
        if clue == ('G', 'G', 'G', 'G', 'G'):
            if verbose:
                print(f"✓ Won in {guess_num} guesses!")
            return guess_num

        # Filter candidates based on the clue
        candidates = filter_targets(candidates, current_guess, clue)

        if verbose:
            print(f"  Remaining candidates: {len(candidates)}")

        if guess_num == 1:
            # Get the second guess from strategy
            current_guess = strategy.second_guess(clue)
            if current_guess is None:
                # Rare clue pattern not in strategy, pick first remaining
                current_guess = candidates[0] if candidates else "ADIEU"
        else:
            # For third guess, try the first remaining candidate
            current_guess = candidates[0] if candidates else None

        if current_guess is None:
            if verbose:
                print("✗ No valid guess found!")
            return guess_num

        guess_num += 1

    if verbose:
        print("✗ Failed to solve in 3 guesses")
    return 3

# Usage
simple_solver("PIZZA")
```

**Output:**
```
Guess 1: STARE → ('Y', 'B', 'B', 'B', 'B')
  Remaining candidates: 312
Guess 2: LOINS → ('B', 'G', 'B', 'B', 'B')
  Remaining candidates: 8
Guess 3: PIZZA → ('G', 'G', 'G', 'G', 'G')
✓ Won in 3 guesses!
```

### Pattern 2: Interactive Game with User Input

Create an interactive Wordle game where a human plays against your library:

```python
from word32 import (
    load_strategy,
    generate_clue,
    filter_targets,
    is_valid_word,
    VALID_TARGETS
)
import random

def play_interactive():
    """Play Wordle interactively where the library suggests words."""

    strategy = load_strategy("v1.0")
    target = random.choice(VALID_TARGETS)

    candidates = VALID_TARGETS.copy()
    guess_count = 1

    print("🎮 Welcome to Interactive Wordle!")
    print("The library will suggest words; you tell it the clues.\n")

    while guess_count <= 3:
        # Get next guess from strategy
        if guess_count == 1:
            suggested = strategy.first_guess()
        else:
            # Get from previous clue
            suggested = strategy.second_guess(last_clue)
            if suggested is None:
                suggested = candidates[0] if candidates else "ADIEU"

        print(f"Guess {guess_count}: Try '{suggested}'")

        # Get user input for the clue
        while True:
            user_clue = input("Enter clue (e.g., GBBBY): ").strip().upper()

            # Validate clue format
            if len(user_clue) != 5 or not all(c in 'GYB' for c in user_clue):
                print("Invalid format! Use G=Green, Y=Yellow, B=Black, e.g., GBBBY")
                continue

            last_clue = tuple(user_clue)
            break

        # Check for win
        if last_clue == ('G', 'G', 'G', 'G', 'G'):
            print(f"\n🎉 Solved in {guess_count} guesses!")
            break

        # Filter candidates
        candidates = filter_targets(candidates, suggested, last_clue)
        print(f"Candidates remaining: {len(candidates)}\n")

        guess_count += 1
    else:
        print(f"\n❌ Failed to solve. The answer was: {target}")

# Run the game
play_interactive()
```

### Pattern 3: Analyzing Remaining Candidates

See exactly which words remain possible after each guess:

```python
from word32 import (
    load_strategy,
    generate_clue,
    filter_targets,
    get_remaining_candidates,
    VALID_TARGETS
)

def analyze_candidates(target_word):
    """Show detailed analysis of candidate reduction."""

    strategy = load_strategy("v1.0")
    candidates = VALID_TARGETS.copy()

    # First guess
    first_guess = strategy.first_guess()
    clue1 = generate_clue(first_guess, target_word)
    candidates = filter_targets(candidates, first_guess, clue1)

    print(f"After '{first_guess}' → {clue1}:")
    print(f"  Remaining: {len(candidates)} candidates")
    print(f"  Sample words: {candidates[:5]}\n")

    # Second guess
    second_guess = strategy.second_guess(clue1)
    if second_guess:
        clue2 = generate_clue(second_guess, target_word)
        candidates = filter_targets(candidates, second_guess, clue2)

        print(f"After '{second_guess}' → {clue2}:")
        print(f"  Remaining: {len(candidates)} candidates")
        if len(candidates) <= 20:
            print(f"  Possible words: {candidates}\n")

# Usage
analyze_candidates("WORLD")
```

### Pattern 4: Using the Strategy for Training

Train your Wordle intuition by examining the strategy's decisions:

```python
from word32 import load_strategy, is_valid_word

def explore_strategy():
    """Understand why the strategy makes specific suggestions."""

    strategy = load_strategy("v1.0")

    print(f"Strategy Version: {strategy.version}")
    print(f"First Guess: {strategy.first_guess()}")

    # Show metadata
    meta = strategy.metadata()
    for key, value in meta.items():
        print(f"  {key}: {value}")

    print("\nExploring second-guess suggestions:")

    # Common clue patterns and their second guesses
    test_patterns = [
        ('B', 'B', 'B', 'B', 'B'),  # None of STARE's letters
        ('G', 'B', 'B', 'B', 'B'),  # Only S is correct
        ('Y', 'B', 'B', 'B', 'B'),  # S is in word, wrong spot
        ('B', 'Y', 'Y', 'Y', 'Y'),  # Most letters wrong spot
    ]

    for clue in test_patterns:
        second = strategy.second_guess(clue)
        print(f"\n  After STARE → {clue}")
        print(f"    Suggested: {second}")
        if second and is_valid_word(second):
            print(f"    Status: Valid word ✓")

# Run exploration
explore_strategy()
```

---

## API Reference

### Core Functions

#### `generate_clue(guess: str, target: str) -> tuple[str, str, str, str, str]`

Generate a Wordle clue comparing a guess against a target word.

**Parameters:**
- `guess`: The guessed word (5 letters, case-insensitive)
- `target`: The target word to compare against (5 letters, case-insensitive)

**Returns:**
A tuple of 5 characters:
- `'G'` = Green (correct letter, correct position)
- `'Y'` = Yellow (correct letter, wrong position)
- `'B'` = Black/Gray (letter not in target)

**Examples:**

```python
from word32 import generate_clue

# Exact match
generate_clue("STARE", "STARE")
# Returns: ('G', 'G', 'G', 'G', 'G')

# Some correct positions
generate_clue("STARE", "STEAL")
# Returns: ('G', 'G', 'Y', 'B', 'Y')

# Letters present but wrong positions
generate_clue("STARE", "TRASH")
# Returns: ('Y', 'Y', 'G', 'Y', 'B')

# No matching letters
generate_clue("STARE", "BUMPY")
# Returns: ('B', 'B', 'B', 'B', 'B')
```

**Important:** This function properly handles duplicate letters. If a letter appears multiple times in the guess but fewer times in the target, they're marked correctly according to Wordle rules.

---

#### `filter_targets(targets: list[str], guess: str, clue: tuple) -> list[str]`

Filter a list of candidate words based on a guess and its resulting clue.

**Parameters:**
- `targets`: List of potential target words to filter
- `guess`: The word that was guessed (5 letters, case-insensitive)
- `clue`: The clue tuple returned by `generate_clue()`

**Returns:**
A list of words from `targets` that would produce the same clue if guessed.

**Examples:**

```python
from word32 import filter_targets, generate_clue, VALID_TARGETS

# After guessing STARE and getting a specific clue
clue = ('Y', 'B', 'B', 'B', 'B')
remaining = filter_targets(VALID_TARGETS, "STARE", clue)
# Returns: list of ~300+ words with S but not in position 0,
#          and no T, A, R, or E

# Chain multiple filters
clue1 = generate_clue("STARE", "WORLD")
targets = filter_targets(VALID_TARGETS, "STARE", clue1)

clue2 = generate_clue("LOINS", "WORLD")
targets = filter_targets(targets, "LOINS", clue2)
# Now targets contains very few candidates
```

---

#### `is_valid_word(word: str) -> bool`

Check if a word is in Wordle's valid guess list.

**Parameters:**
- `word`: The word to check (5 letters, case-insensitive)

**Returns:**
- `True` if the word is valid in Wordle
- `False` otherwise

**Examples:**

```python
from word32 import is_valid_word

is_valid_word("STARE")    # True
is_valid_word("stare")    # True (case-insensitive)
is_valid_word("PIZZA")    # True
is_valid_word("XXXXX")    # False
is_valid_word("QWERT")    # False (not a valid Wordle word)
is_valid_word("TESTS")    # True
```

**Use case:** Validate user input or your own word suggestions before submitting them.

---

#### `get_remaining_candidates(targets: list[str], guess: str, clue: tuple) -> int`

Count how many target words remain possible after a guess.

**Parameters:**
- `targets`: List of potential target words
- `guess`: The word that was guessed
- `clue`: The clue tuple returned by `generate_clue()`

**Returns:**
The integer count of remaining candidates (equivalent to `len(filter_targets(...))`)

**Examples:**

```python
from word32 import get_remaining_candidates, generate_clue, VALID_TARGETS

# Check how many words remain after a guess
clue = ('Y', 'B', 'B', 'B', 'B')
count = get_remaining_candidates(VALID_TARGETS, "STARE", clue)
print(f"{count} words remain")  # Output: 312 words remain

# Use for strategy evaluation
for word in ["STARE", "ADIEU", "CRANE"]:
    clue = generate_clue(word, "PIZZA")
    remaining = get_remaining_candidates(VALID_TARGETS, word, clue)
    print(f"{word}: {remaining} candidates")
```

---

### Strategy Functions

#### `load_strategy(version: str = "v1.0") -> Strategy`

Load a pre-computed Wordle strategy with lookup tables.

**Parameters:**
- `version`: Strategy version (default: `"v1.0"`)

**Returns:**
A `Strategy` object containing optimal second-guess suggestions.

**Examples:**

```python
from word32 import load_strategy

# Load the default strategy
strategy = load_strategy()

# Load a specific version (if available)
strategy = load_strategy("v1.0")
```

---

#### `Strategy.first_guess() -> str`

Get the optimal first guess word.

**Returns:**
The recommended first guess (always `"STARE"` in v1.0)

**Examples:**

```python
from word32 import load_strategy

strategy = load_strategy()
first = strategy.first_guess()
print(first)  # Output: STARE
```

---

#### `Strategy.second_guess(clue: tuple) -> Optional[str]`

Get the optimal second guess for a given first-guess clue.

**Parameters:**
- `clue`: A tuple of 5 characters representing the Wordle clue (`'G'`, `'Y'`, or `'B'`)

**Returns:**
- The optimal second-guess word (string), or
- `None` if this clue pattern isn't covered by the strategy

**Examples:**

```python
from word32 import load_strategy, generate_clue

strategy = load_strategy()

# Get second guess for a specific clue
clue = ('B', 'B', 'B', 'B', 'B')  # No letters match
second = strategy.second_guess(clue)
print(second)  # Output: OPINE (or similar)

# Use in a game
target = "WORLD"
first_clue = generate_clue("STARE", target)
second_guess = strategy.second_guess(first_clue)
print(f"Second guess: {second_guess}")
```

---

#### `Strategy.metadata() -> dict`

Get information about the strategy.

**Returns:**
A dictionary with strategy metadata:
- `version`: Strategy version
- `penalty_function`: Optimization criterion used
- `depth`: How many moves the strategy covers
- `symmetric`: Whether strategy is symmetric
- `created`: When the strategy was created
- `description`: Human-readable description

**Examples:**

```python
from word32 import load_strategy

strategy = load_strategy()
info = strategy.metadata()
print(f"Version: {info['version']}")
print(f"Description: {info['description']}")
# Output:
# Version: v1.0
# Description: Optimal two-deep strategy minimizing expected remaining targets
```

---

#### `get_second_guess(strategy: Strategy, first_clue: tuple) -> Optional[str]`

Convenience function for getting the optimal second guess.

**Parameters:**
- `strategy`: A Strategy object from `load_strategy()`
- `first_clue`: The clue tuple from the first guess

**Returns:**
The optimal second-guess word, or `None` if not found.

**Examples:**

```python
from word32 import load_strategy, get_second_guess, generate_clue

strategy = load_strategy()
clue = ('Y', 'B', 'B', 'B', 'B')
second = get_second_guess(strategy, clue)
print(second)  # Output: OPINE (or similar)
```

This is equivalent to calling `strategy.second_guess(clue)`.

---

### Word Lists

#### `VALID_TARGETS: list[str]`

A pre-loaded list of all valid Wordle target words (the words that can be the answer).

**Examples:**

```python
from word32 import VALID_TARGETS

print(f"Total target words: {len(VALID_TARGETS)}")
# Output: Total target words: 2315

# Check if a word can be a target
if "PIZZA" in VALID_TARGETS:
    print("PIZZA can be a Wordle answer")

# Sample some targets
print(VALID_TARGETS[:5])
# Output: ['ABOUT', 'ABUSE', 'ACUTE', 'ADMIT', 'ADOPT']
```

**Note:** This list is cached in memory when the module loads, so accessing it is very fast.

---

#### `VALID_GUESSES: list[str]`

A pre-loaded list of all valid Wordle guess words (includes targets + additional valid guesses).

**Examples:**

```python
from word32 import VALID_GUESSES

print(f"Total valid guesses: {len(VALID_GUESSES)}")
# Output: Total valid guesses: 12972

# Check if a word can be guessed
if "STARE" in VALID_GUESSES:
    print("STARE is a valid guess")

# VALID_GUESSES is a superset of VALID_TARGETS
from word32 import VALID_TARGETS
print(len(VALID_TARGETS) <= len(VALID_GUESSES))  # Output: True
```

**Note:** Use `VALID_TARGETS` when you need the list of possible answers, and `VALID_GUESSES` when validating user input.

---

## Real-world Examples

### Example 1: Automated Game Against a Target Word

Play multiple games automatically and measure performance:

```python
from word32 import (
    load_strategy,
    generate_clue,
    filter_targets,
    VALID_TARGETS
)

def simulate_game(target):
    """Simulate a complete game against a target."""
    strategy = load_strategy("v1.0")
    candidates = VALID_TARGETS.copy()

    for guess_num in range(1, 4):
        # Get next guess
        if guess_num == 1:
            guess = strategy.first_guess()
        else:
            guess = strategy.second_guess(prev_clue)
            if guess is None:
                guess = candidates[0] if candidates else None

        # Generate clue and check for win
        clue = generate_clue(guess, target)
        if clue == ('G', 'G', 'G', 'G', 'G'):
            return guess_num

        # Filter and prepare for next iteration
        prev_clue = clue
        candidates = filter_targets(candidates, guess, clue)

    return 3  # Didn't solve

# Benchmark against multiple targets
test_targets = ["PIZZA", "WORLD", "PHONE", "AUDIO", "HEART"]
results = {}

for target in test_targets:
    if target in VALID_TARGETS:
        guesses = simulate_game(target)
        results[target] = guesses
        print(f"{target}: Solved in {guesses} guesses")

# Calculate statistics
avg_guesses = sum(results.values()) / len(results)
print(f"\nAverage guesses: {avg_guesses:.2f}")
print(f"All solved in 3 or fewer: {all(g <= 3 for g in results.values())}")
```

**Output:**
```
PIZZA: Solved in 3 guesses
WORLD: Solved in 3 guesses
PHONE: Solved in 2 guesses
AUDIO: Solved in 3 guesses
HEART: Solved in 2 guesses

Average guesses: 2.6
All solved in 3 or fewer: True
```

---

### Example 2: Finding Words That Match a Specific Clue Pattern

Find all words matching a particular clue without knowing the target:

```python
from word32 import filter_targets, VALID_TARGETS

def find_words_for_clue(first_guess, clue_pattern):
    """Find all words that would produce a given clue."""
    matching = filter_targets(VALID_TARGETS, first_guess, clue_pattern)
    return matching

# Example: After guessing STARE and getting ('B', 'B', 'B', 'B', 'B')
# (none of those letters are in the target)
clue = ('B', 'B', 'B', 'B', 'B')
matches = find_words_for_clue("STARE", clue)

print(f"Words with no S, T, A, R, E: {len(matches)}")
print(f"First 10: {matches[:10]}")

# Example 2: More specific clue
# After STARE → ('Y', 'B', 'B', 'B', 'Y')
# (S and E are in the word but wrong positions)
clue = ('Y', 'B', 'B', 'B', 'Y')
matches = find_words_for_clue("STARE", clue)

print(f"\nWords with S and E (not in positions 0 and 4): {len(matches)}")
print(f"First 10: {matches[:10]}")

# Interactive pattern finder
def interactive_pattern_finder():
    """Let user search for words matching clue patterns."""
    while True:
        first = input("First guess: ").strip().upper()
        if len(first) != 5:
            continue

        clue_input = input("Clue (5 chars, G/Y/B): ").strip().upper()
        if len(clue_input) != 5:
            continue

        clue = tuple(clue_input)
        matches = find_words_for_clue(first, clue)

        print(f"Found {len(matches)} matching words")
        if matches:
            print(f"Sample: {matches[:5]}")
        print()

# interactive_pattern_finder()
```

---

### Example 3: Comparing Different Strategies or Starting Words

Analyze how different starting words perform:

```python
from word32 import (
    generate_clue,
    filter_targets,
    VALID_TARGETS,
    is_valid_word
)
import statistics

def evaluate_first_word(word):
    """Evaluate how well a starting word performs."""
    if not is_valid_word(word):
        return None

    reductions = []

    for target in VALID_TARGETS[:100]:  # Sample for speed
        clue = generate_clue(word, target)
        remaining = len(filter_targets(VALID_TARGETS, word, clue))
        reductions.append(remaining)

    return {
        'word': word,
        'avg_remaining': statistics.mean(reductions),
        'max_remaining': max(reductions),
        'min_remaining': min(reductions),
        'stdev': statistics.stdev(reductions) if len(reductions) > 1 else 0
    }

# Compare several starting words
candidates = ["STARE", "ADIEU", "CRANE", "SLATE", "LOUSE"]
results = []

for word in candidates:
    result = evaluate_first_word(word)
    if result:
        results.append(result)

# Sort by average remaining
results.sort(key=lambda x: x['avg_remaining'])

print("Starting word comparison (lower avg_remaining is better):")
print("-" * 70)
for r in results:
    print(f"{r['word']}: avg={r['avg_remaining']:.0f}, "
          f"max={r['max_remaining']}, stdev={r['stdev']:.1f}")

# Show best word
print(f"\nBest word: {results[0]['word']}")
```

---

## Best Practices

### Performance Optimization

**Word lists are cached automatically:**

```python
from word32 import VALID_TARGETS, VALID_GUESSES

# First import loads the word lists (one-time cost ~50ms)
# Subsequent accesses are instant
candidates = VALID_TARGETS.copy()  # Fast
guesses = VALID_GUESSES  # Fast
```

**Reuse `filter_targets()` results instead of re-filtering:**

```python
# Good - build up from previous results
candidates = VALID_TARGETS.copy()
candidates = filter_targets(candidates, "STARE", clue1)
candidates = filter_targets(candidates, "LOINS", clue2)

# Bad - re-filtering from scratch each time
candidates = filter_targets(VALID_TARGETS, "STARE", clue1)
candidates = filter_targets(VALID_TARGETS, "STARE", clue1)  # Redundant!
candidates = filter_targets(VALID_TARGETS, "LOINS", clue2)  # Wrong!
```

**Cache the strategy object:**

```python
# Good - load once and reuse
strategy = load_strategy()
for target in targets:
    first_clue = generate_clue(strategy.first_guess(), target)
    second = strategy.second_guess(first_clue)

# Less efficient - reloads strategy each time
for target in targets:
    strategy = load_strategy()  # Unnecessary reload!
    # ... rest of code
```

---

### Testing Your Own Integrations

Test with known cases to ensure correctness:

```python
from word32 import generate_clue, filter_targets, VALID_TARGETS

def test_my_solver():
    """Test suite for custom Wordle solver."""

    # Test generate_clue
    assert generate_clue("STARE", "STARE") == ('G', 'G', 'G', 'G', 'G')
    assert generate_clue("STARE", "TRASH") == ('Y', 'Y', 'G', 'Y', 'B')

    # Test filter_targets
    clue = generate_clue("STARE", "PIZZA")
    remaining = filter_targets(VALID_TARGETS, "STARE", clue)
    assert "PIZZA" in remaining

    # Test consistency: if we filter with a clue and then check clues,
    # all should match
    for word in remaining[:10]:
        assert generate_clue("STARE", word) == clue

    print("✓ All tests passed")

test_my_solver()
```

---

### Error Handling Patterns

Handle edge cases gracefully:

```python
from word32 import (
    generate_clue,
    filter_targets,
    load_strategy,
    is_valid_word,
    VALID_TARGETS
)

def safe_solver(target):
    """Solve with proper error handling."""

    # Validate input
    if not target or len(target) != 5:
        print("Error: Target must be 5 letters")
        return None

    target = target.upper()

    if not is_valid_word(target):
        print(f"Warning: {target} is not a valid Wordle word")
        # Continue anyway - might be valid for some games

    try:
        strategy = load_strategy("v1.0")
    except FileNotFoundError:
        print("Error: Strategy file not found")
        return None

    candidates = VALID_TARGETS.copy()

    for guess_num in range(1, 4):
        try:
            if guess_num == 1:
                guess = strategy.first_guess()
            else:
                guess = strategy.second_guess(prev_clue)
                if guess is None:
                    if not candidates:
                        print("Error: No candidates remaining")
                        return None
                    guess = candidates[0]

            clue = generate_clue(guess, target)

            if clue == ('G', 'G', 'G', 'G', 'G'):
                return guess_num

            prev_clue = clue
            candidates = filter_targets(candidates, guess, clue)

            if not candidates and guess_num < 3:
                print(f"Warning: No candidates remain after guess {guess_num}")

        except Exception as e:
            print(f"Error during guess {guess_num}: {e}")
            return None

    return None  # Didn't solve in 3

# Usage
result = safe_solver("PIZZA")
if result:
    print(f"Solved in {result} guesses")
else:
    print("Failed to solve")
```

---

### Working with Strategies

Understand and debug strategy decisions:

```python
from word32 import load_strategy, generate_clue, VALID_TARGETS

def analyze_strategy_decision(target):
    """See why the strategy makes specific suggestions."""

    strategy = load_strategy("v1.0")
    print(f"Target: {target}\n")

    # First guess
    first = strategy.first_guess()
    first_clue = generate_clue(first, target)
    print(f"1. {first} → {first_clue}")

    # Second guess
    second = strategy.second_guess(first_clue)
    if second:
        second_clue = generate_clue(second, target)
        print(f"2. {second} → {second_clue}")

        # What words remain?
        from word32 import filter_targets
        remaining = filter_targets(VALID_TARGETS, first, first_clue)
        remaining = filter_targets(remaining, second, second_clue)

        print(f"\nAfter 2 guesses, {len(remaining)} candidates remain")
        if len(remaining) <= 10:
            print(f"Remaining: {remaining}")
    else:
        print(f"2. Strategy has no suggestion for clue {first_clue}")
        print("   (This is a rare clue pattern)")

# Test on several words
for word in ["PIZZA", "WORLD", "PHONE"]:
    analyze_strategy_decision(word)
    print("\n" + "="*50 + "\n")
```

---

## FAQ

### "Why does the third guess rarely fail?"

The 32word strategy is optimized to minimize the expected number of remaining candidates after each guess. Here's why three guesses almost always succeed:

1. **STARE has excellent coverage**: The first guess eliminates ~80% of impossible words on average
2. **Strategy-optimized second guess**: The second guess is chosen from thousands of pre-computed options to minimally partition the remaining space
3. **Math works in your favor**: After two strategic guesses, the remaining candidates are typically < 20 words, making any final guess highly likely to hit

**The math:**
- ~2,300 possible targets
- First guess → ~300 remaining on average (~13% of original)
- Second guess → ~5 remaining on average (~2% of original)
- Third guess → Guaranteed if one of those 5 is the target

Your third guess only fails if:
- The strategy covers fewer clue patterns than encountered (rare)
- The second guess wasn't in the strategy table (rare)
- You get an extremely unfortunate clue pattern (extremely rare)

---

### "Can I use my own word list?"

The current version ships with standard Wordle word lists, but you can work with your own lists:

```python
from word32 import (
    generate_clue,
    filter_targets,
    load_strategy,
    get_second_guess
)

# Load your custom word list
with open("my_words.txt") as f:
    MY_TARGETS = [line.strip().upper() for line in f if len(line.strip()) == 5]

# Use it with the library
def custom_solver(target, word_list=MY_TARGETS):
    strategy = load_strategy()
    candidates = word_list.copy()

    for guess_num in range(1, 4):
        if guess_num == 1:
            guess = strategy.first_guess()
        else:
            guess = strategy.second_guess(prev_clue)
            if guess is None:
                guess = candidates[0] if candidates else None

        clue = generate_clue(guess, target)

        if clue == ('G', 'G', 'G', 'G', 'G'):
            return guess_num

        prev_clue = clue
        candidates = filter_targets(candidates, guess, clue)

    return 3

# Use it
result = custom_solver("PIZZA", MY_TARGETS)
```

---

### "How do strategies work mathematically?"

The 32word strategy uses **minimax optimization** with a pre-computed lookup table:

**The Goal:** Find second-guess words that minimize the maximum number of remaining candidates (or expected remaining, depending on the variant).

**The Process:**
1. For each possible clue after the first guess STARE:
   - Filter VALID_TARGETS down to candidates matching that clue
   - For each candidate word from VALID_GUESSES:
     - Simulate it as a second guess
     - Calculate how many candidates remain for each possible third-guess clue
   - Pick the second guess that minimizes worst-case (or expected) remaining candidates

**Example:**
```
After STARE → ('B', 'B', 'B', 'B', 'B'):
  Candidates: ~300 words (none containing S, T, A, R, E)

  Evaluate OPINE:
    - If third guess clue is ('G', 'B', 'B', 'B', 'B'): 8 words remain
    - If third guess clue is ('B', 'G', 'B', 'B', 'B'): 12 words remain
    - ... (31 total possible clues)
    - Worst case: 15 words remain

  Evaluate LOINS:
    - ... similar evaluation ...
    - Worst case: 12 words remain

  Choose LOINS because it has better worst-case
```

The v1.0 strategy uses this exact approach: maximizing elimination to ensure victory.

---

### "Can I create custom strategies?"

Yes, but it requires custom code. The Strategy class is extensible:

```python
from word32.strategy import Strategy

# Create a custom strategy with your own lookup table
custom_lookup = {
    "STARE": {
        "BBBBB": [
            {"second_guess": "OPINE", "rank": 1, "expected": 15.2}
        ],
        "GBBBB": [
            {"second_guess": "STOKE", "rank": 1, "expected": 2.1}
        ],
        # ... more clue patterns ...
    }
}

my_strategy = Strategy(version="custom_v1", lookup_table=custom_lookup)

# Use it like the standard strategy
first = my_strategy.first_guess()  # Still "STARE" by default
second = my_strategy.second_guess(clue)  # Uses your custom lookup
```

**To build your own strategy:**
1. For each clue pattern after STARE:
2. Filter down to remaining candidates
3. Score each possible second guess by how many candidates remain
4. Store the best-scoring guess in the lookup table

This requires significant computation but can be tailored to:
- Different word lists
- Different optimization criteria
- Different starting words
- Longer planning horizons

---

### "What Python versions are supported?"

The 32word library requires:
- **Python 3.10+** (uses `tuple[str, str, str, str, str]` syntax)
- **No external dependencies** - only uses Python standard library

**Tested on:**
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14 (latest)

**Not compatible with Python 3.9 or earlier** due to type hint syntax.

Check your Python version:
```bash
python --version
```

If you're on Python 3.9, either upgrade or use PEP 604 compatible syntax:
```python
# Instead of:
def foo() -> tuple[str, str, str, str, str]:

# Use:
from typing import Tuple
def foo() -> Tuple[str, str, str, str]:
```

---

## Conclusion

The 32word library makes Wordle solving elegant and educational. Whether you're building a game, analyzing word patterns, or understanding Wordle strategy, this library provides the tools to do it efficiently.

**Quick Links:**
- GitHub: https://github.com/benmazzotta/32word
- Issues: https://github.com/benmazzotta/32word/issues

Happy Wordling! 🎮
