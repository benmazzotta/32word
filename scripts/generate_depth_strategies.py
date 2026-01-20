#!/usr/bin/env python3
"""
Generate depth-based strategy files from tournament results.

Converts tournament result JSON files from the wordle-in-three project
into lightweight strategy JSON files that reference phase3_lookup.json.

Usage:
    # Generate single strategy
    python scripts/generate_depth_strategies.py \
        --input path/to/2d_8r_trice_n3158.json \
        --output word32/data/strategies/2d_8r_trice.json

    # Generate all 2d-8r strategies
    python scripts/generate_depth_strategies.py \
        --batch \
        --depth 8 \
        --input-dir path/to/outputs/strategies \
        --output-dir word32/data/strategies
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def extract_selected_patterns(tournament_data: dict) -> List[str]:
    """Extract pattern list from selected_clue1s array."""
    selected = tournament_data.get("selected_clue1s", [])
    return [item["clue1"] for item in selected]


def generate_strategy_file(
    tournament_file: Path,
    output_file: Path,
    depth: int = None
) -> None:
    """
    Generate a single strategy file from tournament results.

    Args:
        tournament_file: Path to tournament JSON file
        output_file: Path for output strategy JSON
        depth: Expected depth (if None, inferred from file or selected_clue1s count)
    """

    with open(tournament_file, 'r') as f:
        data = json.load(f)

    guess1 = data["guess1"].upper()
    win_rate = data.get("overall_win_rate", 0.0)
    mean_remaining = data.get("mean_remaining", 0.0)
    remainder_guess2 = data.get("remainder_guess2", "").upper()
    selected_patterns = extract_selected_patterns(data)

    # Infer depth if not provided
    if depth is None:
        depth = len(selected_patterns)

    # Validate pattern count matches depth
    if len(selected_patterns) != depth:
        raise ValueError(
            f"Pattern count mismatch: expected {depth}, got {len(selected_patterns)}"
        )

    # Build strategy dict with lightweight format
    strategy = {
        "metadata": {
            "version": f"2d-{depth}r-{guess1.lower()}",
            "guess1": guess1,
            "depth": 2,
            "clue_count": depth,
            "penalty_function": "expected_remaining",
            "optimization": "2deep",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "win_rate_2d": win_rate,
            "mean_remaining_2d": mean_remaining,
            "remainder_guess2": remainder_guess2,
            "description": (
                f"{depth}-clue strategy with {guess1} first guess "
                f"({win_rate*100:.2f}% win rate in 2 guesses)"
            )
        },
        "first_guess": guess1,
        "selected_patterns": selected_patterns,
        "remainder_guess2": remainder_guess2,
        "lookup_source": "phase3_lookup"
    }

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(strategy, f, indent=2)

    print(f"✓ Generated {output_file.name}")
    print(f"  Guess1: {guess1}")
    print(f"  Patterns: {len(selected_patterns)}")
    print(f"  Win rate: {win_rate*100:.2f}%")


def batch_generate(
    depth: int,
    input_dir: Path,
    output_dir: Path,
    guess1_words: List[str] = None
) -> None:
    """
    Generate all strategies for a given depth.

    Args:
        depth: Clue count (8, 16, 32, 64, 243)
        input_dir: Directory containing tournament result files
        output_dir: Directory to write strategy files
        guess1_words: List of first guess words to process (default: top 10)
    """

    if guess1_words is None:
        # Default: top 10 from tournament (plus SITAR for 11 total)
        guess1_words = [
            "trice", "crone", "siren", "dealt", "risen",
            "poser", "rinse", "snore", "adult", "noise", "sitar"
        ]

    for guess1 in guess1_words:
        input_file = input_dir / f"2d_{depth}r_{guess1}_n3158.json"
        output_file = output_dir / f"2d_{depth}r_{guess1}.json"

        if not input_file.exists():
            print(f"⚠ Skipping {guess1}: {input_file.name} not found")
            continue

        try:
            generate_strategy_file(input_file, output_file, depth)
        except Exception as e:
            print(f"✗ Error generating {guess1}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate depth-based strategy files from tournament results"
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Input tournament JSON file"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output strategy JSON file"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: generate all strategies for a depth"
    )
    parser.add_argument(
        "--depth",
        type=int,
        help="Depth for batch mode (8, 16, 32, 64, 243)"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        help="Input directory for batch mode"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for batch mode"
    )

    args = parser.parse_args()

    if args.batch:
        if not all([args.depth, args.input_dir, args.output_dir]):
            parser.error("--batch requires --depth, --input-dir, and --output-dir")

        batch_generate(
            depth=args.depth,
            input_dir=args.input_dir,
            output_dir=args.output_dir
        )
    else:
        if not all([args.input, args.output]):
            parser.error("Single-file mode requires --input and --output")

        # Infer depth from input filename
        # e.g., "2d_8r_trice_n3158.json" → depth=8
        depth = int(args.input.stem.split("_")[1].replace("r", ""))

        generate_strategy_file(
            tournament_file=args.input,
            output_file=args.output,
            depth=depth
        )


if __name__ == "__main__":
    main()
