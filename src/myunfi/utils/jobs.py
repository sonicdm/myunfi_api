from __future__ import annotations
import logging
from concurrent.futures import (
    Future,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    as_completed,
)
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Tuple, Union

from unfi_api.exceptions import (
    CancelledJobException,
    JobErrorException,
    JobRunningException,
)
from unfi_api.utils.threading import threader, get_executor

JOB_STATUSES = ["pending", "running", "finished", "error", "cancelled"]
ENDED_STATUSES = ["finished", "error", "cancelled"]
RUNNING_STATUSES = ["running"]

jobs: Jobs = None

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
# log to stdout
logger.addHandler(logging.StreamHandler())

# disable logging for this module
# logger.disabled = True


class status(Enum):
    """
    Enum for job status.
    """

    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    CANCELLED = "cancelled"


def run_job(
    fn,
    fn_data: Iterable[Any],
    fn_args: Iterable[Any] = None,
    fn_kwargs: Dict[str, Any] = None,
    job: Job = None,
    threaded: bool = False,
    callback: Callable = None,
    finished_callback: Callable = None,
    max_workers: int = None,
    executor_type: str = "thread",
    executor: Union[ThreadPoolExecutor, ProcessPoolExecutor] = None,
    executor_options: Dict[str, Any] = None,
):
    """
    Run a job threaded or not.
    """
    if threaded or executor:
        output = threader(
            fn,
            fn_data,
            fn_args=fn_args,
            fn_kwargs=fn_kwargs,
            callback=callback,
            finished_callback=finished_callback,
            max_workers=max_workers,
            executor_type=executor_type,
            executor_options=executor_options,
            executor=executor,
            job=job,
        )
    else:
        args = []
        if fn_args:
            args.extend(fn_args)
        if fn_kwargs:
            args.extend(fn_kwargs)
        output = []
        job.job_output = []
        for data in fn_data:
            logger.debug(f"Running job {job.job_id} with data {data}")
            logger.debug(f"Job Status: {job.job_status}")
            if job.cancelled():
                break
            result = fn(data, *args)
            job.job_output.append(result)
            output.append(result)
            if callback:
                callback(result)
    if finished_callback:
        finished_callback(output)
    return output


@dataclass
class Job:
    """
        This class defines a job.
        possible statuses:
        - pending
        - running
        - finished
        - cancelled
        - error
        Arguments:
        job_data:         data to be passed to the function
        job_fn:           function to be run
        job_args:         arguments to be passed to the function
        job_kwargs:       keyword arguments to be passed to the function
        callback:         callback function to be run after each iteration
        suppress_errors:  suppress exceptions in the job function and store to job_exceptions
        threading:        True/False run the job in a thread pool
        executor:         executor to be used for the job,
                            you can provide an executor to run the job in a thread using a defined executor
        executor_options: options to be passed to the threader if no executor is set (see threading.threader)

        Properties:
        job_status:      current status of the job
        job_id:          id of the job
        job_output:      output of the job
        job_exceptions:  store of exceptions logged by the job

        Usage Example:
        Define the job:
        job = Job(job_data, job_fn, job_args, job_kwargs, threading=True, executor_options=executor_options)
        Start the job:
        job.start()
        Get the job output if needed:
        output_data = job.output_data

        Cancel the job:
        job.cancel() # raises CancelledJobException and cleanly shuts down all threads attached to the job. Saving any output that has been generated.

        Check status of the job:
        job.cancelled() # True
    """

    job_id: Union[str, int]
    job_data: Iterable
    job_status: str = field(default="pending")
    job_fn: Callable = field(default_factory=lambda: None)
    job_args: Iterable = field(default_factory=tuple)
    job_kwargs: dict = field(default_factory=dict)
    job_output: Any = field(default=None)
    callback: Callable = field(default=None)
    threaded: bool = field(default=False)
    executor_options: dict = field(default_factory=dict)
    executor: Union[ThreadPoolExecutor, ProcessPoolExecutor] = field(default=None)
    suppress_errors: bool = field(default=False)
    thread_type: str = field(default="thread")

    # dict containing the index of the failed arguments, the exception and the values
    job_exceptions: Dict[int, List[Tuple[JobErrorException, Any]]] = field(
        default_factory=dict
    )

    run_count: int = 0

    def cancel(self) -> None:
        """
        Cancel the job.
        """
        # self.set_status("cancelled")
        message = f"Job {self.job_id} cancelled"
        self.end("cancelled")
        raise CancelledJobException(message, job_id=self.job_id, job=self)

    def finish(self) -> None:
        """
        Finish the job.
        """
        self.end("finished")

    def run(self, *args) -> None:
        """
        Run the job.
        """
        self.set_status("running")

    def set_status(self, status: str) -> None:
        """
        Set the job status.
        """
        if status not in JOB_STATUSES:
            raise ValueError(
                f"Invalid job status: {status} must be one of {JOB_STATUSES}"
            )
        self.job_status = status

    def get_result(self) -> Any:
        """
        get job result
        """
        if self.job_output:
            return self.job_output

    def exception(self, exception: Exception, args, kwargs) -> None:
        """
        Set the exception.
        """
        self.error = True
        self.job_status = "error"
        self.job_exceptions[self.run_count] = [(exception, args, kwargs)]

    def start(self) -> None:
        """
        Start the job.
        """
        if self.running():
            raise JobRunningException(
                f"Job {self.job_id} is already running.", job=self, job_id=self.job_id
            )
        elif self.cancelled():
            message = f"Job {self.job_id} is cancelled."
            raise CancelledJobException(job=self, message=message, job_id=self.job_id)
        self.run()
        if not self.executor and self.threaded:
            self.executor = get_executor("thread", self.executor_options)
        self.run_count += 1
        run_job(
            self.__fn,
            self.job_data,
            fn_args=self.job_args,
            fn_kwargs=self.job_kwargs,
            callback=self.callback,
            job=self,
            threaded=self.threaded,
            executor_options=self.executor_options,
            executor=self.executor,
        )
        if not self.errored() and not self.cancelled():
            self.finish()

    def end(self, status="finished") -> None:
        """
        End the job.
        """
        if self.running():
            if self.executor:
                self.executor.shutdown(wait=False)
                del self.executor
                self.executor = None
        self.set_status(status)

    def __fn(self, *args, **kwargs) -> Callable:
        """
        Get the function.
        """
        try:
            if self.cancelled():
                raise CancelledJobException(
                    f"Job {self.job_id} is cancelled.", job=self, job_id=self.job_id
                )
            self.run_count += 1
            return self.job_fn(*args, **kwargs)
        except CancelledJobException:
            self.cancel()
        except Exception as e:
            self.exception(e, args, kwargs)
            if not self.suppress_errors:
                self.end("error")
                raise e

    # status checks
    def ended(self) -> bool:
        """
        Check if the job is ended.
        """
        return self.job_status in ENDED_STATUSES

    def cancelled(self) -> bool:
        """
        Check if the job is cancelled.
        """
        return self.job_status == "cancelled"

    def pending(self) -> bool:
        """
        Check if the job is pending.
        """
        return self.job_status == "pending"

    def finished(self) -> bool:
        """
        Check if the job is finished.
        """
        return self.job_status == "finished"

    def running(self) -> bool:
        """
        Check if the job is running.
        """
        return self.job_status in RUNNING_STATUSES

    def errored(self) -> bool:
        """
        Check if the job is errored.
        """
        return self.job_status == "error"

    def exceptions_count(self) -> int:
        """
        Get the number of exceptions.
        """
        return len(self.job_exceptions)

    def get_exceptions(self) -> List[Tuple[JobErrorException, Any]]:
        """
        Get the exceptions.
        """
        return self.job_exceptions.values()


