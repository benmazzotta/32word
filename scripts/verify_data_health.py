#!/usr/bin/env python3
"""Data health verification script for 32word library.

Generates a comprehensive report on data completeness, consistency, and coverage.
Can be run standalone: python scripts/verify_data_health.py

Exit codes:
    0 - All checks passed
    1 - Data issues found
    2 - Critical errors (missing files, etc.)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


def load_json_file(filepath: Path) -> dict:
    """Load JSON file, return empty dict if not found."""
    if not filepath.exists():
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {filepath} is not valid JSON: {e}", file=sys.stderr)
        return {}


def load_word_list(filepath: Path) -> set:
    """Load word list file, return empty set if not found."""
    if not filepath.exists():
        return set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return {line.strip().upper() for line in f if line.strip() and len(line.strip()) == 5}
    except Exception as e:
        print(f"ERROR: Could not load {filepath}: {e}", file=sys.stderr)
        return set()


def generate_coverage_report(data_dir: Path) -> Dict:
    """Generate comprehensive data health report."""
    report = {
        'summary': {},
        'phase2_to_phase3_coverage': {},
        'clue_pattern_coverage': {},
        'data_consistency': {
            'invalid_words': [],
            'duplicate_patterns': [],
            'missing_data': []
        },
        'per_first_guess': {},
        'recommendations': []
    }
    
    # Load data files
    phase2_file = data_dir / 'phase2_naive_32.json'
    phase3_file = data_dir / 'phase3_lookup.json'
    valid_guesses_file = data_dir / 'valid_guesses.txt'
    targets_file = data_dir / 'targets.txt'
    
    phase2_data = load_json_file(phase2_file)
    phase3_data = load_json_file(phase3_file)
    valid_guesses = load_word_list(valid_guesses_file)
    valid_targets = load_word_list(targets_file)
    
    # Summary
    report['summary'] = {
        'total_first_guesses': len(phase2_data) if isinstance(phase2_data, list) else 0,
        'first_guesses_in_phase3': 0,
        'total_clue_patterns': 0,
        'valid_guesses_count': len(valid_guesses),
        'valid_targets_count': len(valid_targets)
    }
    
    if not phase2_data:
        report['recommendations'].append("CRITICAL: phase2_naive_32.json not found or invalid")
        return report
    
    if not phase3_data:
        report['recommendations'].append("CRITICAL: phase3_lookup.json not found or invalid")
        return report
    
    # Phase 2 to Phase 3 coverage
    phase2_guesses = {entry['guess'].upper() for entry in phase2_data if isinstance(entry, dict) and 'guess' in entry}
    phase3_guesses = set(phase3_data.keys()) if isinstance(phase3_data, dict) else set()
    
    report['phase2_to_phase3_coverage'] = {
        'phase2_guesses': len(phase2_guesses),
        'phase3_guesses': len(phase3_guesses),
        'missing_in_phase3': list(phase2_guesses - phase3_guesses),
        'orphaned_in_phase3': list(phase3_guesses - phase2_guesses)
    }
    
    report['summary']['first_guesses_in_phase3'] = len(phase2_guesses & phase3_guesses)
    
    # Clue pattern coverage
    total_patterns = 0
    low_coverage_guesses = []
    
    for first_guess in phase2_guesses & phase3_guesses:
        patterns = phase3_data.get(first_guess, {})
        if isinstance(patterns, dict):
            pattern_count = len(patterns)
            total_patterns += pattern_count
            
            # Check for duplicate patterns
            pattern_list = list(patterns.keys())
            if len(pattern_list) != len(set(pattern_list)):
                report['data_consistency']['duplicate_patterns'].append(first_guess)
            
            # Check pattern validity
            invalid_patterns = []
            for pattern in patterns.keys():
                if len(pattern) != 5:
                    invalid_patterns.append(pattern)
                elif not all(c in 'GYX' for c in pattern):
                    invalid_patterns.append(pattern)
            
            if invalid_patterns:
                report['data_consistency']['missing_data'].append({
                    'first_guess': first_guess,
                    'invalid_patterns': invalid_patterns
                })
            
            # Check for low coverage
            if pattern_count < 10:
                low_coverage_guesses.append((first_guess, pattern_count))
            
            # Per-first-guess breakdown
            entry = next((e for e in phase2_data if e.get('guess', '').upper() == first_guess), {})
            report['per_first_guess'][first_guess] = {
                'rank': entry.get('rank', 0),
                'clue_pattern_count': pattern_count,
                'coverage_percentage': (pattern_count / 243.0 * 100) if pattern_count > 0 else 0,  # 3^5 = 243 max
                'expected_remaining': entry.get('expected_remaining', 0)
            }
            
            # Check second guess validity
            for pattern, candidates in patterns.items():
                if isinstance(candidates, list) and len(candidates) > 0:
                    top_candidate = candidates[0]
                    if isinstance(top_candidate, dict):
                        second_guess = top_candidate.get('second_guess', '')
                        if second_guess and second_guess.upper() not in valid_guesses:
                            report['data_consistency']['invalid_words'].append({
                                'first_guess': first_guess,
                                'pattern': pattern,
                                'word': second_guess
                            })
    
    report['summary']['total_clue_patterns'] = total_patterns
    report['clue_pattern_coverage'] = {
        'total_patterns': total_patterns,
        'average_patterns_per_guess': total_patterns / len(phase2_guesses & phase3_guesses) if (phase2_guesses & phase3_guesses) else 0,
        'low_coverage_guesses': low_coverage_guesses
    }
    
    # Generate recommendations
    if report['phase2_to_phase3_coverage']['missing_in_phase3']:
        report['recommendations'].append(
            f"Missing {len(report['phase2_to_phase3_coverage']['missing_in_phase3'])} first guesses in phase3_lookup.json"
        )
    
    if report['data_consistency']['invalid_words']:
        report['recommendations'].append(
            f"Found {len(report['data_consistency']['invalid_words'])} invalid second guess words"
        )
    
    if report['data_consistency']['duplicate_patterns']:
        report['recommendations'].append(
            f"Found duplicate clue patterns for {len(report['data_consistency']['duplicate_patterns'])} first guesses"
        )
    
    if low_coverage_guesses:
        report['recommendations'].append(
            f"Found {len(low_coverage_guesses)} first guesses with low clue pattern coverage (<10 patterns)"
        )
    
    if not report['recommendations']:
        report['recommendations'].append("All checks passed - data is healthy!")
    
    return report


def print_report(report: Dict, verbose: bool = False):
    """Print report to console."""
    print("=" * 70)
    print("32word Data Health Report")
    print("=" * 70)
    print()
    
    # Summary
    print("SUMMARY")
    print("-" * 70)
    summary = report['summary']
    print(f"Total first guesses: {summary['total_first_guesses']}")
    print(f"First guesses in phase3_lookup.json: {summary['first_guesses_in_phase3']}")
    print(f"Total clue patterns: {summary['total_clue_patterns']}")
    print(f"Valid guesses count: {summary['valid_guesses_count']}")
    print(f"Valid targets count: {summary['valid_targets_count']}")
    print()
    
    # Phase 2 to Phase 3 coverage
    coverage = report['phase2_to_phase3_coverage']
    if coverage['missing_in_phase3']:
        print("PHASE 2 TO PHASE 3 COVERAGE ISSUES")
        print("-" * 70)
        print(f"Missing in phase3_lookup.json: {len(coverage['missing_in_phase3'])}")
        if verbose:
            for guess in coverage['missing_in_phase3']:
                print(f"  - {guess}")
        print()
    
    # Clue pattern coverage
    clue_coverage = report['clue_pattern_coverage']
    print("CLUE PATTERN COVERAGE")
    print("-" * 70)
    print(f"Average patterns per first guess: {clue_coverage['average_patterns_per_guess']:.1f}")
    if clue_coverage['low_coverage_guesses']:
        print(f"Low coverage guesses (<10 patterns): {len(clue_coverage['low_coverage_guesses'])}")
        if verbose:
            for guess, count in clue_coverage['low_coverage_guesses']:
                print(f"  - {guess}: {count} patterns")
    print()
    
    # Data consistency issues
    consistency = report['data_consistency']
    has_issues = False
    
    if consistency['invalid_words']:
        has_issues = True
        print("DATA CONSISTENCY ISSUES")
        print("-" * 70)
        print(f"Invalid words: {len(consistency['invalid_words'])}")
        if verbose:
            for issue in consistency['invalid_words'][:10]:  # Show first 10
                print(f"  - {issue['first_guess']} / {issue['pattern']}: {issue['word']}")
        print()
    
    if consistency['duplicate_patterns']:
        has_issues = True
        print(f"Duplicate patterns: {len(consistency['duplicate_patterns'])} first guesses")
        if verbose:
            for guess in consistency['duplicate_patterns']:
                print(f"  - {guess}")
        print()
    
    # Recommendations
    print("RECOMMENDATIONS")
    print("-" * 70)
    for rec in report['recommendations']:
        print(f"  - {rec}")
    print()
    
    # Per-first-guess breakdown (if verbose)
    if verbose and report['per_first_guess']:
        print("PER-FIRST-GUESS BREAKDOWN")
        print("-" * 70)
        for guess, info in sorted(report['per_first_guess'].items(), key=lambda x: x[1]['rank']):
            print(f"{guess} (rank {info['rank']}): {info['clue_pattern_count']} patterns "
                  f"({info['coverage_percentage']:.1f}% coverage)")
        print()
    
    return has_issues


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Verify data health for 32word library'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output report to JSON file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed information'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Path to data directory (default: word32/data)'
    )
    
    args = parser.parse_args()
    
    # Determine data directory
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        # Default to word32/data relative to script location
        script_dir = Path(__file__).parent
        data_dir = script_dir.parent / 'word32' / 'data'
    
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(2)
    
    # Generate report
    report = generate_coverage_report(data_dir)
    
    # Print to console
    has_issues = print_report(report, verbose=args.verbose)
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {output_path}")
    
    # Exit code
    if has_issues or report['phase2_to_phase3_coverage']['missing_in_phase3']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
