import random
from domain.chess.Status import Status
from domain.chess.ChessEngine import ChessEngine
from AI.PositionScore import *
import time

class ChessAI:
    CHECKMATE_VALUE = 100
    STALEMATE_VALUE = 0

    def __init__(self) -> None:
        self.pieceScore = {"K": 0,"Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
        self.count = 0
        pass

    def generateMove(self, gameState, validMoves):
        startTime = time.time()
        move = self.performMiniMax(gameState, validMoves, 2)
        print(move)
        print("time taken = %s" %(time.time() - startTime))
        return move
    
    def generateMoveWithQueue(self, gameState, validMoves, queue):
        startTime = time.time()
        move = self.performMiniMax(gameState, validMoves, 2)
        print(move)
        print("time taken = %s" %(time.time() - startTime))
        queue.put(move)

    def getRandomMove(self, validMoves):
        if len(validMoves) == 0: return None
        return random.choice(validMoves)
    
    def performMiniMax(self, gameState: ChessEngine.GameState, validMoves, depth):
        if (depth == 0): return self.getRandomMove(validMoves)
        turnMultiplier = 1 if gameState.whiteTurn else -1
        maxEval = -float('Inf')
        bestMove = None

        self.count = 0

        # random.shuffle(validMoves)

        for move in validMoves:
            self.count += 1
            gameState.performMove(move)
            validMoves2 = gameState.getAllValidMoves(gameState.whiteTurn)
            # eval = turnMultiplier * self.miniMax(gameState, validMoves2, depth - 1, gameState.whiteTurn)
            eval = turnMultiplier * self.miniMaxAlphaBeta(gameState, validMoves2, depth - 1, -float('Inf'), float("Inf"), gameState.whiteTurn)
            # eval = -self.negaMax(gameState, validMoves2, depth - 1, turnMultiplier = 1 if gameState.whiteTurn else -1)
            # eval = -self.negaMaxAlphaBeta(gameState, validMoves2, depth - 1, -float('Inf'), float('Inf'), 1 if gameState.whiteTurn else -1)
            
            gameState.undoMove()

            if eval > maxEval:
                maxEval = eval
                bestMove = move

        print(f"number of counts = {self.count}")
        self.count = 0
        return bestMove
    
    """
        MiniMax Variation
    """
    def miniMax(self, gameState: ChessEngine.GameState, validMoves, depth, whiteTurn):
        self.count += 1
        if depth == 0:
            return self.evaluateBoard(gameState)

        if whiteTurn:
            maxEval = - float('Inf')
            for move in validMoves:
                gameState.performMove(move)
                validMoves2 = gameState.getAllValidMoves(not whiteTurn)

                eval = self.miniMax(gameState, validMoves2, depth - 1, not whiteTurn)
                maxEval = max(maxEval, eval)

                gameState.undoMove()
            return maxEval
        
        else:
            minEval = float('INF')
            for move in validMoves:
                gameState.performMove(move)
                validMoves2 = gameState.getAllValidMoves(not whiteTurn)

                eval = self.miniMax(gameState, validMoves2, depth - 1, not whiteTurn)
                minEval = min(minEval, eval)

                gameState.undoMove()
        return minEval
    
    def miniMaxAlphaBeta(self, gameState: ChessEngine.GameState, validMoves, depth, alpha, beta, whiteTurn):
        """
            Alpha - Best Move for white
            Beta - Best for for black
        """
        self.count += 1
        if depth == 0:
            return self.evaluateBoard(gameState)
        
        if whiteTurn:
            maxEval = - float('Inf')
            for move in validMoves:
                gameState.performMove(move)
                validMoves = gameState.getAllValidMoves(gameState.whiteTurn)

                eval = self.miniMaxAlphaBeta(gameState, validMoves, depth - 1, alpha, beta, gameState.whiteTurn)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)

                gameState.undoMove()

                if beta <= alpha: 
                    break
            return maxEval
        
        else:
            minEval = float('INF')
            for move in validMoves:
                gameState.performMove(move)
                validMoves = gameState.getAllValidMoves(gameState.whiteTurn)

                eval = self.miniMaxAlphaBeta(gameState, validMoves, depth - 1, alpha, beta, gameState.whiteTurn)
                minEval = min(minEval, eval)
                beta = min(beta, eval)

                gameState.undoMove()

                if beta <= alpha: break

        return minEval
    
    """
        NegaMax Variation
    """  

    def negaMax(self, gameState: ChessEngine.GameState, validMoves, depth, turnMultiplier):
        self.count += 1

        if depth == 0 or gameState.status == Status.CHECKMATE or gameState.status == Status.STALEMATE:
            return turnMultiplier * self.evaluateBoard(gameState)

        maxEval = -float('Inf')
        for move in validMoves:
            gameState.performMove(move)
            validMoves = gameState.getAllValidMoves(gameState.whiteTurn)
            eval = -self.negaMax(gameState, validMoves, depth - 1, -turnMultiplier)
            gameState.undoMove()

            maxEval = max(maxEval, eval)

        return maxEval
    
    def negaMaxAlphaBeta(self, gameState: ChessEngine.GameState, validMoves, depth, alpha, beta, turnMultiplier): 
        self.count += 1

        if depth == 0 or gameState.status == Status.CHECKMATE or gameState.status == Status.STALEMATE:
            return turnMultiplier * self.evaluateBoard(gameState)

        maxEval = -float('Inf')
        for move in validMoves:
            gameState.performMove(move)

            validMoves = gameState.getAllValidMoves(gameState.whiteTurn)
            eval = -self.negaMaxAlphaBeta(gameState, validMoves, depth - 1, -beta, -alpha, -turnMultiplier)
            alpha = max(alpha, eval)
            maxEval = max(maxEval, eval)

            gameState.undoMove()

            if beta <= alpha: break

        return maxEval

    # Make Move based on the score evaluation one step ahead
    def getGreedyMove(self, gameState: ChessEngine.GameState, validMoves):
        """
            If its white Turn, turn multiplier is 1 and if evaluate board is high, then score is high
            If its black Turn, turn multiplier is -1 and if evaluate board is low, then score is high 
            Eitherway, we want to find the best possible score
        """
        turnMultiplier = 1 if gameState.whiteTurn else -1
        bestScore = - self.CHECKMATE_VALUE
        bestMove = None
        for move in validMoves:
            gameState.performMove(move)
            score = turnMultiplier * self.evaluateBoard(gameState)
            if score > bestScore:
                bestScore = score
                bestMove = move
            gameState.undoMove()
        return bestMove
    
    """
        Evaluating board functions
    """
    def evaluateBoard(self, gameState):
        """
            Higher points -> White advantage
        """
        # if gameState.status == Status.CHECKMATE: 
        #     return self.CHECKMATE_VALUE if gameState.whiteTurn else - self.CHECKMATE_VALUE
        # elif gameState.status == Status.STALEMATE:
        #     return self.CHECKMATE_VALUE
        
        return self.evaluateBasedOnNumPiece(gameState.board)

    def evaluateBasedOnNumPiece(self, board):
        score = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                currentPiece = board[row][col]

                ## Eva;uate based on piece score and position
                if currentPiece[0] == "w" : score += self.pieceScore[currentPiece[1]] * 10 + positionScore(currentPiece)[row][col] 
                elif currentPiece[0] == "b": score -= self.pieceScore[currentPiece[1]] * 10 + positionScore(currentPiece)[row][col] 
        return score
