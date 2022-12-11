import threading
from config import settings

"""
I want to implement a Pool of threads and deque (FCFS queue) with tasks.
If there are available threads - they take the from queue and do it, if no available threads - waiting
If no tasks - nothing to do, waiting... 
__ But I don't know how to do it....... :(
"""


def pr(text):
	"""Prints "logs" / info if flas is True. Only for thread-related logs"""
	if settings.print_daemons_info:
		print(text)


def can_create_daemon():
	"""Returns True if total threads < than max threads.
	Made to limit connections to RPC"""
	return len(threading.enumerate()) < settings.max_threads_per_time


def start_todo(func, daemon, *args):
	"""
	Start a daemon for tasks
	:param func: Function to do
	:param daemon: is daemon?
	:param args: other args..
	:return: created thread
	"""
	thread = threading.Thread(target=func, daemon=daemon, args=args)
	thread.start()
	return thread