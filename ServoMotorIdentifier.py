import serial
import time

# Cambia esto al puerto correcto de tu adaptador USB TTL
PORT = "/dev/ttyUSB0"  
BAUDRATE = 38400
TIMEOUT = 0.05  # 50 ms, para no leer basura

def checksum(packet):
    """Calcula el checksum según protocolo SCServo"""
    return (~sum(packet[2:]) & 0xFF) & 0xFF

def build_ping(servo_id):
    """Crea paquete de ping para un servo"""
    packet = [0xFF, 0xFF, servo_id, 0x02, 0x01]  # Header + ID + Length + Instruction (Ping)
    packet.append(checksum(packet))
    return bytes(packet)

def is_valid_response(resp):
    """Valida que la respuesta sea correcta"""
    if len(resp) < 6:
        return False
    if resp[0] != 0xFF or resp[1] != 0xFF:
        return False
    # Calcula checksum
    calc = checksum(resp[:len(resp)-1])
    return calc == resp[-1]

def scan_servos():
    found = []
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT) as ser:
            for servo_id in range(1, 255):  # IDs típicos 1–254
                ping = build_ping(servo_id)

                ser.reset_input_buffer()
                ser.write(ping)
                ser.flush()

                time.sleep(0.02)  # espera que responda

                resp = ser.read(6)  # lectura mínima de respuesta

                if is_valid_response(resp):
                    returned_id = resp[2]
                    print(f"Servo encontrado con ID: {returned_id}")
                    found.append(returned_id)

    except serial.SerialException as e:
        print(f"Error abriendo puerto {PORT}: {e}")

    return found

if __name__ == "__main__":
    ids = scan_servos()

    if not ids:
        print("No se encontraron servos")
    else:
        print("\nIDs detectados:", ids)