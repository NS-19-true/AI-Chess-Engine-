# Chess Engine with AI

A Python-based chess game with an AI opponent powered by Pygame. This project implements a full chess engine with move validation, AI decision-making, and a graphical user interface.

## Features

- **Full Chess Engine**: Complete chess rules implementation including castling, en passant, and pawn promotion
- **AI Opponent**: Intelligent AI opponent with piece positioning and strategy evaluation
- **Graphical Interface**: Interactive board display using Pygame
- **Move Logging**: Keeps track of all moves made during the game
- **Check/Checkmate Detection**: Proper detection of check, checkmate, and stalemate conditions

## Project Structure

```
├── ChessMain.py      - Main driver file, handles UI and user input
├── ChessEngine.py    - Core chess engine with game state and move validation
├── ChessAI.py        - AI logic for opponent moves
├── images/           - Chess piece images
└── requirements.txt  - Python dependencies
```

## Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux

## Installation & Setup

Follow these steps to run the chess engine on your local computer:

### Step 1: Clone or Download the Project

Download the project files to your local machine and navigate to the project directory:

```bash
cd path/to/chess-engine/chess
```

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment is recommended to keep dependencies isolated:

**On Windows:**
```bash
python -m venv chess_env
chess_env\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv chess_env
source chess_env/bin/activate
```

### Step 3: Install Dependencies

Install the required packages using pip:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Game

Start the chess game by running:

```bash
python ChessMain.py
```

## How to Play

1. **Starting the Game**: Launch the application using the command above
2. **Making Moves**: 
   - Click on a piece to select it (valid moves will be highlighted)
   - Click on a destination square to move the piece
3. **Undo Moves**: Press 'z' to undo the last move
4. **Reset Game**: Press 'r' to start a new game
5. **AI Opponent**: The AI will automatically make its move after your move

## Game Controls

| Key | Action |
|-----|--------|
| Left Click | Select/Move pieces |
| Z | Undo last move |
| R | Reset/New game |

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pygame'"
- **Solution**: Make sure you've activated your virtual environment and run `pip install -r requirements.txt`

### Issue: Images not loading
- **Solution**: Ensure the `images/` folder is in the same directory as the Python files and contains all chess piece PNG images

### Issue: Game runs slowly
- **Solution**: Close other applications and try again. The game is optimized for 15 FPS display rate.

## Technical Details

### ChessMain.py
- Handles the GUI using Pygame
- Manages user input and board display
- Implements move animation and game flow control
- Uses multiprocessing to run AI calculations in a separate process for responsive UI

### ChessEngine.py
- Implements the core chess logic
- Validates all legal moves according to chess rules
- Tracks game state (pieces, move history, castling rights)
- Detects check, checkmate, and stalemate conditions

### ChessAI.py
- Implements the AI opponent's decision-making
- Uses piece positioning tables (mobility scores) for evaluation
- Evaluates board positions and selects optimal moves

## Algorithms & Problem-Solving Methods

### 1. **Negamax with Alpha-Beta Pruning** (ChessAI.py)
The AI uses the **Negamax algorithm** with **Alpha-Beta pruning** to find the best move:
- **Negamax**: A variant of the minimax algorithm that simplifies code by assuming both players use the same evaluation function, just with opposite signs.
- **Alpha-Beta Pruning**: An optimization technique that eliminates branches from the game tree that don't affect the final decision, significantly reducing computation time.
- **Depth Control**: The algorithm searches up to a depth of 3 moves ahead, balancing move quality with computational efficiency.
- **Time Complexity**: O(b^d) where b is the branching factor and d is the search depth, reduced to approximately O(b^(d/2)) with alpha-beta pruning.

