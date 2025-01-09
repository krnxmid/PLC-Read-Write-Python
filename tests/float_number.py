from fastapi import FastAPI, Form, WebSocket
from fastapi.responses import HTMLResponse
import logging
import pika
import json
import asyncio
import threading
from queue import Queue

# Set up logging
logging.basicConfig(level=logging.INFO)
# Set the logging level for pika to CRITICAL
logging.getLogger('pika').setLevel(logging.CRITICAL)

app = FastAPI()
active_connections = set()
message_queue = Queue()

HTML_TEMPLATE = """
<html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { display: flex; gap: 20px; flex-wrap: wrap; justify-content: space-around; }
            .tag-box { border: 2px solid #ccc; padding: 15px; width: 150px; text-align: center;
                      border-radius: 8px; box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1); background-color: #f9f9f9; }
            .tag-box input { width: 100%; padding: 8px; margin-top: 10px; box-sizing: border-box;
                          border-radius: 4px; border: 1px solid #ccc; }
            .tag-box button { margin-top: 10px; padding: 8px 15px; cursor: pointer; border: none;
                           background-color: #4CAF50; color: white; border-radius: 4px; }
            .tag-value { margin-top: 10px; padding: 5px; background-color: #e9e9e9;
                       border-radius: 4px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h3>Tag Monitor</h3>
        <div class="container">
            <!-- Dynamic tag boxes -->
            <div class="tag-box">
                <label>TAG 1</label><br>
                <input type="text" id="tag1" placeholder="Enter value">
                <button onclick="sendTag('1')">Send</button>
                <div id="value1" class="tag-value">Value: --</div>
            </div>
            <div class="tag-box">
                <label>TAG 2</label><br>
                <input type="text" id="tag2" placeholder="Enter value">
                <button onclick="sendTag('2')">Send</button>
                <div id="value2" class="tag-value">Value: --</div>
            </div>
            <div class="tag-box">
                <label>TAG 3</label><br>
                <input type="text" id="tag3" placeholder="Enter value">
                <button onclick="sendTag('3')">Send</button>
                <div id="value3" class="tag-value">Value: --</div>
            </div>
            <div class="tag-box">
                <label>TAG 4</label><br>
                <input type="text" id="tag4" placeholder="Enter value">
                <button onclick="sendTag('4')">Send</button>
                <div id="value4" class="tag-value">Value: --</div>
            </div>
            <div class="tag-box">
                <label>TAG 5</label><br>
                <input type="text" id="tag5" placeholder="Enter value">
                <button onclick="sendTag('5')">Send</button>
                <div id="value5" class="tag-value">Value: --</div>
            </div>
        </div>
        <script>
            function connect() {
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.onmessage = event => {
                    const data = JSON.parse(event.data);
                    data.forEach(tag => {
                        const num = tag[0].split('_')[1];
                        document.getElementById(`value${num}`).textContent = `Value: ${tag[1]}`;
                    });
                };

                ws.onclose = () => setTimeout(connect, 1000);
            }
            connect();

            function sendTag(num) {
                const value = document.getElementById(`tag${num}`).value;
                if (!value) {
                    alert(`Enter a value for TAG ${ num}`);
                    return;
                }
                
                const formData = new FormData();
                formData.append("tag_number", num);
                formData.append("tag_value", value);
                
                fetch("/", {
                    method: "POST",
                    body: formData
                });
            }
        </script>
    </body>
</html>
"""

def format_value(value):
    """Format the value to have one decimal place."""
    if isinstance(value, int):
        # If the number is an integer, convert it to float and format
        return f"{value // 10}.{value % 10}"
    elif isinstance(value, float):
        # If the number is a float, format to one decimal place
        return f"{value:.1f}"
    return value  # Return as is if not a number

def rabbitmq_consumer():
    while True:
        try:
            with pika.BlockingConnection(pika.ConnectionParameters(
                'localhost', 
                credentials=pika.PlainCredentials('plc_user', 'plc_password')
            )) as connection:
                channel = connection.channel()
                channel.queue_declare(queue='plc_data_queue', durable=True)
                
                def callback(ch, method, properties, body):
                    message_queue.put(eval(body.decode()))
                
                channel.basic_consume('plc_data_queue', callback, auto_ack=True)
                channel.start_consuming()
        except Exception as e:
            logging.error(f"RabbitMQ Error: {e}")
            asyncio.sleep(5)

async def broadcast():
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            formatted_message = [[tag[0], format_value(tag[1])] for tag in message]
            for connection in active_connections.copy():
                try:
                    await connection.send_text(json.dumps(formatted_message))
                except:
                    active_connections.remove(connection)
        await asyncio.sleep(0.1)

@app.on_event("startup")
async def startup():
    threading.Thread(target=rabbitmq_consumer, daemon=True).start()
    asyncio.create_task(broadcast())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

@app.get("/")
def home():
    return HTMLResponse(HTML_TEMPLATE)

@app.post("/")
async def write_tag(tag_number: str = Form(), tag_value: str = Form()):
    try:
        formatted_value = format_value(float(tag_value))  # Format the tag value
        with pika.BlockingConnection(pika.ConnectionParameters(
            'localhost',
            credentials=pika.PlainCredentials('plc_user', 'plc_password')
        )) as connection:
            channel = connection.channel()
            channel.queue_declare(queue='write_requests', durable=False)
            channel.basic_publish(
                exchange='',
                routing_key='write_requests',
                body=str([f"tag_{tag_number}", formatted_value]).encode(),
                properties=pika.BasicProperties(delivery_mode=2)
            )
        return "Success"
    except Exception as e:
        logging.error(f"Write Error: {e}")
        return str(e)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)