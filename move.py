"""
Move and CastleRights classes for chess game state management.
"""


class Move:
    """
    Represents a chess move with source and destination squares.
    Handles special moves: castling, en passant, and pawn promotion.
    Converts between array indices and standard chess notation (e.g., 'a1', 'e4').
    """
    
    # Chess notation mappings
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant_move=False, is_castle_move=False):
        """
        Initialize a move.
        
        Args:
            start_square: Tuple (row, col) of starting position
            end_square: Tuple (row, col) of ending position
            board: Current board state to extract piece information
            is_enpassant_move: Boolean indicating en passant capture
            is_castle_move: Boolean indicating castling move
        """
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        
        # Pawn promotion: pawn reaches last rank
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or \
                                 (self.piece_moved == "bp" and self.end_row == 7)
        
        # En passant move
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"
        
        # Castle move
        self.is_castle_move = is_castle_move
        
        self.is_capture = self.piece_captured != "--"
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """Check if two moves are identical based on their moveID."""
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getRankFile(self, row, col):
        """Convert array indices (row, col) to chess notation (e.g., 'e4')."""
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def getChessNotation(self):
        """
        Return the move in standard chess notation.
        Handles pawn promotion, castling, en passant, and captures.
        """
        if self.is_pawn_promotion:
            return self.getRankFile(self.end_row, self.end_col) + "Q"
        
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"  # Queenside castling
            else:
                return "0-0"    # Kingside castling
        
        if self.is_enpassant_move:
            return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                   self.getRankFile(self.end_row, self.end_col) + " e.p."
        
        if self.piece_captured != "--":
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.start_row, self.start_col)[0] + "x" + \
                       self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.getRankFile(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.getRankFile(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.getRankFile(self.end_row, self.end_col)

    def __str__(self):
        """Return a string representation of the move."""
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.getRankFile(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square


class CastleRights:
    """
    Tracks castling availability for both players.
    Castling rights are lost when king or rook moves, or rook is captured.
    """
    
    def __init__(self, wks, bks, wqs, bqs):
        """
        Initialize castling rights.
        
        Args:
            wks: White kingside castling allowed
            bks: Black kingside castling allowed
            wqs: White queenside castling allowed
            bqs: Black queenside castling allowed
        """
        self.wks = wks  # White kingside
        self.bks = bks  # Black kingside
        self.wqs = wqs  # White queenside
        self.bqs = bqs  # Black queenside
