import numpy as np
from domain.chess.Piece import *
from domain.chess.Status import Status
"""
Responsible for managing all information regarding the state of the chess game.
"""
class GameState():
    ONGOING = 1
    CHECK = 2
    CHECKMATE = 3
    STALEMATE = 4
    def __init__(self):
        """
        Board is an 8x8 2d list
        Each element consist of 2 characters
           1st character - denotes the color of pieces (w - White, b- Black)
           2nd character - denotes the pieces itself (R - Rook, N - Night, B - Bishop, Q - Queen, K - King)
        """
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])

        # ## Check if staleMate is working, move wK foward
        # self.board = np.array([
        #     ["--","--","--","--","--","bK","--","--"],
        #     ["--","--","--","--","--","wP","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","wK","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"],
        #     ["--","--","--","--","--","--","--","--"]
        # ])

        self.whiteTurn = True
        self.status = Status.ONGOING
        self.moveLog = []

        # Find a better way to keep track of king location
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)

        self.moveFunctions = {
            "P": Pawn(self).getPossibleMoves,
            "N": Knight(self).getPossibleMoves,
            "R": Rook(self).getPossibleMoves,
            "B": Bishop(self).getPossibleMoves,
            "Q": Queen(self).getPossibleMoves,
            "K": King(self).getPossibleMoves
        }
    
    """
        Update Board State Functions
    """
    def applyMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved

        if move.pieceMoved == "wK" : self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK": self.blackKingLocation = (move.endRow, move.endCol)

        ## Check Pawn Promotion
        if (move.isPawnPromotion()): 
            #if move.piecePromotion == None: move.setPawnPromotion("Q") #Not needed as Move objects defaults Queen as the piece promotion if needed
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.piecePromotion
        
        ## Check EnPassant
        if move.isEnPassant: # and self.board[move.startRow][move.endCol][1] == "P" for added security but unnecessary condition
            self.board[move.startRow][move.endCol] = "--"

        self.moveLog.append(move)  #log list of moves

        self.whiteTurn = not self.whiteTurn

    def movePiece(self, startLocation, endLocation, piecePromotion = None) -> bool:
        flag = False
        enPassantSquare = self.moveLog[-1].enPassantSquare if len(self.moveLog) != 0 else None
        moveObject = Move(startLocation, endLocation, self.board, piecePromotion, prevEnPassantSquare = enPassantSquare)
        # if moveObject.isPawnPromotion() and moveObject.piecePromotion == None: moveObject.setPawnPromotion("Q")

        currentPiece = self.board[startLocation[0]][startLocation[1]]
        
        #Not allowed to move opponent moving piece or missing piece
        if currentPiece == "--" or currentPiece[0] != self.currentPieceTurn(): return False

        ## Check if move is valid
        possibleMoves = self.moveFunctions[currentPiece[1]](startLocation[0], startLocation[1])
        if (moveObject in possibleMoves) :
            if (self.givesCheck(moveObject, self.whiteTurn)) : 
                print("Your king is in check!")
                return
            print(moveObject)
            self.performMove(moveObject)
            flag = True
        
        #self.updateCurrentStatus()
        
        return flag
    
    def undoMove(self, fromCheck = False):
        if len(self.moveLog) != 0:
            lastMoveObj = self.moveLog.pop()
            self.board[lastMoveObj.startRow][lastMoveObj.startCol] = lastMoveObj.pieceMoved
            self.board[lastMoveObj.endRow][lastMoveObj.endCol] = lastMoveObj.pieceCaptured
            self.whiteTurn = not self.whiteTurn

            if lastMoveObj.pieceMoved == "wK" : self.whiteKingLocation = (lastMoveObj.startRow, lastMoveObj.startCol)
            if lastMoveObj.pieceMoved == "bK": self.blackKingLocation = (lastMoveObj.startRow, lastMoveObj.startCol)

            if (lastMoveObj.isEnPassant):
                self.board[lastMoveObj.endRow][lastMoveObj.endCol] = "--"
                self.board[lastMoveObj.startRow][lastMoveObj.endCol] = lastMoveObj.pieceCaptured
            
            if not fromCheck: self.updateCurrentStatus()

    def reset(self):
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.whiteTurn = True
        self.status = Status.ONGOING
        self.moveLog = []
    
    def updateCurrentStatus(self):
        self.status = Status.ONGOING

        if (self.inCheck(self.whiteTurn)) :   
            self.status = Status.CHECK
        
        if (len(self.getAllValidMoves(self.whiteTurn)) == 0):
            self.status = Status.CHECKMATE if self.status == Status.CHECK else Status.STALEMATE

    def performMove(self, move):
        """
            Same as applyMove but update game status (Check, Checkmate etc.)
        """
        self.applyMove(move)
        self.updateCurrentStatus()

    """
        Validate Check  Functions
    """

    def inCheck(self, whiteTurn: bool) -> bool:
        return self.in_check_naive_OTS(whiteTurn)
    
    def in_check_naive(self, whiteTurn) -> bool:
        possibleMoves = self.getPossibleMoves(not whiteTurn)
        kingLocation = self.whiteKingLocation if whiteTurn else self.blackKingLocation 

        for move in possibleMoves:
            if kingLocation[0] == move.endRow and kingLocation[1] == move.endCol:
                return True
        return False
    
    def in_check_naive_OTS(self, whiteTurn) -> bool: #OTS means on the spot
        """
            Similar to in_check_naive but rather than creating all the possible moves
            into a list and check king location from the output list, we check for king location
            at the same time when we are seaching for the possible moves, i.e on the spot
        """
        kingLocation = self.whiteKingLocation if whiteTurn else self.blackKingLocation

        # We want to indetify the attack piece of the opposing player
        whiteTurn = not whiteTurn
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                allyColor = self.board[row][col][0]
                if (allyColor == "w" and whiteTurn) or (allyColor == "b" and not whiteTurn):
                    allyPiece = self.board[row][col][1]
                    possibleMoves = self.moveFunctions[allyPiece](row, col)
                    for move in possibleMoves:
                        if kingLocation[0] == move.endRow and kingLocation[1] == move.endCol: 
                            return True
        return False

    def givesCheck(self, move, whiteTurn: bool) -> bool:
        self.applyMove(move)
        flag = self.inCheck(whiteTurn)
        self.undoMove(fromCheck = True)
        return flag
    
    def squareUnderAttack_Naive(self, row: int, col: int) -> bool: ##....
        possibleMoves = self.getPossibleMoves(not self.whiteTurn)
        for move in possibleMoves:
            if row == move.endRow and col == move.endCol:
                return True
        return False     
    
    def willBeInPawnPromotion(self, startLocation, endLocation) -> bool:
        currentPiece = self.board[startLocation[0]][startLocation[1]]
        return ((currentPiece == "wP" and endLocation[0] == 0 ) or (currentPiece == "bP" and endLocation[0] == len(self.board[0]) - 1))
        
    """
        Possible Move Functions
    """
    def getPossibleMoves(self, whiteTurn: bool): #Improvmement: Make it more efficient
        possibleMoves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                allyColor = self.board[row][col][0]
                if (allyColor == "w" and whiteTurn) or (allyColor == "b" and not whiteTurn):
                    allyPiece = self.board[row][col][1]
                    possibleMoves += self.moveFunctions[allyPiece](row, col)
        return possibleMoves
    
    def getAllValidMoves(self, whiteTurn: bool):
        allMoves = self.getPossibleMoves(whiteTurn)
        for i in range(len(allMoves) - 1, -1, -1):
            if self.givesCheck(allMoves[i], whiteTurn) : allMoves.remove(allMoves[i])
        return allMoves        

    """
        Current state function
    """
    def currentPieceTurn(self):
        return "w" if self.whiteTurn else "b"


