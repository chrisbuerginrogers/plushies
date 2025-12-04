import time
import asyncio
import json

from collections import deque

import utilities.utilities as utilities
import utilities.lights as lights
import utilities.now as now
import utilities.i2c_bus as i2c_bus
import utilities.base64 as base64
from utilities.colors import *

from games.sound import Notes
from games.shake import Shake
from games.jump import Jump
from games.hotcold import Hot_cold
from games.clap import Clap
from games.rainbow import Rainbow
from games.hibernate import Hibernate

class Stuffie:
    def __init__(self):
        self.mac = None
        self.espnow = None

        self.game = -1
        self.running = False
        self.topic = ''
        self.value = -1
        self.task = None
        self.hidden_gem = None
        self.queue = deque([], 20)

        self.lights = lights.Lights()
        self.lights.default_color = GREEN
        self.lights.default_intensity = 0.1
        self.lights.all_off()
        
        self.accel = i2c_bus.LIS2DW12()
        self.battery = i2c_bus.Battery()
        self.button = utilities.Button()
        self.buzzer = utilities.Buzzer()
        self.buzzer.stop()
        self.hibernate = utilities.Hibernate()
        
        self.game_names = [Notes(self), Shake(self), Hot_cold(self), Jump(self), Clap(self), Rainbow(self), Hibernate(self)]
        self.response_times = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

    def startup(self):
        print('Starting up')
        self.lights.on(0)
        self.espnow = now.Now(self.now_callback)
        self.espnow.connect(True)
        self.lights.on(1)
        self.mac = self.espnow.wifi.config('mac')
        print('my mac address is ',[hex(b) for b in self.mac])
        self.lights.on(2)
        
    async def start_game(self, number):
        if number < 0 or number >= len(self.game_names):
            print('illegal game number')
            return
        if self.game == number:
            print(f'notify {number}')
            self.topic = '/notify'
            return
        print('starting game ', number)
        self.lights.on(3)
        self.running = True
        self.game = number
        self.task = asyncio.create_task(self.game_names[number].run(self.response_times[number]))
        print(f'started {number}')
        
    async def stop_game(self, number):
        print(f'trying to stop {number}')
        self.running = False
        await self.task

    def close(self):
        if self.game >= 0:
            self.stop_game(self.game)
        if self.espnow: self.espnow.close()
        self.lights.all_off()
        self.buzzer.stop()

    def now_callback(self, msg, mac, rssi):
        self.queue.append((mac, msg, rssi))
            
    def pop_queue(self):
        if not len(self.queue):
            return
        try:
            (mac, msg, rssi) = self.queue.pop()
            payload = json.loads(msg)
            topic = payload['topic']
            value = payload['value']
            print(topic)

            if topic == '/ping':
                self.rssi = rssi
                return
            else:
                print(mac, msg, rssi)
                self.execute_queue(topic, value, self.game)
            
        except Exception as e:
            print(e)
                

    async def execute_queue(self, topic, value, game):
        print('running queue', topic, value, game)
        try:
            if topic == "/gem":  #do this here because you do not want to miss it
                bytes_from_string = value.encode('ascii')
                gem_mac = base64.b64decode(bytes_from_string)
                print('hidden gem = ',gem_mac)
                self.hidden_gem = gem_mac
            
            if topic == '/game':
                print('who knows ',value,game)
                if value != game:
                    print('Game ',value)
                    if game >= 0:
                        await self.stop_game(game)
                    #self.game = self.value
                    if value >= 0:
                        print('starting game ',value)
                        self.start_game(value)
            self.topic =  topic
            self.value = value
        except Exception as e:
            print(e)
                    
    async def main(self):
        try:
            self.startup()
            self.start_game(0)
            while self.game >= 0:
                print(len(self.queue),' ',end='')
                while len(self.queue):
                    await self.pop_queue()
                await asyncio.sleep(0.5)
        except Exception as e:
            print('main error: ',e)
        finally:
            print('main shutting down')
            self.close()
   
   
me = Stuffie()
        
asyncio.run(me.main())
    
     