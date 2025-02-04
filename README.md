# Project: PLC Data Monitoring and Logging System

## Overview
This project is a PLC (Programmable Logic Controller) monitoring system that integrates with RabbitMQ for data exchange, logs system activities, and manages log files. The system retrieves and processes data from PLC registers using Modbus communication and supports ASCII conversions.

## Directory Structure

📁 project_root  
├── [conversion.py](conversion.py)      # Functions for handling 16-bit and 32-bit register conversions  
├── [log_deleter.py](log_deleter.py)     # Automated log deletion script  
├── [logger.py](logger.py)          # Logger setup for application logging  
├── [main.py](main.py)            # Main application for reading/writing Modbus data and RabbitMQ communication  
├── [rabbit_mq.py](rabbit_mq.py)       # RabbitMQ connection and data publishing  

## Files and Descriptions

### [`conversion.py`](conversion.py)
Provides utility functions to handle conversion between different data formats (16-bit, 32-bit, and ASCII).

#### Functions:
- `combine_16bit_to_32bit(high_word, low_word)`: Combines two 16-bit registers into a 32-bit value.
- `unsigned_to_signed(value)`: Converts an unsigned integer to signed.
- `split_32bit_to_16bit(value)`: Splits a 32-bit integer into two 16-bit integers.
- `split_16bit_to_8bit(value)`: Splits a 16-bit integer into two 8-bit integers.
- `convert_16bit_to_ascii(value)`: Converts a 16-bit integer into ASCII characters.

---

### [`log_deleter.py`](log_deleter.py)
Automates the deletion of old log files to manage storage efficiently.

#### Features:
- Deletes log files older than `5` days.
- Runs as a scheduled task every 30 minutes.
- Handles various log file naming patterns (`app_log.*`, `network.*`).

---

### [`logger.py`](logger.py)
Sets up logging for the system with both file and console output.

#### Features:
- Logs are stored in `/home/admin/plc_monitoring/log/`.
- Includes timestamps, log levels, module names, and line numbers.
- Prevents duplicate handlers.

---

### [`main.py`](main.py)
Main application that interacts with the PLC using Modbus and exchanges data with RabbitMQ.

#### Features:
- Establishes Modbus connection (`TCP/IP` or `RTU`).
- Reads register values, converts them, and publishes data to RabbitMQ.
- Handles write requests for modifying register values.
- Supports ASCII processing.
- Implements notification logic for specific tag thresholds.
- Runs in an asynchronous loop.

---

### [`rabbit_mq.py`](rabbit_mq.py)
Handles RabbitMQ connectivity and message publishing.

#### Features:
- Establishes a connection to RabbitMQ.
- Publishes PLC data to an exchange (`plc_data_exchange`).

---

## Configuration Parameters
### Modbus Connection:
- **IP_ADDRESS**: `192.168.1.145`
- **PORT**: `502`
- **COM_PORT**: `/dev/ttyUSB0`

### RabbitMQ Connection:
- **HOST_URL**: `3.111.210.28`
- **USER**: `plc_user`
- **PASSWORD**: `plc_password`
- **EXCHANGE_NAME**: `plc_data_exchange`
- **ROUTING_KEY**: `plc_data`

### Logging Configuration:
- **Log Directory**: `/home/admin/plc_monitoring/log/`

### Log Deletion Settings:
- **Log Directory**: `./logs`
- **Retention Period**: `5 days`
- **Schedule**: `Every 30 minutes`

---

## How to Run
1. Ensure dependencies (`pika`, `pymodbus`, `schedule`, etc.) are installed.
2. Start the main application:
   ```bash
   python main.py
   ```
3. The log deletion script runs automatically but can be executed manually:
   ```bash
   python log_deleter.py
   ```

---

## Dependencies
Ensure the following Python packages are installed:
```bash
pip install pymodbus pika schedule
```

---

## Author
[Your Name]
