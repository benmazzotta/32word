# Data Completeness Checklist

This document describes all required data files for the 32word library and how to validate their integrity.

## Required Data Files

The 32word library requires the following data files in the `word32/data/` directory:

### 1. `targets.txt`
- **Purpose**: List of valid Wordle target words (words that can be the answer)
- **Expected Count**: ~3,158 words (one per line) - may vary based on word list version
- **Expected Size**: ~19 KB
- **Format**: One 5-letter word per line, uppercase
- **Used By**: 
  - Phase 1: `load_targets()`, `VALID_TARGETS`
  - Phase 4.2: Remaining words tracking in `build_game_response()`
- **Validation Rules**:
  - All words must be exactly 5 letters
  - All words must be alphabetic (no numbers or special characters)
  - No duplicate words
  - Word count must be between 2,300 and 3,200 (allows for extended word lists)

**Example:**
```
ABACK
ABASE
ABATE
...
```

### 2. `valid_guesses.txt`
- **Purpose**: List of all valid Wordle guess words (words that can be guessed, including targets)
- **Expected Count**: ~14,855 words (one per line) - may vary based on word list version
- **Expected Size**: ~87 KB
- **Format**: One 5-letter word per line, uppercase
- **Used By**:
  - Phase 1: `load_valid_guesses()`, `VALID_GUESSES`, `is_valid_word()`
  - Phase 4.2: Word validation in response schema
- **Validation Rules**:
  - All words must be exactly 5 letters
  - All words must be alphabetic
  - No duplicate words
  - Word count must be between 12,900 and 15,000 (allows for extended word lists)
  - Must include all words from `targets.txt` (targets are a subset of guesses)

**Example:**
```
AAHED
AALII
AARGH
...
```

### 3. `phase2_naive_32.json`
- **Purpose**: List of 32 first guess options with metrics from Phase 2 analysis
- **Expected Count**: 32 entries (JSON array)
- **Expected Size**: ~7.5 KB
- **Format**: JSON array of objects
- **Used By**:
  - Phase 4.3: `get_available_first_guesses()`, `select_first_guess()`
- **Validation Rules**:
  - Must be valid JSON
  - Must be an array with exactly 32 entries
  - Each entry must be an object with required fields:
    - `rank`: integer (1-32)
    - `guess`: string (5-letter word)
    - `expected_remaining`: float
  - Optional fields: `max_remaining`, `clue_diversity`, `variance`, `std_dev`, `total_targets`
  - All guesses must be 5-letter strings

**Example Structure:**
```json
[
  {
    "rank": 1,
    "guess": "RAISE",
    "expected_remaining": 90.14946168461051,
    "max_remaining": 240,
    "clue_diversity": 137,
    "variance": 1546.6908199690981,
    "std_dev": 39.32799028642448,
    "total_targets": 3158
  },
  ...
]
```

### 4. `phase3_lookup.json`
- **Purpose**: Strategy lookup table for all 32 first guesses and their clue patterns
- **Expected Size**: ~425 KB
- **Format**: JSON object (nested dictionary)
- **Used By**:
  - Phase 4.3: `get_strategy_for_first_guess()`, `get_second_guess_recommendation()`
- **Validation Rules**:
  - Must be valid JSON
  - Must be a dictionary (object)
  - Structure: `{first_guess: {clue_pattern: [{second_guess, rank, ...}, ...]}}`
  - Each first_guess key must be a 5-letter string (one of the 32 from phase2_naive_32.json)
  - Each clue_pattern must be a 5-character string (G, Y, X)
  - Each candidate must have `second_guess` field (5-letter string)
  - All second_guess values must be valid words (in valid_guesses.txt)

**Example Structure:**
```json
{
  "RAISE": {
    "XXXXX": [
      {"second_guess": "YMOLT", "rank": 1, "expected_remaining": 10.075, "max_remaining": 23},
      {"second_guess": "BLUDY", "rank": 2, "expected_remaining": 10.308, "max_remaining": 24}
    ],
    "XXXXY": [
      {"second_guess": "TOLED", "rank": 1, "expected_remaining": 11.521, "max_remaining": 30}
    ]
  }
}
```

### 5. `v1.0.json`
- **Purpose**: Legacy strategy file for backwards compatibility (Phase 1)
- **Expected Size**: ~425 KB
- **Format**: JSON object (dictionary)
- **Used By**:
  - Phase 1: `load_strategy()`, `Strategy` class (default ATONE strategy)
- **Validation Rules**:
  - Must be valid JSON
  - Must be a dictionary (object)
  - Structure compatible with `Strategy` class lookup table
  - Used for backwards compatibility with Phase 1 code

## Validation

The library automatically validates all data files on import. If validation fails, a warning is issued but the import succeeds (to allow graceful degradation).

### Running Validation

Validation is performed automatically when you import the library:

```python
import word32  # Validation runs automatically
```

To manually check validation status:

