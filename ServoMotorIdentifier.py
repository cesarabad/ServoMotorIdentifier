import time
import serial

PORT = "/dev/servo_rs485"  # tu symlink
BAUDRATE = 34800

ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)

def build_ping_packet(servo_id):
    # Comando 0x15 = “Read position” / ping (depende del protocolo exacto)
    packet = [0x55, 0x55, servo_id, 3, 0x15]  # longitud y comando
    checksum = (~sum(packet[2:]) + 1) & 0xFF
    packet.append(checksum)
    return bytearray(packet)

def scan_servos(ser):
    found = []
    for sid in range(0, 254):
        packet = build_ping_packet(sid)
        ser.write(packet)
        time.sleep(0.02)  # espera breve para que responda
        if ser.in_waiting:
            resp = ser.read(ser.in_waiting)
            if resp:
                print("Servo detectado: ", sid)
                found.append(sid)
    return found

servo_ids = scan_servos(ser)
print("Servos detectados:", servo_ids)