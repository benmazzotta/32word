# Web App Integration Guide

This guide shows how to integrate the 32word library into a web application (React, Vue, or any frontend framework) with a Python backend (Flask, FastAPI, Django, etc.).

## Overview

The 32word library provides a standardized API for Wordle gameplay. Your web app will:

1. **Fetch available first guesses** - Let users choose from 32 optimal starting words
2. **Start a game** - Initialize with a selected first guess
3. **Submit guesses** - Process each guess and get standardized responses
4. **Display results** - Show clues, remaining words, and strategy recommendations

## API Flow

### 1. GET `/api/first-guesses` - Get Available First Guesses

**Backend (Python):**
```python
from word32 import get_available_first_guesses
from flask import jsonify  # or FastAPI, Django, etc.

@app.route('/api/first-guesses', methods=['GET'])
def get_first_guesses():
    """Return all 32 available first guess options."""
    options = get_available_first_guesses()
    return jsonify({
        'success': True,
        'options': options
    })
```

**Frontend (JavaScript/React):**
```javascript
async function fetchFirstGuesses() {
    const response = await fetch('/api/first-guesses');
    const data = await response.json();
    
    if (data.success) {
        return data.options; // Array of 32 first guess options
    }
    throw new Error('Failed to fetch first guesses');
}

// Usage in React component
function FirstGuessSelector() {
    const [options, setOptions] = useState([]);
    
    useEffect(() => {
        fetchFirstGuesses().then(setOptions);
    }, []);
    
    return (
        <select onChange={(e) => selectFirstGuess(e.target.value)}>
            {options.map(opt => (
                <option key={opt.first_guess} value={opt.first_guess}>
                    {opt.first_guess} (Rank {opt.rank}, Expected: {opt.expected_remaining.toFixed(1)})
                </option>
            ))}
        </select>
    );
}
```

### 2. POST `/api/game/start` - Start a New Game

**Backend (Python):**
```python
from word32 import select_first_guess, generate_clue, filter_targets, VALID_TARGETS
from word32 import build_game_response, get_second_guess_recommendation
import random

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game with selected first guess."""
    data = request.get_json()
    first_guess_choice = data.get('first_guess', 'ATONE').upper()
    
    # Validate first guess selection
    selected = select_first_guess(first_guess_choice)
    if not selected:
        return jsonify({
            'success': False,
            'error': 'INVALID_FIRST_GUESS',
            'message': f'First guess "{first_guess_choice}" not available'
        }), 400
    
    # Pick random target word
    target = random.choice(VALID_TARGETS)
    
    # Generate clue for first guess
    clue = generate_clue(first_guess_choice, target)
    
    # Filter remaining targets
    remaining = filter_targets(VALID_TARGETS, first_guess_choice, clue)
    
    # Get strategy recommendation
    strategy_rec = get_second_guess_recommendation(first_guess_choice, clue)
    
    # Build response
    response = build_game_response(
        guess=first_guess_choice,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0,
            'coverage': selected.get('coverage', 0.8125)
        } if strategy_rec else None,
        game_state={
            'guess_number': 1,
            'guesses_so_far': [first_guess_choice],
            'is_solved': clue == ('G', 'G', 'G', 'G', 'G')
        },
        strategy_version=first_guess_choice,
        mode='full'
    )
    
    # Store game state in session (simplified - use proper session management)
    session['target'] = target
    session['guesses'] = [first_guess_choice]
    session['clues'] = [clue]
    session['first_guess'] = first_guess_choice
    
    return jsonify(response.to_dict())
```

