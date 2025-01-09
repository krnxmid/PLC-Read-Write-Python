from pymodbus.client import ModbusSerialClient
import pika
import time

# Connection parameters
connection_params = pika.ConnectionParameters(host='65.0.237.181', 
                                               credentials=pika.PlainCredentials('plc_user', 'plc_password'))

# Establish connection
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
# Declare the exchange
channel.exchange_declare(exchange='plc_data_exchange', exchange_type='direct', durable=True)

try:
    while True:
        if client.connect():
            print("Connected to modbus device!")
            register = 4294 - 1
                       
            # register = int(input("Enter your register: ")) - 1
            response = client.read_holding_registers(address=register, count=8)
            body=str(response.registers[0]) 
            channel.basic_publish(exchange='plc_data_exchange', routing_key='plc_data', body=body)
            print(f"Sent: {body}")
            time.sleep(5)  # Send a message every 2 seconds
except KeyboardInterrupt:
    print("Stopped sending messages.")
finally:
    connection.close()
