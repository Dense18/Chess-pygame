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
    
    removeInitialPopUp(driver)
    
    board = obtainBoard(driver)
    beautify(board)
    
    print("generating  AI move ...")
    moveObj = generateAIMove(board, ai)
    
    applyMoveToWebsite(driver, moveObj)
    

    
"""
    driver functions 
"""

def removeInitialPopUp(driver: webdriver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-first-time-button"))
        )
        elem = driver.find_element(By.CLASS_NAME, "modal-first-time-button").find_element(By.TAG_NAME, "button")
        # elem = driver.find_element(By.XPATH, "/html/body/div[26]/div/div[2]/div/div[2]/div/button")
        elem.click()
    except TimeoutError:
        return 


def obtainBoard(driver: webdriver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "board-vs-personalities"))
    )
    board_element = driver.find_element(By.ID, "board-vs-personalities")
    pieces_element = board_element.find_elements(By.CLASS_NAME, "piece")
    board = [["-- " for _ in range(8)] for _ in range(8)]
    for piece_element in pieces_element:
        piece_info = piece_element.get_attribute("class")
  
        pattern = r"piece ([a-z]{2}) square-([1-9]{2})"
        m = re.search(pattern, piece_info)
        piece_type, position = m[1], m[2]
        
        row, col = convertPosition(position)
        board[row][col] = website_to_custom[piece_type]
        
        print(piece_info)
        print(website_to_custom[piece_type], m[2])
    
    return board


def applyMoveToWebsite(driver: webdriver, move: Move):
    
    ## Currently, using hint to move the piece
    ## Alternative: Try to automate mouse movement
    
    startPosition = f"{move.startCol + 1}{8 - move.startRow}"     #Website Format 
    pieceMoved = custom_to_website[move.pieceMoved]
    moving_piece_tag  = f"piece.{pieceMoved}.square-{startPosition}"
    print(moving_piece_tag)
    
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, moving_piece_tag))
    )
    pieceElement = driver.find_element(By.CLASS_NAME, moving_piece_tag)
    pieceElement.click()
    # driver.execute_script("document.getElementsByClassName(arguments[0]).item(0).click()", "piece wp square-12")
    
    endPosition = f"{move.endCol + 1}{8 - move.endRow}"
    moving_position_tag = f"hint.square-{endPosition}"
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, moving_position_tag))
    )
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, moving_position_tag))
    )
    moveElement = driver.find_element(By.CLASS_NAME, moving_position_tag)
    
    action = ActionChains(driver)
    action.move_to_element(moveElement).click().perform()

    time.sleep(100)


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