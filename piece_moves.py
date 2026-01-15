"""
Piece movement logic for all chess pieces.
Each piece has specific movement rules that respect board boundaries and piece pinning.
"""

from move import Move
from constants import EMPTY_SQUARE


def getPawnMoves(game_state, row, col, moves):
    """
    Get all valid pawn moves for the pawn at (row, col).
    Handles: normal advances (1 or 2 squares), captures, en passant, and promotion.
    """
    piece_pinned = False
    pin_direction = ()
    
    # Check if this pawn is pinned
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])
            game_state.pins.remove(game_state.pins[i])
            break
    
    if game_state.white_to_move:
        move_amount = -1
        start_row = 6
        enemy_color = "b"
        king_row, king_col = game_state.white_king_location
    else:
        move_amount = 1
        start_row = 1
        enemy_color = "w"
        king_row, king_col = game_state.black_king_location
    
    # Single square advance
    if game_state.board[row + move_amount][col] == EMPTY_SQUARE:
        if not piece_pinned or pin_direction == (move_amount, 0):
            moves.append(Move((row, col), (row + move_amount, col), game_state.board))
            # Two square advance from starting position
            if row == start_row and game_state.board[row + 2 * move_amount][col] == EMPTY_SQUARE:
                moves.append(Move((row, col), (row + 2 * move_amount, col), game_state.board))
    
    # Capture to the left
    if col - 1 >= 0:
        if not piece_pinned or pin_direction == (move_amount, -1):
            if game_state.board[row + move_amount][col - 1][0] == enemy_color:
                moves.append(Move((row, col), (row + move_amount, col - 1), game_state.board))
            # En passant capture to the left
            if (row + move_amount, col - 1) == game_state.enpassant_possible:
                _addEnPassantIfValid(game_state, row, col, move_amount, -1, king_row, king_col, moves, enemy_color)
    
    # Capture to the right
    if col + 1 <= 7:
        if not piece_pinned or pin_direction == (move_amount, +1):
            if game_state.board[row + move_amount][col + 1][0] == enemy_color:
                moves.append(Move((row, col), (row + move_amount, col + 1), game_state.board))
            # En passant capture to the right
            if (row + move_amount, col + 1) == game_state.enpassant_possible:
                _addEnPassantIfValid(game_state, row, col, move_amount, 1, king_row, king_col, moves, enemy_color)


def _addEnPassantIfValid(game_state, row, col, move_amount, col_offset, king_row, king_col, moves, enemy_color):
    """Helper function to check if en passant capture is valid (doesn't expose king)."""
    attacking_piece = False
    blocking_piece = False
    
    if king_row == row:
        if king_col < col:
            inside_range = range(king_col + 1, col - 1)
            outside_range = range(col + 1, 8)
        else:
            inside_range = range(king_col - 1, col, -1)
            outside_range = range(col - 2, -1, -1)
        
        for i in inside_range:
            if game_state.board[row][i] != EMPTY_SQUARE:
                blocking_piece = True
        
        for i in outside_range:
            square = game_state.board[row][i]
            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                attacking_piece = True
            elif square != EMPTY_SQUARE:
                blocking_piece = True
    
    if not attacking_piece or blocking_piece:
        moves.append(Move((row, col), (row + move_amount, col + col_offset), game_state.board, is_enpassant_move=True))


def getRookMoves(game_state, row, col, moves):
    """Get all valid rook moves (horizontal and vertical)."""
    piece_pinned = False
    pin_direction = ()
    
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])
            if game_state.board[row][col][1] != "Q":
                game_state.pins.remove(game_state.pins[i])
            break
    
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
    enemy_color = "b" if game_state.white_to_move else "w"
    
    for direction in directions:
        for i in range(1, 8):
            end_row = row + direction[0] * i
            end_col = col + direction[1] * i
            
            if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
                break
            
            if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                end_piece = game_state.board[end_row][end_col]
                if end_piece == EMPTY_SQUARE:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))
                    break
                else:
                    break


def getKnightMoves(game_state, row, col, moves):
    """Get all valid knight moves (L-shaped, can't be pinned)."""
    piece_pinned = False
    
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            game_state.pins.remove(game_state.pins[i])
            break
    
    knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
    ally_color = "w" if game_state.white_to_move else "b"
    
    for move in knight_moves:
        end_row = row + move[0]
        end_col = col + move[1]
        
        if 0 <= end_row <= 7 and 0 <= end_col <= 7:
            if not piece_pinned:
                end_piece = game_state.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))


def getBishopMoves(game_state, row, col, moves):
    """Get all valid bishop moves (diagonal)."""
    piece_pinned = False
    pin_direction = ()
    
    for i in range(len(game_state.pins) - 1, -1, -1):
        if game_state.pins[i][0] == row and game_state.pins[i][1] == col:
            piece_pinned = True
            pin_direction = (game_state.pins[i][2], game_state.pins[i][3])
            game_state.pins.remove(game_state.pins[i])
            break
    
    directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals
    enemy_color = "b" if game_state.white_to_move else "w"
    
    for direction in directions:
        for i in range(1, 8):
            end_row = row + direction[0] * i
            end_col = col + direction[1] * i
            
            if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
                break
            
            if not piece_pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                end_piece = game_state.board[end_row][end_col]
                if end_piece == EMPTY_SQUARE:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))
                elif end_piece[0] == enemy_color:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))
                    break
                else:
                    break


def getQueenMoves(game_state, row, col, moves):
    """Get all valid queen moves (combination of rook and bishop)."""
    getRookMoves(game_state, row, col, moves)
    getBishopMoves(game_state, row, col, moves)


def getKingMoves(game_state, row, col, moves):
    """Get all valid king moves (one square in any direction)."""
    row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
    col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
    ally_color = "w" if game_state.white_to_move else "b"
    
    for i in range(8):
        end_row = row + row_moves[i]
        end_col = col + col_moves[i]
        
        if 0 <= end_row <= 7 and 0 <= end_col <= 7:
            end_piece = game_state.board[end_row][end_col]
            if end_piece[0] != ally_color:
                # Temporarily move king to check if square is under attack
                if ally_color == "w":
                    game_state.white_king_location = (end_row, end_col)
                else:
                    game_state.black_king_location = (end_row, end_col)
                
                in_check, pins, checks = game_state.checkForPinsAndChecks()
                
                if not in_check:
                    moves.append(Move((row, col), (end_row, end_col), game_state.board))
                
                # Restore king position
                if ally_color == "w":
                    game_state.white_king_location = (row, col)
                else:
                    game_state.black_king_location = (row, col)
