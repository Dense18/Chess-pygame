import re
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


"bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"
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
    url = "https://www.chess.com/play/computer"
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    piece_id = "piece"
    
    time.sleep(700)
    board = obtainBoard(driver)
    beautify(board)
    

def obtainBoard(driver: webdriver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "board-vs-personalities"))
    )
    board_element = driver.find_element(By.ID, "board-vs-personalities")
    pieces_element = board_element.find_elements(By.CLASS_NAME, "piece")
    board = [["  " for _ in range(8)] for _ in range(8)]
    for piece_element in pieces_element:
        piece_info = piece_element.get_attribute("class")
  
        pattern = r"piece ([a-z]{2}) square-([1-9]{2})"
        m = re.search(pattern, piece_info)
        piece_type, position = m[1], m[2]
        
        row, col = convert_position(position)
        board[row][col] = website_to_custom[piece_type]
        
        print(piece_info)
        print(website_to_custom[piece_type], m[2])
    
    return board
    
def beautify(board):
    for row in board:
        print(row)        
def convert_position(position: str) -> tuple[int, int]:
    col = int(position[0]) - 1
    row = 8 - int(position[1])
    return row, col

if __name__ == "__main__":
    main()