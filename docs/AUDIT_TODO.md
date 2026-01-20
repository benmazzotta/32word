# 32word Library - Documentation & Completeness Audit TODO

**Created:** 2026-01-20
**Status:** Pending Review
**Priority:** HIGH
**Version:** 0.2.0

---

## Purpose

This audit checklist identifies potential gaps between implemented features and their documentation, particularly features that exist in the codebase but may not be properly documented or communicated to users.

**Discovery:** The 2d_8r strategy system (11 strategies with 8-clue memorization) is fully implemented and functional but not mentioned in `RELEASE_NOTES_0.2.0.md` or `README.md`.

---

## AUDIT CATEGORY 1: Documentation Gaps - 2d_8r Strategies

### Issue
11 2d_8r strategies are implemented and exported but undocumented in user-facing docs.

### Tasks

- [ ] **Document 2d_8r strategies in RELEASE_NOTES_0.2.0.md**
  - Add section: "New Depth Strategies (Phase 4.8/4.9)"
  - List all 11 available strategies with win rates
  - Document API functions: `load_strategy_by_components()`, `list_strategies_by_depth()`, `list_all_strategies()`
  - Provide usage examples
  - Location: After Phase 4.3 section, before "Improvements"

- [ ] **Document 2d_8r strategies in README.md**
  - Add section: "Advanced: Depth Strategies"
  - Quick-start example for loading TRICE or SIREN strategy
  - Link to comprehensive docs
  - Location: After Phase 4.2/4.3 features section

- [ ] **Create dedicated strategy guide**
  - File: `docs/STRATEGY_SELECTION_GUIDE.md`
  - Compare default (Phase 3) vs 2d_8r strategies
  - When to use 8-clue memorization vs full lookup
  - Performance characteristics (memory, 2-guess win rate)
  - All 11 strategies documented with metadata

- [ ] **Update DOCUMENTATION.md**
  - Add API reference for:
    - `load_strategy_by_components(guess1, depth)`
    - `list_strategies_by_depth(depth)`
    - `list_all_strategies()`
  - Add strategy metadata structure documentation
  - Add examples for each function

- [ ] **Verify strategy data files in package distribution**
  - Confirm `word32/data/strategies/*.json` included in wheel
  - Check `MANIFEST.in` includes `recursive-include word32/data/strategies *.json`
  - Verify `pyproject.toml` package-data configuration
  - Test: Install from wheel and verify files present

### Acceptance Criteria
- [ ] All 11 2d_8r strategies documented in release notes
- [ ] README includes quick-start for depth strategies
- [ ] Strategy selection guide created
- [ ] API documentation complete
- [ ] PyPI package includes all strategy files

---

## AUDIT CATEGORY 2: API Exports vs Documentation

### Issue
Need to verify all exported functions are documented.

### Tasks

- [ ] **Audit all exports in `word32/__init__.py`**
  - List all functions in `__all__`
  - Cross-reference with DOCUMENTATION.md
  - Identify undocumented exports
  - Create tracking spreadsheet: Function name | Documented in DOCUMENTATION.md | Documented in README | Documented in Release Notes

- [ ] **Verify configuration functions documented**
  - `set_guess_validation_mode()` - Check docs
  - `get_guess_validation_mode()` - Check docs
  - `reset_guess_validation_mode()` - Check docs
  - Are these documented in DOCUMENTATION.md?
  - Are these mentioned in RELEASE_NOTES?
  - Do users know these exist?

- [ ] **Verify custom exceptions documented**
  - `Word32Error` - Check docs
  - `DataValidationError` - Check docs
  - `StrategyNotFoundError` - Check docs
  - `InvalidClueError` - Check docs
  - `InvalidGuessError` - Check docs
  - Are error codes documented?
  - Are exception use cases documented?

- [ ] **Create function coverage matrix**
  - File: `docs/API_COVERAGE_MATRIX.md`
  - Columns: Function | DOCUMENTATION.md | README.md | Release Notes | Integration Guides | Tests
  - Identify gaps
  - Prioritize documentation updates

