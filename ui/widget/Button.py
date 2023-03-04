import pygame
from Observer import Observer

class Button(Observer):
    """
        Creates a Button Widget inside a State Class
    """
    def __init__(self, state, x, y, width, height, 
                 text = "", textSize = 50, textColor = (255,255,255),
                 color = (0,0,0), hoverColor = (255,0,0),
                 borderRadius = 12):
        self.state = state
        self.state.register(self)

        self.x = x
        self.y = y
        self.originalY = y
        self.width = width
        self.height = height

        self.color = color
        self.hoverColor = hoverColor
        self.currentColor = color
        
        self.borderRadius = borderRadius
        self.rect = pygame.Rect(self.x, self.y, width, height)

        self.textSize = textSize
        self.textFont = pygame.font.SysFont("cambria", 50)
        self.textColor = textColor
        self.text = self.textFont.render(text, 1, self.textColor)
        self.textRect = self.text.get_rect(center = self.rect.center)

        self.pressed = False
        self.listener = None

    # def update(self, position, mouseEvent, listener = None):
    #     if self.rect.collidepoint(position):
    #         self.currentColor = self.hoverColor
    #         if mouseEvent[0]: ##Left Click
    #             self.dynamicElevation = 0
    #             # if (listener != None): listener()
    #     else:
    #         self.dynamicElevation = self.elevation
    #         self.currentColor = self.color

    def setOnClickListener(self, listener):
        self.listener = listener

    # def update(self, position, mouseEvent):
    #     if self.rect.collidepoint(position):
    #         self.currentColor = self.hoverColor
    #         if mouseEvent[0]: ##Left Click
    #             self.dynamicElevation = 0
    #             self.pressed = True
    #         else:
    #             self.dynamicElevation = self.elevation
    #             if self.pressed:
    #                 if (self.listener != None): self.listener()
    #                 self.pressed = False        
    #     else:
    #         self.dynamicElevation = self.elevation
    #         self.currentColor = self.color

    def update(self, position, mouseEvent, listener = None):
        if self.rect.collidepoint(position):
            self.currentColor = self.hoverColor
            if mouseEvent[0]: ##Left Click
                self.dynamicElevation = 0
                self.pressed = True
            else:
                if self.pressed:
                    if (self.listener != None): self.listener()
                    self.pressed = False        
        else:
            self.currentColor = self.color

    def draw(self, screen):
        pygame.draw.rect(screen, self.currentColor, self.rect, border_radius = self.borderRadius)
        screen.blit(self.text, self.textRect)
