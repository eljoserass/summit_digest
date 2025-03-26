import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable
import threading

logger = logging.getLogger(__name__)

# Dictionary to track running tasks
running_tasks = {}
# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=3)

def start_background_task(task_id: str, func: Callable, *args: Any, **kwargs: Any) -> None:
    """Start a background task in a separate thread"""

    def run_in_thread():
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the coroutine in this thread's event loop
            loop.run_until_complete(func(*args, **kwargs))
            loop.close()

        except Exception as e:
            logger.error(f"Background task {task_id} failed: {str(e)}")
        finally:
            # Clean up after task completes
            if task_id in running_tasks:
                del running_tasks[task_id]

    # Start the function in a new thread
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True  # The thread will exit when the main program exits
    thread.start()

    # Store the thread
    running_tasks[task_id] = thread
    logger.info(f"Started background task {task_id}")

def get_task_status(task_id: str) -> bool:
    """Check if a task is still running"""
    return task_id in running_tasks and running_tasks[task_id].is_alive()
