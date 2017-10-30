from module import Module

import logging

class ModuleEcho(Module):
    def __init__(self):
        super().__init__(__name__)
    def filter(self, message):
        return True
    def operator(self, message):
        self.send({"chat_id":320330606, "text":message["text"]})
