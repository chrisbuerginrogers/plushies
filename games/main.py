import time
import asyncio
import json

import utilities.utilities as utilities
import utilities.lights as lights
import utilities.now as now

import games.test1 as test1
import games.test2 as test2
import games.test3 as test3
from games.shake import shake
from games.jump import jump

game_names = [shake, jump, test3]

class Stuffie:
    def __init__(self):
        self.mac = None
        self.espnow = None
        self.lights = lights.Lights()
        self.lights.default_color = lights.GREEN
        self.lights.default_intensity = 0.1
        self.game = None
        self.running = False
        self.topic = ''
        self.value = 0
        
    def now_callback(self, msg, mac, rssi):
        print(mac, msg, rssi)
        try:
            payload = json.loads(msg)
            topic = payload['topic']
            value = payload['value']
            if topic == '/game':
                if value != self.game:
                    if self.game:
                        self.stop_game(self.game)
                    self.game = value
                    if value > 0:
                        self.start_game(value)
        except:
            pass
                
    def startup(self):
        print('Starting up')
        self.lights.on(0)
        self.espnow = now.Now(self.now_callback)
        self.espnow.connect()
        self.lights.on(1)
        self.mac = self.espnow.wifi.config('mac')
        print('my mac address is ',[hex(b) for b in self.mac])
        self.espnow.antenna()
        self.lights.on(2)
        
    def start_game(self, number):
        if number < 0 or number > len(game_names):
            return
        print('starting game ', number)
        self.lights.on(3)
        self.running = True
        self.game = number
        task = asyncio.create_task(game_names[number-1].main(self))
        print(f'started')

    def stop_game(self, number):
        self.running = False
        print('stopping game ', number)

    def close(self):
        if self.game > 0:
            self.stop_game(self.game)
        if self.espnow: self.espnow.close()
        
    async def main(self):
        try:
            self.startup()
            self.start_game(1)
            while self.game > 0:
                await asyncio.sleep(1)
        finally:
            print('shutting down')
            self.close()
   
   
me = Stuffie()
        
asyncio.run(me.main())
    
    