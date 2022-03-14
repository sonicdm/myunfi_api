from __future__ import annotations
import concurrent.futures.thread
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, Union
from dataclasses import dataclass, field
from unfi_api.exceptions import CancelledJobException, JobErrorException

if TYPE_CHECKING:
    from unfi_api.utils.jobs import Job, Jobs

logger = logging.getLogger(__name__)
cancel = False
job_executors: Dict[Union[str, int], ThreadPoolExecutor] = {}  # job_id: executor
job_status: Dict[str, str] = {}  # job_id: status


def threader(
    func,
    args,
    fn_args=(),
    fn_kwargs={},
    callback=None,
    finished_callback=None,
    max_workers=10,
    executor_type="thread",
    executor_options={},
    executor = None,
    job: Job = None,
):
    """
    This function takes in a function and data, then runs the
    function with the arguments given using the specified thread executor type.

    Args:
    func:              The function to be run.
    args:              The data to be passed to the function.

    Kwargs:
    fn_args:           The arguments to be passed to the function.
    fn_kwargs:         The keyword arguments to be passed to the function.
    callback:          The callback function to be run after each iteration of the function is run.
    finished_callback: The callback function to be run after the function is finished.
    max_workers:       The maximum number of threads to be used. default: 10
    executor_type:     The type of executor to be used. default: "thread"
                           "process" for ProcessPoolExecutor or "thread" for ThreadPoolExecutor
    executor_options:  The thread options to be sent to the executor.
    executor:          The executor to be used. will ignore type, executor_options and max_workers.
    """
    if not executor_options:
        executor_options = dict(max_workers=max_workers)    
    results = []
    if not executor:   
        if executor_type == "thread":
            executor = ThreadPoolExecutor(**executor_options)
        elif executor_type == "process":
            executor = ProcessPoolExecutor(**executor_options)
        else:
            raise ValueError(
                f"Invalid executor type: {executor_type} must be either 'thread' or 'process'."
            )
    try:
        results = run_executor(executor, func, args, fn_args, fn_kwargs, callback, job)
    except CancelledJobException:
        return results
    if finished_callback:
        finished_callback(results)
    executor.shutdown(wait=True)
    return results


def run_executor(
    executor: Union[ThreadPoolExecutor, ProcessPoolExecutor],
    fn,
    fn_data: Iterable[Any],
    fn_args: Iterable[Any] = None,
    fn_kwargs: Dict[str, Any] = None,
    callback: Callable[[Any], Any] = None,
    job: Job = None,
) -> Any:
    """
    Run a job with an executor.
    """
    results = []
    executor_args = []
    if job:
        job.job_output = []
    if fn_args:
        executor_args.append(fn_args)
    if fn_kwargs:
        executor_args.append(fn_kwargs)
    with executor:
        futures = [executor.submit(fn, arg, *executor_args) for arg in fn_data]
        try:
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if callback:
                        callback(result)
                    results.append(result)
                    if job:
                        job.job_output.append(result)
                        if job.cancelled():
                            raise CancelledJobException(message=f"Job: '{job.job_id}' cancelled", job_id=job.job_id, job=job)
                        
                    # if job:
                    #     if job.cancelled():
                    #         message = f"Job {job.job_id} was cancelled."
                    #         raise CancelledJobException(message, job=job, job_id=job.job_id)
                    #     if job.errored():
                    #         message = f"Job {job.job_id} encountered an error."
                    #         print(job.exceptions)
                    #         raise JobErrorException(message, job=job, job_id=job.job_id)
                        
                except CancelledJobException as e:
                    executor.shutdown(wait=False)
                    executor._threads.clear()
                    concurrent.futures.thread._threads_queues.clear()
                    raise e
                    break
                except JobErrorException:
                    break
                except Exception as exc:
                    logger.exception("Something went wrong...")
                    raise
                except KeyboardInterrupt:
                    executor.shutdown(wait=False)
                    raise
        except KeyboardInterrupt:
            executor._threads.clear()
            concurrent.futures.thread._threads_queues.clear()
            raise
    return results



def shutdown_executor(executor: Union[ThreadPoolExecutor, ProcessPoolExecutor]):
    """
    This function shuts down the executor.
    """
    executor.shutdown(wait=False)


def get_executor(executor_type="thread", executor_options=dict()):
    """
    This function returns an executor.
    """
    if not executor_options:
        executor_options = dict(max_workers=10)
    if executor_type == "thread":
        return ThreadPoolExecutor(**executor_options)
    elif executor_type == "process":
        return ProcessPoolExecutor(**executor_options)
    else:
        raise ValueError(
            f"Invalid executor type: {executor_type} must be either 'thread' or 'process'."
        )

def kill_all_threads():
    """
    This function kills all threads in the current thread pool.
    """
    concurrent.futures.thread._threads_queues.clear()

