import pygame
import os
import time
from settings import *
from features.menu.Menu import Menu
from Subject import Subject

class Game(Subject):
    def __init__(self) -> None:
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.dt, self.prevTime = 0, 0
        self.stateStack = []
        self.events = None

        self.observerList = []
        self.loadInitialState()

    
    def loop(self):
        self.getDt()
        self.getEvents()
        self.update()
        self.render()

    def getEvents(self):
        self.events = pygame.event.get()

    def update(self):
        self.stateStack[-1].notify(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
        self.stateStack[-1].update(self.dt,self.events)

    def render(self):
        self.stateStack[-1].draw(None)
        # Render current state to the screen
        # self.screen.blit(pygame.transform.scale(self.game_canvas,(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)), (0,0))
        pygame.display.update()
    
    def getDt(self):
        now = time.time()
        self.dt = now - self.prevTime
        self.prevTime = now

    def loadInitialState(self):
        self.menuScreen = Menu(self, self.screen)
        self.stateStack.append(self.menuScreen)

    """
        Observable functions
    """
    def register(self, observer):
        self.observerList.append(observer)
    
    def unregister(self, observer):
        self.observerList.remove(observer)
    
    def notify(self, position, mouseEvent):
        for observer in self.stateStack[-1].observerList:
            observer.update(position, mouseEvent)