# listen for udp packet on port 4444 and print the data

import socket
import struct
import time
import serial

struct_format = "I4sHBcffffffIIf fff16s16si"
UDP_IP = "127.0.0.1"
UDP_PORT = 4444

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

serial_port = serial.Serial("COM16", 115200, timeout=0)

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
    # serial_port.flush()
    serial_port.read_all()


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