### 2. **Board Evaluation Function** (ChessAI.py)
A sophisticated heuristic evaluation system that scores board positions:
- **Material Evaluation**: Each piece has a numerical value (Queen=9, Rook=5, Bishop/Knight=3, Pawn=1).
- **Position Tables**: Piece-specific scoring matrices (knight_scores, bishop_scores, rook_scores, queen_scores, pawn_scores) that evaluate piece placement quality.
- **Endgame Detection**: Special scoring for checkmate (+1000) and stalemate (0) states to prioritize winning/drawing positions.
- **Turn Multiplier**: Uses positive/negative scoring to favor white/black moves respectively.

### 3. **Pin and Check Detection** (ChessEngine.py)
An advanced algorithm to identify attacks and pinned pieces:
- **Ray Casting**: Shoots rays in 8 directions (horizontal, vertical, diagonal) from the king's position to detect threats.
- **Pin Detection**: Identifies pieces that are pinned (cannot move without exposing the king to check).
- **Check Detection**: Identifies all pieces attacking the king, including special cases for:
  - Pawns (only attack diagonally, different directions for each side)
  - Knights (unique L-shaped attack pattern)
  - Rooks, Bishops, Queens (sliding pieces with directional movement)
  - Kings (1-square attacks)
- **Complex Conditional Logic**: Uses a 5-point conditional to match piece types with attack directions.

### 4. **Move Validation** (ChessEngine.py)
Ensures all moves comply with chess rules:
- **Piece-Specific Movement**: Each piece type has dedicated methods:
  - `getPawnMoves()`: Handles pawn movement, captures, en passant, and promotion
  - `getRookMoves()`: Linear horizontal and vertical movement
  - `getBishopMoves()`: Diagonal movement
  - `getKnightMoves()`: L-shaped movement with no blocking
  - `getQueenMoves()`: Combination of rook and bishop movement
  - `getKingMoves()`: Single-square movement in any direction, with castling
- **Pin Awareness**: Move validation considers pinned pieces and restricts their movement accordingly.
- **Check Response**: Ensures moves either block checks, capture attacking pieces, or move the king to safety.

### 5. **State Management & Undo** (ChessEngine.py)
Efficient game state tracking:
- **Move Log**: Maintains a history of all moves for undo functionality.
- **Castle Rights Tracking**: Tracks whether castling is still legal based on king/rook movements.
- **En Passant Tracking**: Records positions where en passant captures are possible.
- **Reversible Moves**: The `undoMove()` function properly reverses all move effects including special moves (castling, en passant, pawn promotion).

### 6. **Game State Detection** (ChessEngine.py)
Identifies terminal game states:
- **Checkmate Detection**: King is in check AND no legal moves available = opponent wins.
- **Stalemate Detection**: Player is not in check BUT no legal moves available = draw.
- **Check Detection**: Uses the pin/check detection algorithm to determine if the king is under attack.

### 7. **Move Ordering** (ChessAI.py)
Optimizes alpha-beta pruning efficiency:
- **Random Shuffle**: Valid moves are shuffled to reduce best-case scenario bias and improve average pruning efficiency.
- **Future Optimization**: Code includes TODO comment for move ordering improvements (prioritizing captures and checks over quiet moves).

### 8. **Process Management** (ChessMain.py)
Ensures responsive user interface:
- **Multiprocessing**: AI calculations run in a separate process using Python's `multiprocessing` module.
- **Queue Communication**: Results are passed back to the main thread via a queue for thread-safe communication.
- **Non-Blocking UI**: Player can interact with the board while AI is thinking, preventing UI freezes.

## Dependencies

- **pygame** (2.5.2): Used for rendering the game board, pieces, and handling user input

## Notes

- The project uses only the Python standard library (`random`, `sys`, `multiprocessing`) in addition to Pygame
- The AI opponent runs in a separate process for better performance
- The game implements standard chess rules with full move validation

## Future Enhancements

Potential improvements for future versions:
- Difficulty level selection for AI
- Move time limits/depth control
- Game statistics tracking
- Online multiplayer support

---

**Enjoy your chess games!** ♟️
