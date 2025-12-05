from machine import SoftI2C, Pin, ADC
import time, json
import ubinascii

import  utilities.now as now

ROW = 40
LEFT = 20

class Control:
    def connect(self):
        def my_callback(msg, mac, rssi):
            if not ('/ping' in msg):
                print(mac, msg, rssi)

        self.n = now.Now(my_callback)
        self.n.connect(False)
        self.mac = self.n.wifi.config('mac')
        print(self.mac)
        
    def shutdown(self):
        stop = json.dumps({'topic':'/game', 'value':-1})
        self.n.publish(stop)
        
    def ping(self):
        ping = json.dumps({'topic':'/ping', 'value':1})
        self.n.publish(ping)
        
    def notify(self):
        note = json.dumps({'topic':'/notify', 'value':1})
        self.n.publish(note)
        print('notified')
        
    def choose(self, game):
        encoded_bytes = ubinascii.b2a_base64(self.mac)
        encoded_string = encoded_bytes.decode('ascii')
        time.sleep(0.5)
        mac = json.dumps({'topic':'/gem', 'value':encoded_string})
        self.n.publish(mac)
        time.sleep(0.5)
        setup = json.dumps({'topic':'/game', 'value':game})
        self.n.publish(setup)


class Display:
    def __init__(self):
        import config.WS_180_AMOLED as disp
        import fonts.large as font

        self.display = disp.display
        self.row = 1
        self.last_row = None
        
        self.touch = Pin(19, Pin.IN, Pin.PULL_UP)  # Active LOW when touched
        self.button = Pin(0, Pin.IN, Pin.PULL_UP)
        
        self.background = self.display.colorRGB(0,0,0)
        self.foreground = self.display.colorRGB(255,255,255)

        self.display.reset()
        self.clear_screen()
        self.display.init()
        self.display.rotation(3)
        #self.display.jpg("/bmp/smiley_small.jpg",10,50)
        self.display.brightness(255)
        self.font = font
        self.clear_screen()
        
    def clear_screen(self):
        self.display.fill(self.background)
        self.row = 1
        
    def add_text(self, text):
        self.display.write(self.font, text, LEFT, self.row, self.foreground, self.background) 
        self.row += ROW

    def box_row(self, row):
        #if self.last_row: self.display.rect(0,self.last_row,250,ROW-3,255)
        self.display.rect(2,row*ROW,250,ROW-3,255)
        self.last_row = row
        
    def close(self):
        self.clear_screen()

class Button:
    def __init__(self, pin):
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.button.irq(handler=self.update, trigger=Pin.IRQ_FALLING)
        self.state = 0
        
    def update(self, p):
        accept = False
        start = time.ticks_ms()
        #self.state = 0
        while self.button.value() == 0:
            if time.ticks_ms()-start > 50:
                accept = True
                print("button pressed")
                time.sleep(0.2)
                self.state = 1
               
    def close(self):
        self.button.irq = None

class Controller(Control):
    def __init__(self):
        self.display = Display()
        self.display.clear_screen()
        self.display.add_text("   Rebecca Controller")
        text_length = self.display.display.write_len(self.display.font,"Rebecca Controller")
        self.display.add_text('1: Music')
        self.display.add_text('2: Shake')
        self.display.add_text('3: Hot Cold')
        self.display.add_text('4: Jump')
        self.display.add_text('5: Clap')
        self.display.add_text('6: Rainbow')
        self.display.add_text('7: Shutdown')
        
        self.display.last_row = None
        self.row = 2

if __name__ == '__main__':
    controller = Controller()

    def scroll():
        return 3

    old_scroll_val = 3
    controller.display.box_row(old_scroll_val)
    controller.connect()

    i = 0
    while True:
        i += 1
        time.sleep(0.1)
        #if i%10 == 1: controller.ping()
        controller.ping()
        
        scroll_val = scroll()
        controller.display.box_row(scroll_val)
        select = int(scroll_val/10)
        
        '''
        if scroll_val != old_scroll_val:
            if controller.button_select.state == 1:
                controller.button_select.state = 0
                
                print('select ', select)
                controller.choose(select)

                time.sleep(1)
                old_scroll_val = scroll_val
                
        else:
            if controller.button_select.state == 1:
                controller.button_select.state = 0

                print('select again ', select)
                controller.choose(select)
'''