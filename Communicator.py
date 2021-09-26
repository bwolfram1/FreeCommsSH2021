from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
from adafruit_stmpe610 import Adafruit_STMPE610_SPI
import adafruit_ili9341
import adafruit_lis3mdl
import adafruit_sdcard
import digitalio
import displayio
import neopixel
import storage
import board
import time
import os
import busio
import time
import adafruit_gps
from math import sin, cos, sqrt, atan2, radians, degrees
import math
import adafruit_rfm9x
import adafruit_bme680
from analogio import AnalogIn
from adafruit_display_text.label import Label
from adafruit_display_shapes.rect import Rect

import terminalio
import gc

# spotsu lora unit

# Optional Qwiic test
try:
    import adafruit_pct2075
except Exception as e:
    print('Skipping Qwiic test,', e)

all_passed = True

# ui dimensions
header = 16
margin = 0
border = 0

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10
touch_cs = board.D6
sd_cs = board.D5
neopix_pin = board.D11

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)


#battery voltage reader
vbat_voltage = AnalogIn(board.VOLTAGE_MONITOR)

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D13)
RESET = digitalio.DigitalInOut(board.D12)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.

i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)
gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)
sensor = adafruit_lis3mdl.LIS3MDL(i2c)
sensor2 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

sensor2.seaLevelhPa = 1014.5

gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b'PMTK220,500')

splash = displayio.Group()
hview = displayio.Group()
view1 = displayio.Group()
view2 = displayio.Group()
view3 = displayio.Group()
display.show(splash)

def hideLayer(hide_target):
    try:
        splash.remove(hide_target)
    except ValueError:
        pass

def showLayer(show_target):
    try:
        time.sleep(0.1)
        splash.append(show_target)
    except ValueError:
        pass
# background


def bg_stripe(x, color):
    width = display.width
    color_bitmap = displayio.Bitmap(width, 240, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = color
    bg_sprite = displayio.TileGrid(
        color_bitmap, x=x*width, y=0, pixel_shader=color_palette)
    splash.append(bg_sprite)


bg_stripe(0, 0x000000)

# output rect
output_rect = Rect(margin, margin, display.width-margin*2, display.height -
                   margin*2-header-margin, fill=0x000000, outline=0x000000)
hview.append(output_rect)

# output header
header_rect = Rect(margin + border, margin+border,
                   display.width-(margin+border)*2+10, header, fill=0x00FF00)
hview.append(header_rect)

def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2


battery_voltage = get_voltage(vbat_voltage)
battery_level = "{:.2f}".format(battery_voltage)

header_text = Label(terminalio.FONT, text="  shellhacks                               Bat:" + battery_level,
                    x=margin * 2+border, y=int(margin+border+header/2), color=0x000000)
hview.append(header_text)
splash.append(hview)

target_lat = 27.96182
target_lon = -82.463387

# GPS timing stuff
timestamp = time.monotonic()
last_print = time.monotonic()

TABS_X = 5
TABS_Y = 30
TAB_M = 15

label1 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label1.x = TABS_X
label1.y = TABS_Y+(TAB_M*0)
view1.append(label1)

label2 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label2.x = TABS_X
label2.y = TABS_Y+(TAB_M*1)
view1.append(label2)

label3 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label3.x = TABS_X
label3.y = TABS_Y+(TAB_M*2)
view1.append(label3)

label4 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label4.x = TABS_X
label4.y = TABS_Y+(TAB_M*3)
view1.append(label4)

label5 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label5.x = TABS_X
label5.y = TABS_Y+(TAB_M*4)
view1.append(label5)

label6 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label6.x = TABS_X
label6.y = TABS_Y+(TAB_M*5)
view1.append(label6)

label7 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label7.x = TABS_X
label7.y = TABS_Y+(TAB_M*6)
view1.append(label7)

label8 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label8.x = TABS_X
label8.y = TABS_Y+(TAB_M*7)
view1.append(label8)

label9 = Label(terminalio.FONT, text="", color=0xFFFFFF)
label9.x = TABS_X
label9.y = TABS_Y+(TAB_M*8)
view1.append(label9)

def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

# Also from the Adafruit compass sample
def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)

