from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from conversion import *
# client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
IP_ADDRESS = "192.168.1.145"
PORT = 502
client = ModbusTcpClient(IP_ADDRESS, port=PORT)
if client.connect():
    print("Connected to modbus device!")
    
def write_single():
    register = int(input("Enter your register: "))
    value = int(input("Enter a value: "))
    client.write_register(address=register, value=value)
    response = client.read_holding_registers(address=register, count=8)
    high_word = response.registers[0]
    # value_2 = int(input("Enter a value: "))
    # client.write_register(address=register + 1, value=value_2)
    response_2 = client.read_holding_registers(address=register + 1, count=8)
    low_word = response_2.registers[0]
    
    combined_value = (low_word << 16) | high_word
    
    print(high_word, low_word)    
    print(combined_value)
def write_double():
    register = int(input("Enter register: "))
    combined_value = int(input("Enter value: "))
    packed = struct.pack('i', combined_value)
    low_word, high_word = struct.unpack('HH', packed)
    client.write_register(address=register, value=low_word)
    client.write_register(address=register + 1, value=high_word)
    
write_double()