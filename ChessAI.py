"""
AI opponent using Negamax with Alpha-Beta pruning.
"""

import random
from constants import CHECKMATE_SCORE, STALEMATE_SCORE, AI_DEPTH
from evaluation import scoreBoard


def findBestMove(game_state, valid_moves, return_queue):
    """
    Find the best move using Negamax with alpha-beta pruning.
    
    Args:
        game_state: Current GameState
        valid_moves: List of valid moves
        return_queue: Queue to return the best move
    """
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(
        game_state, valid_moves, AI_DEPTH,
        -CHECKMATE_SCORE, CHECKMATE_SCORE,
        1 if game_state.white_to_move else -1
    )
    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    """
    Negamax algorithm with alpha-beta pruning.
    
    Args:
        game_state: Current GameState
        valid_moves: List of valid moves for current position
        depth: Current search depth
        alpha: Alpha cutoff value
        beta: Beta cutoff value
        turn_multiplier: 1 for white, -1 for black
        
    Returns:
        Float: Score of the position
    """
    global next_move
    
    if depth == 0:
        return turn_multiplier * scoreBoard(game_state)
    
    max_score = -CHECKMATE_SCORE
    
    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getValidMoves()
        
        # Recursive call with negated alpha-beta and opposite turn multiplier
        score = -findMoveNegaMaxAlphaBeta(
            game_state, next_moves, depth - 1,
            -beta, -alpha, -turn_multiplier
        )
        
        if score > max_score:
            max_score = score
            if depth == AI_DEPTH:
                next_move = move
        
        game_state.undoMove()
        
        # Alpha-beta pruning
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break  # Beta cutoff
    
    return max_score


def findRandomMove(valid_moves):
    """
    Pick a random valid move (fallback).
    
    Args:
        valid_moves: List of valid moves
        
    Returns:
        Move: A randomly selected move
    """
    return random.choice(valid_moves)
