import time
from pymodbus3.client.sync import ModbusSerialClient  # Correct import for pymodbus3

# Define the serial port and connection parameters
client = ModbusSerialClient(
    method='rtu',  # Specify RTU method
    port='/dev/ttyUSB0',  # Serial port
    baudrate=9600,  # Baud rate
    parity='N',  # No parity
    stopbits=1,  # Stop bits
    bytesize=8,  # Data bits
    timeout=1  # Timeout in seconds
)

# Connect to the Modbus device
if not client.connect():
    print("Failed to connect to Modbus device.")
    exit()

# Retry 3 times with a delay
for _ in range(3):
    try:
        # Specify the unit (Modbus slave address)
        unit = 1  # Change this to your actual slave address
        result = client.read_holding_registers(address=4000, count=1, unit=unit)
        
        if result.isError():
            print(f"Error reading register: {result}")
        else:
            print(f"Register value: {result.registers}")
        
        break  # Exit loop if successful
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)  # Wait for 1 second before retrying

# Close the connection
client.close()
