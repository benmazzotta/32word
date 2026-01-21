# Discord Bot Integration Guide

This guide shows how to integrate the 32word library into a Discord bot using discord.py. The Discord bot uses **minimal response mode** to keep messages concise while still providing essential gameplay information.

## Overview

Discord bots need to:
1. **Display clues** - Show emoji representation (🟩 🟨 ⬜)
2. **Show remaining count** - Display how many words remain
3. **Provide strategy recommendations** - Suggest next guess
4. **Handle game state** - Track multiple users' games simultaneously

## Minimal Response Mode

Use `mode='minimal'` when building responses to reduce payload size and simplify parsing:

```python
from word32 import build_game_response

response = build_game_response(
    guess=guess,
    clue=clue,
    remaining_targets=remaining,
    strategy_recommendation=strategy_info,
    mode='minimal'  # Only essential fields
)
```

Minimal mode includes:
- `success`, `guess`, `clue`, `remaining` (count + sample), `metadata`
- Excludes: `game_state`, `strategy` (even if `strategy_recommendation` is provided)

## Basic Discord Bot Setup

**Install dependencies:**
```bash
pip install discord.py 32word
```

**Basic bot structure:**
```python
import discord
from discord.ext import commands
from word32 import (
    get_available_first_guesses,
    select_first_guess,
    generate_clue,
    filter_targets,
    get_second_guess_recommendation,
    build_game_response,
    build_error_response,
    ErrorCode,
    is_valid_word,
    VALID_TARGETS
)
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store game state per user (in production, use a database)
user_games = {}
```

## Command: Start a Game

```python
@bot.command(name='start')
async def start_game(ctx, first_guess: str = 'ATONE'):
    """Start a new Wordle game.
    
    Usage: !start [first_guess]
    Example: !start RAISE
    """
    user_id = ctx.author.id
    
    # Validate first guess selection
    selected = select_first_guess(first_guess.upper())
    if not selected:
        await ctx.send(f"❌ Invalid first guess: `{first_guess}`. Use `!first-guesses` to see options.")
        return
    
    # Pick random target
    target = random.choice(VALID_TARGETS)
    
    # Generate clue
    clue = generate_clue(first_guess.upper(), target)
    
    # Filter remaining
    remaining = filter_targets(VALID_TARGETS, first_guess.upper(), clue)
    
    # Get strategy recommendation
    strategy_rec = get_second_guess_recommendation(first_guess.upper(), clue)
    
    # Build minimal response
    response = build_game_response(
        guess=first_guess.upper(),
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        mode='minimal'
    )
    
    # Store game state
    user_games[user_id] = {
        'target': target,
        'guesses': [first_guess.upper()],
        'clues': [clue],
        'first_guess': first_guess.upper()
    }
    
    # Format and send message
    message = format_game_response(response)
    await ctx.send(message)
```

## Command: Submit a Guess

```python
@bot.command(name='guess')
async def submit_guess(ctx, guess: str):
    """Submit a guess.
    
    Usage: !guess WORD
    Example: !guess CLOUD
    """
    user_id = ctx.author.id
    
    # Check for active game
    if user_id not in user_games:
        await ctx.send("❌ No active game. Use `!start` to begin.")
        return
    
    guess = guess.upper()
    
    # Validate guess
    if not is_valid_word(guess):
        await ctx.send(f"❌ `{guess}` is not a valid Wordle word.")
        return
    
    game = user_games[user_id]
    target = game['target']
    
    # Generate clue
    clue = generate_clue(guess, target)
    
    # Update game state
    game['guesses'].append(guess)
    game['clues'].append(clue)
    guess_number = len(game['guesses'])
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    # Filter remaining
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game['guesses'], game['clues']):
        remaining = filter_targets(remaining, g, c)
    
    # Get strategy recommendation (only for second guess)
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(
            game['first_guess'],
            game['clues'][0]
        )
    
    # Build minimal response
    response = build_game_response(
        guess=guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        mode='minimal'
    )
    
    # Format and send
    message = format_game_response(response)
    await ctx.send(message)
    
    # Handle solved game
    if is_solved:
        await ctx.send(f"🎉 **Solved in {guess_number} guesses!** The word was `{target}`.")
        del user_games[user_id]
    elif guess_number >= 3:
        await ctx.send(f"❌ Game over. The word was `{target}`.")
        del user_games[user_id]
```

## Formatting Game Responses

**Format clues as emoji:**
```python
def format_clue_emoji(clue):
    """Convert clue codes to emoji."""
    emoji_map = {
        'G': '🟩',  # Green
        'Y': '🟨',  # Yellow
        'X': '⬜',  # Black/Gray
        'B': '⬜'   # Black/Gray (alternative)
    }
    return ' '.join(emoji_map.get(code, '⬜') for code in clue)
```

