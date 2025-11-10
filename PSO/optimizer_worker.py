from threading import Thread, Event
from queue import Queue


def run_optimizer_task(optimize_fun, kwargs, result_queue, cancel_event: Event):
    if cancel_event.is_set():
        result_queue.put((False, "cancelled"))
        return
    try:
        res = optimize_fun(**kwargs)
        result_queue.put((True, res))
    except Exception as e:
        result_queue.put((False, e))
