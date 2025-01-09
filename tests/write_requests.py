import pika

# Define connection parameters (ensure this matches your vhost and credentials)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='65.0.237.181',  # Replace with the IP of your mini-computer
    virtual_host='/',  # Ensure this matches the vhost you're using
    credentials=pika.PlainCredentials('plc_user', 'plc_password')  # Adjust if needed
))

channel = connection.channel()

# Declare the queue to listen to (ensure it exists or will be created)
channel.queue_declare(queue='write_requests', durable=False)

# Callback function to handle received messages
def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")

# Subscribe to the queue
channel.basic_consume(queue='write_requests', on_message_callback=callback, auto_ack=False)

print("Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
