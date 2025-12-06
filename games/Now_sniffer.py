from machine import SoftI2C, Pin, ADC
import time, json
import ubinascii
from collections import deque
import asyncio

import  utilities.now as now
from games.controller import Control
from games.controller_ws import Display

class Controller(Control):
    def __init__(self):
        self.display = Display()
        self.display.clear_screen()
        self.display.add_text("      Now Sniffer")
        
        self.queue = deque([], 20)
        self.topics = {}
        
    def connect(self):
        def my_callback(msg, mac, rssi):
            self.queue.append((mac, msg, rssi))
            if not ('/ping' in msg):
                print(mac, msg, rssi)

        self.n = now.Now(my_callback)
        self.n.connect(False)
        self.mac = self.n.wifi.config('mac')
        print('MAC: ',self.mac)

    async def pop_queue(self):
        if not len(self.queue):
            return
        try:
            (mac, msg, rssi) = self.queue.pop()
            payload = json.loads(msg)
            topic = payload['topic']
            value = payload['value']
            num = 1
            if topic in self.topics.keys():
                num = 1 + self.topics[topic][1]
            
            self.topics[topic] = (value,num)
        except Exception as e:
            print('pop error ',e)


class Sniffer:
    def __init__(self):
        self.controller = Controller()

    async def main(self):
        try:
            self.controller.connect()
            while True:
                await asyncio.sleep(0.1)
                if not len(self.controller.queue): continue
                
                print(len(self.controller.queue),' ',end='')
                while len(self.controller.queue):
                    await self.controller.pop_queue()
                self.controller.display.row = 1
                self.controller.display.add_text("      Now Sniffer")
                for s in self.controller.topics.items():
                    self.controller.display.add_text(f'{s[0]}: {s[1][0]}  {s[1][1]}')
                
        except Exception as e:
            print('main error: ',e)
        finally:
            print('main shutting down')
   
me = Sniffer()
        
asyncio.run(me.main())
    