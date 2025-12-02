import random
import math
import asyncio
import time

from utilities.utilities import Button, hibernate
import utilities.lights as lights
import utilities.i2c_bus as i2c_bus
from games.game import Game

INTENSITY = 0.1

class Clap(Game):
    def __init__(self, main):
        super().__init__('Clap Game')
        self.main = main
        
    def start(self):
        self.button = Button()
        
    async def loop(self):
        for i in range(12):
            self.lights.on(i, lights.GREEN, INTENSITY)

    def close(self):
        self.lights.all_off()
        if not self.button.pressed:
            hibernate()
        self.button.irq = None