**Frontend (JavaScript/React):**
```javascript
async function startGame(firstGuess) {
    const response = await fetch('/api/game/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ first_guess: firstGuess })
    });
    
    const data = await response.json();
    
    if (data.success) {
        return data; // GameResponse object
    } else {
        throw new Error(data.message);
    }
}

// Usage
function GameComponent() {
    const [gameState, setGameState] = useState(null);
    
    const handleStart = async (firstGuess) => {
        try {
            const data = await startGame(firstGuess);
            setGameState(data);
        } catch (error) {
            console.error('Failed to start game:', error);
        }
    };
    
    return (
        <div>
            {gameState && (
                <div>
                    <ClueDisplay clue={gameState.clue} />
                    <RemainingWordsDisplay remaining={gameState.remaining} />
                    {gameState.strategy && (
                        <StrategyRecommendation rec={gameState.strategy} />
                    )}
                </div>
            )}
        </div>
    );
}
```

### 3. POST `/api/game/guess` - Submit a Guess

**Backend (Python):**
```python
from word32 import (
    generate_clue,
    filter_targets,
    get_second_guess_recommendation,
    build_game_response,
    build_error_response,
    ErrorCode,
    is_valid_word,
    VALID_TARGETS
)

@app.route('/api/game/guess', methods=['POST'])
def submit_guess():
    """Process a guess and return game response."""
    data = request.get_json()
    guess = data.get('guess', '').upper()
    
    # Get game state from session
    target = session.get('target')
    guesses = session.get('guesses', [])
    clues = session.get('clues', [])
    first_guess = session.get('first_guess', 'ATONE')
    
    if not target:
        return jsonify(build_error_response(
            'INCOMPLETE_GAME',
            'No active game found. Please start a new game.',
            ErrorCode.INCOMPLETE_GAME
        ).to_dict()), 400
    
    # Validate guess
    if not is_valid_word(guess):
        return jsonify(build_error_response(
            'INVALID_GUESS',
            f'"{guess}" is not a valid Wordle word.',
            ErrorCode.INVALID_GUESS
        ).to_dict()), 400
    
    # Generate clue
    clue = generate_clue(guess, target)
    
    # Update game state
    guesses.append(guess)
    clues.append(clue)
    guess_number = len(guesses)
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    # Filter remaining targets
    remaining = VALID_TARGETS.copy()
    for g, c in zip(guesses, clues):
        remaining = filter_targets(remaining, g, c)
    
    # Get strategy recommendation (only for second guess)
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(first_guess, clues[0])
    
    # Build response
    response = build_game_response(
        guess=guess,
        clue=clue,
        remaining_targets=remaining,
        strategy_recommendation={
            'recommended_guess': strategy_rec,
            'confidence': 0.95 if strategy_rec else 0.0,
            'coverage': 0.8125
        } if strategy_rec else None,
        game_state={
            'guess_number': guess_number,
            'guesses_so_far': guesses,
            'is_solved': is_solved,
            'solved_word': target if is_solved else None
        },
        strategy_version=first_guess,
        mode='full'
    )
    
    # Update session
    session['guesses'] = guesses
    session['clues'] = clues
    
    return jsonify(response.to_dict())
```

**Frontend (JavaScript/React):**
```javascript
async function submitGuess(guess) {
    const response = await fetch('/api/game/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ guess: guess })
    });
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.message);
    }
    
    return data; // GameResponse object
}

// Usage in React component
function GuessInput({ onGuessSubmitted }) {
    const [guess, setGuess] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await submitGuess(guess);
            onGuessSubmitted(response);
            setGuess('');
        } catch (error) {
            alert(error.message);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={guess}
                onChange={(e) => setGuess(e.target.value.toUpperCase())}
                maxLength={5}
                pattern="[A-Z]{5}"
            />
            <button type="submit">Submit</button>
        </form>
    );
}
```

## Displaying Clues

### Clue Emoji Mapping

The clue array uses codes: `'G'` (green), `'Y'` (yellow), `'X'` or `'B'` (black/gray).

**React Component:**
```javascript
function ClueDisplay({ clue }) {
    const emojiMap = {
        'G': '🟩',  // Green
        'Y': '🟨',  // Yellow
        'X': '⬜',  // Black/Gray
        'B': '⬜'   // Black/Gray (alternative)
    };
    
    return (
        <div className="clue-display">
            {clue.map((code, i) => (
                <span key={i} className={`clue-${code.toLowerCase()}`}>
                    {emojiMap[code]}
                </span>
            ))}
        </div>
    );
}
```

