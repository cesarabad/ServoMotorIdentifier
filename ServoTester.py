import serial
import time

PORT = "/dev/servo_rs485"   # o /dev/ttyACM0
BAUDRATE = 38400

SERVO1_ID = 1
SERVO2_ID = 2


def degrees_to_pos(deg):
    # muchos servos de bus usan 0-1000 para 0-240 grados aprox
    return int((deg / 240.0) * 1000)


def build_packet(servo_id, position, time_ms):
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF

    time_low = time_ms & 0xFF
    time_high = (time_ms >> 8) & 0xFF

    packet = [
        0x55, 0x55,
        servo_id,
        7,
        1,  # MOVE command
        pos_low,
        pos_high,
        time_low,
        time_high
    ]

    checksum = (~sum(packet[2:]) + 1) & 0xFF
    packet.append(checksum)

    return bytearray(packet)


def move_servo(ser, servo_id, deg, time_ms):
    pos = degrees_to_pos(deg)
    packet = build_packet(servo_id, pos, time_ms)
    ser.write(packet)


def main():

    ser = serial.Serial(PORT, BAUDRATE, timeout=1)

    print("Moviendo servos...")

    # velocidad máxima → tiempo mínimo
    move_servo(ser, SERVO1_ID, 100, 0)
    move_servo(ser, SERVO2_ID, 30, 0)

    time.sleep(5)

    print("Volviendo a 0...")

    move_servo(ser, SERVO1_ID, 0, 0)
    move_servo(ser, SERVO2_ID, 0, 0)

    ser.close()


if __name__ == "__main__":
    main()