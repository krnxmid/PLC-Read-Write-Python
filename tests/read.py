from pymodbus.client import ModbusSerialClient
import struct
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

if client.connect():
    print("Connected to modbus device!")
    
    register = int(input("Enter your register: "))
    response = client.read_holding_registers(address=register, count=8)
    high_word = response.registers[0]
    response_2 = client.read_holding_registers(address=register + 1, count=8)
    low_word = response_2.registers[0]
    
    combined_value = (low_word << 16) | high_word
    combined_value_2 = (high_word << 16) | low_word
    signed_value = struct.unpack('i', struct.pack('I', combined_value))[0]
    print(high_word, low_word)    
    print(combined_value)
    print(signed_value)
    
client.close()
