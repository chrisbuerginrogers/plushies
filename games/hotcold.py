import time, json

import utilities.lights as lights
from games.game import Game

class Hot_cold(Game):
    def __init__(self):
        super().__init__('Hot/Cold Game')
        hidden_gem=b'\xf0\xf5\xbd-\x17x'
            
        self.led = lights.Lights()
        
    async def loop(self):
        """
        Async task to read the ping strength of hidden_gem.
        """
        if self.topic == '/ping':
            try:
                strength = self.rssi[hidden_gem][0]
                strength += 30 # best possbile case
                s = int(12 + 3 * strength/10)
                max(0, min(s, 11))
                print(strength)
                self.led.show_number(s, lights.RED, 0.1)
            except:
                pass

        
    def close(self):
        self.lights.all_off() 
        self.buzzer.close()
        self.button.irq = None
        