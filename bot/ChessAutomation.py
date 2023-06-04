import re
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from typing import Protocol
from AI.ChessAI import ChessAI
from domain.chess.ChessEngine import GameState
from domain.chess.Move import Move

from bot.PageLocators import PageLocators

webPiece_to_customPiece = {
        "bp": "bP",
        "br": "bR", 
        "bn": "bN",
        "bb": "bB",
        "bq": "bQ",
        "bk": "bK",
        "wp": "wP", 
        "wr": "wR",
        "wn": "wN",
        "wb": "wB",
        "wq": "wQ",
        "wk": "wK",
    }
customPiece_to_webPiece = {v: k for k, v in webPiece_to_customPiece.items()}

class AiBot(Protocol):
    def generatemove(*args, **kwargs) -> Move:
        ...
        
class ChessAutomation:
    """
    Automates a chess bot battle on chess.com
    """
    def __init__(self, driver: WebDriver, ai: AiBot) -> None:
        self.driver = driver
        self.ai = ai
        
        url = "https://www.chess.com/play/computer"
        driver.get(url)
        

    def run(self):
        self.removeInitialPopUp()
        
        while(True):
            board = self.obtainBoard()
            self.beautify(board)

            print("generating  AI move ...")
            moveObj = self.generateAIMove(board)
            
            print("Applying Move")
            self.applyMoveToWebsite(moveObj)
            
            print("Checking Game Over")
            if self.isGameOver():
                break
            
            print("Waiting for opponent")
            self.waitForOpponentMove()
            print("Opponent have moved")
            
            if self.isGameOver():
                break
        
        print("Game Over")
        time.sleep(100)
        self.driver.quit()
        
    """
        driver functions 
    """


    def removeInitialPopUp(self):
        """
        Close the initial popup window from chess.com
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(PageLocators.INITIAL_MODAL)
            )
            elem = self.driver.find_element(*PageLocators.INITIAL_MODAL).find_element(By.TAG_NAME, "button")
            elem.click()
        except TimeoutException:
            return 

    def obtainBoard(self):
        """
        Returns the current board state of the chess board from the website
        """
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(PageLocators.BOARD)
        )
        board_element = self.driver.find_element(*PageLocators.BOARD)
        pieces_element = board_element.find_elements(By.CLASS_NAME, "piece")
        
        board = [["--" for _ in range(8)] for _ in range(8)]
        for piece_element in pieces_element:
            piece_type, (row, col) = self.getPieceInfoFromElement(piece_element)
            if piece_type == None:
                continue
            board[row][col] = piece_type

        return board

    def getPieceInfoFromElement(self, pieceElement: WebElement):
        """
        Parses the piece information based on the [pieceElement].
        Returns in (pieceType, (pieceRow, pieceCol)) format
        """
        piece_info = pieceElement.get_attribute("class")
            
        pattern = r"piece ([a-z]{2}) square-([1-9]{2})"
        m = re.search(pattern, piece_info)
        if m == None: 
            return None, (None, None)
        
        piece_type, position = m[1], m[2]
        return webPiece_to_customPiece[piece_type], self.convertPosition(position)

    def applyMoveToWebsite(self, move: Move):    
        """
        Applies a piece move to the website based on the [move] Object
        """
        startPosition = f"{move.startCol + 1}{8 - move.startRow}"     
        pieceMoved = customPiece_to_webPiece[move.pieceMoved]
        moving_piece_tag  = f"piece.{pieceMoved}.square-{startPosition}"
        print("starting piece: ", moving_piece_tag)
        
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, moving_piece_tag))
        )
        pieceElement = self.driver.find_element(By.CLASS_NAME, moving_piece_tag)
        pieceElement.click()
        
        endPosition = f"{move.endCol + 1}{8 - move.endRow}"
        moving_position_tag = ""
        
        
        if move.pieceCaptured != "--":
            moving_position_tag = f"piece.{customPiece_to_webPiece[move.pieceCaptured]}.square-{endPosition}"
        else:
            moving_position_tag = f"hint.square-{endPosition}"
            
        print("ending position: ", moving_position_tag)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, moving_position_tag))
        )
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, moving_position_tag))
        )
        moveElement = self.driver.find_element(By.CLASS_NAME, moving_position_tag)
        
        print("Creating action chain")
        action = ActionChains(self.driver)
        action.move_to_element(moveElement).click().perform()
        print("Finished action chain")
        
        if move.endRow == 7 and move.pieceMoved == "wP": #end of chess Piece
            print("Promotion Move!")
            self.checkForPromotion()
        
        print("printing board after movement")
        self.beautify(self.obtainBoard())
        print("Done movement")

    def checkForPromotion(self, piece = "wP"):
        """
        Identify if a promotion window is available, and chooses the [piece] option if available
        """
        try:
            WebDriverWait(self.driver,10).until(
                EC.visibility_of_element_located(PageLocators.PROMOTION_WINDOW)
            )
            promotion_window = self.driver.find_element(*PageLocators.PROMOTION_WINDOW)
            piece_element = promotion_window.find_elements(By.CLASS_NAME, piece)
            piece_element.click()
            print("Promotion!")
        except TimeoutException:
            return
        
    def waitForOpponentMove(self):
        """
        Blocking function that waits for the opponent to make a move
        """
        board = self.obtainBoard()
        WebDriverWait(self.driver, 10).until(
            lambda driver: self.hasOpponentMoved(board)
        )

    def isGameOver(self) -> bool:
        """
        Checks if the current game has ended
        """
        game_over_element = self.driver.find_element(*PageLocators.GAME_OVER_MODAL)
        return game_over_element.get_attribute("innerHTML") != ""

    def hasOpponentMoved(self, board: list[list[str]]) -> bool:
        """
            Checks if an opponent has made a move
        """
        highlight_elements = self.driver.find_elements(*PageLocators.HIGHLIGHT)
        
        print(f"Num of Highlight elements: {len(highlight_elements)}")
        if len(highlight_elements) != 2:
            return False
        
        return any(map(lambda element: self.checkHighlightPieceColor(element, board, "b"), highlight_elements))     
        
    def checkHighlightPieceColor(self, highlightElement: WebElement, board: list[list[str]], pieceColor: str):
        """
        Identify if the highlighted piece based on the [highlightElement] is the same as the given [pieceColor]
        """
        row, col = self.getHighlightPosition(highlightElement)
        if row == None or col == None:
            return False
        return board[row][col][0] == pieceColor

    def getHighlightPosition(self, highlightElement: WebElement):
        """
            Returns the position in the correct format obtained from the [highlightElement]
        """
        highlightInfo = highlightElement.get_attribute("class")
        pattern = r"highlight square-([1-9]{2})"
        match = re.search(pattern, highlightInfo)
        if match == None:
            return None, None
        
        position = match[1]
        return self.convertPosition(position)
        
    """
        A.I Move    
    """
    def generateAIMove(self, board: list[list[str]]) -> Move:
        """
            Generate a Move Object based on the given [board] and [ai] engine
        """
        gameState = GameState()
        gameState.board = board
        gameState.whiteTurn = True
        
        move_obj = self.ai.generateMove(gameState, gameState.getAllValidMoves(True))
        
        print(f"Moving {move_obj.pieceMoved} from {move_obj.startRow}{move_obj.startCol} to {move_obj.endRow}{move_obj.endCol}")
        return move_obj

    """
    Utility       
    """
    def beautify(self, board: list[list[str]]):
        """
        Prints a formatted board state to the console
        """
        for row in board:
            print(row)        
            
    def convertPosition(self, position: str) -> tuple[int, int]:
        """
        Convert the piece position from the website page source to the correct format used by this application
        """
        col = int(position[0]) - 1
        row = 8 - int(position[1])
        return row, col