**CSS Styling:**
```css
.clue-display {
    display: flex;
    gap: 4px;
    font-size: 24px;
}

.clue-g {
    background-color: #6aaa64;
    color: white;
}

.clue-y {
    background-color: #c9b458;
    color: white;
}

.clue-x, .clue-b {
    background-color: #787c7e;
    color: white;
}
```

## Displaying Remaining Words

**React Component:**
```javascript
function RemainingWordsDisplay({ remaining }) {
    return (
        <div className="remaining-words">
            <h3>{remaining.count} words remain</h3>
            {remaining.count > 0 && (
                <div className="word-sample">
                    {remaining.sample.map((word, i) => (
                        <span key={i} className="word-tag">{word}</span>
                    ))}
                    {!remaining.all_words && (
                        <span className="more-indicator">...</span>
                    )}
                </div>
            )}
        </div>
    );
}
```

## Displaying Strategy Recommendations

**React Component:**
```javascript
function StrategyRecommendation({ rec }) {
    if (!rec || !rec.recommended_guess) {
        return null;
    }
    
    return (
        <div className="strategy-recommendation">
            <h4>Suggested next guess: <strong>{rec.recommended_guess}</strong></h4>
            {rec.confidence && (
                <div className="confidence">
                    Confidence: {(rec.confidence * 100).toFixed(0)}%
                </div>
            )}
        </div>
    );
}
```

## Edge Cases

### No Strategy Recommendation Available

```javascript
// In your component
{gameState.strategy && gameState.strategy.recommended_guess ? (
    <StrategyRecommendation rec={gameState.strategy} />
) : (
    <div className="no-strategy">
        No strategy recommendation available for this clue pattern.
        Choose from remaining words.
    </div>
)}
```

### Remaining = 0 (Invalid State)

```javascript
if (remaining.count === 0 && !gameState.is_solved) {
    // This shouldn't happen, but handle gracefully
    return <div className="error">Invalid game state: no remaining words</div>;
}
```

### Remaining = 1 (Solved Next Guess)

```javascript
if (remaining.count === 1 && !gameState.is_solved) {
    return (
        <div className="almost-solved">
            <strong>Only 1 word remains: {remaining.sample[0]}</strong>
        </div>
    );
}
```

## Complete Example: React + Flask

**Backend (`app.py`):**
```python
import os
import secrets
from flask import Flask, request, jsonify, session
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

app = Flask(__name__)
# Use environment variable for production, generate for development
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

@app.route('/api/first-guesses', methods=['GET'])
def get_first_guesses():
    options = get_available_first_guesses()
    return jsonify({'success': True, 'options': options})

@app.route('/api/game/start', methods=['POST'])
def start_game():
    data = request.get_json()
    first_guess = data.get('first_guess', 'ATONE').upper()
    
    selected = select_first_guess(first_guess)
    if not selected:
        return jsonify(build_error_response(
            'INVALID_FIRST_GUESS',
            f'First guess "{first_guess}" not available',
            ErrorCode.INVALID_GUESS
        ).to_dict()), 400
    
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
            'confidence': 0.95 if strategy_rec else 0.0,
            'coverage': selected.get('coverage', 0.8125)
        } if strategy_rec else None,
        game_state={
            'guess_number': 1,
            'guesses_so_far': [first_guess],
            'is_solved': clue == ('G', 'G', 'G', 'G', 'G')
        },
        strategy_version=first_guess
    )
    
    session['target'] = target
    session['guesses'] = [first_guess]
    session['clues'] = [clue]
    session['first_guess'] = first_guess
    
    return jsonify(response.to_dict())

@app.route('/api/game/guess', methods=['POST'])
def submit_guess():
    data = request.get_json()
    guess = data.get('guess', '').upper()
    
    target = session.get('target')
    if not target:
        return jsonify(build_error_response(
            'INCOMPLETE_GAME',
            'No active game found',
            ErrorCode.INCOMPLETE_GAME
        ).to_dict()), 400
    
    if not is_valid_word(guess):
        return jsonify(build_error_response(
            'INVALID_GUESS',
            f'"{guess}" is not a valid Wordle word',
            ErrorCode.INVALID_GUESS
        ).to_dict()), 400
    
    clue = generate_clue(guess, target)
    guesses = session.get('guesses', []) + [guess]
    clues = session.get('clues', []) + [clue]
    guess_number = len(guesses)
    is_solved = clue == ('G', 'G', 'G', 'G', 'G')
    
    remaining = VALID_TARGETS.copy()
    for g, c in zip(guesses, clues):
        remaining = filter_targets(remaining, g, c)
    
    first_guess = session.get('first_guess', 'ATONE')
    strategy_rec = None
    if guess_number == 2:
        strategy_rec = get_second_guess_recommendation(first_guess, clues[0])
    
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
            'guesses_so_far': guesses,
            'is_solved': is_solved,
            'solved_word': target if is_solved else None
        },
        strategy_version=first_guess
    )
    
    session['guesses'] = guesses
    session['clues'] = clues
    
    return jsonify(response.to_dict())
```

