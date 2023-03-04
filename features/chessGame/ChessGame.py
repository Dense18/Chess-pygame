"""
Main Driver file
"""
import pygame
from settings import *
import domain.chess.ChessEngine as ChessEngine
from domain.chess.Status import Status
from features.chessGame.ChessUI import ChessUI
from AI.ChessAI import ChessAI
from domain.chess.Piece import *
from features.State import State
from multiprocessing import Process, Queue
import os

class ChessGame(State):    
    """
        Class to run the game of Chess
    """
    def __init__(self, game, isPlayerTwoHuman = True):
        State.__init__(self, game)
        # pygame.init()
        self.clock = pygame.time.Clock()

        self.gameState = ChessEngine.GameState()
        self.isRunning = True

        self.squareSelected = ()
        self.playerClick = []
        
        self.chessUI = ChessUI(self.gameState, self.game.screen)
        self.moveToHighlight = []

        self.chessAI = ChessAI()
        self.AIProcess = None
        self.isAIInProgress = False
        self.returnMoveQueue = Queue() 

        self.isPlayerOneHuman = True
        self.isPlayerTwoHuman = isPlayerTwoHuman
        self.humanTurn = True

        self.moveSound = pygame.mixer.Sound(os.path.join("Asset\\Sounds", "Move.ogg"))
        self.captureSound = pygame.mixer.Sound(os.path.join("Asset\\Sounds", "Capture.ogg"))
    
    def draw(self, surface):
        self.chessUI.drawGameState(squareToHighlight=self.squareSelected, 
                                       showHighlight = True, moveToHighlight = self.moveToHighlight,
                                       moveLog = self.gameState.moveLog)
    
    def update(self, deltaTime, events):
        self.humanTurn = (self.gameState.whiteTurn and self.isPlayerOneHuman) or (not self.gameState.whiteTurn and self.isPlayerTwoHuman)

        for event in events:
            if event.type == pygame.QUIT:
                self.stopAIProcess()
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    self.exitState()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: 
                    self.undoAction()
                    return
                mouseLocation = pygame.mouse.get_pos()
                self.handleMouseClick(mouseLocation, deltaTime)
        
        if (not self.humanTurn and not (self.gameState.status == Status.CHECKMATE or self.gameState.status == Status.STALEMATE) ): 
            self.AIMoveWithProcess(deltaTime)

    """
        A.I functions
    """
    def stopAIProcess(self):
        if self.AIProcess != None:
            self.AIProcess.terminate()
        self.isAIInProgress = False

    def AIMoveWithProcess(self, deltaTime):
        if not self.isAIInProgress:
            self.isAIInProgress = True
            print("Thinking...")
            validMoves = self.gameState.getAllValidMoves(self.gameState.whiteTurn)
            if (len(validMoves) != 0):
                self.AIProcess = Process(target = self.chessAI.generateMoveWithQueue, args = (self.gameState, validMoves, self.returnMoveQueue))
                self.AIProcess.start()
            else:
                return
        
        if self.AIProcess != None and not self.AIProcess.is_alive():
            print("Done thinking")
            move = self.returnMoveQueue.get()
            self.gameState.performMove(move)
            if (len(self.gameState.moveLog)): 
                self.performLastMoveEffects(deltaTime)
            self.isAIInProgress = False
            
    def AIMove(self, deltaTime):
        self.isAIInProgress = True
        validMoves = self.gameState.getAllValidMoves(self.gameState.whiteTurn)
        if (len(validMoves) != 0):
            self.gameState.performMove(self.chessAI.generateMove(self.gameState, validMoves))
            if (len(self.gameState.moveLog)): 
                self.performLastMoveEffects(deltaTime)
        self.isAIInProgress = False
    
    """
        Main functions
    """
    def undoAction(self):
        self.gameState.undoMove()

        ##Terminate AI if it is still calculating moves
        if self.isAIInProgress:
            self.stopAIProcess()

        if (not self.isPlayerTwoHuman and not self.gameState.whiteTurn): 
            self.gameState.undoMove() # undo Move twice if the opponent is an AI
        self.clearSelected()
        
    def handleMouseClick(self, mouseLocation, deltaTime):
        col = mouseLocation[0] // SQUARE_SIZE
        row = mouseLocation[1] // SQUARE_SIZE 

        #Invalid position
        if row < 0 or row >= len(self.gameState.board) or col < 0 or col >= len(self.gameState.board[row]): return

        # Prevent movement if game is already over
        if (self.gameState.status == Status.CHECKMATE or self.gameState.status == Status.STALEMATE):
            return

        ## only allow the first click to be a chess piece
        if len(self.playerClick) == 0 and self.gameState.board[row][col] == "--": return

        # Check if the new location selected is on a new position than the previous selected location
        if self.squareSelected == (row, col):
            self.clearSelected()
        else:
            self.squareSelected = (row, col)
            #Show highlight on first piece moved
            if (len(self.playerClick) == 0):
                selectedPiece = self.gameState.board[row][col]
                self.moveToHighlight = self.gameState.moveFunctions[selectedPiece[1]](row, col)
            self.playerClick.append((row,col))
         
        #Move chess piece
        if len(self.playerClick) == 2:            
            if self.gameState.board[row][col][0] == self.gameState.currentPieceTurn(): #reselect piece
                self.playerClick = [self.squareSelected]
                selectedPiece = self.gameState.board[row][col]
                self.moveToHighlight = self.gameState.moveFunctions[selectedPiece[1]](row, col)
                return
            
            ## Already did this self.gameState.movePiece(...)
            # if startPiece[0] != self.gameState.currentPieceTurn(): #prevent moving enemy piece on players turn
            #     self.clearSelected()
            #     return
            if self.humanTurn:
                pp = None
                if (self.gameState.willBeInPawnPromotion(self.playerClick[0], self.playerClick[1])):
                    #pp = input("Please select an appropiate promotion(Q/R/N/B): ").upper().strip()
                    pp = "Q"
                isMoveSuccessful = self.gameState.movePiece(self.playerClick[0], self.playerClick[1], pp)

                if (len(self.gameState.moveLog) != 0 and isMoveSuccessful): 
                    self.performLastMoveEffects(deltaTime)
                    
            ## Reselect piece regardless of current turn color
            # if not isMoveSuccessful and self.gameState.board[self.playerClick[1][0]][self.playerClick[1][1]] != "--":
            #     self.playerClick = [self.squareSelected]
            #     selectedPiece = self.gameState.board[row][col]
            #     self.moveToHighlight = self.gameState.moveFunctions[selectedPiece[1]](row, col)
            #     return
            
            self.clearSelected()

    def clearSelected(self):
        self.squareSelected = ()
        self.playerClick.clear()
        self.moveToHighlight = []

    def reset(self):
        self.stopAIProcess()

        self.gameState.reset()
        self.clearSelected()

        self.humanTurn = (self.gameState.whiteTurn and self.isPlayerOneHuman) or (not self.gameState.whiteTurn and self.isPlayerTwoHuman)

    
    """
        Effects functions
    """

    def performLastMoveEffects(self, deltaTime):
        """
            Peform Animation and Sound effects on the last move played
        """
        self.chessUI.animateMove(self.gameState.moveLog[-1], self.squareSelected, deltaTime)
        self.playSound()

    def playSound(self):
        """
            Peform Sound effects on the last move played
        """
        lastMove = self.gameState.moveLog[-1] if len(self.gameState.moveLog) else None
        if (not lastMove): return

        if lastMove.pieceCaptured == "--" : self.moveSound.play()
        else: self.captureSound.play()

