from Subject import Subject

class State(Subject):
    """
        Abstract Interface of each State of the Game
    """
    def __init__(self, game):
        self.game = game
        self.prevState = None

        self.observerList = [] #Keep track of the oberserver when removing and entering state
        pass

    def update(self, deltaTime, events):
        pass

    def draw(self, surface):
        pass

    def register(self, observer):
        self.observerList.append(observer)
    
    def unregister(self, observer):
        self.observerList.remove(observer)
    
    def notify(self, position, mouseEvent):
        for observer in self.observerList:
            observer.update(position, mouseEvent)

    def enterState(self):
        if len(self.game.stateStack) > 1:
            self.prevState = self.game.stateStack[-1]
        self.game.stateStack.append(self)
    
    def exitState(self):
        self.game.stateStack.pop()