### Acceptance Criteria
- [ ] All 109 exports verified against documentation
- [ ] Configuration functions fully documented
- [ ] Exception classes fully documented
- [ ] Coverage matrix created

---

## AUDIT CATEGORY 3: Data Files vs Documentation

### Issue
Verify all data files are documented and included in package.

### Tasks

- [ ] **Audit data directory structure**
  - List all files in `word32/data/`
  - List all files in `word32/data/strategies/`
  - Compare against DATA_COMPLETENESS_CHECKLIST.md
  - Identify undocumented files

- [ ] **Verify strategy files documented**
  - Expected: 11 strategy files (2d_8r_*.json)
  - Document: File structure, metadata format
  - Document: How to add new strategies
  - Document: Validation requirements

- [ ] **Check legacy files**
  - `v1.0.json` - Still needed? Documented?
  - Are there other legacy files not documented?
  - Should old files be deprecated?

- [ ] **Verify MANIFEST.in completeness**
  - Check all data files included
  - Check all strategy files included
  - Verify recursive includes for subdirectories
  - Test: Build package and inspect contents

### Acceptance Criteria
- [ ] All data files documented in DATA_COMPLETENESS_CHECKLIST.md
- [ ] All strategy files listed and described
- [ ] Legacy file status clarified
- [ ] Package distribution verified

---

## AUDIT CATEGORY 4: Test Coverage for New Features

### Issue
Verify 2d_8r strategies have adequate test coverage.

### Tasks

- [ ] **Audit test coverage for depth strategies**
  - Are `load_strategy_by_components()` tests comprehensive?
  - Are `list_strategies_by_depth()` tests comprehensive?
  - Are `list_all_strategies()` tests comprehensive?
  - Review `tests/test_strategy.py` for depth strategy tests

- [ ] **Verify edge cases tested**
  - Loading non-existent strategy (error handling)
  - Invalid depth parameter
  - Invalid first guess parameter
  - Corrupted strategy file handling

- [ ] **Integration tests for depth strategies**
  - Full game flow with TRICE strategy
  - Full game flow with SIREN strategy
  - Compare results to default ATONE strategy
  - Verify 2-guess win rate matches metadata

- [ ] **Performance tests for depth strategies**
  - Memory usage comparison (8-clue vs full lookup)
  - Load time comparison
  - Lookup speed comparison
  - Document findings

### Acceptance Criteria
- [ ] All depth strategy functions have 5+ tests each
- [ ] Edge cases covered
- [ ] Integration tests for at least 2 strategies
- [ ] Performance benchmarks documented

---

## AUDIT CATEGORY 5: Migration & Upgrade Path

### Issue
Users upgrading from v0.1.x may not know about new features.

### Tasks

- [ ] **Create migration guide for v0.1.x → v0.2.0**
  - File: `docs/MIGRATION_GUIDE_0.2.0.md`
  - What's new section highlighting 2d_8r strategies
  - Breaking changes (if any)
  - Deprecation notices (if any)
  - Step-by-step upgrade instructions
  - Code examples: before/after

- [ ] **Update RELEASE_NOTES with "What's New" highlights**
  - Top 5 features users should know about
  - Make 2d_8r strategies prominent
  - Include "try this first" examples

- [ ] **Create "What Should I Use?" decision tree**
  - Default Phase 3 (32 options, full coverage) vs
  - 2d_8r strategies (11 options, 8-clue memorization)
  - When to use which?
  - Trade-offs documented

### Acceptance Criteria
- [ ] Migration guide created
- [ ] Release notes updated with highlights
- [ ] Decision tree/selection guide created

---

## AUDIT CATEGORY 6: Integration Guide Completeness

### Issue
Integration guides may not cover all features.

### Tasks

- [ ] **Audit INTEGRATION_WEB_APP.md**
  - Does it mention 2d_8r strategies?
  - Does it show how to let users select a strategy?
  - Does it cover configuration functions?
  - Update with depth strategy examples

- [ ] **Audit INTEGRATION_DISCORD_BOT.md**
  - Does it mention 2d_8r strategies?
  - Does it show minimal mode with TRICE/SIREN?
  - Update with depth strategy examples

