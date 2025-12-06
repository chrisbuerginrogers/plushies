from machine import SoftI2C, Pin, ADC
import time, json
import ubinascii

import  utilities.now as now

ROW = 40
LEFT = 20

# ===== I2C Device Addresses =====
TOUCH_WIDTH = 368
TOUCH_HEIGHT = 448
FT3168_ADDR = 0x38      # Touch controller
TCA9554_ADDR = 0x20     # GPIO expander (or 0x34)
PWR_BUTTON_PIN = 4      # EXIO4 on the expander

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
        if row < 1 or row > 7:
            return
        if self.last_row: self.display.rect(2,self.last_row*ROW,250,ROW-3,0)
        self.display.rect(2,row*ROW,250,ROW-3,255)
        self.last_row = row
        
    def read_i2c_quick(self,address, register, num_bytes):
        """Quick I2C read - may fail due to GPIO 14 conflict"""
        try:
            i2c = SoftI2C(scl=Pin(14), sda=Pin(15), freq=400000, timeout=10000)
            return i2c.readfrom_mem(address, register, num_bytes)
        except:
            return None

    def read_touch_coords(self):
        """Read touch coordinates from FT3168"""
        data = self.read_i2c_quick(FT3168_ADDR, 0x02, 1)
        if data and data[0] > 0:
            touch_data = self.read_i2c_quick(FT3168_ADDR, 0x03, 4)
            if touch_data:
                x_raw = ((touch_data[0] & 0x0F) << 8) | touch_data[1]
                y_raw = ((touch_data[2] & 0x0F) << 8) | touch_data[3]
                x = TOUCH_WIDTH - x_raw
                y = TOUCH_HEIGHT - y_raw
                return (True, x, y)
        return (False, 0, 0)

    def read_pwr_button(self):
        """Read PWR button state from GPIO expander (active HIGH)"""
        # TCA9554 input register is 0x00
        data = self.read_i2c_quick(TCA9554_ADDR, 0x00, 1)
        if data:
            # Check bit 4 (EXIO4)
            return (data[0] >> PWR_BUTTON_PIN) & 0x01
        return 0
        
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
    controller.connect()
    
    last_touch_state = 1
    last_pwr_state = 0
    touch_count = 0
    i = 0
    select = 0
    
    while True:
        i += 1
        time.sleep(0.1)
        #if i%10 == 1: controller.ping()
        controller.ping()
        
        touch_state = controller.display.touch.value()
        if touch_state == 0 and last_touch_state == 1:
            touch_count += 1
            success, x, y = controller.display.read_touch_coords()
            if success:
                #print(f"Touch {touch_count}: ({x}, {y})")
                controller.display.box_row(int(y/ROW))
                select = int(y/ROW)-1
                print('boxed ',select)
        last_touch_state = touch_state
        
        # Check PWR button (upper button - active HIGH)
        pwr_state = controller.display.read_pwr_button()
        if pwr_state == 1 and last_pwr_state == 0:
            print("PWR button pressed!")
        last_pwr_state = pwr_state
        
        # Check BOOT button (lower button - active LOW)
        if controller.display.button.value() == 0:
            print('select ', select)
            controller.choose(select)
            time.sleep(0.3)
        
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