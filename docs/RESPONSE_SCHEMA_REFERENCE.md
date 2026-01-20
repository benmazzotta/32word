# Response Schema Reference

Complete documentation for the 32word response schema API. This schema provides standardized JSON structures for all gameplay interactions across CLI, Web App, and Discord bot platforms.

## Overview

The 32word library uses a consistent response schema for all game interactions. Responses are structured as JSON objects with well-defined fields for easy parsing and display.

**Response Types:**
- `GameResponse` - Success response with game data
- `ErrorResponse` - Error response with error details

## GameResponse

A successful game response containing clue, remaining words, and strategy recommendations.

### Structure

```json
{
  "success": true,
  "guess": "RAISE",
  "clue": ["G", "Y", "X", "X", "G"],
  "remaining": {
    "count": 42,
    "sample": ["AGILE", "ALIAS", "AMISS", "ARISE", "AROSE"],
    "all_words": false
  },
  "strategy": {
    "recommended_guess": "CLOUD",
    "confidence": 0.95,
    "coverage": 0.8125
  },
  "game_state": {
    "guess_number": 1,
    "guesses_so_far": ["RAISE"],
    "is_solved": false,
    "solved_word": null
  },
  "metadata": {
    "strategy_version": "RAISE",
    "response_version": "1.0"
  }
}
```

### Fields

#### `success` (boolean, required)
Always `true` for success responses.

#### `guess` (string, required)
The word that was guessed (always uppercase).

**Example:** `"RAISE"`

#### `clue` (array[string], required)
Array of 5 clue codes representing Wordle feedback:
- `'G'` - Green (correct letter, correct position)
- `'Y'` - Yellow (correct letter, wrong position)
- `'X'` or `'B'` - Black/Gray (letter not in target)

**Example:** `["G", "Y", "X", "X", "G"]`

**Note:** The library accepts both `'X'` and `'B'` for black/gray, but responses use `'X'` consistently.

#### `remaining` (object, required)
Information about remaining possible target words.

**Fields:**
- `count` (integer) - Total number of remaining words
- `sample` (array[string]) - Sample of remaining words (up to `sample_size`)
- `all_words` (boolean) - `true` if `sample` contains all remaining words

**Example:**
```json
{
  "count": 42,
  "sample": ["AGILE", "ALIAS", "AMISS", "ARISE", "AROSE"],
  "all_words": false
}
```

**Edge Cases:**
- If `count = 0` and `is_solved = false`: Invalid state (should not occur)
- If `count = 1` and `is_solved = false`: Next guess will solve
- If `count <= sample_size`: `all_words = true`, `sample` contains all words

#### `strategy` (object, optional)
Strategy recommendation for the next guess. Only present when:
- A recommendation is available
- Response mode is not `'minimal'`

**Fields:**
- `recommended_guess` (string) - Suggested next guess word
- `confidence` (float) - Confidence level (0.0 to 1.0)
- `coverage` (float) - Strategy coverage percentage (0.0 to 1.0). Note: The default value of 0.8125 is an estimated coverage for the 32 first guess options. Actual coverage may vary.
- `pattern_info` (string, optional) - Human-readable pattern description
- `expected_remaining` (float, optional) - Expected remaining words after this guess
- `max_remaining` (integer, optional) - Maximum remaining words possible
- `rank` (integer, optional) - Strategy rank (1-32)

**Example:**
```json
{
  "recommended_guess": "CLOUD",
  "confidence": 0.95,
  "coverage": 0.8125
}
```

**Note:** The `coverage` field value of 0.8125 shown in examples is a default estimated value. Actual coverage depends on the specific first guess and strategy data.

**Note:** `strategy` may be `null` if:
- No strategy recommendation available for this clue pattern
- Response mode is `'minimal'`
- Game is already solved

#### `game_state` (object, optional)
Current game state metadata. Only present when response mode is not `'minimal'`.

**Fields:**
- `guess_number` (integer) - Current guess number (1, 2, or 3)
- `guesses_so_far` (array[string]) - All guesses made so far
- `is_solved` (boolean) - `true` if game is solved
- `solved_word` (string, optional) - The solved word (only if `is_solved = true`)

**Example:**
```json
{
  "guess_number": 2,
  "guesses_so_far": ["RAISE", "CLOUD"],
  "is_solved": false,
  "solved_word": null
}
```

#### `metadata` (object, always present)
Response metadata. Always included in responses from `build_game_response()` and `build_error_response()`.

**Fields:**
- `strategy_version` (string, optional) - First guess word used (e.g., "RAISE", "ATONE")
- `response_version` (string) - Schema version (currently "1.0")

**Example:**
```json
{
  "strategy_version": "RAISE",
  "response_version": "1.0"
}
```

## ErrorResponse

An error response containing error details.

### Structure

```json
{
  "success": false,
  "error": "INVALID_GUESS",
  "error_code": "INVALID_GUESS",
  "message": "\"QWERT\" is not a valid Wordle word.",
  "metadata": {
    "response_version": "1.0"
  }
}
```

### Fields

#### `success` (boolean, required)
Always `false` for error responses.

