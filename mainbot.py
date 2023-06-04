from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from AI.ChessAI import ChessAI
from bot.ChessAutomation import ChessAutomation

def setUpDriver() -> WebDriver:
    """
    Sets up the WebDriver 
    """
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window() 
    
    return driver

def main():
    driver = setUpDriver()
    ai = ChessAI()
    automate = ChessAutomation(driver, ai)
    automate.run()

if __name__ == "__main__":
    main()