from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)

if client.connect():
    print("Connected to modbus device!")
    
    register = int(input("Enter your register: ")) - 1
    value = int(input("Enter the value you want to write: "))
    
    response = client.write_register(address=register, value=value)
    
    print(response.registers[0])
