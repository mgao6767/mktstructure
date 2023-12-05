"""parx"""
from os import cpu_count
from typing import Callable, Iterable
from threading import Thread
from multiprocessing import Manager, Queue, current_process
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm


__all__ = ["parx"]


def producer_manager(in_queue: Queue, data: Iterable) -> None:
    """producer_manager enqueues tasks

    This is executed in a thread

    Args:
        in_queue (Queue): queue of inputs
        data (Iterable): input data
    """
    for idx, obs in enumerate(data):
        in_queue.put((idx, obs))


def worker(in_queue: Queue, out_queue: Queue, pid: int, func: Callable) -> None:
    """worker performs calculation and puts results in out_queue

    Args:
        in_queue (Queue): queue of inputs
        out_queue (Queue): queue of outputs
        pid (int): worker id
        func (Callable): function
    """
    while True:
        value = in_queue.get(block=False)
        if value is not None:
            # msg = f"Process {pid} got: {func} {value}"
            idx, obs = value
            out_queue.put((idx, func(obs)))
        else:
            in_queue.put(None)
            return


def worker_manager(
    in_queue: Queue, out_queue: Queue, func: Callable, workers: Iterable
) -> None:
    """worker_manager manages worker processes

    This is executed in a thread

    Args:
        in_queue (Queue): queue of inputs
        out_queue (Queue): queue of outputs
        func (Callable): function
        workers (Iterable): number of workers
    """
    with ProcessPoolExecutor(workers) as exe:
        futures = [
            exe.submit(worker, in_queue, out_queue, pid, func) for pid in range(workers)
        ]
        for _ in as_completed(futures):
            pass


def result_collector(
    out_queue: Queue, result: list, progress_update: Callable | None
) -> None:
    """result_collector collects results and puts them in result list

    Args:
        out_queue (Queue): queue of outputs
        result (list): list of results
        progress_update (Callable | None): handler of tqdm.update
    """
    if not isinstance(progress_update, Callable):
        progress_update = None
    while True:
        res = out_queue.get()
        if res is None:
            return
        result.append(res)
        if progress_update is not None:
            progress_update()


def run(
    func: Callable, data: Iterable, workers: int, progress_update: Callable | None
) -> list:
    """run manages the parallel execution

    Args:
        func (Callable): function
        data (Iterable): data
        workers (int): number of workers
        progress_update (Callable | None): handler of tqdm.update

    Returns:
        list: list of results in order of input data
    """
    result = []
    with Manager() as m:
        in_queue, out_queue = m.Queue(), m.Queue()
        t_collector = Thread(
            target=result_collector,
            args=(out_queue, result, progress_update),
        )
        t_worker = Thread(
            target=worker_manager,
            args=(in_queue, out_queue, func, workers),
        )
        t_producer = Thread(
            target=producer_manager,
            args=(in_queue, data),
        )
        t_collector.start()
        t_worker.start()
        t_producer.start()
        t_producer.join()
        t_worker.join()
        # all workers completed their tasks, put a terminal signal for collector
        out_queue.put(None)
        t_collector.join()

    # restore the order of results as per input order
    final_result = []
    result.sort(key=lambda res: res[0])
    for _, res in result:
        final_result.append(res)

    return final_result


def run_in_main_only(func: Callable):
    """run_in_main_only acts as an entry guard

    If `parx()` is not guarded by __name__=="__main__", spawned child processes
    will import and hence run everything again. `noop` does nothing. But if user
    attempts to print(parx(func, data)), it displays some information instead of
    simply None.

    Args:
        func (Callable): function
    """

    def noop(*args, **kwargs):  # pylint: disable=unused-argument
        return f"{current_process().name} running"

    if current_process().name == "MainProcess":
        return func
    return noop


# @run_in_main_only
def parx(
    func: Callable, data: Iterable, progress_bar=True, workers=cpu_count()
) -> list:
    """parx executes the function on the data in a parallel way

    Args:
        func (Callable): function
        data (Iterable): data
        progress_bar (bool, optional): show progress. Defaults to True.
        workers (_type_, optional): number of workers. Defaults to cpu_count().

    Returns:
        list: list of results
    """
    assert isinstance(func, Callable)
    assert isinstance(data, Iterable)
    assert isinstance(progress_bar, bool)
    assert isinstance(workers, int)
    parallel = not (workers is None or workers <= 1)

    match (parallel, progress_bar):
        case False, False:
            print("Sequential execution with 1 worker")
            return list(map(func, data))
        case False, True:
            print("Sequential execution with 1 worker")
            return list(map(func, tqdm(data)))
        case True, True:
            print(f"Parallel execution with {workers} workers")
            with tqdm(total=len(data)) as pbar:
                return run(func, data, workers, progress_update=pbar.update)
        case True, False:
            print(f"Parallel execution with {workers} workers")
            return run(func, data, workers, progress_update=None)
