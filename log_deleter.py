import os
import datetime
import schedule
import time

logs_dir = "./logs"
number_of_days = 5


def delete_old_logs():
    try:
        if os.path.isdir(logs_dir):
            current_date = datetime.datetime.now()
            list_files = os.listdir(logs_dir)
            print("[+] Got files:")
            print(list_files)
            
            if list_files:
                # Check if number of files is greater than the threshold
                if len(list_files) > number_of_days:
                    for log_file in list_files:
                        # Skipping the current day's log (if you have a specific log file like "app_log")
                        if log_file == "app_log":
                            continue

                        # Check for logs with patterns (app_log.*, network.*, etc.)
                        date_of_log_creation_str = None
                        if "app_log." in log_file:
                            date_of_log_creation_str = log_file.split(".")[1]
                        elif "network." in log_file:
                            date_of_log_creation_str = log_file.split(".")[1]

                        # If log file creation date is found, process it
                        if date_of_log_creation_str:
                            try:
                                date_of_log_creation = datetime.datetime.strptime(date_of_log_creation_str, "%Y-%m-%d")
                                print(f"Date of log creation: {date_of_log_creation}")

                                # If log is older than the specified number of days, delete it
                                if (current_date - date_of_log_creation).days > number_of_days:
                                    os.remove(os.path.join(logs_dir, log_file))
                                    print(f"[+] Deleted log file: {log_file}")
                            except ValueError as e:
                                print(f"[-] Failed to parse date for log file {log_file}: {e}")
                        else:
                            print(f"[-] Log file does not match any expected pattern: {log_file}")
                else:
                    print("[+] Less than or equal to 5 log files found.")
            else:
                print("[-] No log files found in the directory.")
        else:
            print(f"[-] Directory not found: {logs_dir}")
    except Exception as e:
        print(f"Error while deleting logs: {e}")


# Schedule the log deletion task every 30 minutes
schedule.every(30).minutes.do(delete_old_logs)

# Initial execution of the function to delete old logs immediately
try:
    delete_old_logs()
    while True:
        schedule.run_pending()
        time.sleep(10)
except Exception as e:
    print(f"Error while running the schedule: {e}")
    time.sleep(10)
