"""
Pin and check detection using ray-casting algorithm.
"""

from constants import EMPTY_SQUARE


def checkForPinsAndChecks(game_state):
    """
    Advanced ray-casting algorithm to detect pins and checks.
    
    Shoots rays in 8 directions (4 orthogonal + 4 diagonal) from the king's position
    to identify attacking pieces and pinned friendly pieces.
    
    Returns:
        tuple: (in_check, pins, checks)
            - in_check: Boolean indicating if king is in check
            - pins: List of pinned pieces in format (row, col, direction_row, direction_col)
            - checks: List of checking pieces in same format as pins
    """
    pins = []
    checks = []
    in_check = False
    
    if game_state.white_to_move:
        enemy_color = "b"
        ally_color = "w"
        start_row = game_state.white_king_location[0]
        start_col = game_state.white_king_location[1]
    else:
        enemy_color = "w"
        ally_color = "b"
        start_row = game_state.black_king_location[0]
        start_col = game_state.black_king_location[1]
    
    # Check in all 8 directions from king
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1),  # orthogonal
                  (-1, -1), (-1, 1), (1, -1), (1, 1))  # diagonal
    
    for j in range(len(directions)):
        direction = directions[j]
        possible_pin = ()
        
        # Check each square along the ray
        for i in range(1, 8):
            end_row = start_row + direction[0] * i
            end_col = start_col + direction[1] * i
            
            if not (0 <= end_row <= 7 and 0 <= end_col <= 7):
                break  # Off board
            
            end_piece = game_state.board[end_row][end_col]
            
            # Found an allied piece
            if end_piece[0] == ally_color and end_piece[1] != "K":
                if possible_pin == ():
                    possible_pin = (end_row, end_col, direction[0], direction[1])
                else:
                    break  # Second allied piece blocks ray
            
            # Found an enemy piece
            elif end_piece[0] == enemy_color:
                enemy_type = end_piece[1]
                
                # Check if this enemy piece can attack along this ray
                if _isValidAttackDirection(j, enemy_type, i):
                    if possible_pin == ():
                        # No blocking piece - it's a check
                        in_check = True
                        checks.append((end_row, end_col, direction[0], direction[1]))
                        break
                    else:
                        # Blocking piece - it's pinned
                        pins.append(possible_pin)
                        break
                else:
                    break  # Enemy piece can't attack this way
    
    # Check for knight checks (special case - knights jump)
    _checkForKnightChecks(game_state, start_row, start_col, enemy_color, checks, in_check)
    
    return in_check, pins, checks


def _isValidAttackDirection(direction_index, piece_type, distance):
    """
    Determine if a piece can attack along the given direction.
    
    Args:
        direction_index: Index 0-7 representing the ray direction
        piece_type: Type of enemy piece ('R', 'B', 'Q', 'K', 'p')
        distance: Distance from king to piece (1-7)
    
    Returns:
        Boolean indicating if the piece can attack along this direction
    """
    # Orthogonal directions: 0=up, 1=left, 2=down, 3=right
    # Diagonal directions: 4=up-left, 5=up-right, 6=down-left, 7=down-right
    
    is_orthogonal = 0 <= direction_index <= 3
    is_diagonal = 4 <= direction_index <= 7
    
    # Rooks attack orthogonally
    if is_orthogonal and piece_type == "R":
        return True
    
    # Bishops attack diagonally
    if is_diagonal and piece_type == "B":
        return True
    
    # Queens attack in all directions
    if piece_type == "Q":
        return True
    
    # Pawns only attack diagonally, one square away, in specific directions
    if distance == 1 and piece_type == "p":
        # White pawns attack upward-diagonals (indices 4, 5)
        # Black pawns attack downward-diagonals (indices 6, 7)
        return direction_index in (4, 5, 6, 7)
    
    # Kings attack one square in any direction
    if distance == 1 and piece_type == "K":
        return True
    
    return False


def _checkForKnightChecks(game_state, start_row, start_col, enemy_color, checks, in_check):
    """
    Check if any enemy knights are attacking the king.
    Knights have unique movement pattern (L-shaped), so they're checked separately.
    """
    knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
    
    for move in knight_moves:
        end_row = start_row + move[0]
        end_col = start_col + move[1]
        
        if 0 <= end_row <= 7 and 0 <= end_col <= 7:
            end_piece = game_state.board[end_row][end_col]
            if end_piece[0] == enemy_color and end_piece[1] == "N":
                in_check = True
                checks.append((end_row, end_col, move[0], move[1]))
