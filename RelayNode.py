import displayio
import time
import board
import busio
import displayio
import digitalio
import terminalio
import adafruit_rfm9x
from adafruit_display_text.label import Label
import adafruit_displayio_sh1107

# can try import bitmap_label below for alternative
from adafruit_display_text import label
import adafruit_displayio_sh1107

displayio.release_displays()
# oled_reset = board.D9

# Use for I2C
i2c = board.I2C()
RADIO_FREQ_MHZ = 915.0

CS = digitalio.DigitalInOut(board.D5)
RESET = digitalio.DigitalInOut(board.D6)

display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)

# Make the display context
splash = displayio.Group(max_size=25)
view1 = displayio.Group(max_size=25)
display.show(splash)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White


text_area = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=8, y=10)
view1.append(text_area)
text_area2 = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=35, y=10)
view1.append(text_area2)
text_area3 = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=60, y=10)
view1.append(text_area3)
text_area4 = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=8, y=25)
view1.append(text_area4)
text_area5 = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=35, y=25)
view1.append(text_area5)
text_area6 = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=70, y=25)
view1.append(text_area6)
splash.append(view1)
rssi = ""
counter = 0

timestamp = time.monotonic()

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
rfm9x.tx_power = 23
r = "N/A"
while True:
    text_area.text = "LoRa"
    text_area2.text = "Node"
    text_area3.text = " #1"
    text_area4.text = "RSSI"
    packet = rfm9x.receive()
    if packet is None:
        # Packet has not been received
        print("Received nothing! Listening again...")
        #text_area5.text = "N/A"
    else:
        counter += 1
        print("Received (raw bytes): {0}".format(packet))
        rssi = rfm9x.last_rssi
        r = str(rssi)
        text_area6.text = str(counter)
        rfm9x.send(packet)
        print("Repeated")
        print("Received signal strength: {0} dB".format(rssi))
    text_area5.text = r