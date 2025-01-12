import pika
import time

# Connection parameters
connection_params = pika.ConnectionParameters(host='3.111.210.28', 
                                               credentials=pika.PlainCredentials('plc_user', 'plc_password'))

# Establish connection
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare the exchange
channel.exchange_declare(exchange='plc_data_exchange', exchange_type='direct', durable=True)

try:
    while True:
        message = "Hello from Mini Computer!"
        channel.basic_publish(exchange='plc_data_exchange', routing_key='plc_data', body=message)
        print(f"Sent: {message}")
        time.sleep(2)  # Send a message every 2 seconds
except KeyboardInterrupt:
    print("Stopped sending messages.")
finally:
    connection.close()
