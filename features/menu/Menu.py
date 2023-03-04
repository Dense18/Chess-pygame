from features.State import State
import pygame
from settings import *
from features.chessGame.ChessGame import ChessGame
from ui.widget.AnimatedButton import AnimatedButton

class Menu(State):
    """
        Menu State of the program. 
        Contains the VsPlayer, VSComputer, and Quit options
    """
    def __init__(self, game, screen):
        super().__init__(game)
        self.buttonWidth = 300
        self.buttonHeight = 100
        self.paddingTop = 50

        self.buttonX = self.game.screen.get_width()//2 - self.buttonWidth/2
        self.paddingTop = (self.game.screen.get_height() - (self.buttonHeight * 3)) / 4

        self.buttonColor = (79, 121, 66)
        self.setUpButtons()

        
    def setUpButtons(self):
        self.vsPlayerButton = AnimatedButton(self, self.buttonX,self.paddingTop,
                                  self.buttonWidth,self.buttonHeight, 
                                  color = self.buttonColor, text = "Vs Player")
        self.vsPlayerButton.setOnClickListener(self.onVsPlayerButtonClick)

        self.vsAiButton = AnimatedButton(self, self.buttonX, self.vsPlayerButton.y + self.vsPlayerButton.height + self.paddingTop,
                                  self.buttonWidth,self.buttonHeight, 
                                  color = self.buttonColor, text = "Vs Computer")
        self.vsAiButton.setOnClickListener(self.onVsAIButtonClick)

        self.endButton = AnimatedButton(self, self.buttonX, self.vsAiButton.y + self.vsAiButton.height + self.paddingTop, 
                                self.buttonWidth, self.buttonHeight, 
                                color = self.buttonColor, text = "Quit")
        self.endButton.setOnClickListener(self.onQuitButtonClick)


        self.buttonList = [self.vsPlayerButton, self.vsAiButton, self.endButton]

    def draw(self, surface):
        rect = pygame.Rect(0,0, SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.game.screen, (237,238,209), rect)
        self.drawButtons()
    
    def update(self, deltaTime, events):
        for event in events:
            if event.type == pygame.QUIT: self.game.running = False
    
    def drawButtons(self):
        for button in self.buttonList: button.draw(self.game.screen)

    """
        Button Listener
    """
    def onVsPlayerButtonClick(self):
        chessGameState = ChessGame(self.game)
        chessGameState.enterState()

    def onVsAIButtonClick(self):
        chessGameState = ChessGame(self.game, isPlayerTwoHuman = False)
        chessGameState.enterState()
    
    def onQuitButtonClick(self):
        self.game.running = False