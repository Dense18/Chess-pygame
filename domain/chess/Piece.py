import domain.chess.ChessEngine as ChessEngine
from typing import Tuple
from domain.chess.Move import Move
from domain.chess.CastleRights import CastleRights

class Piece:
    """
        Base structure for the chess Pieces
    """
    def __init__(self, gamestate, isWhite = True):
        self.gamestate = gamestate
        self.isWhite = isWhite
    
    def getPossibleMoves(self, row: int, col: int):
        raise NotImplementedError

class Pawn(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        self.enPassantSquare = self.gamestate.moveLog[-1].enPassantSquare if len(self.gamestate.moveLog) != 0 else None

        board = self.gamestate.board
        possibleMoves = []
        allyPiece = board[row][col][0]
        enemyPiece = "b" if allyPiece == "w" else "w"

        incr = {"w": -1, "b": 1}
        offsets = [-1, 1] # left, right

        if (0 <= row + incr[allyPiece] <= 7):
            if board[row + incr[allyPiece]][col] == "--":
                possibleMoves.append(Move((row, col), (row + incr[allyPiece], col), board))

        if 0 <= row + 2 * incr[allyPiece]<= 7: # Might be uneccesaery
            if (row == 6 and allyPiece == "w") or (row == 1 and allyPiece == "b"):
                if board[row + incr[allyPiece]][col] == "--" and board[row + 2 * incr[allyPiece]][col] == "--":
                    possibleMoves.append(Move((row, col), (row + 2 * incr[allyPiece], col), board))

        for i in offsets:
            if (0 <= row + incr[allyPiece] <= 7 and 0 <= col + i <= 7):
                if (board[row + incr[allyPiece]][col + i][0] == enemyPiece): 
                    possibleMoves.append(Move((row, col), (row + incr[allyPiece], col + i), board))
                elif board[row + incr[allyPiece]][col + i] == "--" and (row + incr[allyPiece], col + i) == self.enPassantSquare:   
                    #TODO: If enpassantsquare, then it should be empty, so the first condition might not be needed to reduce computational cost          
                    possibleMoves.append(ChessEngine.Move((row, col), (row + incr[allyPiece], col + i), board, None, isEnPassant = True))
                    #possibleMoves.append(ChessEngine.Move((row, col), (row + incr[allyPiece], col + i), board, prevEnPassantSquare=enPassantSquare))

        return possibleMoves


class Rook(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        board = self.gamestate.board
        possibleMoves = []
        enemypiece = "b" if board[row][col][0] == "w" else "w"
        
        dir = ((-1, 0), (1, 0), (0, -1), (0, 1)) #up, down, left, right
        for move in dir:
            i = 1
            while(i < 8) :
                endRow = row + move[0] * i
                endCol = col + move[1] * i
                if ( 0 <= endRow <= 7 and 0 <= endCol <= 7 ):
                    endPiece = board[endRow][endCol]
                    if endPiece == "--": 
                        possibleMoves.append(Move((row, col), (endRow, endCol), board))
                        i += 1
                    elif endPiece[0] == enemypiece : 
                        possibleMoves.append(Move((row, col), (endRow, endCol), board))
                        break
                    else: break
                else: break
        return possibleMoves

class Knight(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        ##row and column
        board = self.gamestate.board
        allyPiece  = board[row][col][0]

        possibleMoves = []
        dir = ((1, -2), (-1,-2),
               (2,-1), (-2,-1),
               (2, 1), (-2, 1),
               (1,2), (-1,2))

        for move in dir:
            endRow = row + move[0]
            endCol = col + move[1]
            if (0 <= endRow <= 7 and 0 <= endCol <= 7 ): 
                endPiece = board[endRow][endCol]
                if (endPiece[0] != allyPiece): possibleMoves.append(Move((row,col), (endRow, endCol), board))
        return possibleMoves

class Bishop(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        board = self.gamestate.board
        possibleMoves = []
        enemypiece = "b" if board[row][col][0] == "w" else "w"
        
        dir = ((1, -1), (-1, -1), (1, 1), (-1, 1)) #up-left, down-left, up-right, down-right
        for move in dir:
            i = 1
            while(i < 8) :
                endRow = row + move[0] * i
                endCol = col + move[1] * i
                if ( 0 <= endRow <= 7 and 0 <= endCol <= 7 ):
                    endPiece = board[endRow][endCol]
                    if endPiece == "--": 
                        possibleMoves.append(ChessEngine.Move((row, col), (endRow, endCol), board))
                        i += 1
                    elif endPiece[0] == enemypiece : 
                        possibleMoves.append(ChessEngine.Move((row, col), (endRow, endCol), board))
                        break
                    else: break
                else: break
        return possibleMoves

class Queen(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        return Rook(self.gamestate).getPossibleMoves(row, col) + Bishop(self.gamestate).getPossibleMoves(row, col)

class King(Piece):
    def __init__(self, gamestate):
        super().__init__(gamestate)
    
    def getPossibleMoves(self, row: int, col: int):
        board = self.gamestate.board
        castleRights = CastleRights.copy(self.gamestate.moveLog[-1].castleRights) if len(self.gamestate.moveLog) != 0 else CastleRights()

        possibleMoves = []
        allyPiece  = board[row][col][0]

        dir = (1,0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1) #up, up-right, right, down-right, down-left, left, up - left
        for move in dir:
            endRow = row + move[0]
            endCol = col + move[1]
            if (0 <= endRow <= 7 and 0 <= endCol <= 7):
                endPiece = board[endRow][endCol]
                if (endPiece[0] != allyPiece): 
                    possibleMoves.append(Move((row, col), (endRow, endCol), board))
        
        ## Check castling move
        ## TODO: Implement functionality of castleRights in which the spaces between two pieces should not be in check
        if allyPiece == "w":
            if row == 7 and col == 4:
                if board[row][col + 1] == "--" and board[row][col + 2] == "--" and castleRights.whiteKingSide: #Kingside castle
                    possibleMoves.append(Move((row, col), (row, col + 2), board))
                if board[row][col - 1] == "--" and board[row][col - 2] == "--" and castleRights.whiteQueenSide: #Queenside Castle
                    possibleMoves.append(Move((row, col), (row, col - 2), board))
        if allyPiece == "b":
            if row == 0 and col == 4:
                if board[row][col + 1] == "--" and board[row][col + 2] == "--" and castleRights.blackKingSide: #Kingside castle
                    possibleMoves.append(Move((row, col), (row, col + 2), board))
                if board[row][col - 1] == "--" and board[row][col - 2] == "--" and castleRights.blackQueenSide: #Queenside Castle
                    possibleMoves.append(Move((row, col), (row, col - 2), board))
        return possibleMoves