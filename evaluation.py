"""
Board evaluation functions for AI decision-making.
Evaluates positions using material count and piece positioning.
"""

from constants import (
    PIECE_VALUES, PIECE_POSITION_SCORES, CHECKMATE_SCORE, STALEMATE_SCORE, EMPTY_SQUARE
)


def scoreBoard(game_state):
    """
    Evaluate the current board position.
    
    Scoring method:
    - Positive score favors white
    - Negative score favors black
    - Checkmate: +1000 (white wins) or -1000 (black wins)
    - Stalemate: 0 (draw)
    
    Returns:
        Float: Score representing position evaluation
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE_SCORE  # Black wins
        else:
            return CHECKMATE_SCORE   # White wins
    
    elif game_state.stalemate:
        return STALEMATE_SCORE
    
    score = 0
    
    # Evaluate each square on the board
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            
            if piece != EMPTY_SQUARE:
                # Get material value (how much the piece is worth)
                piece_value = PIECE_VALUES[piece[1]]
                
                # Get positional bonus (where the piece is positioned)
                piece_position_score = 0
                if piece[1] != "K":  # King position score handled differently
                    piece_position_score = PIECE_POSITION_SCORES[piece][row][col]
                
                total_piece_value = piece_value + piece_position_score
                
                # Add or subtract based on piece color
                if piece[0] == "w":
                    score += total_piece_value
                else:
                    score -= total_piece_value
    
    return score


def evaluatePiece(piece, row, col):
    """
    Evaluate a single piece based on its material and position.
    
    Args:
        piece: Piece string (e.g., 'wQ', 'bp')
        row: Row position on board
        col: Column position on board
    
    Returns:
        Float: Combined material and positional value
    """
    if piece == EMPTY_SQUARE:
        return 0
    
    material_value = PIECE_VALUES.get(piece[1], 0)
    position_value = 0
    
    if piece[1] != "K":
        position_value = PIECE_POSITION_SCORES[piece][row][col]
    
    return material_value + position_value
