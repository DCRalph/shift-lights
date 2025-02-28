# listen for udp packet on port 4444 and print the data

import socket
import struct
import time
import serial

struct_format = "I4sHBcffffffIIf fff16s16si"
UDP_IP = "127.0.0.1"
UDP_PORT = 4444

UDP_IP_ADDRESS = "10.99.20.20"
UDP_PORT_NO = 21324
NUM_PIXELS = 120

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

serial_port = serial.Serial("COM7", 115200, timeout=0)

# parse data using the following schema
# unsigned       time;            // time in milliseconds (to check order) // N/A, hardcoded to 0
# char           car[4];          // Car name // N/A, fixed value of "beam"
# unsigned short flags;           // Info (see OG_x below)
# char           gear;            // Reverse:0, Neutral:1, First:2...
# char           plid;            // Unique ID of viewed player (0 = none) // N/A, hardcoded to 0
# float          speed;           // M/S
# float          rpm;             // RPM
# float          turbo;           // BAR
# float          engTemp;         // C
# float          fuel;            // 0 to 1
# float          oilPressure;     // BAR // N/A, hardcoded to 0
# float          oilTemp;         // C
# unsigned       dashLights;      // Dash lights available (see DL_x below)
# unsigned       showLights;      // Dash lights currently switched on
# float          throttle;        // 0 to 1
# float          brake;           // 0 to 1
# float          clutch;          // 0 to 1
# char           display1[16];    // Usually Fuel // N/A, hardcoded to ""
# char           display2[16];    // Usually Settings // N/A, hardcoded to ""
# int            id;              // optional - only if OutGauge ID is specified


def send(msg):
    bytesToSend = bytes([2, 2] + msg)
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.sendto(bytesToSend, (UDP_IP_ADDRESS, UDP_PORT_NO))


num_leds = 120
colors_per_led = 3

# Create an array to represent the LED colors
led_array = [0] * (num_leds * colors_per_led)

# Define the colors for the shift lights
shift_light_colors = [(0, 255, 0), (255, 150, 0), (255, 0, 0)]  # Green  # Yellow  # Red

tachColor = []

for i in range(0, num_leds):
    if i < num_leds / 2:
        tachColor.append(shift_light_colors[0])
    elif i < num_leds * 3 / 4:
        tachColor.append(shift_light_colors[1])
    else:
        tachColor.append(shift_light_colors[2])


lightShiftRPM = []

for i in range(0, num_leds):
    # from 1000 to 6000 over the 120 leds
    lightShiftRPM.append(1000 + (5000 / num_leds) * i)


def set_led_color(led_index, red, green, blue):
    start_index = led_index * colors_per_led
    led_array[start_index] = min(255, max(0, red))
    led_array[start_index + 1] = min(255, max(0, green))
    led_array[start_index + 2] = min(255, max(0, blue))


def update_shift_lights(rpm):
    global limiter_flash

    if rpm > 7500:
        if time.time() % 0.1 > 0.05:
            for i in range(num_leds):
                set_led_color(i, 255, 0, 0)
        else:
            for i in range(num_leds):
                set_led_color(i, 0, 0, 0)

        pass
    elif rpm > 7000:
        if time.time() % 0.1 > 0.05:
            for i in range(num_leds):
                set_led_color(i, 0, 0, 255)
        else:
            for i in range(num_leds):
                set_led_color(i, 0, 0, 0)
    else:
        for i in range(num_leds):
            if rpm > lightShiftRPM[i]:
                set_led_color(i, *tachColor[i])
            else:
                set_led_color(i, 0, 0, 0)


def parseData(data):
    parsed_data = struct.unpack(struct_format, data)

    parsed_struct = {
        "time": parsed_data[0],
        "car": parsed_data[1].decode("utf-8").rstrip("\x00"),
        "flags": parsed_data[2],
        "gear": parsed_data[3],
        "plid": parsed_data[4].decode("utf-8"),
        "speed": round(parsed_data[5], 2) * 3.6,
        "rpm": round(parsed_data[6], 2),
        "turbo": parsed_data[7],
        "engTemp": parsed_data[8],
        "fuel": parsed_data[9],
        "oilPressure": parsed_data[10],
        "oilTemp": parsed_data[11],
        "dashLights": parsed_data[12],
        "showLights": parsed_data[13],
        "throttle": parsed_data[14],
        "brake": parsed_data[15],
        "clutch": parsed_data[16],
        "display1": parsed_data[17].decode("utf-8").rstrip("\x00"),
        "display2": parsed_data[18].decode("utf-8").rstrip("\x00"),
        "id": parsed_data[19],
    }

    # for key, value in parsed_struct.items():
    #     print(f"{key}: {value}")

    # print(
    #     f"Speed: {parsed_struct['speed']} \t rpm {parsed_struct['rpm']} \t gear {parsed_struct['gear']}"
    # )

    rpmString = f"{parsed_struct['rpm']}\n"
    serial_port.write(rpmString.encode("utf-8"))
    serial_port.read_all()

    # update_shift_lights(parsed_struct["rpm"])
    # send(led_array)


start_time = time.time()
packet_count = 0

while True:
    try:
        data, addr = sock.recvfrom(2048)
        # print("received message:", data)
        parseData(data)

        # clear sock buffer
        packet_count += 1
        sock.recv(2048)

    except socket.error:
        # No data received
        pass

    # Print the packet rate every second
    current_time = time.time()
    if current_time - start_time >= 1:
        print(f"Packets per second: {packet_count}")
        packet_count = 0
        start_time = current_time
