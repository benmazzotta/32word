# CLI Usage Guide

This guide shows how to build a command-line interface (CLI) for the 32word library. You can create a standalone CLI tool or integrate CLI functionality into your application.

## Overview

A CLI for 32word should support:
1. **Starting games** - Select first guess, initialize game state
2. **Submitting guesses** - Process guesses and display results
3. **Showing status** - Display current game state
4. **Listing options** - Show available first guesses and strategies

## Basic CLI Structure

### Using argparse

```python
#!/usr/bin/env python3
"""32word CLI - Command-line interface for Wordle solving."""

import argparse
import random
import sys
from word32 import (
    get_available_first_guesses,
    select_first_guess,
    generate_clue,
    filter_targets,
    get_second_guess_recommendation,
    build_game_response,
    is_valid_word,
    VALID_TARGETS
)

# Game state storage (in production, use a file or database)
game_state = {
    'target': None,
    'guesses': [],
    'clues': [],
    'first_guess': None
}

def format_clue_colored(clue):
    """Format clue with terminal colors."""
    colors = {
        'G': '\033[92m',  # Green
        'Y': '\033[93m',  # Yellow
        'X': '\033[90m',  # Black/Gray
        'B': '\033[90m'   # Black/Gray (alternative)
    }
    reset = '\033[0m'
    symbols = {'G': '█', 'Y': '█', 'X': '░', 'B': '░'}
    
    result = []
    for code in clue:
        color = colors.get(code, '')
        symbol = symbols.get(code, '░')
        result.append(f"{color}{symbol}{reset}")
    return ' '.join(result)

def print_game_response(response):
    """Print formatted game response."""
    print(f"\nGuess: {response['guess']}")
    print(f"Clue:  {format_clue_colored(response['clue'])}")
    
    remaining = response['remaining']
    print(f"\n{remaining['count']} words remain")
    
    if remaining['count'] <= 20:
        sample = ', '.join(remaining['sample'])
        print(f"Possible words: {sample}")
    elif remaining['count'] <= 100:
        sample = ', '.join(remaining['sample'][:10])
        print(f"Sample: {sample}...")
    
    if response.get('strategy') and response['strategy'].get('recommended_guess'):
        rec = response['strategy']['recommended_guess']
        print(f"\n💡 Suggested next guess: {rec}")

def cmd_start(args):
    """Start a new game."""
    first_guess = args.first_guess.upper() if args.first_guess else 'ATONE'
    
    # Validate first guess
    selected = select_first_guess(first_guess)
    if not selected:
        print(f"❌ Invalid first guess: {first_guess}")
        print("Use '32word list-guesses' to see available options.")
        return 1
    
    # Pick random target
    if args.seed:
        random.seed(args.seed)
    target = random.choice(VALID_TARGETS)
    
    # Generate clue
    clue = generate_clue(first_guess, target)
    
    # Filter remaining
    remaining = filter_targets(VALID_TARGETS, first_guess, clue)
    
    # Get strategy recommendation
    strategy_rec = get_second_guess_recommendation(first_guess, clue)
    
    # Build response
    response = build_game_response(
        guess=first_guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        game_state={
            'guess_number': 1,
            'guesses_so_far': [first_guess],
            'is_solved': clue == ('G', 'G', 'G', 'G', 'G')
        },
        strategy_version=first_guess,
        mode='full'
    )
    
    # Store game state
    game_state['target'] = target
    game_state['guesses'] = [first_guess]
    game_state['clues'] = [clue]
    game_state['first_guess'] = first_guess
    
    print_game_response(response.to_dict())
    
    if response['game_state']['is_solved']:
        print(f"\n🎉 Solved in 1 guess! The word was {target}.")
        game_state['target'] = None
    
    return 0

def cmd_guess(args):
    """Submit a guess."""
    guess = args.word.upper()
    
    # Check for active game
    if not game_state['target']:
        print("❌ No active game. Use '32word start' to begin.")
        return 1
    
    # Validate guess
    if not is_valid_word(guess):
        print(f"❌ '{guess}' is not a valid Wordle word.")
        return 1
    
    target = game_state['target']
    clue = generate_clue(guess, target)
    
    # Update game state
    game_state['guesses'].append(guess)
    game_state['clues'].append(clue)
    guess_number = len(game_state['guesses'])
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    # Filter remaining
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game_state['guesses'], game_state['clues']):
        remaining = filter_targets(remaining, g, c)
    
    # Get strategy recommendation (only for second guess)
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(
            game_state['first_guess'],
            game_state['clues'][0]
        )
    
    # Build response
    response = build_game_response(
        guess=guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        game_state={
            'guess_number': guess_number,
            'guesses_so_far': game_state['guesses'],
            'is_solved': is_solved,
            'solved_word': target if is_solved else None
        },
        strategy_version=game_state['first_guess'],
        mode='full'
    )
    
    print_game_response(response.to_dict())
    
    if is_solved:
        print(f"\n🎉 Solved in {guess_number} guesses! The word was {target}.")
        game_state['target'] = None
    elif guess_number >= 3:
        print(f"\n❌ Game over. The word was {target}.")
        game_state['target'] = None
    
    return 0

def cmd_status(args):
    """Show current game status."""
    if not game_state['target']:
        print("No active game. Use '32word start' to begin.")
        return 0
    
    print(f"\nGame Status (Guess {len(game_state['guesses'])}/3)")
    print("=" * 50)
    
    for i, (guess, clue) in enumerate(zip(game_state['guesses'], game_state['clues']), 1):
        clue_str = format_clue_colored(clue)
        print(f"{i}. {guess:5} → {clue_str}")
    
    # Calculate remaining
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game_state['guesses'], game_state['clues']):
        remaining = filter_targets(remaining, g, c)
    
    print(f"\n{len(remaining)} words remain")
    if len(remaining) <= 20:
        print(f"Possible: {', '.join(remaining)}")
    
    return 0

def cmd_list_guesses(args):
    """List available first guess options."""
    options = get_available_first_guesses()
    limit = args.limit if args.limit else len(options)
    
    print(f"\nAvailable First Guesses (showing {min(limit, len(options))} of {len(options)}):")
    print("=" * 70)
    print(f"{'Word':<8} {'Rank':<6} {'Expected':<12} {'Max':<8} {'Variance':<10}")
    print("-" * 70)
    
    for opt in options[:limit]:
        print(f"{opt['first_guess']:<8} {opt['rank']:<6} "
              f"{opt['expected_remaining']:<12.1f} "
              f"{opt['metrics']['max_remaining']:<8} "
              f"{opt['metrics'].get('variance', 0):<10.1f}")
    
    return 0

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='32word CLI - Solve Wordle in three guesses',
        prog='32word'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start a new game')
    start_parser.add_argument(
        '--first-guess', '-f',
        type=str,
        help='First guess word (default: ATONE)'
    )
    start_parser.add_argument(
        '--seed', '-s',
        type=int,
        help='Random seed for reproducible games'
    )
    
    # Guess command
    guess_parser = subparsers.add_parser('guess', help='Submit a guess')
    guess_parser.add_argument('word', type=str, help='Word to guess')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show game status')
    
    # List guesses command
    list_parser = subparsers.add_parser('list-guesses', help='List available first guesses')
    list_parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of results (default: all)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    handlers = {
        'start': cmd_start,
        'guess': cmd_guess,
        'status': cmd_status,
        'list-guesses': cmd_list_guesses
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

## Using click (Alternative)

For a more feature-rich CLI, use the `click` library:

```python
#!/usr/bin/env python3
"""32word CLI using click."""

