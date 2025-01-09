import pika
import time

# Connection parameters
connection_params = pika.ConnectionParameters(host='65.0.237.181', 
                                               credentials=pika.PlainCredentials('plc_user', 'plc_password'))

# Establish connection
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare the exchange as durable
channel.exchange_declare(exchange='plc_data_exchange', exchange_type='direct', durable=True)
i = 1
try:
    while True:
        message = f"message number: {i}"
        channel.basic_publish(exchange='plc_data_exchange', routing_key='plc_data', body=message)
        print(f"Sent: {message}")
        time.sleep(5)
        i += 1
except KeyboardInterrupt:
    print("Stopped sending messages.")
finally:
    connection.close()