```python
from word32.data_manager import get_data_manager

dm = get_data_manager()
issues = dm.validate_data_completeness()
if issues:
    print("Validation issues:", issues)
else:
    print("All data files are valid!")
```

### Getting File Information

To get detailed information about all data files:

```python
from word32.data_manager import get_data_manager

dm = get_data_manager()
file_info = dm.get_required_files()
for filename, info in file_info.items():
    print(f"{filename}: exists={info['exists']}, size={info['size']} bytes")
```

## Troubleshooting

### "Data validation issues detected"

**Symptom**: Warning message on import listing missing or invalid files.

**Causes**:
- Missing data files
- Corrupted JSON files
- Invalid file format (wrong word count, invalid structure)

**Recovery Steps**:
1. Check that all 5 required files exist in `word32/data/`
2. Verify file sizes match expected ranges
3. For JSON files, validate JSON syntax: `python3 -m json.tool word32/data/phase2_naive_32.json`
4. For word lists, check line count: `wc -l word32/data/targets.txt`
5. If files are missing, copy from the source repository (wordle-in-three)

### "Missing phase3_lookup.json"

**Symptom**: Warning about missing `phase3_lookup.json` file.

**Impact**: 
- `get_strategy_for_first_guess()` will return empty dict
- `get_second_guess_recommendation()` will return None
- Phase 4.3 strategy features will not work

**Recovery**:
1. Ensure `phase3_lookup.json` exists in `word32/data/`
2. Verify file size is ~425 KB
3. Validate JSON structure: `python3 -c "import json; json.load(open('word32/data/phase3_lookup.json'))"`
4. If missing, copy from wordle-in-three repository

### "Missing phase2_naive_32.json"

**Symptom**: Warning about missing `phase2_naive_32.json` file.

**Impact**:
- `get_available_first_guesses()` will return empty list
- `select_first_guess()` will return None for all guesses
- Phase 4.3 first guess selection will not work

**Recovery**:
1. Ensure `phase2_naive_32.json` exists in `word32/data/`
2. Verify file size is ~7.5 KB
3. Validate JSON structure and count: `python3 -c "import json; data = json.load(open('word32/data/phase2_naive_32.json')); print(f'Count: {len(data)}')"`
4. If missing, copy from wordle-in-three repository

### "Invalid JSON in [filename]"

**Symptom**: Warning about JSON parsing errors.

**Causes**:
- Corrupted file
- Invalid JSON syntax
- File encoding issues

**Recovery**:
1. Validate JSON syntax: `python3 -m json.tool word32/data/[filename]`
2. Check file encoding (should be UTF-8)
3. If corrupted, restore from backup or source repository

### "Expected [count] words, got [count]"

**Symptom**: Warning about incorrect word count in word list files.

**Causes**:
- File truncated or incomplete
- Extra blank lines or formatting issues
- Wrong version of data file

**Recovery**:
1. Verify line count: `wc -l word32/data/[filename]`
2. Check for blank lines: `grep -c '^$' word32/data/[filename]`
3. Verify all words are 5 letters: `python3 -c "words = [line.strip() for line in open('word32/data/[filename]') if line.strip()]; print(f'Valid: {all(len(w) == 5 for w in words)}')"`
4. If incorrect, restore from source repository

### "Stale data"

**Symptom**: Data files exist but may be outdated.

**Impact**: 
- Strategy recommendations may be suboptimal
- Word lists may be missing new words
- Performance may be affected

**Recovery**:
1. Check data file modification dates
2. Compare checksums with source repository
3. Update from wordle-in-three repository if newer versions available
4. Re-run validation after update

## File Checksums

The library computes MD5 checksums at runtime for integrity verification. To get checksums:

```python
from word32.data_manager import get_data_manager

dm = get_data_manager()
file_info = dm.get_required_files()
for filename, info in file_info.items():
    if info['exists']:
        print(f"{filename}: {info['checksum']}")
```

## Performance

- **First validation**: < 100ms (includes file reads and checksum computation)
- **Subsequent validations**: < 10ms (cached results)
- **JSON integrity check**: < 20ms per file
- **File checksum computation**: < 50ms per file

## Data Sources

All data files should be synchronized with the wordle-in-three repository:
- `targets.txt` and `valid_guesses.txt`: Standard Wordle word lists
- `phase2_naive_32.json`: Generated from Phase 2 analysis
- `phase3_lookup.json`: Generated from Phase 3 strategy computation
- `v1.0.json`: Legacy strategy file for backwards compatibility

## Version Compatibility

- **Library Version 0.1.3**: Requires all 5 data files
- **Phase 4.2/4.3 Features**: Require `phase2_naive_32.json` and `phase3_lookup.json`
- **Phase 1 Features**: Require `targets.txt`, `valid_guesses.txt`, `v1.0.json`
- **Backwards Compatibility**: All Phase 1 features work with Phase 1 data files only
