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
from smtp_email import Send_email
from wapp import Send_wapp

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
IP_ADDRESS = "192.168.1.145"
PORT = 502
COM_PORT = "/dev/ttyUSB0"
HOST_URL = "3.111.210.28"
USER = "plc_user"
USER_PASSWORD = "plc_password" 
EXCAHNGE_NAME = "plc_data_exchange"

async def initiate_modbus():
    '''Initiate modbus connection'''
    try:
        # Initiating Connection
        client = ModbusTcpClient(IP_ADDRESS, port=PORT)
        log.info("Modbus Device Connected")
        
    except Exception as e:
        log.error(f"Couldn't initiate modbus connection: {e}")

    return client

def get_tags_data(client):
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
            

        if tag_name == "tag_5":
            ascii_read(low_word, high_word, data)
        else:
            data.append([tag_name, tag_value])
        
    log.info(f"Data after conversion: {data}")
    return data

    
async def get_write_requests(client):
    '''Get any requests for writing a register from write_requests queue'''
    
    # Connect to RabbitMQ
    channel, connection = declare_connection(HOST_URL, USER, USER_PASSWORD)
    # Declare the queue to listen to (ensure it exists or will be created)
    channel.queue_declare(queue='write_requests', durable=False)

    # Fetch a single message from the queue
    method_frame, header_frame, body = channel.basic_get(queue='write_requests')

    # Check if a message was received
    if method_frame:  # If method_frame is not None, a message was received
        try:
            log.info(f"Received message: {body.decode()}")

            # Assuming the body is a stringified list like ['tag_1', '123.0']
            message_data = ast.literal_eval(body.decode())  # Convert string to list
            tag_name = message_data[0]
            
            
            if tag_name == "tag_5": # Recieve request for writing tag 5
                ascii_write(message_data, client)   
            else: # Write for tags other than tag 5
                try:
                    tag_value = message_data[1]
                    # Format value for proper decimal
                    converted_value = format_value(tag_value)
                    
                    try:
                        response = write_double(client, tag_name, converted_value)
                        log.info("Tag Written successfully!")
                    except Exception as e:
                        log.error(f"Tag not written: {e}")
                except Exception as e:
                    log.error(f"Tag not written, Unexpected error: {e}")
                
            # Acknowledge the message to avoid repitetion
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            log.error(f"Error processing message: {e}")
    else:
        log.info("No messages in the queue.")

    # Close the connection
    connection.close()

def ascii_read(low_word, high_word, data):
    char1, char2 = convert_16bit_to_ascii(high_word)
    char3, char4 = convert_16bit_to_ascii(low_word)
    final_char = char1+char2+char3+char4
    data.append(["tag_5", final_char])
    log.info(f"ASCII of tag_5: {final_char}")
    
def format_value(value):
    # Convert the input to a string to handle it easily
    value_str = str(value).strip()
    
    # Check if the value is a float
    if '.' in value_str:
        # Split the string into whole and fractional parts
        whole_part, fractional_part = value_str.split('.')
        
        # Keep only the first digit of the fractional part
        if len(fractional_part) > 1:
            fractional_part = fractional_part[0]  # Keep only the first digit
        
        # Combine the whole part and the truncated fractional part
        result = whole_part + fractional_part
    else:
        # If it's an integer, just add a zero at the end
        result = value_str + '0'
    
    return int(result)

def write_double(client, tag_name, tag_value):
    '''Write both low and high word Registers'''
    tag_register = None
    
    # Find the tag address from name
    for tag in GL_TAGS:
        if tag_name == tag[0]:
            tag_register = tag[1]
            break
    
    # Convert the value into 32 bit value (bytes)
    packed = struct.pack('i', tag_value)
    
    # split the 32 bits into two low word and high word
    low_word, high_word = struct.unpack('HH', packed)
    
    # Write both the low word and high word
    client.write_register(address=tag_register, value=low_word)
    client.write_register(address=tag_register + 1, value=high_word)
    
def ascii_write(message_data, client):
    tag_name = "5"
    tag_lower = int(message_data[1])  # Keep it as a string for now
    tag_higher = int(message_data[2])
    tag_address = 6104
    try:
        # Write the values to corresponding registers
        response2 = client.write_register(address=tag_address, value = tag_higher)
        response1 = client.write_register(address=tag_address + 1, value = tag_lower)
        
        # Log the values
        log.info("Tag Written successfully!")
        log.info(client.read_holding_registers(address=6105, count=2))
    except Exception as e:
        log.error(f"Tag not written: {e}")


previous_value = 0
def email_notify(data):
    global previous_value
    TAG2_LIMIT = 1500
    '''Email Notification system'''
    tag_name = None
    tag_value = None
    
    # Extract tag_2 value from the data
    for tag in data:
        if tag[0] == "tag_2":
            tag_name = tag[0]
            tag_value = tag[1]
            break  # Exit loop once the required tag is found

    # Log the tag value (value exceeding or moderate)
    if tag_value > TAG2_LIMIT:
        log.critical(f"{tag_name} VALUE EXCEEDED {TAG2_LIMIT}!")
        log.critical(f"{tag_name} VALUE: {tag_value}")
    else:
        log.info(f"{tag_name} Value Moderate")    
        log.critical(f"{tag_name} Value: {tag_value}")

    # Check if the tag_value exceeds the limit and if the previous_value was below the limit
    if tag_value > TAG2_LIMIT and previous_value <= TAG2_LIMIT:
        try:
            # Send notification only when the value crosses the limit from below
            response = Send_email(tag_name, f"{tag_value}, Previous Value: {previous_value}")
            # wapp_response = Send_wapp(tag_name, TAG2_LIMIT, tag_value, f"Previous Value: {previous_value}")
            log.info(f"previous value: {previous_value}")
            log.info("Notification Sent")
            previous_value = tag_value  # Update the previous_value after notification is sent
        except Exception as e:
            log.info(f"Previous Value: {previous_value}")
            log.error(f"Cannot send Email notification: {e}")
    else:
        # If no notification is sent, just update the previous_value without sending a notification
        previous_value = tag_value
        log.info(f"Previous Value: {previous_value}")
        log.info("Notification Not Sent.")
        
async def process():
    '''Main process for functioning'''
    # Declare the connection for RabbitMQ and Modbus Device
    start = time.time()
    rabbitmq_channel, connection = declare_connection(HOST_URL, USER, USER_PASSWORD)
    client = await initiate_modbus()
    
    # Get the values for all the tags
    data_tags = get_tags_data(client)
    
    email_notify(data_tags)
    get_write_requests(client)
    # Check for any notification
    # await asyncio.gather(email_notify(data_tags),get_write_requests(client))
    
    publish_data(rabbitmq_channel, data_tags, EXCAHNGE_NAME)
    end = time.time()
    log.info(f"Total time: {end-start}")
    # Wait before next cycle
    time.sleep(1)
    client.close()

async def main():
    while True:
        await process()

# Running the whole process
if __name__ == "__main__":
    asyncio.run(main())