from rabbit_mq import declare_connection, publish_data
import pika

from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusSerialClient
import time

from conversion import *
import struct

from logger import log

import ast

import asyncio

from smtp_email import Send

GL_TAGS = [
    ("tag_1", 6096, 0, "Signed"),
    ("tag_2", 6098, 0, "Signed"),
    ("tag_3", 6100, 0, "Signed"),
    ("tag_4", 6102, 0, "Signed"),
    ("tag_5", 6104, 0, "Signed"),
]

COM_PORT = "/dev/ttyUSB0"

async def initiate_modbus():
    '''Initiate modbus connection'''
    try:
        # Modbus Rtu Connection
        # client = ModbusSerialClient(port=COM_PORT, baudrate=9600, timeout=1)
        
        # TCP/IP Connection Params
        IP_ADDRESS = "192.168.1.145"
        PORT = 502
        
        # Initiating Connection
        client = ModbusTcpClient(IP_ADDRESS, port=PORT)
        log.info("Modbus Device Connected")
        
    except Exception as e:
        log.info(e)
    return client

async def get_tags_data(client):
    '''Get final tag values after conversions'''
    # List containing data of all tags
    data = []
    
    log.info("Getting Tags Data...")
    for tag in GL_TAGS:
        # async define name, address, decimals for the tags
        tag_name = tag[0]
        tag_address = tag[1]
        tag_decimals = tag[2]
        log.info(f"Reading tag: {tag_name}")
        
        # Reading Data from the tag address
        try:
            response = client.read_holding_registers(address=tag_address, count=2)
            
            if response is None or response.isError():
                log.error(f"Error reading tag {tag_name} at address {tag_address}")
                continue
            
        except Exception as e:
            log.error(f"Failed to read data for tag {tag_name} at address {tag_address}: {e}")
            continue
        
        # define low word and high word for the register since high word is +1 address of low word
        if response:
            high_word = response.registers[1]
            low_word = response.registers[0]
        
        # Combine the 16 bit low_word and high_word to make a single 32 bit word
        log.info(f"Converting data for tag {tag_name} - High Word: {low_word}, Low Word: {high_word}")
        combined = combine_16bit_to_32bit(low_word, high_word)
        log.info(f"Converted value for {tag_name}: {combined}")
        
        # Check for Signed or UnSigned values and then deal with them appropriately
        if len(tag) > 3:
            tag_type = tag[3]

            if tag_type == "Signed":
                tag_value = unsigned_to_signed(combined)
                log.info(f"Converted {tag_name} into signed: {tag_value}")
        else:
            tag_value = combined
            
        # Handling for specific tag processing
        if tag_name == "tag_5":
            ascii_read(low_word, high_word, data)
        else:
            data.append([tag_name, tag_value])
        
    log.info(f"Data after conversion: {data}")
    return data

def ascii_read(low_word, high_word, data):
    char1, char2 = convert_16bit_to_ascii(high_word)
    char3, char4 = convert_16bit_to_ascii(low_word)
    final_char = char1+char2+char3+char4
    data.append(["tag_5", final_char])
    log.info("Tag 5 ASCII Value: %s", final_char)

def format_value(value):
    '''Format the value to ensure correct decimal precision'''
    value_str = str(value).strip()
    
    if '.' in value_str:
        whole_part, fractional_part = value_str.split('.')
        if len(fractional_part) > 0:
            fractional_part = fractional_part[0]  
        result = whole_part + fractional_part
    else:
        result = value_str + '0'
    
    return int(result)

def write_double(client, tag_name, tag_value):
    '''Write both low and high word Registers'''
    tag_register = None
    
    for tag in GL_TAGS:
        if tag_name == tag[0]:
            tag_register = tag[1]
            break
    
    packed = struct.pack('i', tag_value)
    low_word, high_word = struct.unpack('HH', packed)
    
    client.write_register(address=tag_register, value=low_word)
    client.write_register(address=tag_register + 1, value=high_word)
    
async def get_write_requests(client):
    '''Get any requests for writing a register from write_requests queue'''
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='65.0.237.181',  # Replace with your mini-computer IP
        virtual_host='/',
        credentials=pika.PlainCredentials('plc_user', 'plc_password')
    ))

    channel = connection.channel()

    channel.queue_declare(queue='write_requests', durable=False)

    method_frame, header_frame, body = channel.basic_get(queue='write_requests')

    if method_frame:  
        try:
            log.info(f"Received message: {body.decode()}")

            message_data = ast.literal_eval(body.decode())  
            tag_name = message_data[0]
            
            if tag_name == "tag_5": 
                ascii_write(message_data, client)   
            else: 
                try:
                    tag_value = message_data[1]
                    converted_value = format_value(tag_value)
                    response = write_double(client, tag_name, converted_value)
                    log.info("Tag Written successfully!")
                except Exception as e:
                    log.error(f"Tag not written: {e}")
                
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            log.error(f"Error processing message: {e}")
    else:
        log.info("No messages in the queue.")

    connection.close()

def ascii_write(message_data, client):
    '''Handle ASCII write for specific tags'''
    tag_name = "tag_5"
    tag_lower = int(message_data[1])  
    tag_higher = int(message_data[2])
    tag_address = 6104
    try:
        response2 = client.write_register(address=tag_address, value=tag_higher)
        response1 = client.write_register(address=tag_address + 1, value=tag_lower)
        
        log.info("Tag Written successfully!")
        log.info(client.read_holding_registers(address=6105, count=2))
    except Exception as e:
        log.error(f"Tag not written: {e}")

def email_notify(data):
    '''Email Notification for specific conditions'''
    for tag in data:
        if tag[0] == "tag_2":
            tag_name = tag[0]
            tag_value = tag[1]
        
    if tag_value > 1500:
        log.info("TAG 2 Value exceeded 1500!")
        try:
            response = Send(tag_name, tag_value)
        except Exception as e:
            log.info(f"Not Sent!: {e}")
    else:
        log.info("TAG 2 Value Moderate")

async def process():
    '''Main process function'''
    start_time = time.time()
    rabbitmq_channel = declare_connection()
    client = await initiate_modbus()
    
    data_tags = await get_tags_data(client)
    email_notify(data_tags)
    
    await get_write_requests(client)
    publish_data(rabbitmq_channel, data_tags)
    
    time.sleep(1)
    client.close()
    
    end_time = time.time()
    log.info(f"Time taken: {end_time - start_time}")

async def main():
    '''Main loop to continuously run the process'''
    while True:
        await process()

if __name__ == "__main__":
    asyncio.run(main())
