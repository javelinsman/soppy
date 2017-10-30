from module import Module

import logging

class ModuleEcho(Module):
    def __init__(self):
        super().__init__(__name__)
    def filter(self, message):
        return True
    def operator(self, message):
        self.send(message)