#### `error` (string, required)
Human-readable error type.

**Examples:**
- `"INVALID_GUESS"`
- `"INVALID_CLUE"`
- `"INCOMPLETE_GAME"`
- `"MISSING_DATA"`
- `"INVALID_TARGET"`
- `"UNKNOWN_ERROR"`

#### `error_code` (string, required)
Standardized error code (same as `error` field).

**Valid codes:**
- `INVALID_GUESS` - Guess word is not valid
- `INVALID_CLUE` - Clue format is invalid
- `INCOMPLETE_GAME` - No active game found
- `MISSING_DATA` - Required data files missing
- `INVALID_TARGET` - Target word is invalid
- `UNKNOWN_ERROR` - Unexpected error occurred

#### `message` (string, required)
Detailed error message explaining what went wrong and how to fix it.

**Example:** `"\"QWERT\" is not a valid Wordle word."`

#### `metadata` (object, optional)
Response metadata (same structure as GameResponse).

## Response Modes

The `build_game_response()` function supports three response modes:

### Full Mode (default)

Includes all fields: `strategy`, `game_state`, `metadata`.

**Use when:**
- Web applications needing complete game state
- Debugging and development
- Full-featured integrations

### Minimal Mode

Includes only essential fields: `success`, `guess`, `clue`, `remaining`, `metadata`.

**Note:** When `mode='minimal'`, the `strategy` and `game_state` fields are excluded from the response, even if `strategy_recommendation` or `game_state` parameters are provided to `build_game_response()`. The `metadata` field is always included.

**Use when:**
- Discord bots (concise messages)
- Bandwidth-constrained environments
- Simple integrations

**Example:**
```json
{
  "success": true,
  "guess": "RAISE",
  "clue": ["G", "Y", "X", "X", "G"],
  "remaining": {
    "count": 42,
    "sample": ["AGILE", "ALIAS", "AMISS"],
    "all_words": false
  },
  "metadata": {
    "strategy_version": "RAISE",
    "response_version": "1.0"
  }
}
```

### Extended Mode

Includes all fields plus additional optional metadata.

**Use when:**
- Analytics and logging
- Detailed strategy analysis
- Research applications

## Response Examples

### Example 1: First Guess (Full Mode)

```json
{
  "success": true,
  "guess": "RAISE",
  "clue": ["G", "Y", "X", "X", "G"],
  "remaining": {
    "count": 42,
    "sample": ["AGILE", "ALIAS", "AMISS", "ARISE", "AROSE"],
    "all_words": false
  },
  "strategy": {
    "recommended_guess": "CLOUD",
    "confidence": 0.95,
    "coverage": 0.8125,
    "expected_remaining": 8.2,
    "max_remaining": 15,
    "rank": 1
  },
  "game_state": {
    "guess_number": 1,
    "guesses_so_far": ["RAISE"],
    "is_solved": false,
    "solved_word": null
  },
  "metadata": {
    "strategy_version": "RAISE",
    "response_version": "1.0"
  }
}
```

### Example 2: Second Guess (Minimal Mode)

```json
{
  "success": true,
  "guess": "CLOUD",
  "clue": ["X", "Y", "X", "X", "X"],
  "remaining": {
    "count": 8,
    "sample": ["AGILE", "ALIAS", "AMISS", "ARISE", "AROSE", "ASIDE", "ASSET", "AWAIT"],
    "all_words": true
  }
}
```

### Example 3: Solved Game

```json
{
  "success": true,
  "guess": "AGILE",
  "clue": ["G", "G", "G", "G", "G"],
  "remaining": {
    "count": 1,
    "sample": ["AGILE"],
    "all_words": true
  },
  "strategy": null,
  "game_state": {
    "guess_number": 3,
    "guesses_so_far": ["RAISE", "CLOUD", "AGILE"],
    "is_solved": true,
    "solved_word": "AGILE"
  },
  "metadata": {
    "strategy_version": "RAISE",
    "response_version": "1.0"
  }
}
```

### Example 4: Error - Invalid Guess

```json
{
  "success": false,
  "error": "INVALID_GUESS",
  "error_code": "INVALID_GUESS",
  "message": "\"QWERT\" is not a valid Wordle word.",
  "metadata": {
    "response_version": "1.0"
  }
}
```

### Example 5: Error - No Active Game

```json
{
  "success": false,
  "error": "INCOMPLETE_GAME",
  "error_code": "INCOMPLETE_GAME",
  "message": "No active game found. Please start a new game.",
  "metadata": {
    "response_version": "1.0"
  }
}
```

### Example 6: Edge Case - Remaining = 1 (Not Solved)

```json
{
  "success": true,
  "guess": "CLOUD",
  "clue": ["X", "X", "X", "X", "X"],
  "remaining": {
    "count": 1,
    "sample": ["AGILE"],
    "all_words": true
  },
  "game_state": {
    "guess_number": 2,
    "guesses_so_far": ["RAISE", "CLOUD"],
    "is_solved": false,
    "solved_word": null
  }
}
```

**Note:** This means the next guess will solve the game.

### Example 7: No Strategy Recommendation

