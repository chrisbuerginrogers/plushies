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
        
        self.button = Pin(0, Pin.IN, Pin.PULL_UP)
        
        self.queue = deque([],1000)
        self.topics = {}
        
    def connect(self):
        def my_callback(msg, mac, rssi):
            try:
                self.queue.append((msg, mac, rssi))
            except Exception as e:
                print(f"Callback error: {e}")
        
        self.n = now.Now(my_callback)
        self.n.connect(False)
        self.mac = self.n.wifi.config('mac')
        print('MAC: ',self.mac)

    async def pop_queue(self):
        if not len(self.queue):
            return
        try:
            (msg, mac, rssi) = self.queue.popleft()
            if not ('/ping' in msg): print(mac, msg, rssi)
            payload = json.loads(msg)
            topic = payload['topic']
            value = payload['value']
            num = 1
            if topic in self.topics.keys():
                num = 1 + self.topics[topic][1]
            
            self.topics[topic] = (value,num)
            #print(self.topics[topic])
        except Exception as e:
            print('pop error ',e)


class Sniffer:
    def __init__(self):
        self.controller = Controller()

    async def main(self):
        try:
            self.controller.connect()
            last_update = 0
            update = 1.0  # Update display every 1 sec

            while self.controller.display.button.value() != 0:
                if not len(self.controller.queue): continue
                
                print(len(self.controller.queue),' ',end='')
                j=0
                while len(self.controller.queue):
                    await self.controller.pop_queue()

                # Update display only every ~1 second
                current = time.time()
                if current - last_update >= update:
                    self.controller.display.clear_screen()
                    self.controller.display.add_text("      Now Sniffer")
                    for s in self.controller.topics.items():
                        self.controller.display.add_text(f'{s[0]}: {s[1][0]}  {s[1][1]}')
                    last_update = current
            else:
                await asyncio.sleep(0)  # Yield to event loop when nothing to do


        except Exception as e:
            print('main error: ',e)
        finally:
            print('main shutting down')
   
me = Sniffer()
        
asyncio.run(me.main())
    