**Format complete response:**
```python
def format_game_response(response):
    """Format GameResponse for Discord message."""
    lines = []
    
    # Clue emoji
    clue_emoji = format_clue_emoji(response['clue'])
    lines.append(f"**{response['guess']}** → {clue_emoji}")
    
    # Remaining count
    remaining = response['remaining']
    count = remaining['count']
    lines.append(f"**{count}** words remain")
    
    # Sample words (if small enough)
    if count <= 10:
        sample = ', '.join(remaining['sample'])
        lines.append(f"Possible: `{sample}`")
    elif count <= 50:
        sample = ', '.join(remaining['sample'][:5])
        lines.append(f"Sample: `{sample}...`")
    
    # Strategy recommendation
    if response.get('strategy') and response['strategy'].get('recommended_guess'):
        rec = response['strategy']['recommended_guess']
        lines.append(f"💡 **Suggested:** `{rec}`")
    
    return '\n'.join(lines)
```

**Example output:**
```
RAISE → 🟩 🟨 ⬜ ⬜ 🟩
42 words remain
Sample: `AGILE, ALIAS, AMISS, ARISE, AROSE...`
💡 Suggested: `CLOUD`
```

## Command: List Available First Guesses

```python
@bot.command(name='first-guesses')
async def list_first_guesses(ctx, limit: int = 10):
    """List available first guess options.
    
    Usage: !first-guesses [limit]
    Example: !first-guesses 5
    """
    options = get_available_first_guesses()
    
    lines = ["**Available First Guesses:**"]
    for opt in options[:limit]:
        lines.append(
            f"`{opt['first_guess']}` - Rank {opt['rank']}, "
            f"Expected remaining: {opt['expected_remaining']:.1f}"
        )
    
    if len(options) > limit:
        lines.append(f"\n*Showing {limit} of {len(options)} options. Use `!start WORD` to begin.*")
    
    await ctx.send('\n'.join(lines))
```

## Command: Show Game Status

```python
@bot.command(name='status')
async def show_status(ctx):
    """Show current game status."""
    user_id = ctx.author.id
    
    if user_id not in user_games:
        await ctx.send("❌ No active game. Use `!start` to begin.")
        return
    
    game = user_games[user_id]
    guesses = game['guesses']
    clues = game['clues']
    
    lines = [f"**Game Status** (Guess {len(guesses)}/3)"]
    
    for i, (guess, clue) in enumerate(zip(guesses, clues), 1):
        clue_emoji = format_clue_emoji(clue)
        lines.append(f"{i}. `{guess}` → {clue_emoji}")
    
    # Calculate remaining
    remaining = VALID_TARGETS.copy()
    for g, c in zip(guesses, clues):
        remaining = filter_targets(remaining, g, c)
    
    lines.append(f"\n**{len(remaining)}** words remain")
    
    await ctx.send('\n'.join(lines))
```

## Error Handling

```python
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: `{error.param.name}`")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.send(f"❌ Error: {str(error)}")
```

## Complete Example Bot

