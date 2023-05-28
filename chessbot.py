import re
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from AI.ChessAI import ChessAI
from domain.chess.ChessEngine import GameState
from domain.chess.Move import Move

from PageLocators import PageLocators
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

def main():
    ai = ChessAI()
    driver = setUpDriver()
    
    removeInitialPopUp(driver)
    
    while(True):
        board = obtainBoard(driver)
        beautify(board)

        print("generating  AI move ...")
        moveObj = generateAIMove(board, ai)
        
        print("Applying Move")
        applyMoveToWebsite(driver, moveObj)
        
        print("Checking Game Over")
        if isGameOver(driver):
            print("Game Over")
            time.sleep(100)
            break
        
        print("Waiting for opponent")
        waitForOpponentMove(driver)
        print("Opponent have moved")
        
        if isGameOver(driver):
            print("Game Over")
            time.sleep(100)
            break
    
    driver.quit()
    
"""
    driver functions 
"""

def setUpDriver() -> WebDriver:
    url = "https://www.chess.com/play/computer"
    
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.maximize_window() 
    
    return driver

def removeInitialPopUp(driver: WebDriver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(PageLocators.INITIAL_MODAL)
        )
        elem = driver.find_element(*PageLocators.INITIAL_MODAL).find_element(By.TAG_NAME, "button")
        elem.click()
    except TimeoutException:
        print("Wassup hoimie")
        return 


def obtainBoard(driver: WebDriver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(PageLocators.BOARD)
    )
    board_element = driver.find_element(*PageLocators.BOARD)
    pieces_element = board_element.find_elements(By.CLASS_NAME, "piece")
    
    board = [["--" for _ in range(8)] for _ in range(8)]
    for piece_element in pieces_element:
        piece_type, (row, col) = getPieceInfoFromElement(piece_element)
        if piece_type == None:
            continue
        board[row][col] = piece_type

    return board

def getPieceInfoFromElement(piece_element: WebElement):
    piece_info = piece_element.get_attribute("class")
        
    pattern = r"piece ([a-z]{2}) square-([1-9]{2})"
    m = re.search(pattern, piece_info)
    if m == None: 
        return None, (None, None)
    
    piece_type, position = m[1], m[2]
    return webPiece_to_customPiece[piece_type], convertPosition(position)

def applyMoveToWebsite(driver: WebDriver, move: Move):
    ## Currently, using hint to move the piece
    ## Alternative: Try to automate mouse movement
    
    startPosition = f"{move.startCol + 1}{8 - move.startRow}"     #Website Format 
    pieceMoved = customPiece_to_webPiece[move.pieceMoved]
    moving_piece_tag  = f"piece.{pieceMoved}.square-{startPosition}"
    print("starting piece: ", moving_piece_tag)
    
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, moving_piece_tag))
    )
    pieceElement = driver.find_element(By.CLASS_NAME, moving_piece_tag)
    pieceElement.click()
    
    endPosition = f"{move.endCol + 1}{8 - move.endRow}"
    moving_position_tag = ""
    
    
    if move.pieceCaptured != "--":
        moving_position_tag = f"piece.{customPiece_to_webPiece[move.pieceCaptured]}.square-{endPosition}"
    else:
        moving_position_tag = f"hint.square-{endPosition}"
        
    print("ending position: ", moving_position_tag)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, moving_position_tag))
    )
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, moving_position_tag))
    )
    moveElement = driver.find_element(By.CLASS_NAME, moving_position_tag)
    
    print("Creating action chain")
    action = ActionChains(driver)
    action.move_to_element(moveElement).click().perform()
    print("Finished action chain")
    
    if move.endRow == 7 and move.pieceMoved == "wP": #end of chess Piece
        print("Promotion Move!")
        checkForPromotion(driver)
    
    print("printing board after movement")
    beautify(obtainBoard(driver))
    print("Done movement")

def checkForPromotion(driver: WebDriver):
    try:
        WebDriverWait(driver,1).until(
            EC.visibility_of_element_located(PageLocators.PROMOTION_WINDOW)
        )
        promotion_window = driver.find_element(*PageLocators.PROMOTION_WINDOW)
        piece_element = promotion_window.find_elements(By.CLASS_NAME, "wq")
        piece_element.click()
        print("Promotion!")
    except TimeoutException:
        return
    
def waitForOpponentMove(driver: WebDriver):
    board = obtainBoard(driver)
    WebDriverWait(driver, 10).until(
        lambda driver: hasOpponentMoved(driver, board)
    )

def isGameOver(driver: WebDriver) -> bool:
    game_over_element = driver.find_element(*PageLocators.GAME_OVER_MODAL)
    return game_over_element.get_attribute("innerHTML") != ""

def hasOpponentMoved(driver: WebDriver, board: list[list[str]]) -> bool:
    highlight_elements = driver.find_elements(*PageLocators.HIGHLIGHT)
    
    print(f"Num of Highlight elements: {len(highlight_elements)}")
    """
        Make sure not to touch the screen, or undo your own highlight
    """
    if len(highlight_elements) != 2:
        return False
    
    
    for element in highlight_elements:
        row, col = getHighlightPosition(element)
        if row == None or col == None:
            return False
        
        if board[row][col][0] == "b":
            return True
        
    return False

def getHighlightPosition(highlight_element: WebElement):
    highlight_info = highlight_element.get_attribute("class")
    pattern = r"highlight square-([1-9]{2})"
    match = re.search(pattern, highlight_info)
    if match == None:
        return None, None
    
    position = match[1]
    return convertPosition(position)
    
"""
    A.I Move    
"""
def generateAIMove(board: list[list[str]], ai: ChessAI) -> Move:
    gameState = GameState()
    gameState.board = board
    gameState.whiteTurn = True
    
    move_obj = ai.generateMove(gameState, gameState.getAllValidMoves(True))
    
    print(f"Moving {move_obj.pieceMoved} from {move_obj.startRow}{move_obj.startCol} to {move_obj.endRow}{move_obj.endCol}")
    return move_obj

"""
Utility       
"""
def beautify(board: list[list[str]]):
    for row in board:
        print(row)        
        
def convertPosition(position: str) -> tuple[int, int]:
    col = int(position[0]) - 1
    row = 8 - int(position[1])
    return row, col


if __name__ == "__main__":
    main()