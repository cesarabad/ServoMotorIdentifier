import serial
import time

PORT = "/dev/ServoMotors" 
BAUDRATE = 38400  

def checksum(packet):
    return (~sum(packet[2:]) & 0xFF)

def build_ping(servo_id):
    packet = [0xFF, 0xFF, servo_id, 0x02, 0x01]
    packet.append(checksum(packet))
    return bytes(packet)

def scan_servos():
    found = []

    with serial.Serial(PORT, BAUDRATE, timeout=0.02) as ser:
        for servo_id in range(0, 254):
            ping = build_ping(servo_id)

            ser.reset_input_buffer()
            ser.write(ping)

            time.sleep(0.01)

            resp = ser.read(6)

            if len(resp) >= 6 and resp[0] == 0xFF and resp[1] == 0xFF:
                returned_id = resp[2]
                print(f"Servo encontrado con ID: {returned_id}")
                found.append(returned_id)

    return found


if __name__ == "__main__":
    ids = scan_servos()

    if not ids:
        print("No se encontraron servos")
    else:
        print("\nIDs detectados:", ids)