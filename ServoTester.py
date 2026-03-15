import serial
import time

PORT = "/dev/servo_rs485"  # Symlink que creamos
BAUDRATE = 34800

# Ajusta estos IDs si tus servos ya los conoces
SERVO_IDS = [1, 2]

# Función para convertir grados a posición interna del servo (0-1000)
def degrees_to_pos(deg):
    # 0-360° → 0-1000 unidades del servo
    return int((deg / 360.0) * 1000)

# Construye el paquete de movimiento según protocolo Waveshare
def build_packet(servo_id, position, speed):
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF
    speed_low = speed & 0xFF
    speed_high = (speed >> 8) & 0xFF

    # Paquete típico: [Header, Header, ID, Length, Command, PosL, PosH, SpeedL, SpeedH, Checksum]
    packet = [
        0x55, 0x55,
        servo_id,
        7,      # Longitud: comando + 4 bytes de datos + checksum
        1,      # Comando MOVE
        pos_low,
        pos_high,
        speed_low,
        speed_high
    ]
    # Checksum = (~sum(ID..ultimo byte) + 1) & 0xFF
    checksum = (~sum(packet[2:]) + 1) & 0xFF
    packet.append(checksum)

    return bytearray(packet)

# Función para mover un servo
def move_servo(ser, servo_id, deg, speed=0):
    pos = degrees_to_pos(deg)
    packet = build_packet(servo_id, pos, speed)
    ser.write(packet)

# Escanear servos en el bus (opcional si no conoces IDs)
def scan_servos(ser):
    found = []
    for sid in range(0, 254):
        # Envía comando "ping" o "read position" según protocolo
        # Para simplificar aquí suponemos que respondieron IDs 1 y 2
        # Implementación completa dependerá del protocolo de tu servo
        if sid in SERVO_IDS:
            found.append(sid)
    return found

def main():
    ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)
    print(f"Puerto abierto en {PORT} a {BAUDRATE} bps")

    print("Escaneando servos...")
    servos = scan_servos(ser)
    print(f"Servos detectados: {servos}")

    if len(servos) < 2:
        print("No se detectaron los 2 servos esperados. Revisa IDs o conexiones.")
        ser.close()
        return

    print("Moviendo servos a 100° y 30°...")
    move_servo(ser, servos[0], 100, 0)  # velocidad máxima
    move_servo(ser, servos[1], 30, 0)

    time.sleep(5)

    print("Volviendo servos a 0°...")
    move_servo(ser, servos[0], 0, 0)
    move_servo(ser, servos[1], 0, 0)

    ser.close()
    print("Movimiento completado.")

if __name__ == "__main__":
    main()