import click
import random
from word32 import (
    get_available_first_guesses,
    select_first_guess,
    generate_clue,
    filter_targets,
    get_second_guess_recommendation,
    build_game_response,
    is_valid_word,
    VALID_TARGETS
)

game_state = {
    'target': None,
    'guesses': [],
    'clues': [],
    'first_guess': None
}

@click.group()
def cli():
    """32word CLI - Solve Wordle in three guesses."""
    pass

@cli.command()
@click.option('--first-guess', '-f', default='ATONE', help='First guess word')
@click.option('--seed', '-s', type=int, help='Random seed')
def start(first_guess, seed):
    """Start a new game."""
    first_guess = first_guess.upper()
    selected = select_first_guess(first_guess)
    
    if not selected:
        click.echo(f"❌ Invalid first guess: {first_guess}", err=True)
        click.echo("Use '32word list-guesses' to see options.")
        return
    
    if seed:
        random.seed(seed)
    
    target = random.choice(VALID_TARGETS)
    clue = generate_clue(first_guess, target)
    remaining = filter_targets(VALID_TARGETS, first_guess, clue)
    strategy_rec = get_second_guess_recommendation(first_guess, clue)
    
    response = build_game_response(
        guess=first_guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        game_state={
            'guess_number': 1,
            'guesses_so_far': [first_guess],
            'is_solved': clue == ('G', 'G', 'G', 'G', 'G')
        },
        strategy_version=first_guess
    )
    
    game_state['target'] = target
    game_state['guesses'] = [first_guess]
    game_state['clues'] = [clue]
    game_state['first_guess'] = first_guess
    
    print_response(response.to_dict())
    
    if response['game_state']['is_solved']:
        click.echo(f"\n🎉 Solved in 1 guess! The word was {target}.")
        game_state['target'] = None

