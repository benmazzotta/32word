# Release Notes: 32word v0.1.3

**Release Date:** 2026-01-19  
**Version:** 0.1.3  
**Status:** Stable Release

---

## Summary

Version 0.1.3 introduces major enhancements for building interactive Wordle applications, including standardized response schemas, custom first guess selection, and comprehensive data validation. This release maintains full backwards compatibility with v0.1.2 and earlier versions.

### Key Highlights

- **Phase 4.2**: Standardized JSON response schema for cross-platform consistency
- **Phase 4.3**: 32 optimal first guess options with custom selection
- **Data Validation**: Automatic validation on import with clear error messages
- **Code Quality**: Comprehensive type hints, error handling, and logging
- **Documentation**: Complete integration guides for Web App, Discord Bot, and CLI

---

## New Features

### Phase 4.2: Response Schema

Standardized JSON response structure for consistent cross-platform integration:

#### New Classes

- **`GameResponse`** - Complete game response with clue, remaining words, strategy recommendations
- **`ErrorResponse`** - Standardized error responses with error codes
- **`RemainingWords`** - Remaining candidates count and sample
- **`StrategyRecommendation`** - Recommended next guess with confidence
- **`GameState`** - Game state metadata (guess number, guesses so far, solved status)
- **`ResponseMetadata`** - Response version and strategy information
- **`ErrorCode`** - Enumeration of standard error codes
- **`ResponseVersion`** - Response schema version enumeration

#### New Functions

- **`build_game_response()`** - Build standardized game response
  ```python
  from word32 import build_game_response
  
  response = build_game_response(
      guess="RAISE",
      clue=('G', 'Y', 'X', 'X', 'G'),
      remaining_targets=['AGILE', 'ALIAS', 'AMISS'],
      strategy_recommendation={'recommended_guess': 'CLOUD', 'confidence': 0.95},
      game_state={'guess_number': 1, 'guesses_so_far': ['RAISE'], 'is_solved': False}
  )
  ```

- **`build_error_response()`** - Build standardized error response
  ```python
  from word32 import build_error_response, ErrorCode
  
  error = build_error_response(
      error_code=ErrorCode.INVALID_GUESS,
      message="Word must be 5 letters"
  )
  ```

- **`validate_response()`** - Validate response against schema
  ```python
  from word32 import validate_response
  
  is_valid, error_msg = validate_response(response_dict, schema_version="1.0")
  ```

- **`get_remaining_sample()`** - Get sample of remaining words
  ```python
  from word32 import get_remaining_sample
  
  sample, is_complete = get_remaining_sample(
      targets=['AGILE', 'ALIAS', 'AMISS', 'AMINO', 'AMITY'],
      size=3,
      random_sample=True
  )
  ```

### Phase 4.3: Custom First Guess Selection

Choose from 32 optimal first guess options ranked by performance:

#### New Functions

- **`get_available_first_guesses()`** - Get all 32 first guess options
  ```python
  from word32 import get_available_first_guesses
  
  options = get_available_first_guesses()
  # Returns list of 32 dicts with: first_guess, rank, expected_remaining, variance
  ```

- **`select_first_guess(user_choice)`** - Select and validate a first guess
  ```python
  from word32 import select_first_guess
  
  selected = select_first_guess("RAISE")
  # Returns dict with first_guess info if valid, None otherwise
  ```

- **`get_strategy_for_first_guess(first_guess)`** - Get strategy for any first guess
  ```python
  from word32 import get_strategy_for_first_guess
  
  strategy = get_strategy_for_first_guess("RAISE")
  # Returns dict mapping clue patterns to second guess recommendations
  ```

- **`get_second_guess_recommendation(first_guess, clue)`** - Get recommendation for (first_guess, clue) pair
  ```python
  from word32 import get_second_guess_recommendation
  
  recommendation = get_second_guess_recommendation("RAISE", ('G', 'Y', 'X', 'X', 'G'))
  # Returns recommended second guess string or None
  ```

#### Data Files

- **`data/phase2_naive_32.json`** - 32 optimal first guess options with metrics
- **`data/phase3_lookup.json`** - Strategy lookup table for all 32 first guesses

---

## Improvements

### Data Validation

- **Automatic validation on import** - Data files are validated when the package is imported
- **Clear error messages** - Helpful warnings if data files are missing or invalid
- **Data completeness checking** - `DataManager` class validates all required files
- **Recovery guidance** - Documentation provides steps to fix validation issues

```python
# Validation runs automatically on import
import word32  # Will warn if data files are missing

# Manual validation
from word32.data_manager import get_data_manager
dm = get_data_manager()
issues = dm.validate_data_completeness()
```

### Error Handling

New custom exception classes for better error handling:

- **`Word32Error`** - Base exception for all library errors
- **`DataValidationError`** - Data file validation issues
- **`StrategyNotFoundError`** - Missing strategy data
- **`InvalidClueError`** - Invalid clue tuple format
- **`InvalidGuessError`** - Invalid guess word

```python
from word32 import InvalidGuessError, DataValidationError

try:
    # Your code
except InvalidGuessError as e:
    print(f"Invalid guess: {e}")
```

### Type Hints

Comprehensive type hints added throughout the library:

- All functions have complete type annotations
- Type aliases for common patterns (`ClueCode`, `ClueTuple`)
- TypedDict definitions for structured data (`FirstGuessOption`, `FirstGuessMetrics`)
- Better IDE support and static type checking

