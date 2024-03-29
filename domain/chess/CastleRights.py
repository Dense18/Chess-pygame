class CastleRights:
    """
        Information regarding the chess Castle Rights
    """
    def __init__(self, whiteKingSide = True, whiteQueenSide = True, blackKingSide = True, blackQueenSide = True):
        self.whiteKingSide = whiteKingSide
        self.whiteQueenSide = whiteQueenSide
        self.blackKingSide = blackKingSide
        self.blackQueenSide = blackQueenSide
    
    @staticmethod
    def copy(castleRights):
        return CastleRights(
            whiteKingSide = castleRights.whiteKingSide,
            whiteQueenSide = castleRights.whiteQueenSide,
            blackKingSide = castleRights.blackKingSide,
            blackQueenSide = castleRights.blackQueenSide
        )
    
    def setFalse(self, pieceColor):
        if pieceColor == "w":
            self.whiteKingSide = False
            self.whiteQueenSide = False
        elif pieceColor == "b":
            self.blackKingSide = False
            self.blackQueenSide = False
    
    def setCastleRookWhite(self, row, col):
        if row == 7:
            if col == 0:
                self.whiteQueenSide = False
            elif col == 7:
                self.whiteKingSide = False

    def setCastleRookBlack(self, row, col):
        if row == 0:
            if col == 0:
                self.blackQueenSide = False
            elif col == 7:
                self.blackKingSide = False

    def __str__(self) -> str:
        return f"[wks: {self.whiteKingSide}, wqs: {self.whiteQueenSide}, bks: {self.blackKingSide}, bqs: {self.blackQueenSide}]"
