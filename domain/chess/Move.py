from domain.chess.CastleRights import CastleRights
class Move():
    """
        Stores the movement information of the Chess state, such as the pieceMoved, pieceCaptured, and enPassant
    """
    rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRank = {value: key for key, value in rankToRow.items()}

    fileToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colToFile = {value: key for key, value in fileToCol.items()}

    legalPromotionPieces = ["R", "N", "B", "Q"]

    def __init__(self, startLocation, endLocation, board, 
                 piecePromotion = None,  isEnPassant = False, 
                 prevEnPassantSquare = None, prevCastleMoveRights = None,
                 status = None): #location in terms of (row,col)
        
        self.startRow = startLocation[0]
        self.startCol = startLocation[1]
        self.endRow = endLocation[0]
        self.endCol = endLocation[1]

        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.board = board

        # Pawn promotion
        self.piecePromotion = None if not self.isPawnPromotion() else "Q" if piecePromotion == None else piecePromotion

        # En Passant
        self.setEnPassant(isEnPassant)
        if prevEnPassantSquare != None: self.verifyEnPassant(prevEnPassantSquare)
        self.checkEnPassantSquare()

        # Castle Rights
        self.castleRights = CastleRights.copy(prevCastleMoveRights) if prevCastleMoveRights != None else CastleRights()
        self.updateCastleRight()
        self.isCastleMove = self.isCastlingMove()

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    def isPawnPromotion(self) -> bool:
        return ((self.pieceMoved == "wP" and self.endRow == 0 ) or (self.pieceMoved == "bP" and self.endRow == len(self.board[0]) - 1))
    
    def setPawnPromotion(self, promotedPiece):
        #If promoted piece is illegal, the default promotion is Queen
        self.piecePromotion = promotedPiece if promotedPiece in self.legalPromotionPieces else "Q"

    """
        Enpassant Move
    """
    def isEnPassantMove(self, enPassantSquare):
            #The last condition might not be needed as an enPassantSquare is always an empty square
        return (self.pieceMoved[1] == "P" and (self.endRow, self.endCol) == enPassantSquare\
                and abs(self.endRow - self.startRow) == 1 and abs(self.endCol - self.startCol) == 1\
                    and self.board[self.endRow][self.endCol] == "--") 
    
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
    
    """
        Chess Notation
    """
    def getRankFile(self, row, col):
        return self.colToFile[col] + self.rowToRank[row] 
    
    def getChessNotation(self):
        capturedNotation = "x" if self.pieceCaptured != "--" else ""
        pieceCapturedNotation = self.pieceCaptured[1] if self.pieceCaptured != "--" else ""
        return self.pieceMoved[1] + self.getRankFile(self.startRow, self.startCol) + capturedNotation +\
              pieceCapturedNotation+ self.getRankFile(self.endRow, self.endCol)
    
    """
        Castle Rights
    """
    def updateCastleRight(self):
        if self.pieceMoved[0] == "w":
            if self.pieceMoved[1] == "K":
                self.castleRights.setFalse("w")
            elif self.pieceMoved[1] == "R":
                self.castleRights.setCastleRookWhite(self.startRow, self.startCol)
        
        elif self.pieceMoved[0] == "b":
            if self.pieceMoved[1] == "K":
                self.castleRights.setFalse("b")
            elif self.pieceMoved[1] == "R":
                self.castleRights.setCastleRookBlack(self.startRow, self.startCol)

    def isCastlingMove(self):
        return (self.pieceMoved[1] == "K" and abs(self.endCol - self.startCol) > 1)

    def __eq__(self, other) -> bool:
        if isinstance(other, Move): return self.moveID == other.moveID
    
    def __str__(self) -> str:
        piecePromotion = "None" if self.piecePromotion == None else self.piecePromotion
        isEnPassant = "True" if self.isEnPassant else "False"
        enPassantSquare = f"({self.enPassantSquare[0], self.enPassantSquare[1]})" if self.enPassantSquare != () else "None"
        return "Move: [" + self.getChessNotation() + ", piecePromotion = " + piecePromotion + ", isEnPassant = " +  isEnPassant + \
            ", enPassantSquare = " + enPassantSquare + "]\n" + str(self.castleRights)
    
