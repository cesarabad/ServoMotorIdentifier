import serial
import time
import struct

# Configuración del puerto
PORT = "/dev/ServoMotors"  # Cambia según tu adaptador
BAUDRATE = 38400
TIMEOUT = 0.05

# Construye el checksum del paquete
def checksum(packet):
    return (~sum(packet[2:]) & 0xFF) & 0xFF

# Construye paquete de ping (opcional)
def build_ping(servo_id):
    packet = [0xFF, 0xFF, servo_id, 0x02, 0x01]  # HEADER + ID + LENGTH + INSTRUCTION(PING)
    packet.append(checksum(packet))
    return bytes(packet)

# Construye paquete para mover servo a posición (0–4095)
def build_write_position(servo_id, position):
    # SCServo usa posición en 2 bytes (little endian)
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF
    packet = [0xFF, 0xFF, servo_id, 0x05, 0x03, pos_low, pos_high]  # WRITE instruction
    packet.append(checksum(packet))
    return bytes(packet)

# Construye paquete para leer posición
def build_read_position(servo_id):
    # Leer 2 bytes de posición desde registro 0x2A
    packet = [0xFF, 0xFF, servo_id, 0x04, 0x02, 0x2A, 0x02]  # READ instruction
    packet.append(checksum(packet))
    return bytes(packet)

# Valida respuesta
def is_valid_response(resp):
    if len(resp) < 6:
        return False
    if resp[0] != 0xFF or resp[1] != 0xFF:
        return False
    calc = checksum(resp[:len(resp)-1])
    return calc == resp[-1]

# Extrae la posición de la respuesta
def extract_position(resp):
    if len(resp) < 8:
        return None
    return resp[5] | (resp[6] << 8)

# Escanea IDs probando moverlos a 50
def scan_servos_by_moving(target_position=50):
    found = []
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            for servo_id in range(1, 255):
                # Enviar comando de mover
                move_packet = build_write_position(servo_id, target_position)
                ser.reset_input_buffer()
                ser.write(move_packet)
                ser.flush()
                time.sleep(0.05)  # espera que se mueva

                # Leer posición
                read_packet = build_read_position(servo_id)
                ser.write(read_packet)
                ser.flush()
                time.sleep(0.02)
                resp = ser.read(8)  # respuesta esperada

                if is_valid_response(resp):
                    pos = extract_position(resp)
                    if pos == target_position:
                        print(f"Servo válido con ID: {servo_id}, posición: {pos}")
                        found.append(servo_id)

    except serial.SerialException as e:
        print(f"Error abriendo puerto {PORT}: {e}")

    return found

if __name__ == "__main__":
    ids = scan_servos_by_moving(50)
    if not ids:
        print("No se encontraron servos válidos")
    else:
        print("\nIDs detectados y válidos:", ids)