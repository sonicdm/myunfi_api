class JobException(Exception):
    def __init__(self, message=None, job_id=None, job=None) -> None:
        self.job_id = job_id
        self.job = job
        super().__init__(message)


class CancelledJobException(JobException):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class JobRunningException(JobException):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class PausedJobException(JobException):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class JobErrorException(JobException):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


