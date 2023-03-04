from features.Game import Game
import pygame
import sys

def main():
    game = Game()
    while game.running:
        game.loop()

    ## Exiting the program
    print("Exiting game....")
    pygame.quit()
    sys.exit()
        
if __name__ == "__main__":
    main()