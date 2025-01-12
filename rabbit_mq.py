import pika

from logger import log

def declare_connection(HOST_URL, USER, USER_PASSWORD):
    '''Declare the connection and other things like exchanges, queues'''
    # Try to connect to RabbitMQ
    try:
        connection_params = pika.ConnectionParameters(host=HOST_URL, credentials=pika.PlainCredentials(USER, USER_PASSWORD))
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        # channel.exchange_declare(exchange=EXCAHNGE_NAME, exchange_type='direct', durable=True)
        log.info("Connected to RabbitMQ")
    except Exception as e:
        log.info(f"Failed to connect with rabbit mq: {e}")
    return channel, connection
    
def publish_data(channel, tags_data, EXCAHNGE_NAME):
    '''Publish data to EC2'''
    
    channel.exchange_declare(exchange=EXCAHNGE_NAME, exchange_type='direct', durable=True)
    # Convert the tags data into bytes to make it compatible with RabbitMQ's message body
    body = str(tags_data).encode("utf-8")
    
    try:
        channel.basic_publish(
            exchange='plc_data_exchange',
            routing_key='plc_data',
            body=body
        )
        log.info("Message published successfully.")
    except Exception as e:
        log.info(f"Failed to publish message: {e}")

if __name__ == "__main__":
    channel = declare_connection()
    publish_data(channel, "hello")