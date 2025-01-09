from pymodbus.client import ModbusTcpClient

# Replace with your Modbus server's IP and port
IP_ADDRESS = "192.168.1.145"  # Modbus server's IP
# IP_ADDRESS = "192.168.1.16"
PORT = 502  # Default Modbus TCP port

# Initialize Modbus TCP client
client = ModbusTcpClient(IP_ADDRESS, port=PORT)

# Connect to the Modbus server
if client.connect():
    # Read 8 holding registers starting from address 6096
    response = client.read_holding_registers(address=6096, count=8)
    if response.isError():
        print(f"Error: {response}")
    else:
        print(f"Registers: {response.registers}")
else:
    print("Failed to connect to Modbus TCP server.")

# Close the client connection
client.close()
