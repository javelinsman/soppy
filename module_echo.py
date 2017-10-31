"""This module defines simple echo-ing module"""

from module import Module

class ModuleEcho(Module):
    "simple echo-ing module"
    def __init__(self):
        super().__init__(__name__)
    def filter(self, message):
        return True
    def operator(self, message):
        self.send(message)