# Awesome public domain compass bearing code from Jérôme Renard
# https://gist.github.com/jeromer/2005586
def calculate_initial_compass_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

# Rough Calculation of distance (in meters)
# https://janakiev.com/blog/gps-points-distance-python/
def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))


showLayer(view1)
hideLayer(view2)
hideLayer(view3)
display.show(splash)

p = displayio.Palette(2)
p.make_transparent(0)
p[1] = 0xFFFFFF

w, h = terminalio.FONT.get_bounding_box()

tilegrid = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=p, x=margin*2+border, y=int(
    margin+border+header+margin/2), width=48, height=15, tile_width=w, tile_height=h)
term = terminalio.Terminal(tilegrid, terminalio.FONT)
view2.append(tilegrid)


# input textarea
input_rect = Rect(margin, display.height-header-3,
                  display.width, header, fill=0x000000, outline=0x000000)
view2.append(input_rect)

# input text
input_text = Label(terminalio.FONT, text='', x=margin*2+border,
                   y=int(display.height-margin-border-header*0.7), color=0xFFFFFF, max_glyphs=50)
view2.append(input_text)

# carret
carret = Rect(input_text.x + input_text.bounding_box[2] + 1, int(
    display.height-margin-header/2-header/4), 1, header//2, fill=0xFFFFFF)
view2.append(carret)

tilegrid2 = displayio.TileGrid(terminalio.FONT.bitmap, pixel_shader=p, x=margin*2+border, y=int(
    margin+border+header+margin/2), width=48, height=15, tile_width=w, tile_height=h)
term2 = terminalio.Terminal(tilegrid2, terminalio.FONT)
view3.append(tilegrid2)

rfm9x.send(bytes("shellhacks online - commlink open\r\n", "utf-8"))
term.write("shellhacks online - commlink open\r\n")

carret_blink_time = time.monotonic()
carret_blink_state = True

bat_refresh_time = time.monotonic()
bat_refresh_state = True

pixels = neopixel.NeoPixel(neopix_pin, 1)

run = 1

while True:
    key_count = kbd.key_count
    counter = 0
    packet = None
    packet = rfm9x.receive()
    pixels[0] = [0, 0, 0]

    if packet is None:
        pixels[0] = [0, 0, 0]
        kbd.backlight = 0.5
    else:
        try:
            packet_text = str(packet, "ascii")
        except:
            packet_text = "incoming non-ascii message"
        rssi = rfm9x.last_rssi

        term.write("{0}".format(
            packet_text) + "\n \r".format(rssi))

        if packet_text == "hello":
            print("hello")
    if time.monotonic() - carret_blink_time >= 0.01:
        if carret_blink_state:
            view2.remove(carret)
        else:
            view2.append(carret)

        carret_blink_state = not carret_blink_state
        carret_blink_time = time.monotonic()


    if key_count > 0:
        key = kbd.key
        state = 'pressed'
        if key[0] == STATE_LONG_PRESS:
            state = 'held down'
        elif key[0] == STATE_RELEASE:
            state = 'released'
        print("key: '%s' (dec %d, hex %02x) %s" % (key[1], ord(key[1]), ord(key[1]), state))
        if key[0] == STATE_PRESS:
            if key[1] == '\x08':  # Backspace
                if len(input_text.text) > 0:
                    input_text.text = input_text.text[:-1]
            elif key[1] == '\n':
                text = 'sh:' + input_text.text
                rfm9x.send(bytes(text, "utf-8"))
                term.write(text.encode('utf-8') + '\n \r')

                input_text.text = ''
            else:  # Anything else, we add to the text field
                input_text.text += key[1]

            carret.x = input_text.x + input_text.bounding_box[2] + 1
        if ord(key[1]) == 7:
            hideLayer(view1)
            showLayer(view2)
            hideLayer(view3)
        if ord(key[1]) == 18 and state == 'pressed':
            hideLayer(view1)
            hideLayer(view2)
            showLayer(view3)
            term2.write('Temperature: {} degrees C \n \r'.format(sensor2.temperature))
            term2.write('Gas: {} ohms \n \r'.format(sensor2.gas))
            term2.write('Humidity: {}% \n \r'.format(sensor2.humidity))
            term2.write('Pressure: {}hPa \n \r'.format(sensor2.pressure))
            term2.write('Altitude: {} meters \n \r'.format(sensor2.altitude))
            term2.write('\n \r')

        if ord(key[1]) == 18 and state == 'held down':
            if gps.has_fix:
                vals = "{:.2f} {:.2f} {:.2f} {:.2f} {:.2f}".format(gps.latitude, gps.longitude, sensor2.temperature, sensor2.humidity, sensor2.pressure)
            else:
                vals = "{:.2f} {:.2f} {:.2f}".format(sensor2.temperature, sensor2.humidity, sensor2.pressure)
            rfm9x.send(bytes(vals, "utf-8"))
            term2.write("LoRa Sent \n \r")
        if ord(key[1]) == 6 and state == 'pressed':
            showLayer(view1)
            hideLayer(view2)
            hideLayer(view3)
        if ord(key[1]) == 6 and state == 'held down':
            latmenux1 = True
            lonmenux1 = True
            gpsmenu_target = True
            gpsmenu_stats = True

            while gpsmenu_target is True:
                label1.text = "--Target Coordinates--"
                label2.text = ""
                label3.text = "Lat: {:.5f}".format(target_lat)
                label4.text = "Lon: {:.5f}".format(target_lon)
                label5.text = ""
                label6.text = ""
                label7.text = ""
                label8.text = ""
                label9.text = "L1=Next"
                key_count = kbd.key_count
                if key_count > 0:
                    key = kbd.key
                if ord(key[1]) == 17:
                    print("L1 pressed")
                    counter = 1
                    gpsmenu_target = False
            while gpsmenu_stats is True:
                gps.update()
                current = time.monotonic()
                if current - last_print >= 1.0:
                    last_print = current
                label1.text = "--GPS Info--"
                label2.text = ""
                label3.text = "Lat: {:.5f}".format(gps.latitude)
                label4.text = "Long: {:.5f}".format(gps.longitude)
                label5.text = "GPS Sat#: {}".format(gps.satellites)
                label6.text = "Altitude: {:.5f}".format(gps.altitude_m)
                label7.text = "Track Angle: {:.5f}".format(gps.track_angle_deg)
                label8.text = "{}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,   # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,   # month!
                gps.timestamp_utc.tm_sec)
                label9.text = "L1=Next"
                key_count = kbd.key_count
                if key_count > 0:
                    key = kbd.key
                    state = 'pressed'
                    if key[0] == STATE_LONG_PRESS:
                        state = 'held down'
                    elif key[0] == STATE_RELEASE:
                        state = 'released'
                print("key: '%s' (dec %d, hex %02x) %s" % (key[1], ord(key[1]), ord(key[1]), state))
                if ord(key[1]) == 17 and state == 'pressed':
                    gpsmenu_stats = False
            while latmenux1 is True:
                label1.text = "Set Target Lat."
                label2.text = "Current-Lat: {:.5f}".format(target_lat)
                label3.text = "Current-Lon: {:.5f}".format(target_lon)
                label4.text = " "
                label5.text = "New-Lat: "
                label6.text = ""
                label7.text = "New-Lon: "
                label8.text = " "
                label9.text = "L1=Next"
                key_count = kbd.key_count
                if key_count > 0:
                    key = kbd.key
                    state = 'pressed'
                    if key[0] == STATE_LONG_PRESS:
                        state = 'held down'
                    elif key[0] == STATE_RELEASE:
                        state = 'released'
                if ord(key[1]) == 17 and state == 'pressed':
                    latmenux1 = False


    gps.update()
    current = time.monotonic()

    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            label1.text = "Waiting for fix"
            continue
        label1.text = "Navigator"
        label2.text = ""
        current_pos = (gps.latitude, gps.longitude)
        target_pos = (target_lat, target_lon)
        label3.text = "Current Heading:"
        label4.text = " {:.2f} degrees".format(get_heading(sensor))
        label5.text = "Target Heading:"
        label6.text = " {:.1f} deg".format(calculate_initial_compass_bearing(current_pos,target_pos))
        label7.text = "Target Distance"
        label8.text = " {:.1f} meters".format(haversine(current_pos,target_pos))
        label9.text = "A=Toggle Display"