@cli.command()
@click.argument('word')
def guess(word):
    """Submit a guess."""
    guess = word.upper()
    
    if not game_state['target']:
        click.echo("❌ No active game. Use '32word start' to begin.", err=True)
        return
    
    if not is_valid_word(guess):
        click.echo(f"❌ '{guess}' is not a valid Wordle word.", err=True)
        return
    
    target = game_state['target']
    clue = generate_clue(guess, target)
    game_state['guesses'].append(guess)
    game_state['clues'].append(clue)
    guess_number = len(game_state['guesses'])
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game_state['guesses'], game_state['clues']):
        remaining = filter_targets(remaining, g, c)
    
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(
            game_state['first_guess'],
            game_state['clues'][0]
        )
    
    response = build_game_response(
        guess=guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        game_state={
            'guess_number': guess_number,
            'guesses_so_far': game_state['guesses'],
            'is_solved': is_solved,
            'solved_word': target if is_solved else None
        },
        strategy_version=game_state['first_guess']
    )
    
    print_response(response.to_dict())
    
    if is_solved:
        click.echo(f"\n🎉 Solved in {guess_number} guesses! The word was {target}.")
        game_state['target'] = None
    elif guess_number >= 3:
        click.echo(f"\n❌ Game over. The word was {target}.")
        game_state['target'] = None

@cli.command()
def status():
    """Show current game status."""
    if not game_state['target']:
        click.echo("No active game. Use '32word start' to begin.")
        return
    
    click.echo(f"\nGame Status (Guess {len(game_state['guesses'])}/3)")
    click.echo("=" * 50)
    
    for i, (g, c) in enumerate(zip(game_state['guesses'], game_state['clues']), 1):
        click.echo(f"{i}. {g:5} → {format_clue(c)}")
    
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game_state['guesses'], game_state['clues']):
        remaining = filter_targets(remaining, g, c)
    
    click.echo(f"\n{len(remaining)} words remain")
    if len(remaining) <= 20:
        click.echo(f"Possible: {', '.join(remaining)}")

@cli.command()
@click.option('--limit', '-l', type=int, help='Limit results')
def list_guesses(limit):
    """List available first guess options."""
    options = get_available_first_guesses()
    limit = limit or len(options)
    
    click.echo(f"\nAvailable First Guesses:")
    click.echo("=" * 70)
    
    for opt in options[:limit]:
        click.echo(
            f"{opt['first_guess']:<8} Rank {opt['rank']:<3} "
            f"Expected: {opt['expected_remaining']:>6.1f}"
        )

def format_clue(clue):
    """Format clue with terminal colors."""
    colors = {
        'G': '\033[92m',  # Green
        'Y': '\033[93m',  # Yellow
        'X': '\033[90m',  # Black/Gray
        'B': '\033[90m'   # Black/Gray (alternative)
    }
    reset = '\033[0m'
    symbols = {'G': '█', 'Y': '█', 'X': '░', 'B': '░'}
    
    result = []
    for code in clue:
        color = colors.get(code, '')
        symbol = symbols.get(code, '░')
        result.append(f"{color}{symbol}{reset}")
    return ' '.join(result)

