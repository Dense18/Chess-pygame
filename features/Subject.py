from abc import ABC, abstractmethod

class Subject(ABC):
    @abstractmethod
    def register(self, observer):
        raise NotImplementedError
    
    @abstractmethod
    def unregister(self, observer):
        raise NotImplementedError
    
    @abstractmethod
    def notify(self):
        raise NotImplementedError