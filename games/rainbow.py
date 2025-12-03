import random
import math
import asyncio
import time

from games.game import Game
from utilities.colors import *

INTENSITY = 0.1

class Rainbow(Game):
    def __init__(self, main):
        super().__init__('Rainbow Game')
        self.main = main
        
    def start(self):
        pass
        
    async def loop(self):
        for i in range(12):
            self.main.lights.on(i, COLORS[i%7], INTENSITY)

    def close(self):
        self.main.lights.all_off()
        if not self.main.button.pressed:
            self.main.utilities.hibernate()
