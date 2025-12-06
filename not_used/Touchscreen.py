# https://github.com/dobodu/Lilygo_Waveshare_Amoled_Micropython/tree/main
# https://www.waveshare.com/product/arduino/displays/amoled/esp32-s3-touch-amoled-1.8.htm

from machine import SoftI2C, Pin
import config.WS_180_AMOLED as disp
import time

# ===== Display Setup =====
display = disp.display
display.reset()
display.init()
display.rotation(3)
display.brightness(255)
display.fill(0)
#display.jpg("/bmp/smiley_small.jpg", 10, 50)

# ===== Pin Setup =====
touch_int = Pin(19, Pin.IN, Pin.PULL_UP)  # Touch interrupt
boot_button = Pin(0, Pin.IN, Pin.PULL_UP)  # BOOT button (lower)

# ===== I2C Device Addresses =====
TOUCH_WIDTH = 368
TOUCH_HEIGHT = 448
FT3168_ADDR = 0x38      # Touch controller
TCA9554_ADDR = 0x20     # GPIO expander (or 0x34)
PWR_BUTTON_PIN = 4      # EXIO4 on the expander

def read_i2c_quick(address, register, num_bytes):
    """Quick I2C read - may fail due to GPIO 14 conflict"""
    try:
        i2c = SoftI2C(scl=Pin(14), sda=Pin(15), freq=400000, timeout=10000)
        return i2c.readfrom_mem(address, register, num_bytes)
    except:
        return None

def read_touch_coords():
    """Read touch coordinates from FT3168"""
    data = read_i2c_quick(FT3168_ADDR, 0x02, 1)
    if data and data[0] > 0:
        touch_data = read_i2c_quick(FT3168_ADDR, 0x03, 4)
        if touch_data:
            x_raw = ((touch_data[0] & 0x0F) << 8) | touch_data[1]
            y_raw = ((touch_data[2] & 0x0F) << 8) | touch_data[3]
            x = TOUCH_WIDTH - x_raw
            y = TOUCH_HEIGHT - y_raw
            return (True, x, y)
    return (False, 0, 0)

def read_pwr_button():
    """Read PWR button state from GPIO expander (active HIGH)"""
    # TCA9554 input register is 0x00
    data = read_i2c_quick(TCA9554_ADDR, 0x00, 1)
    if data:
        # Check bit 4 (EXIO4)
        return (data[0] >> PWR_BUTTON_PIN) & 0x01
    return 0

# ===== Main Loop =====
print("Ready! Touch screen or press buttons")
print("BOOT button (lower) = Clear screen")
print("PWR button (upper) = Change brightness")

last_touch_state = 1
last_pwr_state = 0
touch_count = 0
brightness = 255

colors = [
    display.colorRGB(255, 0, 0),    # Red
    display.colorRGB(0, 255, 0),    # Green
    display.colorRGB(0, 0, 255),    # Blue
    display.colorRGB(255, 255, 0),  # Yellow
    display.colorRGB(255, 0, 255),  # Magenta
    display.colorRGB(0, 255, 255),  # Cyan
]

try:
    while True:
        # Check touch interrupt
        touch_state = touch_int.value()
        if touch_state == 0 and last_touch_state == 1:
            touch_count += 1
            success, x, y = read_touch_coords()
            if success:
                color = colors[touch_count % len(colors)]
                print(f"Touch {touch_count}: ({x}, {y})")
                display.fill_circle(x, y, 10, color)
        last_touch_state = touch_state
        
        # Check PWR button (upper button - active HIGH)
        pwr_state = read_pwr_button()
        if pwr_state == 1 and last_pwr_state == 0:
            print("PWR button pressed!")
            # Cycle brightness
            brightness = 100 if brightness == 255 else 255
            display.brightness(brightness)
            print(f"Brightness: {brightness}")
        last_pwr_state = pwr_state
        
        # Check BOOT button (lower button - active LOW)
        if boot_button.value() == 0:
            print("BOOT button pressed - clearing")
            display.fill(0)
            display.jpg("/bmp/smiley_small.jpg", 10, 50)
            touch_count = 0
            time.sleep(0.3)
        
        time.sleep(0.02)
        
except KeyboardInterrupt:
    print("\nStopped")
    display.fill(0)