```python
import os
import discord
from discord.ext import commands
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
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

user_games = {}

def format_clue_emoji(clue):
    """Convert clue codes to emoji."""
    emoji_map = {'G': '🟩', 'Y': '🟨', 'X': '⬜', 'B': '⬜'}
    return ' '.join(emoji_map.get(code, '⬜') for code in clue)

def format_game_response(response):
    """Format GameResponse for Discord."""
    lines = []
    clue_emoji = format_clue_emoji(response['clue'])
    lines.append(f"**{response['guess']}** → {clue_emoji}")
    
    remaining = response['remaining']
    count = remaining['count']
    lines.append(f"**{count}** words remain")
    
    if count <= 10:
        sample = ', '.join(remaining['sample'])
        lines.append(f"Possible: `{sample}`")
    elif count <= 50:
        sample = ', '.join(remaining['sample'][:5])
        lines.append(f"Sample: `{sample}...`")
    
    if response.get('strategy') and response['strategy'].get('recommended_guess'):
        rec = response['strategy']['recommended_guess']
        lines.append(f"💡 **Suggested:** `{rec}`")
    
    return '\n'.join(lines)

@bot.command(name='start')
async def start_game(ctx, first_guess: str = 'ATONE'):
    """Start a new Wordle game."""
    user_id = ctx.author.id
    
    selected = select_first_guess(first_guess.upper())
    if not selected:
        await ctx.send(f"❌ Invalid first guess: `{first_guess}`. Use `!first-guesses` to see options.")
        return
    
    target = random.choice(VALID_TARGETS)
    clue = generate_clue(first_guess.upper(), target)
    remaining = filter_targets(VALID_TARGETS, first_guess.upper(), clue)
    strategy_rec = get_second_guess_recommendation(first_guess.upper(), clue)
    
    response = build_game_response(
        guess=first_guess.upper(),
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        mode='minimal'
    )
    
    user_games[user_id] = {
        'target': target,
        'guesses': [first_guess.upper()],
        'clues': [clue],
        'first_guess': first_guess.upper()
    }
    
    await ctx.send(format_game_response(response.to_dict()))

@bot.command(name='guess')
async def submit_guess(ctx, guess: str):
    """Submit a guess."""
    user_id = ctx.author.id
    
    if user_id not in user_games:
        await ctx.send("❌ No active game. Use `!start` to begin.")
        return
    
    guess = guess.upper()
    if not is_valid_word(guess):
        await ctx.send(f"❌ `{guess}` is not a valid Wordle word.")
        return
    
    game = user_games[user_id]
    target = game['target']
    clue = generate_clue(guess, target)
    game['guesses'].append(guess)
    game['clues'].append(clue)
    guess_number = len(game['guesses'])
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    remaining = VALID_TARGETS.copy()
    for g, c in zip(game['guesses'], game['clues']):
        remaining = filter_targets(remaining, g, c)
    
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(game['first_guess'], game['clues'][0])
    
    response = build_game_response(
        guess=guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0
        } if strategy_rec else None,
        mode='minimal'
    )
    
    await ctx.send(format_game_response(response.to_dict()))
    
    if is_solved:
        await ctx.send(f"🎉 **Solved in {guess_number} guesses!** The word was `{target}`.")
        del user_games[user_id]
    elif guess_number >= 3:
        await ctx.send(f"❌ Game over. The word was `{target}`.")
        del user_games[user_id]

@bot.command(name='first-guesses')
async def list_first_guesses(ctx, limit: int = 10):
    """List available first guess options."""
    options = get_available_first_guesses()
    lines = ["**Available First Guesses:**"]
    for opt in options[:limit]:
        lines.append(
            f"`{opt['first_guess']}` - Rank {opt['rank']}, "
            f"Expected: {opt['expected_remaining']:.1f}"
        )
    if len(options) > limit:
        lines.append(f"\n*Showing {limit} of {len(options)} options.*")
    await ctx.send('\n'.join(lines))

@bot.command(name='status')
async def show_status(ctx):
    """Show current game status."""
    user_id = ctx.author.id
    if user_id not in user_games:
        await ctx.send("❌ No active game. Use `!start` to begin.")
        return
    
    game = user_games[user_id]
    lines = [f"**Game Status** (Guess {len(game['guesses'])}/3)"]
    for i, (guess, clue) in enumerate(zip(game['guesses'], game['clues']), 1):
        clue_emoji = format_clue_emoji(clue)
        lines.append(f"{i}. `{guess}` → {clue_emoji}")
    await ctx.send('\n'.join(lines))

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Run bot
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
```

## Advanced Features

### Embed Messages

Use Discord embeds for richer formatting:

```python
def create_game_embed(response):
    """Create a Discord embed from GameResponse."""
    embed = discord.Embed(
        title=f"Guess: {response['guess']}",
        color=discord.Color.blue()
    )
    
    # Clue emoji
    clue_emoji = format_clue_emoji(response['clue'])
    embed.add_field(name="Clue", value=clue_emoji, inline=False)
    
    # Remaining count
    remaining = response['remaining']
    embed.add_field(name="Remaining Words", value=str(remaining['count']), inline=True)
    
    # Strategy recommendation
    if response.get('strategy') and response['strategy'].get('recommended_guess'):
        rec = response['strategy']['recommended_guess']
        embed.add_field(name="Suggested", value=f"`{rec}`", inline=True)
    
    return embed

# Usage
embed = create_game_embed(response.to_dict())
await ctx.send(embed=embed)
```

### Database Storage

For production, store game state in a database:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('games.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS games (
            user_id INTEGER PRIMARY KEY,
            target TEXT,
            guesses TEXT,
            clues TEXT,
            first_guess TEXT
        )
    ''')
    conn.close()

def save_game(user_id, game):
    conn = sqlite3.connect('games.db')
    conn.execute(
        'INSERT OR REPLACE INTO games VALUES (?, ?, ?, ?, ?)',
        (user_id, game['target'], ','.join(game['guesses']), 
         ','.join([''.join(c) for c in game['clues']]), game['first_guess'])
    )
    conn.commit()
    conn.close()
```

## Testing

Test your bot commands:

```python
# In a test script
import asyncio
from word32 import build_game_response

async def test_formatting():
    response = build_game_response(
        guess="RAISE",
        clue=('G', 'Y', 'X', 'X', 'G'),
        remaining_targets=['AGILE', 'ALIAS', 'AMISS'],
        strategy_recommendation={'recommended_guess': 'CLOUD'},
        mode='minimal'
    )
    print(format_game_response(response.to_dict()))

asyncio.run(test_formatting())
```

## Next Steps

- See [Response Schema Reference](./RESPONSE_SCHEMA_REFERENCE.md) for complete API documentation
- See [Web App Integration Guide](./INTEGRATION_WEB_APP.md) for full response mode examples
- See [CLI Usage Guide](./INTEGRATION_CLI.md) for command-line patterns
