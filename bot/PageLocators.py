from selenium.webdriver.common.by import By

class PageLocators :
    """
    Class storing Page Locators for chess.com
    """
    HIGHLIGHT = (By.CLASS_NAME, "highlight")
    GAME_OVER_MODAL = (By.ID, "game-over-modal")
    BOARD = (By.ID, "board-vs-personalities")
    INITIAL_MODAL = (By.CLASS_NAME, "modal-first-time-button")
    PROMOTION_WINDOW = (By.CLASS_NAME, "promotion-window")