**Frontend (`App.js`):**
```javascript
import React, { useState, useEffect } from 'react';

function App() {
    const [firstGuesses, setFirstGuesses] = useState([]);
    const [selectedFirstGuess, setSelectedFirstGuess] = useState(null);
    const [gameState, setGameState] = useState(null);
    const [currentGuess, setCurrentGuess] = useState('');
    
    useEffect(() => {
        fetch('/api/first-guesses')
            .then(res => res.json())
            .then(data => setFirstGuesses(data.options));
    }, []);
    
    const startGame = async (firstGuess) => {
        const response = await fetch('/api/game/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ first_guess: firstGuess })
        });
        const data = await response.json();
        setGameState(data);
        setSelectedFirstGuess(firstGuess);
    };
    
    const submitGuess = async (guess) => {
        const response = await fetch('/api/game/guess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ guess: guess })
        });
        const data = await response.json();
        setGameState(data);
        setCurrentGuess('');
    };
    
    return (
        <div className="app">
            {!selectedFirstGuess ? (
                <div>
                    <h1>Choose Your First Guess</h1>
                    <select onChange={(e) => startGame(e.target.value)}>
                        <option>Select...</option>
                        {firstGuesses.map(opt => (
                            <option key={opt.first_guess} value={opt.first_guess}>
                                {opt.first_guess} (Rank {opt.rank})
                            </option>
                        ))}
                    </select>
                </div>
            ) : (
                <div>
                    <h1>Game in Progress</h1>
                    {gameState && (
                        <>
                            <ClueDisplay clue={gameState.clue} />
                            <RemainingWordsDisplay remaining={gameState.remaining} />
                            {gameState.strategy && (
                                <StrategyRecommendation rec={gameState.strategy} />
                            )}
                            {!gameState.game_state.is_solved && (
                                <GuessInput onSubmit={submitGuess} />
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
```

## Testing Your Integration

Test your endpoints with curl:

```bash
# Get first guesses
curl http://localhost:5000/api/first-guesses

# Start a game
curl -X POST http://localhost:5000/api/game/start \
  -H "Content-Type: application/json" \
  -d '{"first_guess": "RAISE"}'

# Submit a guess (requires session cookie)
curl -X POST http://localhost:5000/api/game/guess \
  -H "Content-Type: application/json" \
  -d '{"guess": "CLOUD"}' \
  --cookie "session=..."
```

## Next Steps

- See [Response Schema Reference](./RESPONSE_SCHEMA_REFERENCE.md) for complete API documentation
- See [Discord Bot Integration Guide](./INTEGRATION_DISCORD_BOT.md) for minimal response mode examples
- See [CLI Usage Guide](./INTEGRATION_CLI.md) for command-line integration patterns