- [ ] **Audit INTEGRATION_CLI.md**
  - Does it document strategy selection parameter?
  - Does it show how to use `--strategy 2d-8r-trice`?
  - Are all CLI options documented?

- [ ] **Create INTEGRATION_ADVANCED.md**
  - Advanced use cases
  - Custom strategy development
  - Performance tuning
  - Memory optimization
  - Strategy comparison tools

### Acceptance Criteria
- [ ] All 3 integration guides mention depth strategies
- [ ] Code examples updated
- [ ] Advanced integration guide created

---

## AUDIT CATEGORY 7: Package Distribution Verification

### Issue
Ensure PyPI package includes all necessary files.

### Tasks

- [ ] **Build test package**
  - Run: `python -m build`
  - Inspect wheel contents: `python -m zipfile -l dist/32word-*.whl`
  - Verify all strategy files present
  - Verify all data files present
  - Verify all docs included (if intended for package)

- [ ] **Test installation from wheel**
  - Create clean venv
  - Install from wheel
  - Test import: `import word32`
  - Test loading all 11 strategies
  - Verify data validation passes
  - Document any issues

- [ ] **Verify PyPI metadata**
  - Long description (from README?) accurate?
  - Keywords include "wordle", "strategy", "depth", "2d-8r"?
  - Classifiers appropriate?
  - Project URLs complete?

- [ ] **Check package size**
  - Is package size reasonable?
  - Are unnecessary files excluded?
  - Are large files documented as necessary?

### Acceptance Criteria
- [ ] Package builds successfully
- [ ] All files present in wheel
- [ ] Installation test passes
- [ ] PyPI metadata accurate

---

## AUDIT CATEGORY 8: Version Consistency & Changelog

### Issue
Ensure version numbers consistent and changelog complete.

### Tasks

- [ ] **Verify version consistency across all files**
  - `word32/__init__.py`: `__version__ = "0.2.0"` ✓
  - `pyproject.toml`: `version = "0.2.0"` ✓
  - `RELEASE_NOTES_0.2.0.md`: Title matches ✓
  - Any other files with version references?