@dataclass
class Jobs:
    jobs: Dict[str, Job] = field(default_factory=dict)

    def create_job(
        self,
        job_id,
        job_fn,
        job_data,
        job_args=None,
        job_kwargs=None,
        callback=None,
        threaded=False,
        executor_options=None,
        executor=None,
        suppress_errors=False,
        thread_type="thread",
    ):

        job = Job(
            job_id=job_id,
            job_data=job_data,
            job_fn=job_fn,
            job_args=job_args,
            job_kwargs=job_kwargs,
            callback=callback,
            threaded=threaded,
            executor_options=executor_options,
            executor=executor,
            suppress_errors=suppress_errors,
            thread_type=thread_type,
        )
        self.add_job(job)
        return job

    def add_job(self, job: Job) -> None:
        """
        Add a job to the list of jobs.
        """
        self.jobs[job.job_id] = job

    def start_job(self, job_id: str) -> None:
        """
        Start a job.
        """
        self.jobs[job_id].start()

    def cancel_job(self, job_id: Union[str, int]) -> None:
        """
        Cancel a job.
        """
        self.jobs[job_id].cancel()

    def get_job(self, job_id: Union[str, int]) -> Job:
        """
        Get a job.
        """
        return self.jobs[job_id]

    def delete_job(self, job_id: Union[str, int]) -> None:
        """
        Delete a job.
        """
        del self.jobs[job_id]

    def get_job_status(self, job_id: Union[str, int]) -> str:
        """
        Get status of a job.
        """
        return self.jobs[job_id].job_status

    def set_job_status(self, job_id: Union[str, int], status: str) -> None:
        """
        Set the status of a job.
        """
        self.jobs[job_id].set_status(status)

    def get_running_jobs(self) -> Dict[str, Job]:
        """
        return dict of running jobs
        """
        return {job_id: job for job_id, job in self.jobs.items() if job.running()}

    def get_finished_jobs(self) -> Dict[str, Job]:
        """
        return dict of running jobs
        """
        return {job_id: job for job_id, job in self.jobs.items() if job.finished()}

    def get_failed_jobs(self) -> Dict[str, Job]:
        """
        get dict of jobs that failed
        """
        return {job_id: job for job_id, job in self.jobs.items() if job.errored()}

    def get_cancelled_jobs(self) -> Dict[str, Job]:
        return {job_id: job for job_id, job in self.jobs.items() if job.cancelled()}

    def get_jobs(self) -> Dict[str, Job]:
        """
        Get the list of jobs.
        """
        return self.jobs

    def __getitem__(self, job_id: Union[str, int]) -> Job:
        """
        Get the job.
        """
        return self.jobs[job_id]

    def __setitem__(self, job_id: Union[str, int], job: Job) -> None:
        """
        Set the job.
        """
        self.jobs[job_id] = job

    def __iadd__(self, job: Job) -> "Jobs":
        """
        Add a job to the list of jobs.
        """
        self.add_job(job)
        return self

    def __add__(self, job: Job) -> "Jobs":
        """
        Add a job to the list of jobs.
        """
        self.add_job(job)
        return self

    def __contains__(self, job_id: Union[str, int]) -> bool:
        """
        Check if the job is in the list of jobs.
        """
        return job_id in self.jobs
