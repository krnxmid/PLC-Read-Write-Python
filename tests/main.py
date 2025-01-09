from rabbit_mq import declare_connection
from pymodbus.client import ModbusSerialClient
import pika
import time

GL_TAGS = [
    ("tag_1", 4296, 10),
    ("tag_2", 4306, 0, "Signed"),
    ("tag_3", 4308, 0, "Signed"),
    ("tag_4", 4310, 0, "Signed"),
    ("tag_5", 4312, 0, "Signed"),
    ("tag_6", 4314, 0, "Signed"),
    ("tag_7", 4316, 0, "Signed"),
    ("tag_8", 4318, 0, "Signed"),
    ("tag_9", 4320, 0, "Signed"),
    ("tag_10", 4322, 0, "Signed"),
    ("tag_11", 4324, 0, "Signed"),
    ("tag_12", 4326, 10),
    ("tag_13", 4336, 0, "Unsigned"),
    ("tag_14", 4338, 0, "Unsigned"),
    ("tag_15", 4340, 0, "Signed"),
    ("tag_16", 4342, 0, "Signed"),
    ("tag_17", 4344, 0, "Signed"),
    ("tag_18", 4346, 0, "Signed"),
    ("tag_19", 4348, 0, "Signed"),
    ("tag_20", 4350, 0, "Signed"),
]

COM_PORT = "/dev/ttyUSB0"

declare_connection()
def initiate_modbus():
    try:
        client = ModbusSerialClient(port=COM_PORT, baudrate=9600, timeout=1)
    except Exception as e:
        log.info

try:
    while True:
        tag_values_combined = []
        if client.connect():
            log.info("[*] Modbus connection successful!")
            for tag in GL_TAGS:
                tag_name = tag[0]
                tag_address = tag[1]
                tag_count = tag[2]

                if len(tag) > 3:
                    tag_type = tag[3]

                response = client.read_holding_registers(address=tag_address, count=2)
                value = response.registers[0]

                combined = (tag_name, value)
                tag_values_combined.append(combined)
            body = str(tag_values_combined).encode("utf-8")
            log.info(f"{body}")
            try:
                channel.basic_publish(
                    exchange='plc_data_exchange',
                    routing_key='plc_data',
                    body=body
                )
                log.info("Message published successfully.")
            except Exception as e:
                log.info(f"Failed to publish message: {e}")
            
            time.sleep(5)  # Send a message every 2 seconds
        else:
            log.info("[*] Modbus Connection failed!")
except KeyboardInterrupt:
    log.info("Stopped sending messages.")
    
connection.close()

