from rabbit_mq import declare_connection, publish_data
import pika

from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusSerialClient
import time

from conversion import combine_16bit_to_32bit, unsigned_to_signed, split_16bit
import struct

from logger import log

import ast

# GL_TAGS = [
#     ("tag_1", 4296, 10),
#     ("tag_2", 4306, 0, "Signed"),
#     ("tag_3", 4308, 0, "Signed"),
#     ("tag_4", 4310, 0, "Signed"),
#     ("tag_5", 4312, 0, "Signed"),
#     ("tag_6", 4314, 0, "Signed"),
#     ("tag_7", 4316, 0, "Signed"),
#     ("tag_8", 4318, 0, "Signed"),
#     ("tag_9", 4320, 0, "Signed"),
#     ("tag_10", 4322, 0, "Signed"),
#     ("tag_11", 4324, 0, "Signed"),
#     ("tag_12", 4326, 10),
#     ("tag_13", 4336, 0, "Unsigned"),
#     ("tag_14", 4338, 0, "Unsigned"),
#     ("tag_15", 4340, 0, "Signed"),
#     ("tag_16", 4342, 0, "Signed"),
#     ("tag_17", 4344, 0, "Signed"),
#     ("tag_18", 4346, 0, "Signed"),
#     ("tag_19", 4348, 0, "Signed"),
#     ("tag_20", 4350, 0, "Signed"),
# ]
GL_TAGS = [
    ("tag_1", 6096, 0, "Signed"),
    ("tag_2", 6098, 0, "Signed"),
    ("tag_3", 6100, 0, "Signed"),
    ("tag_4", 6102, 0, "Signed"),
    ("tag_5", 6104, 0, "Signed"),

]

COM_PORT = "/dev/ttyUSB0"

def initiate_modbus():
    '''Initiate modbus connection'''
    try:
        # client = ModbusSerialClient(port=COM_PORT, baudrate=9600, timeout=1)
        IP_ADDRESS = "192.168.1.145"
        PORT = 502
        client = ModbusTcpClient(IP_ADDRESS, port=PORT)
        log.info("Modbus Device Connected")
    except Exception as e:
        log.info(e)
    return client

def get_tags_data(client):
    '''Get final tag values after conversions'''
    data = []
    log.info("Getting Tags Data...")
    for tag in GL_TAGS:
        tag_name = tag[0]
        tag_address = tag[1]
        tag_decimals = tag[2]
        log.info(f"Reading tag: {tag_name}")
        
        try:
            response = client.read_holding_registers(address=tag_address, count=2)
            
            if response is None or response.isError():
                log.error(f"Error reading tag {tag_name} at address {tag_address}")
                continue
            
        except Exception as e:
            log.error(f"Failed to read data for tag {tag_name} at address {tag_address}: {e}")
            continue
        
        if response:
            low_word = response.registers[1]
            high_word = response.registers[0]
        
        log.info(f"Converting data for tag {tag_name} - High Word: {high_word}, Low Word: {low_word}")
        combined = combine_16bit_to_32bit(high_word, low_word)
        log.info(f"Converted value for {tag_name}: {combined}")
        
        if len(tag) > 3:
            tag_type = tag[3]

            if tag_type == "Signed":
                tag_value = unsigned_to_signed(combined)
                log.info(f"Converted {tag_name} into signed: {tag_value}")
        else:
            tag_value = combined
            
        data.append([tag_name, tag_value])
    log.info(f"Data after conversion: {data}")
    
    return data

def write_double(client, tag_name, tag_value):
    '''Write Registers'''
    tag_register = None
    for tag in GL_TAGS:
        if tag_name == tag[0]:
            tag_register = tag[1]
            break
    
    packed = struct.pack('i', tag_value)
    low_word, high_word = struct.unpack('HH', packed)
    client.write_register(address=tag_register, value=low_word)
    client.write_register(address=tag_register + 1, value=high_word)
    
def get_write_requests(client):
    '''Get any requests for writing a register from write_requests queue'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='65.0.237.181',  # Replace with the IP of your mini-computer
        virtual_host='/',  # Ensure this matches the vhost you're using
        credentials=pika.PlainCredentials('plc_user', 'plc_password')  # Adjust if needed
    ))

    channel = connection.channel()

    # Declare the queue to listen to (ensure it exists or will be created)
    channel.queue_declare(queue='write_requests', durable=False)

    # Fetch a single message from the queue
    method_frame, header_frame, body = channel.basic_get(queue='write_requests')

    # Check if a message was received
    if method_frame:  # If method_frame is not None, a message was received
        try:
            log.info(f"Received message: {body.decode()}")

            # Assuming the body is a stringified list like ['tag_1', '-2140071000']
            message_data = ast.literal_eval(body.decode())  # Convert string to list

            # Unpack the data from the list
            tag_name = message_data[0]
            tag_value = int(message_data[1])
            # Process the request (e.g., write to register)
            try:
                response = write_double(client, tag_name, tag_value)
                log.info("Tag Written successfully!")
            except Exception as e:
                log.error(f"Tag not written: {e}")

            # Acknowledge the message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            log.error(f"Error processing message: {e}")
    else:
        log.info("No messages in the queue.")

    # Close the connection
    connection.close()


def process():
    '''Main process for functioning'''
    rabbitmq_channel = declare_connection()
    client = initiate_modbus()
    data_tags = get_tags_data(client)
    get_write_requests(client)
    publish_data(rabbitmq_channel, data_tags)
    time.sleep(5)
    client.close()

while True:
    process()