def print_response(response):
    """Print formatted game response."""
    print(f"\nGuess: {response['guess']}")
    print(f"Clue:  {format_clue(response['clue'])}")
    
    remaining = response['remaining']
    print(f"\n{remaining['count']} words remain")
    
    if remaining['count'] <= 20:
        sample = ', '.join(remaining['sample'])
        print(f"Possible words: {sample}")
    elif remaining['count'] <= 100:
        sample = ', '.join(remaining['sample'][:10])
        print(f"Sample: {sample}...")
    
    if response.get('strategy') and response['strategy'].get('recommended_guess'):
        rec = response['strategy']['recommended_guess']
        print(f"\n💡 Suggested next guess: {rec}")

if __name__ == '__main__':
    cli()
```

## Making It Executable

**Create setup.py entry point:**
```python
# In setup.py or pyproject.toml
[project.scripts]
word32 = "word32.cli:main"
```

**Or create a standalone script:**
```bash
#!/usr/bin/env python3
# Save as word32-cli or 32word
chmod +x word32-cli
```

## Usage Examples

**Start a game:**
```bash
$ 32word start
$ 32word start --first-guess RAISE
$ 32word start --first-guess STALE --seed 42
```

**Submit guesses:**
```bash
$ 32word guess CLOUD
$ 32word guess AGILE
```

**Check status:**
```bash
$ 32word status
```

**List available first guesses:**
```bash
$ 32word list-guesses
$ 32word list-guesses --limit 10
```

## Terminal Output Examples

**Starting a game:**
```
$ 32word start --first-guess RAISE

Guess: RAISE
Clue:  █ ░ ░ ░ █

42 words remain
Sample: AGILE, ALIAS, AMISS, ARISE, AROSE...

💡 Suggested next guess: CLOUD
```

**Submitting a guess:**
```
$ 32word guess CLOUD

Guess: CLOUD
Clue:  ░ █ ░ ░ ░

8 words remain
Possible words: AGILE, ALIAS, AMISS, ARISE, AROSE, ASIDE, ASSET, AWAIT

💡 Suggested next guess: AGILE
```

**Game status:**
```
$ 32word status

Game Status (Guess 2/3)
==================================================
1. RAISE → █ ░ ░ ░ █
2. CLOUD → ░ █ ░ ░ ░

8 words remain
Possible: AGILE, ALIAS, AMISS, ARISE, AROSE, ASIDE, ASSET, AWAIT
```

## Interactive Mode

Create an interactive game loop:

```python
def interactive_mode():
    """Interactive game mode."""
    print("🎮 32word Interactive Mode")
    print("Type 'start' to begin, 'guess WORD' to guess, 'status' for status, 'quit' to exit\n")
    
    while True:
        try:
            cmd = input("32word> ").strip().split()
            if not cmd:
                continue
            
            if cmd[0] == 'quit':
                break
            elif cmd[0] == 'start':
                first_guess = cmd[1] if len(cmd) > 1 else 'ATONE'
                cmd_start(type('args', (), {'first_guess': first_guess, 'seed': None})())
            elif cmd[0] == 'guess' and len(cmd) > 1:
                cmd_guess(type('args', (), {'word': cmd[1]})())
            elif cmd[0] == 'status':
                cmd_status(type('args', (), {})())
            elif cmd[0] == 'list-guesses':
                limit = int(cmd[1]) if len(cmd) > 1 else None
                cmd_list_guesses(type('args', (), {'limit': limit})())
            else:
                print("Unknown command. Try: start, guess WORD, status, list-guesses, quit")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_mode()
    else:
        main()
```

## Persisting Game State

Save game state to a file:

```python
import json
import os

STATE_FILE = os.path.expanduser('~/.32word_state.json')

def load_state():
    """Load game state from file."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'target': None, 'guesses': [], 'clues': [], 'first_guess': None}

def save_state(state):
    """Save game state to file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def clear_state():
    """Clear saved game state."""
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
```

## Testing

Test your CLI:

```bash
# Test start command
python -m word32.cli start --first-guess RAISE

# Test guess command
python -m word32.cli guess CLOUD

# Test status
python -m word32.cli status

# Test list
python -m word32.cli list-guesses --limit 5
```

## Next Steps

- See [Response Schema Reference](./RESPONSE_SCHEMA_REFERENCE.md) for complete API documentation
- See [Web App Integration Guide](./INTEGRATION_WEB_APP.md) for API endpoint patterns
- See [Discord Bot Integration Guide](./INTEGRATION_DISCORD_BOT.md) for minimal response mode