```json
{
  "success": true,
  "guess": "RARE",
  "clue": ["X", "X", "X", "X", "X"],
  "remaining": {
    "count": 150,
    "sample": ["ABOUT", "ABUSE", "ACUTE", "ADMIT", "ADOPT"],
    "all_words": false
  },
  "strategy": null,
  "game_state": {
    "guess_number": 1,
    "guesses_so_far": ["RARE"],
    "is_solved": false,
    "solved_word": null
  }
}
```

**Note:** `strategy` is `null` because this clue pattern is not covered by the strategy.

## Validation

Use `validate_response()` to validate response structure:

```python
from word32 import validate_response

response_dict = {
    "success": True,
    "guess": "RAISE",
    "clue": ["G", "Y", "X", "X", "G"],
    "remaining": {
        "count": 42,
        "sample": ["AGILE", "ALIAS"],
        "all_words": False
    }
}

is_valid, error = validate_response(response_dict, schema_version="1.0")
if not is_valid:
    print(f"Validation error: {error}")
```

**Validation checks:**
- Required fields present
- Clue format (5 elements, valid codes)
- Remaining structure (count, sample, all_words)
- Metadata version match
- Error response structure (if `success = false`)

## Versioning

**Current version:** `1.0`

**Versioning strategy:**
- Major version changes: Breaking API changes
- Minor version changes: New optional fields
- Backwards compatible: Old clients can parse new responses (ignore unknown fields)

**Migration guide:**
- Version 1.0 → 1.1: No changes required (new fields are optional)
- Version 1.0 → 2.0: Check `response_version` field, update parsing logic

## Best Practices

### Parsing Responses

**Always check `success` first:**
```python
response = get_game_response()
if not response['success']:
    handle_error(response)
    return
```

**Handle missing optional fields:**
```python
strategy = response.get('strategy')
if strategy and strategy.get('recommended_guess'):
    use_recommendation(strategy['recommended_guess'])
```

### Displaying Clues

**Convert codes to emoji:**
```python
emoji_map = {'G': '🟩', 'Y': '🟨', 'X': '⬜', 'B': '⬜'}
clue_emoji = ' '.join(emoji_map.get(code, '⬜') for code in response['clue'])
```

**Or use terminal colors:**
```python
colors = {'G': '\033[92m', 'Y': '\033[93m', 'X': '\033[90m'}
# ... format with colors
```

### Handling Remaining Words

**Show all words if small:**
```python
remaining = response['remaining']
if remaining['all_words']:
    display_all_words(remaining['sample'])
else:
    display_sample(remaining['sample'])
    show_count(remaining['count'])
```

**Handle edge cases:**
```python
if remaining['count'] == 0 and not response['game_state']['is_solved']:
    # Invalid state - should not occur
    log_error("Invalid game state")
elif remaining['count'] == 1 and not response['game_state']['is_solved']:
    # Next guess will solve
    show_almost_solved(remaining['sample'][0])
```

## API Reference

### `build_game_response()`

Build a standardized game response.

**Parameters:**
- `guess` (str) - The guessed word
- `clue` (tuple) - Clue tuple ('G', 'Y', 'X')
- `remaining_targets` (list[str]) - List of remaining target words
- `strategy_recommendation` (dict, optional) - Strategy recommendation data
- `game_state` (dict, optional) - Game state data
- `strategy_version` (str, optional) - Strategy version identifier
- `mode` (str) - Response mode: 'full', 'minimal', 'extended' (default: 'full')
- `sample_size` (int) - Number of words in sample (default: 5)
- `random_sample` (bool) - Use random sampling (default: False)

**Returns:** `GameResponse` object

**Example:**
```python
response = build_game_response(
    guess="RAISE",
    clue=('G', 'Y', 'X', 'X', 'G'),
    remaining_targets=['AGILE', 'ALIAS', 'AMISS'],
    strategy_recommendation={'recommended_guess': 'CLOUD', 'confidence': 0.95},
    mode='full'
)
```

### `build_error_response()`

Build a standardized error response.

**Parameters:**
- `error_type` (str) - Human-readable error type
- `message` (str) - Detailed error message
- `error_code` (ErrorCode, optional) - Standard error code

**Returns:** `ErrorResponse` object

**Example:**
```python
error = build_error_response(
    'INVALID_GUESS',
    '"QWERT" is not a valid Wordle word.',
    ErrorCode.INVALID_GUESS
)
```

### `validate_response()`

Validate response structure.

**Parameters:**
- `response` (dict) - Response dictionary to validate
- `schema_version` (str) - Expected schema version (default: "1.0")

**Returns:** `tuple[bool, Optional[str]]` - (is_valid, error_message)

**Example:**
```python
is_valid, error = validate_response(response_dict)
if not is_valid:
    print(f"Error: {error}")
```

## Next Steps

- See [Web App Integration Guide](./INTEGRATION_WEB_APP.md) for API endpoint examples
- See [Discord Bot Integration Guide](./INTEGRATION_DISCORD_BOT.md) for minimal mode usage
- See [CLI Usage Guide](./INTEGRATION_CLI.md) for command-line patterns
