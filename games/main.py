import time
import asyncio
import json

import utilities.utilities as utilities
import utilities.lights as lights
import utilities.now as now

from games.sound import Notes
from games.shake import Shake
from games.sound import Notes

game_names = [Notes, Shake, Notes, Notes, Notes, Notes]

class Stuffie:
    def __init__(self):
        self.mac = None
        self.espnow = None
        self.lights = lights.Lights()
        self.lights.default_color = lights.GREEN
        self.lights.default_intensity = 0.1
        self.game = -1
        self.running = False
        self.topic = ''
        self.value = -1
        self.task = None
        
    def now_callback(self, msg, mac, rssi):
        print(mac, msg, rssi)
        try:
            payload = json.loads(msg)
            self.topic = payload['topic']
            self.value = payload['value']
            self.rssi = rssi
        except Exception as e:
            print(e)
                
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
        if number < 0 or number >= len(game_names):
            print('illegal game number')
            return
        print('starting game ', number)
        self.lights.on(3)
        self.running = True
        self.game = number
        self.task = asyncio.create_task(game_names[number]().run(self))
        print(f'started {number}')
        
    async def stop_game(self, number):
        print('trying to stop')
        self.running = False
        await self.task

    def close(self):
        if self.game >= 0:
            self.stop_game(self.game)
        if self.espnow: self.espnow.close()

    async def main(self):
        try:
            self.startup()
            self.start_game(0)
            while self.game >= 0:
                print('@',end='')
                if self.topic == '/game':
                    if self.value != self.game:
                        print('Game ',self.value)
                        if self.game >= 0:
                            await self.stop_game(self.game)
                        self.game = self.value
                        if self.value >= 0:
                            print('starting game ',self.value)
                            self.start_game(self.value)

                await asyncio.sleep(1)
        finally:
            print('shutting down')
            self.close()
   
   
me = Stuffie()
        
asyncio.run(me.main())
    
    