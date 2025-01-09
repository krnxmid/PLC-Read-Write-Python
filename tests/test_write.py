import pika
import ast
from logger import log

def get_write_requests():
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
    if method_frame:
        try:
            print(f"Received message: {body.decode()}")
            print(type(body.decode()))
            tag_name = (ast.literal_eval(body.decode()))[0]
            tag_value = (ast.literal_eval(body.decode()))[1]
            # Process the request here (for example, write to a register)
            response = write_double(tag_name, tag_value)
            if response:
                log.info("Tag Written successfully!")

            # Acknowledge the message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            log.error(f"Error processing message: {e}")
    else:
        print("No messages in the queue.")

    # Close the connection
    connection.close()

# Example of write_double function (you should implement your logic for this)
def write_double(tag_name, tag_value):
    # Implement your logic to write to a register
    print(f"Writing data: {tag_value}, for tag {tag_name}")
    return True  # Simulate a successful write

def clear_queue():
    '''Clear all messages from the write_requests queue'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='65.0.237.181',  # Replace with the IP of your mini-computer
        virtual_host='/',  # Ensure this matches the vhost you're using
        credentials=pika.PlainCredentials('plc_user', 'plc_password')  # Adjust if needed
    ))

    channel = connection.channel()

    # Purge the queue to remove all messages
    channel.queue_purge(queue='write_requests')

    print("Queue cleared successfully.")

    # Close the connection
    connection.close()

# Call the function to clear the queue
clear_queue()