class Move():
    rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRank = {value: key for key, value in rankToRow.items()}

    fileToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colToFile = {value: key for key, value in fileToCol.items()}

    legalPromotionPieces = ["R", "N", "B", "Q"]

    def __init__(self, startLocation, endLocation, board, piecePromotion = None, isEnPassant = False, prevEnPassantSquare = None, status = None): #location in terms of (row,col)
        self.startRow = startLocation[0]
        self.startCol = startLocation[1]
        self.endRow = endLocation[0]
        self.endCol = endLocation[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.board = board

        #Pawn promotion
        self.piecePromotion = piecePromotion
        if self.isPawnPromotion() and piecePromotion == None: self.piecePromotion = "Q"

        # For added security but is inefficient as uncessary condition
        # self.piecePromotion == None if not self.isPawnPromotion() else "Q" if piecePromotion == None else piecePromotion

        #Update information if move is an EnPassant
        self.setEnPassant(isEnPassant)
        if prevEnPassantSquare != None: self.verifyEnPassant(prevEnPassantSquare)

        # Update if an enPassantSquare is available
        self.checkEnPassantSquare()

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    def isPawnPromotion(self) -> bool:
        return ((self.pieceMoved == "wP" and self.endRow == 0 ) or (self.pieceMoved == "bP" and self.endRow == len(self.board[0]) - 1))
    
    def setPawnPromotion(self, promotedPiece):
        #If promoted piece is illegal, the default promotion is Queen
        self.piecePromotion = promotedPiece if promotedPiece in self.legalPromotionPieces else "Q"

    ## Update Enpassant
    def isEnPassantMove(self, enPassantSquare):
        return (self.pieceMoved[1] == "P" and (self.endRow, self.endCol) == enPassantSquare\
                and abs(self.endRow - self.startRow) == 1 and abs(self.endCol - self.startCol) == 1\
                    and self.board[self.endRow][self.endCol] == "--") 
    #TODO: The last condition might not be needed as an enPassantSquare is always an empty square
    
    def setEnPassant(self, isEnpassant):
            self.isEnPassant = isEnpassant
            if (self.isEnPassant): self.pieceCaptured = "bP" if self.pieceMoved == "wP" else "wP"
    
    def verifyEnPassant(self, enPassantSquare):
        self.setEnPassant(self.isEnPassantMove(enPassantSquare))
        
    def checkEnPassantSquare(self):
        if self.pieceMoved[1] == "P" and abs(self.endRow - self.startRow) == 2:  
            # and self.board[(self.endRow + self.startRow) // 2][self.endCol][1] == "--" for added security but uncessary condition
            self.enPassantSquare = ((self.endRow + self.startRow) // 2, self.endCol)
        else:
            self.enPassantSquare = ()

    # Modify this to a real chess notation
    def getChessNotation(self):
        capturedNotation = "x" if self.pieceCaptured != "--" else ""
        pieceCapturedNotation = self.pieceCaptured[1] if self.pieceCaptured != "--" else ""
        return self.pieceMoved[1] + self.getRankFile(self.startRow, self.startCol) + capturedNotation +\
              pieceCapturedNotation+ self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colToFile[col] + self.rowToRank[row] 
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Move): return self.moveID == other.moveID
    
    def __str__(self) -> str:
        piecePromotion = "None" if self.piecePromotion == None else self.piecePromotion
        isEnPassant = "True" if self.isEnPassant else "False"
        enPassantSquare = f"({self.enPassantSquare[0], self.enPassantSquare[1]})" if self.enPassantSquare != () else "None"
        return "Move: [" + self.getChessNotation() + ", piecePromotion = " + piecePromotion + ", isEnPassant = " +  isEnPassant + \
            ", enPassantSquare = " + enPassantSquare + "]"
    
