import random
import math
import asyncio

from utilities.utilities import Button
import utilities.lights as lights
import utilities.i2c_bus as i2c_bus
from games.game import Game

COLORS = [lights.VIOLET, lights.INDIGO, lights.BLUE, lights.GREEN, lights.YELLOW, lights.ORANGE, lights.RED]

class Rainbow(Game):
    def __init__(self):
        super().__init__('Rainbow Game')
        self.button = Button()
        self.level = 0
        self.accel = i2c_bus.LIS2DW12()
        
    def abs_accel(self):
        x,y,z = self.accel.read_accel()
        return math.sqrt(x**2+y**2+z**2) - 1
        

    async def loop(self):
        """
        Async task to play increase the number of leds shown with how
        vigorous you shake.  Hitting the button resets
        """
        if self.button.pressed:  # Button pressed
            self.level = 0
            self.lights.all_off()
        else:  # Button released
            acc = min(12, int(abs(self.abs_accel()) * 4))
            if self.level < acc: self.level = acc
            for i in range(12):
                self.lights.on(i, COLORS[i%12])

    def close(self):
        self.lights.all_off()
        self.button.irq = None



