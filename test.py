import asyncio
import multiprocessing

# Define your async function
async def background_task():
    print("Background task started")
    await asyncio.sleep(5)  # Simulate a long-running task
    print("Background task finished")

# Wrapper to run async function in a process
def run_in_background():
    asyncio.run(background_task())  # Run the async function in a new event loop

# Start the task in the background process
background_process = multiprocessing.Process(target=run_in_background)
background_process.start()

# Main function can continue running
print("Main task running")
