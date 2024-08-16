from abc import ABC

class BaseAction(ABC):
    def __init__(self, AR):
        from main import AlwaysReddy
        self.AR: AlwaysReddy = AR
        self.setup()

    def setup(self):
        # This method should be overridden by subclasses
        pass