### Logging

Structured logging added to key modules:

- Data loading operations
- Strategy lookups
- Response building
- Validation operations

Enable logging to debug issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Configuration

New configuration options for guess validation:

- **`set_guess_validation_mode(mode)`** - Set validation mode ('all' or 'targets_only')
- **`get_guess_validation_mode()`** - Get current validation mode
- **`reset_guess_validation_mode()`** - Reset to default

```python
from word32 import set_guess_validation_mode

# Only validate against target words (faster)
set_guess_validation_mode('targets_only')

# Validate against all valid guesses (default)
set_guess_validation_mode('all')
```

### Strategy Class Enhancements

- **Support for all 32 first guesses** - Strategy class now works with any of the 32 optimal first guesses
- **Automatic fallback** - Falls back to phase3_lookup when needed
- **O(1) lookup performance** - StrategyIndex class ensures fast lookups
- **Backwards compatible** - Default behavior unchanged (ATONE first guess)

---

## Documentation

### New Documentation Files

- **`docs/INTEGRATION_WEB_APP.md`** - Complete guide for integrating with web applications (React/Flask examples)
- **`docs/INTEGRATION_DISCORD_BOT.md`** - Guide for Discord bot integration (discord.py examples)
- **`docs/INTEGRATION_CLI.md`** - CLI usage guide with examples
- **`docs/RESPONSE_SCHEMA_REFERENCE.md`** - Complete API reference for response schema
- **`docs/DATA_COMPLETENESS_CHECKLIST.md`** - Data file requirements and troubleshooting

### Updated Documentation

- **`README.md`** - Added Phase 4.2/4.3 features section with examples
- **`DOCUMENTATION.md`** - Enhanced with new API functions and examples

---

## Technical Details

### Data Requirements

The library requires 5 data files for full functionality:

1. **`data/targets.txt`** - 2,309 target words (Wordle answers)
2. **`data/valid_guesses.txt`** - 12,950 valid guess words
3. **`data/phase2_naive_32.json`** - 32 optimal first guess options
4. **`data/phase3_lookup.json`** - Strategy lookup for all 32 first guesses
5. **`data/v1.0.json`** - Legacy strategy file (for backwards compatibility)

All data files are included in the package distribution.

### Performance Characteristics

- **Strategy lookup**: < 1 microsecond per call (O(1) lookup)
- **First guess selection**: < 10ms
- **Response building**: < 1ms
- **Sampling**: < 0.5ms even with random mode
- **Data validation** (first import): < 100ms, cached after

### Backwards Compatibility

✅ **All Phase 1 functions work identically:**

- `generate_clue()` - No changes
- `filter_targets()` - No changes
- `is_valid_word()` - Enhanced but backwards compatible
- `get_remaining_candidates()` - No changes
- `load_strategy()` - No changes
- `Strategy` class - Enhanced but backwards compatible (default ATONE)

✅ **No breaking changes to public API**

✅ **Existing code requires no modifications**

---

## Migration Guide

### Upgrading from v0.1.2

No code changes required! All existing code continues to work.

### New Features (Optional)

To use new features, simply import them:

```python
# Phase 4.2: Response schema
from word32 import build_game_response, GameResponse

# Phase 4.3: Custom first guesses
from word32 import get_available_first_guesses, select_first_guess
```

### Data Files

If you're upgrading from source, ensure all 5 data files are present:

```bash
# Verify data files
python -c "from word32.data_manager import get_data_manager; \
          dm = get_data_manager(); \
          issues = dm.validate_data_completeness(); \
          print('Issues:', issues if issues else 'None')"
```

---

## Testing

Comprehensive test suite included:

- **99+ test cases** covering all functionality
- **Integration tests** for full game workflows
- **Cross-platform tests** for consistency
- **Performance tests** to verify targets
- **Backwards compatibility tests**

Run tests:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Bug Fixes

- Fixed version consistency (now 0.1.3 across all files)
- Improved error messages for invalid data files
- Enhanced validation to catch edge cases

---

## Known Issues

None at this time.

---

## Contributors

Built by Ben Mazzotta as part of the 3-2-Word project.

---

## Links

- **GitHub**: https://github.com/benmazzotta/32word
- **PyPI**: https://pypi.org/project/32word/
- **Documentation**: See `docs/` directory in repository

---

## Changelog

### v0.1.3 (2026-01-19)

- Added Phase 4.2 response schema (GameResponse, ErrorResponse, etc.)
- Added Phase 4.3 custom first guess selection (32 options)
- Added data validation on import
- Added custom exception classes
- Added comprehensive type hints
- Added logging throughout
- Added configuration options
- Enhanced Strategy class to support all 32 first guesses
- Created comprehensive integration documentation
- Fixed version consistency

### v0.1.2

- Initial release with core functionality

---

**Get started:**

```bash
pip install 32word
```

```python
from word32 import get_available_first_guesses, build_game_response

# Get all 32 first guess options
options = get_available_first_guesses()
print(f"Available first guesses: {len(options)}")

# Build a game response
response = build_game_response(
    guess="RAISE",
    clue=('G', 'Y', 'X', 'X', 'G'),
    remaining_targets=['AGILE', 'ALIAS', 'AMISS']
)
print(f"Remaining words: {response.remaining.count}")
```
