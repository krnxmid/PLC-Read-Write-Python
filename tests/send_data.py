	from pymodbus.client import ModbusSerialClient
import pika
import time

GL_TAGS = [
    ("tag_1", 4296, 10),
    ("tag_2", 4306, 1, "Signed"),
    ("tag_3", 4308, 2, "Signed"),
    ("tag_4", 4310, 1, "Signed"),
    ("tag_5", 4312, 2, "Signed"),
    ("tag_6", 4314, 1, "Signed"),
    ("tag_7", 4316, 1, "Signed"),
    ("tag_8", 4318, 1, "Signed"),
    ("tag_9", 4320, 2, "Signed"),
    ("tag_10", 4322, 1, "Signed"),
    ("tag_11", 4324, 1, "Signed"),
    ("tag_12", 4326, 10),
    ("tag_13", 4336, 2, "Unsigned"),
    ("tag_14", 4338, 1, "Unsigned"),
    ("tag_15", 4340, 1, "Signed"),
    ("tag_16", 4342, 1, "Signed"),
    ("tag_17", 4344, 1, "Signed"),
    ("tag_18", 4346, 1, "Signed"),
    ("tag_19", 4348, 1, "Signed"),
    ("tag_20", 4350, 1, "Signed"),
]

# Connection parameters
connection_params = pika.ConnectionParameters(host='65.0.237.181', credentials=pika.PlainCredentials('plc_user', 'plc_password'))
# Establish connection
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, timeout=1)
# Declare the exchange
channel.exchange_declare(exchange='plc_data_exchange', exchange_type='direct', durable=True)

try:
    while True:
        tag_values_combined = []
        if client.connect():
            print("[*] Modbus connection successful!")
            for tag in GL_TAGS:
                tag_name = tag[0]
                tag_address = tag[1]
                tag_count = tag[2]

                if len(tag) > 3:
                    tag_type = tag[3]

                response = client.read_holding_registers(address=tag_address, count=tag_count)
                value = response.registers[0]

                combined = (tag_name, value)
                tag_values_combined.append(combined)
            body = str(tag_values_combined).encode("utf-8")
            print(f"[*] {str(tag_values_combined)}")
            channel.basic_publish(exchange='plc_data_exchange', routing_key='plc_data', body=body)
            time.sleep(5)  # Send a message every 2 seconds
        else:
            print("[*] Modbus Connection failed!")
except KeyboardInterrupt:
    print("Stopped sending messages.")
finally:
    connection.close()

