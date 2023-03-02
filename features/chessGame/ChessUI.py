from settings import *
import pygame
import os
import time
from domain.chess.Status import Status
class ChessUI:
    def __init__(self, gamestate, screen):
        # pygame.init()
        # pygame.display.set_caption("Chess")
        
        self.gameState = gamestate
        self.screen = screen
        self.IMAGES = {}
        self.loadImages()

        self.moveLogTopBorder = 0
        self.moveLogLeftBorder = 2

        self.moveLogTopPadding = 3
        self.moveLogNotationSpacing = 5

        self.colors = [(237,238,209), (121,149,52)] #Grenish White and Greenish Gray
        self.moveLogBackgroundColor = (38,36,33) #Grayish black
        self.textNotationSize = int(SQUARE_SIZE * 0.35)
        self.textNotationFont = pygame.font.SysFont("1", self.textNotationSize)

        # Variables for MoveLog display
        self.textMoveSize = 15
        self.textMoveFont = pygame.font.SysFont("1", self.textMoveSize)
        self.textSpacing = 3  
        self.movePerRow = 3

        self.clock = pygame.time.Clock()
        self.rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
        self.rowToRank = {value: key for key, value in self.rankToRow.items()}

        self.fileToCol = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        self.colToFile = {value: key for key, value in self.fileToCol.items()}
        pass

    def drawPieces(self):
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                piece = self.gameState.board[row, col]
                if (piece != "--"):
                    self.screen.blit(self.IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def drawBoard(self):
        #Color taken by inspecting the html source from chess.com [#pastel white, #dark green]
        for row in range(DIMENSION):
            for col in range(DIMENSION):
                self.drawSquare(row, col)
                    
    def drawSquare(self, row, col):
        #Draw Square
        color = self.colors[(row + col) % 2]
        pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        #Draw Text Notation
        textColor = self.colors[((row + col) % 2 + 1) % 2]
        if col == 0: 
            text = self.rowToRank[row]
            textToDraw = self.textNotationFont.render(text, 1, textColor)

            offset = SQUARE_SIZE * 0.1
            self.screen.blit(textToDraw, (col * SQUARE_SIZE + offset, row * SQUARE_SIZE + offset))
        if row == DIMENSION - 1: 
            text = self.colToFile[col]
            textToDraw = self.textNotationFont.render(text, 1, textColor)
            offset = SQUARE_SIZE * 0.2
            self.screen.blit(textToDraw, (col * SQUARE_SIZE + SQUARE_SIZE - offset, row * SQUARE_SIZE + SQUARE_SIZE - offset))
                    
    def drawHighlight(self, squareSelected, moveToHighlight): 
        if squareSelected == () : return

        # HighLight Selected Square
        row, col = squareSelected
        square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        square.set_alpha(100)
        square.fill(pygame.Color("blue"))
        self.screen.blit(square, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        selectedPiece = self.gameState.board[row][col]
        if (selectedPiece == "--"): return

        # Highlight Move
        for move in moveToHighlight:
            square = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            square.set_alpha(150)
            square.fill(pygame.Color("orange"))
            self.screen.blit(square, (move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE))

    def drawLastMoveHighlight(self):
        # Highlight first and last position
        lastMove = self.gameState.moveLog[-1] if self.gameState.moveLog else None
        if lastMove != None:
            movedSquare = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            movedSquare.set_alpha(200)
            movedSquare.fill((230,230,0))
            self.screen.blit(movedSquare, (lastMove.startCol * SQUARE_SIZE, lastMove.startRow * SQUARE_SIZE))
            self.screen.blit(movedSquare, (lastMove.endCol * SQUARE_SIZE, lastMove.endRow * SQUARE_SIZE))

    def drawGameState(self, squareToHighlight, 
                      showHighlight = False, moveToHighlight = None, moveLog = [], update = True,
                      drawGameOverText = True):
        self.drawBoard()
        self.drawLastMoveHighlight()
        if (showHighlight): self.drawHighlight(squareToHighlight, moveToHighlight)
        self.drawPieces()

        if (drawGameOverText): self.drawGameOverText()
        self.drawMoveLog(moveLog)
        
        if update: pygame.display.update()
        
    def animateMove(self, move, squareSelected, deltaTime): #TODO: Try to only draw the portion/section that is changed, and not the entire section
        if move == None: return

        dRow = move.endRow - move.startRow
        dCol = move.endCol - move.startCol

        framePerSquare = 0.13 / deltaTime
        # frameCount = int (min(2.5 * framePerSquare, (abs(dRow) + abs(dCol)) * framePerSquare))
        frameCount = int ( (max(abs(dRow), abs(dCol))) * framePerSquare )

        for frame in range(frameCount + 1):
            col, row = (move.startCol + (dCol * frame/frameCount)), (move.startRow + (dRow * frame/frameCount))
            self.drawGameState(squareSelected, showHighlight=False, update = False, drawGameOverText = False)

            # Erase the captured piece to prevent having two exact same piece in the screen
            endSquare = pygame.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            self.drawSquare(move.endRow, move.endCol)

            if (move.pieceCaptured != "--"):
                if move.isEnPassant: ## Animation for enPassant
                    enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == "b" else (move.endRow - 1)
                    endSquare = pygame.Rect(move.endCol * SQUARE_SIZE, enPassantRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                self.screen.blit(self.IMAGES[move.pieceCaptured], endSquare)

            # if (move.pieceMoved != "--"): Unessary condition if move is added properly
            self.screen.blit(self.IMAGES[move.pieceMoved], pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            pygame.display.update((0,0, BOARD_WIDTH, BOARD_HEIGHT))
       
    def drawMoveLog(self, moveLog = []):
        moveLogRect = pygame.Rect(BOARD_WIDTH - self.moveLogLeftBorder, 0 + self.moveLogTopBorder, MOVELOG_WIDTH, BOARD_HEIGHT)
        pygame.draw.rect(self.screen, self.moveLogBackgroundColor, moveLogRect)

        textY = self.moveLogTopPadding + self.textMoveSize
        j = 0
        for i in range(0, len(moveLog), 2):
            j += 1
            chessNotationText = moveLog[i].getChessNotation()
            if i + 1 < len(moveLog): 
                j += 1
                chessNotationText += " " + moveLog[i + 1].getChessNotation()
            if ( i % (self.movePerRow * 2) == 0):
                moveLogRect.y = moveLogRect.y + textY
                moveLogRect.x = BOARD_WIDTH + self.textSpacing
            else:
                if (j % 2 == 1 and j != 1):
                    moveLogRect.move_ip(moveLogTextObj.get_width() + self.moveLogNotationSpacing, 0)
                if (j % 2 == 0 and j >= 3):
                    moveLogRect.move_ip(moveLogTextObj.get_width() + self.moveLogNotationSpacing, 0)

            moveLogTextObj = self.textMoveFont.render(f"{i//2 + 1}. {chessNotationText}", 1, pygame.Color("White"))
            self.screen.blit(moveLogTextObj, moveLogRect)

    def drawGameOverText(self):
        if self.gameState.status != Status.CHECKMATE and self.gameState.status != Status.STALEMATE:
            return
        
        rectWidth = 150
        rectHeight = 100
        rectX = self.screen.get_width()//2 - rectWidth//2
        rectY = self.screen.get_height()//2 - rectHeight//2
        rect = pygame.Rect(rectX, rectY, rectWidth, rectHeight)

        text = "CheckMate" if self.gameState.status == Status.CHECKMATE else "StaleMate"
        textObj = self.textNotationFont.render(text, 1, (255, 255, 255))
        textRect = textObj.get_rect(center = rect.center)

        pygame.draw.rect(self.screen, (100,100,100), rect)
        self.screen.blit(textObj, textRect)

    # def drawMoveLog(self, moveLog = []):
    #     moveLogRect = pygame.Rect(BOARD_WIDTH + self.moveLogBorder, 0 + self.moveLogBorder, MOVELOG_WIDTH, BOARD_HEIGHT)
    #     pygame.draw.rect(self.screen, self.moveLogBackgroundColor, moveLogRect)

    #     moveText = []
    #     for i in range(0, len(moveLog), 2):
    #         moveString = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " "
    #         if (i + 1 < len(moveLog)):
    #             moveString += moveLog[i + 1].getChessNotation() + "   "
    #         moveText.append(moveString)

    #     textY = self.moveLogPadding + self.textMoveSize
    #     for i in range(0, len(moveLog), self.movePerRow):
    #         chessNotationText = ""
    #         for j in range(self.movePerRow):
    #             if i + j < len(moveText): 
    #                 chessNotationText += moveText[i + j]

    #         moveLogTextObj = self.textMoveFont.render(chessNotationText, 1, pygame.Color("White"))
    #         moveLogRect.move_ip(0, textY)
    #         self.screen.blit(moveLogTextObj, moveLogRect)

    ## Should only be initialized once during creation of class
    def loadImages(self):
        """
            Loads required images for the chess piece
        """
        pieces = ["bP", "bR","bN","bB","bQ","bK","wP", "wR","wN","wB","wQ","wK"]
        for piece in pieces:
            chessImg = pygame.image.load(os.path.join("Asset\\Images", piece + ".png"))
            self.IMAGES[piece] = pygame.transform.smoothscale(chessImg, (SQUARE_SIZE , SQUARE_SIZE))
    
    
    