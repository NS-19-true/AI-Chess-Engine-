"""
Core chess game engine.
Manages game state, move validation, and game logic.
"""

from constants import (
    BOARD_SIZE, EMPTY_SQUARE, WHITE_COLOR, BLACK_COLOR,
    PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING,
    INITIAL_BOARD, WHITE_KING_START, BLACK_KING_START
)
from move import Move, CastleRights
import piece_moves
import check_detection as cd


class GameState:
    """
    Represents the current state of a chess game.
    Tracks board position, move history, castling rights, and game status.
    """
    
    def __init__(self):
        """Initialize a new chess game with standard starting position."""
        self.board = [row[:] for row in INITIAL_BOARD]  # Deep copy initial board
        
        # Map piece types to their movement functions
        self.moveFunctions = {
            PAWN: piece_moves.getPawnMoves,
            ROOK: piece_moves.getRookMoves,
            KNIGHT: piece_moves.getKnightMoves,
            BISHOP: piece_moves.getBishopMoves,
            QUEEN: piece_moves.getQueenMoves,
            KING: piece_moves.getKingMoves
        }
        
        # Game state tracking
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = WHITE_KING_START
        self.black_king_location = BLACK_KING_START
        
        # Game status
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        
        # Check/pin tracking
        self.pins = []
        self.checks = []
        
        # En passant tracking
        self.enpassant_possible = ()
        self.enpassant_possible_log = [self.enpassant_possible]
        
        # Castling rights tracking
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs
            )
        ]

    def makeMove(self, move):
        """
        Execute a move on the board.
        Updates board state, move log, king location, and special move flags.
        
        Args:
            move: Move object to execute
        """
        # Move the piece
        self.board[move.start_row][move.start_col] = EMPTY_SQUARE
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        
        # Update king location if it moved
        if move.piece_moved == WHITE_COLOR + KING:
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == BLACK_COLOR + KING:
            self.black_king_location = (move.end_row, move.end_col)
        
        # Handle pawn promotion (always promote to queen for AI)
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + QUEEN
        
        # Handle en passant capture
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = EMPTY_SQUARE
        
        # Update en passant availability
        if move.piece_moved[1] == PAWN and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()
        
        # Handle castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = EMPTY_SQUARE
            else:  # Queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = EMPTY_SQUARE
        
        self.enpassant_possible_log.append(self.enpassant_possible)
        
        # Update castling rights
        self.updateCastleRights(move)
        self.castle_rights_log.append(
            CastleRights(
                self.current_castling_rights.wks,
                self.current_castling_rights.bks,
                self.current_castling_rights.wqs,
                self.current_castling_rights.bqs
            )
        )

    def undoMove(self):
        """
        Undo the last move and restore previous game state.
        """
        if not self.move_log:
            return
        
        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move
        
        # Restore king location
        if move.piece_moved == WHITE_COLOR + KING:
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == BLACK_COLOR + KING:
            self.black_king_location = (move.start_row, move.start_col)
        
        # Restore en passant capture
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = EMPTY_SQUARE
            self.board[move.start_row][move.end_col] = move.piece_captured
        
        self.enpassant_possible_log.pop()
        self.enpassant_possible = self.enpassant_possible_log[-1]
        
        # Restore castling rights
        self.castle_rights_log.pop()
        self.current_castling_rights = self.castle_rights_log[-1]
        
        # Restore castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # Kingside
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                self.board[move.end_row][move.end_col - 1] = EMPTY_SQUARE
            else:  # Queenside
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = EMPTY_SQUARE
        
        self.checkmate = False
        self.stalemate = False

    def updateCastleRights(self, move):
        """
        Update castling rights based on the move.
        Castling rights are lost when king/rook moves or rook is captured.
        
        Args:
            move: Move object that was just executed
        """
        # King captures rook
        if move.piece_captured == WHITE_COLOR + ROOK:
            if move.end_col == 0:
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:
                self.current_castling_rights.wks = False
        elif move.piece_captured == BLACK_COLOR + ROOK:
            if move.end_col == 0:
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:
                self.current_castling_rights.bks = False
        
        # King moves
        if move.piece_moved == WHITE_COLOR + KING:
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == BLACK_COLOR + KING:
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        
        # Rook moves
        elif move.piece_moved == WHITE_COLOR + ROOK:
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == BLACK_COLOR + ROOK:
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

    def checkForPinsAndChecks(self):
        """Wrapper for check detection - updates game state and returns results."""
        self.in_check, self.pins, self.checks = cd.checkForPinsAndChecks(self)
        return self.in_check, self.pins, self.checks

    def getValidMoves(self):
        """
        Get all legal moves considering pins and checks.
        Filters out moves that would leave the king in check.
        
        Returns:
            List of valid Move objects
        """
        temp_castle_rights = CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs
        )
        
        moves = []
        self.checkForPinsAndChecks()
        
        if self.white_to_move:
            king_row, king_col = self.white_king_location
        else:
            king_row, king_col = self.black_king_location
        
        if self.in_check:
            if len(self.checks) == 1:  # Single check - can block or move king
                moves = self.getAllPossibleMoves()
                
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                
                # Knight checks must be captured or king moves
                if piece_checking[1] == KNIGHT:
                    valid_squares = [(check_row, check_col)]
                else:
                    # Block the check
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square == (check_row, check_col):
                            break
                
                # Remove moves that don't block or capture
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != KING:
                        if (moves[i].end_row, moves[i].end_col) not in valid_squares:
                            moves.remove(moves[i])
            else:  # Double check - only king moves
                self.getKingMoves(king_row, king_col, moves)
        else:  # Not in check
            moves = self.getAllPossibleMoves()
            if self.white_to_move:
                self.getCastleMoves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.getCastleMoves(self.black_king_location[0], self.black_king_location[1], moves)
        
        # Determine game status
        if not moves:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        self.current_castling_rights = temp_castle_rights
        return moves

    def inCheck(self):
        """Determine if the current player's king is in check."""
        if self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])

    def squareUnderAttack(self, row, col):
        """
        Determine if a square is under attack by opponent.
        """
        self.white_to_move = not self.white_to_move
        opponents_moves = self.getAllPossibleMoves()
        self.white_to_move = not self.white_to_move
        
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def getAllPossibleMoves(self):
        """
        Get all possible moves without considering checks.
        """
        moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                turn = self.board[row][col][0]
                if (turn == WHITE_COLOR and self.white_to_move) or \
                   (turn == BLACK_COLOR and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](self, row, col, moves)
        return moves

    def getKingMoves(self, row, col, moves):
        """Get king moves."""
        piece_moves.getKingMoves(self, row, col, moves)

    def getCastleMoves(self, row, col, moves):
        """
        Generate castling moves if available.
        """
        if self.squareUnderAttack(row, col):
            return  # Can't castle while in check
        
        if (self.white_to_move and self.current_castling_rights.wks) or \
           (not self.white_to_move and self.current_castling_rights.bks):
            self._getKingsideCastleMoves(row, col, moves)
        
        if (self.white_to_move and self.current_castling_rights.wqs) or \
           (not self.white_to_move and self.current_castling_rights.bqs):
            self._getQueensideCastleMoves(row, col, moves)

    def _getKingsideCastleMoves(self, row, col, moves):
        """Kingside castling (O-O)."""
        if self.board[row][col + 1] == EMPTY_SQUARE and self.board[row][col + 2] == EMPTY_SQUARE:
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def _getQueensideCastleMoves(self, row, col, moves):
        """Queenside castling (O-O-O)."""
        if self.board[row][col - 1] == EMPTY_SQUARE and \
           self.board[row][col - 2] == EMPTY_SQUARE and \
           self.board[row][col - 3] == EMPTY_SQUARE:
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))
