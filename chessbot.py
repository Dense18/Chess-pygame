import re
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from AI.ChessAI import ChessAI
from domain.chess.ChessEngine import GameState
from domain.chess.Move import Move
website_to_custom = {
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
custom_to_website = {v: k for k, v in website_to_custom.items()}

def main():
    
    ai = ChessAI()
    url = "https://www.chess.com/play/computer"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    driver.maximize_window()
    
    removeInitialPopUp(driver)
    
    while(True):
        board = obtainBoard(driver)
        beautify(board)

        print("generating  AI move ...")
        moveObj = generateAIMove(board, ai)
        
        print("Applying Move")
        applyMoveToWebsite(driver, moveObj)
        
        if isGameOver(driver):
            print("Game Over")
            time.sleep(9)
            break
        
        print("Waiting for opponent")
        waitForOpponentMove(driver)
        print("Opponent have moved")
        
        if isGameOver(driver):
            print("Game Over")
            time.sleep(9)
            break
        
    driver.quit()
    
"""
    driver functions 
"""
def removeInitialPopUp(driver: webdriver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-first-time-button"))
        )
        elem = driver.find_element(By.CLASS_NAME, "modal-first-time-button").find_element(By.TAG_NAME, "button")
        elem.click()
    except TimeoutError:
        return 


def obtainBoard(driver: webdriver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "board-vs-personalities"))
    )
    board_element = driver.find_element(By.ID, "board-vs-personalities")
    pieces_element = board_element.find_elements(By.CLASS_NAME, "piece")
    board = [["--" for _ in range(8)] for _ in range(8)]
    
    
    for piece_element in pieces_element:
        piece_info = piece_element.get_attribute("class")
        

        pattern = r"piece ([a-z]{2}) square-([1-9]{2})"
        m = re.search(pattern, piece_info)
        if m is None: continue
        
        piece_type, position = m[1], m[2]
        
        row, col = convertPosition(position)
        board[row][col] = website_to_custom[piece_type]

    return board


def applyMoveToWebsite(driver: webdriver, move: Move):
    ## Currently, using hint to move the piece
    ## Alternative: Try to automate mouse movement
    
    startPosition = f"{move.startCol + 1}{8 - move.startRow}"     #Website Format 
    pieceMoved = custom_to_website[move.pieceMoved]
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
        moving_position_tag = f"piece.{custom_to_website[move.pieceCaptured]}.square-{endPosition}"
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
    
    beautify(obtainBoard(driver))


def waitForOpponentMove(driver: webdriver):
    board = obtainBoard(driver)
    WebDriverWait(driver, 10).until(
        lambda driver: hasOpponentMoved(driver, board)
    )

def isGameOver(driver: webdriver) -> bool:
    game_over_element = driver.find_element(By.ID, "game-over-modal")
    return game_over_element.get_attribute("innerHTML") != ""

def hasOpponentMoved(driver: webdriver, board: list[list[str]]) -> bool:
    highlight_elements = driver.find_elements(By.CLASS_NAME, "highlight")
    """
        Make sure not to touch the screen, or undo your own highlight
    """
    if len(highlight_elements) != 2:
        return False
    
    
    for element in highlight_elements:
        highlight_info = element.get_attribute("class")
        pattern = r"highlight square-([1-9]{2})"
        match = re.search(pattern, highlight_info)
        if match == None:
            return False
        
        position = match[1]
        row, col = convertPosition(position)
        
        if board[row][col][0] == "b":
            return True
        
    return False
    
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
def beautify(board):
    for row in board:
        print(row)        
        
def convertPosition(position: str) -> tuple[int, int]:
    col = int(position[0]) - 1
    row = 8 - int(position[1])
    return row, col


if __name__ == "__main__":
    main()