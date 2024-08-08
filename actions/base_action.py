from abc import ABC

class BaseAction(ABC):
    def __init__(self, AR):
        from main import AlwaysReddy
        self.AR: AlwaysReddy = AR