- [ ] **Create/update CHANGELOG.md**
  - Does CHANGELOG.md exist?
  - If not, create it
  - Format: Keep a Changelog (https://keepachangelog.com/)
  - Sections: Added, Changed, Deprecated, Removed, Fixed, Security
  - Include all changes from v0.1.x to v0.2.0

- [ ] **Document feature timeline**
  - When were 2d_8r strategies added?
  - What phase workplan do they correspond to? (Phase 4.8? 4.9?)
  - Cross-reference with workplan docs in parent repo

- [ ] **Update roadmap if needed**
  - Check: `../wordle-in-three/docs/core/roadmap.md`
  - Mark depth strategies as complete
  - Update status for 32word library

### Acceptance Criteria
- [ ] All version numbers consistent
- [ ] CHANGELOG.md created/updated
- [ ] Feature timeline documented
- [ ] Roadmap updated in parent repo

---

## AUDIT CATEGORY 9: Performance & Benchmarks

### Issue
Document performance characteristics of depth strategies.

### Tasks

- [ ] **Benchmark depth strategies vs default**
  - Memory usage: 2d_8r vs phase3_lookup
  - Load time: Each strategy file load time
  - Lookup speed: Second guess recommendation speed
  - 2-guess win rate: Verify matches metadata
  - Create benchmarking script

- [ ] **Document trade-offs**
  - File: `docs/PERFORMANCE_CHARACTERISTICS.md`
  - Memory: 2d_8r (~650 bytes) vs phase3 (435KB)
  - Coverage: 8 clues vs ~30 clues per first guess
  - Win rate: Best 2d_8r (39.14%) vs default ATONE
  - Load time comparison
  - Use case recommendations

- [ ] **Create comparison table**
  - Strategy | File Size | Memory | 2-Guess Win Rate | Coverage
  - Include all 11 2d_8r options
  - Include default ATONE/phase3
  - Include phase2 naive options

### Acceptance Criteria
- [ ] Benchmarks run and documented
- [ ] Performance guide created
- [ ] Comparison table in docs

---

## AUDIT CATEGORY 10: Examples & Tutorials

### Issue
Need real-world examples of using depth strategies.

### Tasks

- [ ] **Create examples directory**
  - Directory: `examples/`
  - Gitignore if sensitive
  - Or include in package

- [ ] **Example 1: Simple game with TRICE**
  - File: `examples/simple_game_trice.py`
  - Load TRICE strategy
  - Play full game
  - Show 2-guess win example

- [ ] **Example 2: Strategy comparison**
  - File: `examples/compare_strategies.py`
  - Compare ATONE vs TRICE vs SIREN
  - Run 100 games each
  - Report win rates, mean remaining

- [ ] **Example 3: List and select strategy**
  - File: `examples/interactive_strategy_selection.py`
  - List all available strategies
  - Let user select one
  - Play game with selected strategy

- [ ] **Example 4: Web app integration snippet**
  - File: `examples/web_app_strategy_selector.py`
  - Flask/FastAPI endpoint
  - Return available strategies as JSON
  - Handle user selection

### Acceptance Criteria
- [ ] Examples directory created
- [ ] 4+ working examples
- [ ] Examples tested and verified
- [ ] Examples mentioned in README

---

## PRIORITY MATRIX

### Critical (Block PyPI Release)
- [ ] Verify all data files in package distribution
- [ ] Test installation from built wheel
- [ ] All 11 strategies loadable after install

### High (Should fix before promoting v0.2.0)
- [ ] Document 2d_8r strategies in RELEASE_NOTES
- [ ] Document 2d_8r strategies in README
- [ ] Create API coverage matrix
- [ ] Verify MANIFEST.in completeness

### Medium (Improve discoverability)
- [ ] Create STRATEGY_SELECTION_GUIDE.md
- [ ] Update integration guides
- [ ] Create migration guide
- [ ] Add examples directory

### Low (Nice to have)
- [ ] Performance benchmarks
- [ ] Advanced integration guide
- [ ] Tutorial examples
- [ ] Comparison tools

---

## IMPLEMENTATION PLAN

### Phase 1: Critical Issues (Week 1)
1. Build package and verify contents
2. Test installation
3. Verify all strategies loadable

### Phase 2: Documentation (Week 1-2)
1. Update RELEASE_NOTES_0.2.0.md
2. Update README.md
3. Create STRATEGY_SELECTION_GUIDE.md
4. Update DOCUMENTATION.md

### Phase 3: Verification (Week 2)
1. Create API coverage matrix
2. Audit all integration guides
3. Update guides with depth strategy examples

### Phase 4: Enhancement (Week 3+)
1. Create migration guide
2. Add examples directory
3. Performance benchmarks
4. Advanced guides

---

## TRACKING

### Completion Status
- **Total Tasks:** 70+
- **Completed:** 0
- **In Progress:** 0
- **Blocked:** 0

### Last Updated
- **Date:** 2026-01-20
- **By:** Initial draft
- **Status:** Awaiting review and prioritization

---

## NOTES

### Discovery Context
This audit was triggered by discovering that:
1. 11 2d_8r strategies fully implemented in codebase
2. All strategies have data files (word32/data/strategies/*.json)
3. All strategies are tested (tests/test_strategy.py)
4. All strategies are exported via public API
5. **BUT**: No mention in RELEASE_NOTES_0.2.0.md or README.md

This suggests a pattern: Features implemented but not documented/communicated.

### Questions to Resolve
1. Were 2d_8r strategies intentionally excluded from v0.2.0 release notes?
2. Are there other features in similar "implemented but undocumented" state?
3. Should we publish v0.2.0 as-is or update docs first?
4. Should we create v0.2.1 with documentation updates?

### Recommendations
1. **Before PyPI publication:** Verify package contents (Critical tasks)
2. **Before promotion:** Update RELEASE_NOTES and README (High priority tasks)
3. **After publication:** Add comprehensive guides (Medium/Low priority)

---

## SIGN-OFF

- [ ] Audit reviewed by: __________
- [ ] Priority confirmed by: __________
- [ ] Implementation plan approved by: __________
- [ ] Ready to begin: __________

---

**Status:** DRAFT - Awaiting Review
