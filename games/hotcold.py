import time, json

from utilities.utilities import Button
import utilities.lights as lights
from games.game import Game

INTENSITY = 0.1

class Hot_cold(Game):
    def __init__(self, main):
        super().__init__(main, 'Hot/Cold Game')
        self.main = main
        
    def start(self):
        self.button = Button()
        self.led = lights.Lights()
        self.led.all_off()
        
    async def loop(self):
        """
        Async task to read the ping strength of hidden_gem.
        """
        if self.main.topic == '/ping':
            try:
                #print(self.main.hidden_gem)
                #print(self.main.rssi)
                strength = self.main.rssi[self.main.hidden_gem][0]
                s = int(-11 * (strength+20)/50)   # assuming -60dB to -10dB is the best
                strength = max(0, min(s, 11))
                print('strength = ',strength)
                self.led.all_off()
                self.led.all_on(lights.RED, INTENSITY, 11-strength)
            except Exception as e:
                print(e)

        
    def close(self):
        self.lights.all_off() 
        self.button.irq = None
        